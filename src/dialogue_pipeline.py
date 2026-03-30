"""対話形式XMLから複数話者音声を生成するパイプラインモジュール.

US3: 対話形式音声の生成
対話形式XMLを解析し、3話者（ナレーター、博士A、助手B）による音声ファイルを生成する。
"""

from __future__ import annotations

import argparse
import io
import logging
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import numpy as np
import soundfile as sf

from src.chapter_processor import load_sound
from src.dict_manager import get_xml_content_hash, load_dict
from src.llm_reading_generator import apply_llm_readings
from src.number_normalizer import normalize_numbers
from src.reading_dict import apply_reading_rules

logger = logging.getLogger(__name__)

# 効果音セグメントの話者ID（実在話者と衝突しない識別子）
_SOUND_EFFECT_SPEAKER_ID = "__sound_effect__"

# Module-level reading dictionary (set via init_readings)
_READINGS: dict[str, str] = {}

# 日本語文字のUnicode範囲（ひらがな、カタカナ、漢字）
_JAPANESE_PATTERN = re.compile(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]")


def init_readings(dict_source_path: Path | None) -> None:
    """Initialize reading dictionary from source file.

    Args:
        dict_source_path: Path to the original XML/MD file for dictionary lookup.
                         If None, readings dictionary will be empty.
    """
    global _READINGS
    if dict_source_path is not None and dict_source_path.exists():
        _READINGS = load_dict(dict_source_path)
        if _READINGS:
            logger.info("Loaded %d readings from dict for: %s", len(_READINGS), dict_source_path.name)
        else:
            logger.warning("No dictionary found for: %s", dict_source_path.name)
    else:
        _READINGS = {}
        if dict_source_path is not None:
            logger.warning("Dict source file not found: %s", dict_source_path)


def apply_readings_to_text(text: str) -> str:
    """Apply reading rules and dictionary to text for TTS.

    Applies in order:
    1. Number normalization (123 → ひゃくにじゅうさん)
    2. Static reading rules (common technical terms)
    3. LLM-generated readings (per-book dictionary)

    Args:
        text: Input text to process

    Returns:
        Text with readings applied
    """
    # 1. Normalize numbers (must be first - before reading rules)
    text = normalize_numbers(text)

    # 2. Apply static reading rules (critical terms like SRE, API, AWS)
    text = apply_reading_rules(text)

    # 3. Apply LLM-generated readings if available
    if _READINGS:
        text = apply_llm_readings(text, _READINGS)

    return text


def is_speakable_text(text: str) -> bool:
    """テキストがTTS合成可能かどうかを判定する.

    日本語文字（ひらがな、カタカナ、漢字）を1文字以上含む場合にTrueを返す。

    Args:
        text: 判定するテキスト

    Returns:
        TTS合成可能な場合True
    """
    if not text:
        return False
    return bool(_JAPANESE_PATTERN.search(text))


# デフォルト話者スタイルIDマッピング
DEFAULT_STYLE_MAPPING: dict[str, int] = {
    "narrator": 13,  # 青山龍星
    "SPEAKER_A": 11,  # 玄野武宏（博士）- 67は未対応のため変更
    "SPEAKER_B": 2,  # 四国めたん（助手）
}


@dataclass
class Speaker:
    """話者を表すデータクラス.

    Attributes:
        id: 話者識別子 ("narrator", "SPEAKER_A", "SPEAKER_B")
        role: 話者の役割説明
        voicevox_style_id: VOICEVOXのスタイルID
        character_name: キャラクター名
    """

    id: str
    role: str
    voicevox_style_id: int
    character_name: str


