"""対話XMLの長文テキストを分割するパイプラインモジュール.

dialogue_book.xml 内の長いテキスト（introduction, utterance, conclusion）を
TTS合成に適した長さに分割する。
"""

from __future__ import annotations

import argparse
import logging
import xml.etree.ElementTree as ET
from pathlib import Path

logger = logging.getLogger(__name__)

# デフォルトの最大文字数
DEFAULT_MAX_LENGTH = 300


def split_text(text: str, max_length: int = DEFAULT_MAX_LENGTH) -> list[str]:
    """長いテキストを句点・読点で分割する.

    Args:
        text: 分割するテキスト
        max_length: 1チャンクの最大文字数

    Returns:
        分割されたテキストのリスト
    """
    if not text or len(text) <= max_length:
        return [text] if text else []

    chunks: list[str] = []
    current = ""

    # 句点で分割
    for char in text:
        current += char
        if char in "。．.！？":
            if len(current) >= max_length:
                chunks.append(current.strip())
                current = ""

    if current.strip():
        chunks.append(current.strip())

    # それでも長すぎるチャンクがあれば、読点で再分割
    result: list[str] = []
    for chunk in chunks:
        if len(chunk) <= max_length:
            result.append(chunk)
        else:
            # 読点で分割
            sub_chunks: list[str] = []
            sub_current = ""
            for char in chunk:
                sub_current += char
                if char in "、，," and len(sub_current) >= max_length // 2:
                    sub_chunks.append(sub_current.strip())
                    sub_current = ""
            if sub_current.strip():
                sub_chunks.append(sub_current.strip())
            result.extend(sub_chunks if sub_chunks else [chunk])

    return result if result else [text]


def process_dialogue_xml(
    input_path: Path,
    output_path: Path,
    max_length: int = DEFAULT_MAX_LENGTH,
) -> dict[str, int]:
    """対話XMLを読み込み、長文を分割して出力する.

    Args:
        input_path: 入力XMLファイルパス
        output_path: 出力XMLファイルパス
        max_length: 1テキストの最大文字数

    Returns:
        処理統計 {"sections": int, "split_count": int, "original_count": int}
    """
    tree = ET.parse(input_path)
    root = tree.getroot()

    stats = {"sections": 0, "split_count": 0, "original_count": 0}

    for section in root.iter("dialogue-section"):
        stats["sections"] += 1
        section_num = section.get("number", "")
        section_title = section.get("title", "")[:30]

        # introduction を処理
        intro = section.find("introduction")
        if intro is not None and intro.text:
            original_text = intro.text.strip()
            if len(original_text) > max_length:
                chunks = split_text(original_text, max_length)
                logger.info(
                    "Section %s: introduction を %d チャンクに分割 (元: %d文字)",
                    section_num or section_title,
                    len(chunks),
                    len(original_text),
                )
                # 最初のチャンクをintroductionに残す
                intro.text = chunks[0]
                stats["split_count"] += len(chunks) - 1
                stats["original_count"] += 1

                # 残りをdialogue内にnarrator発話として追加
                dialogue = section.find("dialogue")
                if dialogue is None:
                    dialogue = ET.SubElement(section, "dialogue")

                # 既存のutterancesを取得
                existing_utterances = list(dialogue.findall("utterance"))

                # dialogueをクリア
                for utt in existing_utterances:
                    dialogue.remove(utt)

                # 残りのintroチャンクをnarrator発話として先頭に追加
                for chunk in chunks[1:]:
                    new_utt = ET.SubElement(dialogue, "utterance")
                    new_utt.set("speaker", "narrator")
                    new_utt.text = chunk

                # 既存のutterancesを戻す
                for utt in existing_utterances:
                    dialogue.append(utt)

        # dialogue/utterance を処理
        dialogue = section.find("dialogue")
        if dialogue is not None:
            utterances = list(dialogue.findall("utterance"))
            for utt in utterances:
                if utt.text and len(utt.text.strip()) > max_length:
                    original_text = utt.text.strip()
                    speaker = utt.get("speaker", "A")
                    chunks = split_text(original_text, max_length)
                    logger.info(
                        "Section %s: utterance(%s) を %d チャンクに分割 (元: %d文字)",
                        section_num or section_title,
                        speaker,
                        len(chunks),
                        len(original_text),
                    )

                    # 最初のチャンクを元のutteranceに設定
                    utt.text = chunks[0]
                    stats["split_count"] += len(chunks) - 1
                    stats["original_count"] += 1

                    # 残りを同じspeakerの新しいutteranceとして追加
                    utt_index = list(dialogue).index(utt)
                    for i, chunk in enumerate(chunks[1:], 1):
                        new_utt = ET.Element("utterance")
                        new_utt.set("speaker", speaker)
                        new_utt.text = chunk
                        dialogue.insert(utt_index + i, new_utt)

        # conclusion を処理
        conclusion = section.find("conclusion")
        if conclusion is not None and conclusion.text:
            original_text = conclusion.text.strip()
            if len(original_text) > max_length:
                chunks = split_text(original_text, max_length)
                logger.info(
                    "Section %s: conclusion を %d チャンクに分割 (元: %d文字)",
                    section_num or section_title,
                    len(chunks),
                    len(original_text),
                )
                # 最後のチャンクをconclusionに残す
                conclusion.text = chunks[-1]
                stats["split_count"] += len(chunks) - 1
                stats["original_count"] += 1

                # 残りをdialogue末尾にnarrator発話として追加
                dialogue = section.find("dialogue")
                if dialogue is None:
                    dialogue = ET.SubElement(section, "dialogue")

                for chunk in chunks[:-1]:
                    new_utt = ET.SubElement(dialogue, "utterance")
                    new_utt.set("speaker", "narrator")
                    new_utt.text = chunk

    # インデント付きで出力
    _indent_xml(root)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

    return stats


def _indent_xml(elem: ET.Element, level: int = 0) -> None:
    """XMLにインデントを追加する."""
    indent = "\n" + "  " * level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
        for child in elem:
            _indent_xml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = indent
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """CLI引数をパースする."""
    parser = argparse.ArgumentParser(
        description="対話XMLの長文テキストを分割する",
        prog="dialogue_text_splitter",
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="入力XMLファイルパス (dialogue_book.xml)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="出力XMLファイルパス (省略時は入力ファイルを上書き)",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=DEFAULT_MAX_LENGTH,
        help=f"1テキストの最大文字数 (デフォルト: {DEFAULT_MAX_LENGTH})",
    )
    return parser.parse_args(args)


def main() -> int:
    """CLIエントリーポイント."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    args = parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        logger.error("入力ファイルが見つかりません: %s", input_path)
        return 1

    output_path = Path(args.output) if args.output else input_path

    try:
        stats = process_dialogue_xml(input_path, output_path, args.max_length)
        logger.info(
            "完了: %d セクション処理, %d テキストを %d チャンクに分割",
            stats["sections"],
            stats["original_count"],
            stats["original_count"] + stats["split_count"],
        )
        logger.info("出力: %s", output_path)
    except ET.ParseError as e:
        logger.error("XMLパースエラー: %s", e)
        return 1
    except Exception as e:
        logger.error("処理エラー: %s", e)
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