def parse_dialogue_xml(xml_str_or_path: str) -> list[dict[str, Any]]:
    """対話形式XMLを解析してセクションリストを返す.

    XMLの文字列またはファイルパスを受け取り、各セクションの情報を
    dictのリストとして返す。

    Args:
        xml_str_or_path: XML文字列またはファイルパス文字列

    Returns:
        セクション情報のリスト。各dictは以下のキーを持つ:
        - section_number: セクション番号 (str)
        - section_title: セクションタイトル (str)
        - introduction: {"speaker": str, "text": str} または None
        - utterances: [{"speaker": str, "text": str}, ...]
        - conclusion: {"speaker": str, "text": str} または None

    Raises:
        ValueError: XML文字列が空の場合
        xml.etree.ElementTree.ParseError: XMLの解析に失敗した場合
    """
    if not xml_str_or_path:
        raise ValueError("xml_str_or_path must not be empty")

    # ファイルパスかどうかを判定
    path = Path(xml_str_or_path)
    if path.exists() and path.is_file():
        xml_content = path.read_text(encoding="utf-8")
    else:
        xml_content = xml_str_or_path

    # XMLパース（ParseErrorは自然に伝播させる）
    root = ElementTree.fromstring(xml_content)

    sections: list[dict[str, Any]] = []

    for dialogue_section in root.iter("dialogue-section"):
        section_number = dialogue_section.get("number", "")
        section_title = dialogue_section.get("title", "")

        # introduction パース
        intro_elem = dialogue_section.find("introduction")
        if intro_elem is not None:
            intro_text = (intro_elem.text or "").strip()
            introduction: dict[str, str] | None = {
                "speaker": intro_elem.get("speaker", "narrator"),
                "text": intro_text,
            }
        else:
            introduction = None

        # dialogue/utterance パース
        utterances: list[dict[str, str]] = []
        dialogue_elem = dialogue_section.find("dialogue")
        if dialogue_elem is not None:
            for utterance_elem in dialogue_elem.findall("utterance"):
                utterances.append(
                    {
                        "speaker": utterance_elem.get("speaker", ""),
                        "text": (utterance_elem.text or "").strip(),
                    }
                )

        # conclusion パース
        conclusion_elem = dialogue_section.find("conclusion")
        if conclusion_elem is not None:
            conclusion: dict[str, str] | None = {
                "speaker": conclusion_elem.get("speaker", "narrator"),
                "text": (conclusion_elem.text or "").strip(),
            }
        else:
            conclusion = None

        sections.append(
            {
                "section_number": section_number,
                "section_title": section_title,
                "introduction": introduction,
                "utterances": utterances,
                "conclusion": conclusion,
            }
        )

    return sections


def get_style_id(
    speaker_id: str,
    style_mapping: dict[str, int] | None = None,
) -> int:
    """話者IDに対応するVOICEVOXスタイルIDを返す.

    Args:
        speaker_id: 話者識別子 ("narrator", "SPEAKER_A", "SPEAKER_B" など)
        style_mapping: カスタムスタイルIDマッピング。Noneの場合はデフォルトを使用。

    Returns:
        VOICEVOXスタイルID (int)

    Raises:
        TypeError: speaker_id が None の場合
        ValueError: 話者IDがマッピングに存在しない場合
        KeyError: 話者IDがマッピングに存在しない場合
    """
    if speaker_id is None:
        raise TypeError("speaker_id must not be None")

    mapping = style_mapping if style_mapping is not None else DEFAULT_STYLE_MAPPING

    if speaker_id not in mapping:
        raise ValueError(f"Unknown speaker_id: {speaker_id!r}")

    return mapping[speaker_id]


def synthesize_utterance(
    text: str,
    speaker_id: str,
    synthesizer: Any,
    speed_scale: float | None = None,
) -> tuple[np.ndarray, int]:
    """発話テキストから音声データを生成する.

    Args:
        text: 発話テキスト
        speaker_id: 話者識別子 ("narrator", "SPEAKER_A", "SPEAKER_B")
        synthesizer: VoicevoxSynthesizerインスタンス（またはモック）
        speed_scale: 読み上げ速度スケール（Noneの場合はデフォルト）

    Returns:
        (波形データ as numpy.ndarray, サンプルレート as int)

    Raises:
        ValueError: text が空文字列の場合
        TypeError: text が None の場合
        ValueError: 未知の話者IDが指定された場合
    """
    if text is None:
        raise TypeError("text must not be None")

    if not text:
        raise ValueError("text must not be empty")

    # Apply reading rules and dictionary before TTS
    processed_text = apply_readings_to_text(text)

    # 話者IDからスタイルIDを取得（未知IDはエラー）
    style_id = get_style_id(speaker_id)

    # 音声合成
    kwargs: dict[str, Any] = {"style_id": style_id}
    if speed_scale is not None:
        kwargs["speed_scale"] = speed_scale

    wav_bytes: bytes = synthesizer.synthesize(processed_text, **kwargs)

    # バイト列をnumpy配列に変換
    with io.BytesIO(wav_bytes) as buf:
        waveform, sample_rate = sf.read(buf)

    return np.asarray(waveform, dtype=np.float32), int(sample_rate)


def get_chapter_number(section_number: str) -> str:
    """セクション番号からチャプター番号を抽出する.

    Args:
        section_number: セクション番号 (例: "2.1", "2.2", "3")

    Returns:
        チャプター番号 (例: "2", "3")。ドットがない場合はそのまま返す。
        空文字列の場合は "0" を返す。
    """
    if not section_number:
        return "0"
    # "2.1" -> "2", "3" -> "3"
    return section_number.split(".")[0]


def concatenate_section_audio(
    segments: list[tuple[np.ndarray, int, str]],
    silence_duration: float = 0.5,
    output_path: Path | str | None = None,
) -> tuple[np.ndarray, int]:
    """複数の音声セグメントを結合する.

    同一話者の連続セグメントは無音なしで結合し、
    話者が変わる場合のみ無音を挿入する。

    Args:
        segments: 音声セグメントのリスト。各要素は (waveform, sample_rate, speaker_id) のタプル。
        silence_duration: 話者交代時の無音時間（秒）
        output_path: 結合結果の保存先パス。Noneの場合は保存しない。

    Returns:
        (結合された波形データ as numpy.ndarray, サンプルレート as int)

    Raises:
        ValueError: segments が空リストの場合
    """
    if not segments:
        raise ValueError("segments must not be empty")

    sample_rate = segments[0][1]
    parts: list[np.ndarray] = []

    for i, (waveform, sr, speaker) in enumerate(segments):
        parts.append(np.asarray(waveform, dtype=np.float32))
        # 最後のセグメント以外で、次の話者が異なる場合のみ無音を挿入
        if i < len(segments) - 1:
            next_speaker = segments[i + 1][2]
            if speaker != next_speaker:
                silence_samples = int(sr * silence_duration)
                parts.append(np.zeros(silence_samples, dtype=np.float32))

    combined = np.concatenate(parts)

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(output_path), combined, sample_rate)
        logger.info("Saved combined audio: %s", output_path)

    return combined, sample_rate


def _synthesize_section(
    section: dict[str, Any],
    synthesizer: Any,
    speed_scale: float,
) -> list[tuple[np.ndarray, int, str]]:
    """1セクションの音声セグメントを生成する.

    Args:
        section: セクション情報 (parse_dialogue_xml の出力要素)
        synthesizer: VoicevoxSynthesizerインスタンス
        speed_scale: 読み上げ速度スケール

    Returns:
        音声セグメントのリスト。各要素は (waveform, sample_rate, speaker_id) のタプル。
    """
    section_number = section["section_number"]
    section_title = section.get("section_title", "")
    logger.info(
        "Processing section %s: %s",
        section_number or "(no number)",
        section_title[:50] + "..." if len(section_title) > 50 else section_title,
    )

    segments: list[tuple[np.ndarray, int, str]] = []

    # introduction
    intro = section.get("introduction")
    if intro and intro.get("text"):
        intro_text = intro["text"]
        intro_speaker = intro["speaker"]
        if is_speakable_text(intro_text):
            logger.info(
                "  [intro] speaker=%s, len=%d: %s",
                intro_speaker,
                len(intro_text),
                intro_text[:80] + "..." if len(intro_text) > 80 else intro_text,
            )
            waveform, sr = synthesize_utterance(
                text=intro_text,
                speaker_id=intro_speaker,
                synthesizer=synthesizer,
                speed_scale=speed_scale,
            )
            segments.append((waveform, sr, intro_speaker))
        else:
            logger.warning("  [intro] skipped (no speakable text): %r", intro_text)

    # utterances
    for i, utterance in enumerate(section.get("utterances", [])):
        if utterance.get("text"):
            utt_text = utterance["text"]
            utt_speaker = utterance["speaker"]
            if is_speakable_text(utt_text):
                logger.info(
                    "  [utterance %d] speaker=%s, len=%d: %s",
                    i + 1,
                    utt_speaker,
                    len(utt_text),
                    utt_text[:80] + "..." if len(utt_text) > 80 else utt_text,
                )
                waveform, sr = synthesize_utterance(
                    text=utt_text,
                    speaker_id=utt_speaker,
                    synthesizer=synthesizer,
                    speed_scale=speed_scale,
                )
                segments.append((waveform, sr, utt_speaker))
            else:
                logger.warning("  [utterance %d] skipped (no speakable text): %r", i + 1, utt_text)

    # conclusion
    conclusion = section.get("conclusion")
    if conclusion and conclusion.get("text"):
        concl_text = conclusion["text"]
        concl_speaker = conclusion["speaker"]
        if is_speakable_text(concl_text):
            logger.info(
                "  [conclusion] speaker=%s, len=%d: %s",
                concl_speaker,
                len(concl_text),
                concl_text[:80] + "..." if len(concl_text) > 80 else concl_text,
            )
            waveform, sr = synthesize_utterance(
                text=concl_text,
                speaker_id=concl_speaker,
                synthesizer=synthesizer,
                speed_scale=speed_scale,
            )
            segments.append((waveform, sr, concl_speaker))
        else:
            logger.warning("  [conclusion] skipped (no speakable text): %r", concl_text)

    return segments


def process_dialogue_sections(
    sections: list[dict[str, Any]],
    synthesizer: Any,
    output_dir: Path,
    speed_scale: float = 1.0,
    chapter_sound: np.ndarray | None = None,
    section_sound: np.ndarray | None = None,
) -> list[Path]:
    """対話セクションリストから音声ファイルを生成する統合関数.

    各セクションの introduction, utterances, conclusion を合成し、
    チャプター単位でWAVファイルとして保存する。
    チャプター開始時にチャプター効果音、セクション開始時にセクション効果音を挿入可能。

    Args:
        sections: parse_dialogue_xml() が返すセクションリスト
        synthesizer: VoicevoxSynthesizerインスタンス
        output_dir: 音声ファイルの出力ディレクトリ
        speed_scale: 読み上げ速度スケール
        chapter_sound: チャプター開始時の効果音 (numpy配列, None=なし)
        section_sound: セクション開始時の効果音 (numpy配列, None=なし)

    Returns:
        生成したWAVファイルのパスリスト
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # セクションをチャプター番号でグループ化
    chapters: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for section in sections:
        chapter_num = get_chapter_number(section["section_number"])
        chapters[chapter_num].append(section)

    logger.info("Grouped %d sections into %d chapters", len(sections), len(chapters))

    generated: list[Path] = []
    sample_rate = 24000  # VOICEVOX標準サンプルレート

    # チャプター番号順にソートして処理
    for chapter_num in sorted(chapters.keys(), key=lambda x: (int(x) if x.isdigit() else 0, x)):
        chapter_sections = chapters[chapter_num]
        logger.info(
            "Processing chapter %s (%d sections)",
            chapter_num,
            len(chapter_sections),
        )

        # チャプター内の全セクションの音声セグメントを収集
        all_segments: list[tuple[np.ndarray, int, str]] = []

        # チャプター効果音を挿入
        if chapter_sound is not None:
            all_segments.append((chapter_sound, sample_rate, _SOUND_EFFECT_SPEAKER_ID))
            logger.info("  Inserted chapter sound effect")

        for i, section in enumerate(chapter_sections):
            # 2番目以降のセクションにセクション効果音を挿入
            if i > 0 and section_sound is not None:
                all_segments.append((section_sound, sample_rate, _SOUND_EFFECT_SPEAKER_ID))
                logger.info("  Inserted section sound effect before section %s", section.get("section_number", ""))

            section_segments = _synthesize_section(section, synthesizer, speed_scale)
            all_segments.extend(section_segments)

        if all_segments:
            output_path = output_dir / f"chapter_{chapter_num.zfill(3)}.wav"
            concatenate_section_audio(all_segments, output_path=output_path)
            generated.append(output_path)
            logger.info("Generated chapter audio: %s", output_path)

    return generated


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """CLIコマンドライン引数を解析する.

    Args:
        args: 引数リスト（Noneの場合は sys.argv を使用）

    Returns:
        解析済みの引数 Namespace オブジェクト
    """
    parser = argparse.ArgumentParser(
        description="対話形式XMLから複数話者音声を生成する",
        prog="dialogue_pipeline",
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="対話形式XMLファイルパス",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="./output",
        help="出力ディレクトリ（デフォルト: ./output）",
    )
    parser.add_argument(
        "--narrator-style",
        type=int,
        default=13,
        help="ナレーターのVOICEVOXスタイルID（デフォルト: 13）",
    )
    parser.add_argument(
        "--speaker-a-style",
        type=int,
        default=11,
        help="博士（A）のスタイルID（デフォルト: 11）",
    )
    parser.add_argument(
        "--speaker-b-style",
        type=int,
        default=2,
        help="助手（B）のスタイルID（デフォルト: 2）",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="読み上げ速度（デフォルト: 1.0）",
    )
    parser.add_argument(
        "--voicevox-dir",
        default="./voicevox_core",
        help="VOICEVOXディレクトリ（デフォルト: ./voicevox_core）",
    )
    parser.add_argument(
        "--acceleration-mode",
        default="AUTO",
        help="VOICEVOX加速モード（デフォルト: AUTO）",
    )
    parser.add_argument(
        "--dict-source",
        type=str,
        default=None,
        help="元のXML/MDファイルパス（読み辞書参照用）",
    )
    parser.add_argument(
        "--chapter-sound",
        type=str,
        default="assets/sounds/chapter.mp3",
        help="チャプター開始時の効果音ファイル（デフォルト: assets/sounds/chapter.mp3）",
    )
    parser.add_argument(
        "--section-sound",
        type=str,
        default="assets/sounds/section.mp3",
        help="セクション開始時の効果音ファイル（デフォルト: assets/sounds/section.mp3）",
    )
    parser.add_argument(
        "--no-chapter-sound",
        action="store_true",
        default=False,
        help="チャプター効果音を無効化する",
    )
    parser.add_argument(
        "--no-section-sound",
        action="store_true",
        default=False,
        help="セクション効果音を無効化する",
    )

    parsed = parser.parse_args(args)

    # --no-chapter-sound / --no-section-sound が指定された場合はNoneに設定
    if parsed.no_chapter_sound:
        parsed.chapter_sound = None
    if parsed.no_section_sound:
        parsed.section_sound = None

    return parsed


def main() -> int:
    """エントリーポイント.

    Returns:
        終了コード (0: 成功, 1: 入力エラー, 2: VOICEVOX初期化エラー, 3: 音声生成エラー)
    """

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    args = parse_args()

    # 入力ファイル確認
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error("Input file not found: %s", input_path)
        return 1

    # Initialize reading dictionary from source file
    dict_source_path = Path(args.dict_source) if args.dict_source else None
    init_readings(dict_source_path)

    # Note: カスタムスタイル設定は将来のバージョンで実装予定
    # 現在は DEFAULT_SPEAKERS を使用
    _ = (args.narrator_style, args.speaker_a_style, args.speaker_b_style)  # noqa: F841

    try:
        # XMLパース
        sections = parse_dialogue_xml(str(input_path))
        logger.info("Parsed %d sections", len(sections))
    except Exception as e:
        logger.error("Failed to parse dialogue XML: %s", e)
        return 1

    # ハッシュベースの出力ディレクトリを生成（元のXMLファイルから計算）
    if dict_source_path and dict_source_path.exists():
        content_hash = get_xml_content_hash(dict_source_path)
    else:
        logger.error("--dict-source is required for hash-based output directory")
        return 1
    output_base = Path(args.output)
    output_dir = output_base / content_hash
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Output directory: %s", output_dir)

    try:
        # VOICEVOX初期化
        from src.voicevox_client import VoicevoxConfig, VoicevoxSynthesizer

        config = VoicevoxConfig(
            acceleration_mode=args.acceleration_mode,
            speed_scale=args.speed,
        )
        synthesizer = VoicevoxSynthesizer(config)
        synthesizer.initialize()

        # 必要な話者モデルのみロード（全モデルロードを回避してGPUメモリ節約）
        for style_id in DEFAULT_STYLE_MAPPING.values():
            logger.info("Loading voice model for style_id=%d", style_id)
            synthesizer.load_model_for_style_id(style_id)
    except Exception as e:
        logger.error("Failed to initialize VOICEVOX: %s", e)
        return 2

    # 効果音ファイルの読み込み
    chapter_sound = None
    section_sound = None

    if args.chapter_sound:
        sound_path = Path(args.chapter_sound)
        if sound_path.exists():
            chapter_sound = load_sound(sound_path)
            logger.info("Loaded chapter sound: %s", sound_path)
        else:
            logger.warning("Chapter sound file not found: %s", sound_path)

    if args.section_sound:
        sound_path = Path(args.section_sound)
        if sound_path.exists():
            section_sound = load_sound(sound_path)
            logger.info("Loaded section sound: %s", sound_path)
        else:
            logger.warning("Section sound file not found: %s", sound_path)

    try:
        # 音声生成
        generated = process_dialogue_sections(
            sections=sections,
            synthesizer=synthesizer,
            output_dir=output_dir,
            speed_scale=args.speed,
            chapter_sound=chapter_sound,
            section_sound=section_sound,
        )
        logger.info("Generated %d audio files in %s", len(generated), output_dir)
    except Exception as e:
        logger.error("Failed to generate audio: %s", e)
        return 3

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
