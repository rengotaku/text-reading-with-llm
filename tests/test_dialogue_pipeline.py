"""Tests for dialogue_pipeline.py - Phase 4 RED Tests.

Phase 4 RED Tests - US3: 対話形式音声の生成
対話形式XMLから3話者（ナレーター、博士、助手）による音声ファイルを生成する機能のテスト。

Target module: src/dialogue_pipeline.py

Test coverage:
- T049: Speaker データクラスのテスト
- T050: 対話XMLパース関数 parse_dialogue_xml() のテスト
- T051: 話者別スタイルID取得 get_style_id() のテスト
- T052: 発話単位音声生成 synthesize_utterance() のテスト
- T053: セクション音声結合 concatenate_section_audio() のテスト
- T054: CLI引数パース parse_args() のテスト
"""

from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

# src/dialogue_pipeline.py はまだ未実装のため、ImportError をキャッチして
# テスト内で明示的に FAIL させる（skip ではなく FAIL）
try:
    from src.dialogue_pipeline import (
        Speaker,
        apply_readings_to_text,
        concatenate_section_audio,
        get_chapter_number,
        get_style_id,
        init_readings,
        is_speakable_text,
        parse_args,
        parse_dialogue_xml,
        synthesize_utterance,
    )

    _MODULE_AVAILABLE = True
except ImportError:
    _MODULE_AVAILABLE = False
    Speaker = None  # type: ignore[assignment,misc]
    apply_readings_to_text = None  # type: ignore[assignment]
    concatenate_section_audio = None  # type: ignore[assignment]
    get_chapter_number = None  # type: ignore[assignment]
    get_style_id = None  # type: ignore[assignment]
    init_readings = None  # type: ignore[assignment]
    is_speakable_text = None  # type: ignore[assignment]
    parse_args = None  # type: ignore[assignment]
    parse_dialogue_xml = None  # type: ignore[assignment]
    synthesize_utterance = None  # type: ignore[assignment]


def _require_module() -> None:
    """モジュールが未実装の場合にテストを FAIL させる。"""
    if not _MODULE_AVAILABLE:
        raise ImportError(
            "src.dialogue_pipeline is not yet implemented. Create src/dialogue_pipeline.py with the required functions."
        )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_DIALOGUE_XML = """\
<dialogue-book>
  <chapter number="1">
    <heading level="1">テスト章</heading>
    <dialogue-section number="1.1" title="テストセクション">
      <introduction speaker="narrator">
        この節では、テストについて説明します。
      </introduction>
      <dialogue>
        <utterance speaker="A">
          まず、基本的な概念から説明しましょう。
        </utterance>
        <utterance speaker="B">
          はい、お願いします。テストとは何ですか？
        </utterance>
        <utterance speaker="A">
          テストとは、ソフトウェアの品質を確認する手法です。
        </utterance>
      </dialogue>
      <conclusion speaker="narrator">
        以上がテストの基本的な説明でした。
      </conclusion>
    </dialogue-section>
  </chapter>
</dialogue-book>"""

SAMPLE_DIALOGUE_XML_MULTI_SECTION = """\
<dialogue-book>
  <chapter number="1">
    <heading level="1">テスト章</heading>
    <dialogue-section number="1.1" title="セクション1">
      <introduction speaker="narrator">導入1</introduction>
      <dialogue>
        <utterance speaker="A">発話A1</utterance>
        <utterance speaker="B">発話B1</utterance>
      </dialogue>
      <conclusion speaker="narrator">結論1</conclusion>
    </dialogue-section>
    <dialogue-section number="1.2" title="セクション2">
      <introduction speaker="narrator">導入2</introduction>
      <dialogue>
        <utterance speaker="A">発話A2</utterance>
        <utterance speaker="B">発話B2</utterance>
      </dialogue>
      <conclusion speaker="narrator">結論2</conclusion>
    </dialogue-section>
  </chapter>
</dialogue-book>"""


def _create_wav_bytes(samples: np.ndarray, sample_rate: int) -> bytes:
    """テスト用のWAVバイト列を生成する。"""
    import io

    import soundfile as sf

    buffer = io.BytesIO()
    sf.write(buffer, samples, sample_rate, format="WAV")
    return buffer.getvalue()


# ===========================================================================
# T049: Speaker データクラスのテスト
# ===========================================================================


class TestSpeaker:
    """Speaker データクラスの基本動作テスト。"""

    def test_speaker_narrator_creation(self) -> None:
        """ナレーターのSpeakerを正しく生成できる。"""
        _require_module()
        speaker = Speaker(
            id="narrator",
            role="導入・結論",
            voicevox_style_id=13,
            character_name="青山龍星",
        )
        assert speaker.id == "narrator"
        assert speaker.role == "導入・結論"
        assert speaker.voicevox_style_id == 13
        assert speaker.character_name == "青山龍星"

    def test_speaker_a_creation(self) -> None:
        """博士（A）のSpeakerを正しく生成できる。"""
        _require_module()
        speaker = Speaker(
            id="A",
            role="博士（説明役）",
            voicevox_style_id=11,
            character_name="玄野武宏",
        )
        assert speaker.id == "A"
        assert speaker.voicevox_style_id == 11

    def test_speaker_b_creation(self) -> None:
        """助手（B）のSpeakerを正しく生成できる。"""
        _require_module()
        speaker = Speaker(
            id="B",
            role="助手（質問役）",
            voicevox_style_id=2,
            character_name="四国めたん",
        )
        assert speaker.id == "B"
        assert speaker.voicevox_style_id == 2
        assert speaker.character_name == "四国めたん"

    def test_speaker_equality(self) -> None:
        """同じ値のSpeakerは等価である。"""
        _require_module()
        s1 = Speaker(id="A", role="博士", voicevox_style_id=11, character_name="玄野武宏")
        s2 = Speaker(id="A", role="博士", voicevox_style_id=11, character_name="玄野武宏")
        assert s1 == s2

    def test_speaker_inequality(self) -> None:
        """異なる値のSpeakerは不等である。"""
        _require_module()
        s1 = Speaker(id="A", role="博士", voicevox_style_id=11, character_name="玄野武宏")
        s2 = Speaker(id="B", role="助手", voicevox_style_id=2, character_name="四国めたん")
        assert s1 != s2

    def test_speaker_fields_are_required(self) -> None:
        """全フィールドが必須である。"""
        _require_module()
        with pytest.raises(TypeError):
            Speaker(id="A")  # type: ignore[call-arg]

    def test_speaker_voicevox_style_id_is_int(self) -> None:
        """voicevox_style_idがint型で保持される。"""
        _require_module()
        speaker = Speaker(id="narrator", role="ナレーター", voicevox_style_id=13, character_name="青山龍星")
        assert isinstance(speaker.voicevox_style_id, int)


# ===========================================================================
# T050: 対話XMLパース関数 parse_dialogue_xml() のテスト
# ===========================================================================


class TestParseDialogueXml:
    """parse_dialogue_xml()の動作テスト。"""

    def test_parse_single_section(self) -> None:
        """単一セクションのXMLをパースできる。"""
        _require_module()
        result = parse_dialogue_xml(SAMPLE_DIALOGUE_XML)
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_parse_section_number(self) -> None:
        """セクション番号が正しく取得される。"""
        _require_module()
        result = parse_dialogue_xml(SAMPLE_DIALOGUE_XML)
        first_section = result[0]
        assert first_section["section_number"] == "1.1"

    def test_parse_section_title(self) -> None:
        """セクションタイトルが正しく取得される。"""
        _require_module()
        result = parse_dialogue_xml(SAMPLE_DIALOGUE_XML)
        first_section = result[0]
        assert first_section["section_title"] == "テストセクション"

    def test_parse_introduction(self) -> None:
        """introduction部分が正しくパースされる。"""
        _require_module()
        result = parse_dialogue_xml(SAMPLE_DIALOGUE_XML)
        first_section = result[0]
        assert "introduction" in first_section
        assert first_section["introduction"]["speaker"] == "narrator"
        assert "テストについて説明" in first_section["introduction"]["text"]

    def test_parse_utterances(self) -> None:
        """dialogue内のutteranceが正しくパースされる。"""
        _require_module()
        result = parse_dialogue_xml(SAMPLE_DIALOGUE_XML)
        first_section = result[0]
        utterances = first_section["utterances"]
        assert len(utterances) == 3
        assert utterances[0]["speaker"] == "A"
        assert utterances[1]["speaker"] == "B"
        assert utterances[2]["speaker"] == "A"

    def test_parse_utterance_text(self) -> None:
        """utteranceのテキストが正しく取得される。"""
        _require_module()
        result = parse_dialogue_xml(SAMPLE_DIALOGUE_XML)
        utterances = result[0]["utterances"]
        assert "基本的な概念" in utterances[0]["text"]
        assert "テストとは何ですか" in utterances[1]["text"]

    def test_parse_conclusion(self) -> None:
        """conclusion部分が正しくパースされる。"""
        _require_module()
        result = parse_dialogue_xml(SAMPLE_DIALOGUE_XML)
        first_section = result[0]
        assert "conclusion" in first_section
        assert first_section["conclusion"]["speaker"] == "narrator"
        assert "基本的な説明" in first_section["conclusion"]["text"]

    def test_parse_multiple_sections(self) -> None:
        """複数セクションを含むXMLをパースできる。"""
        _require_module()
        result = parse_dialogue_xml(SAMPLE_DIALOGUE_XML_MULTI_SECTION)
        assert len(result) == 2
        assert result[0]["section_number"] == "1.1"
        assert result[1]["section_number"] == "1.2"

    def test_parse_empty_xml_raises(self) -> None:
        """空のXML文字列でエラーが発生する。"""
        _require_module()
        with pytest.raises((ValueError, Exception)):
            parse_dialogue_xml("")

    def test_parse_invalid_xml_raises(self) -> None:
        """不正なXMLでエラーが発生する。"""
        _require_module()
        with pytest.raises((ValueError, Exception)):
            parse_dialogue_xml("<not-valid>")

    def test_parse_no_dialogue_sections(self) -> None:
        """dialogue-sectionがないXMLでは空リストが返る。"""
        _require_module()
        xml_no_sections = "<dialogue-book><chapter number='1'></chapter></dialogue-book>"
        result = parse_dialogue_xml(xml_no_sections)
        assert result == []

    def test_parse_xml_with_unicode(self) -> None:
        """Unicode文字（日本語）を含むXMLをパースできる。"""
        _require_module()
        xml_unicode = """\
<dialogue-book>
  <chapter number="1">
    <dialogue-section number="1.1" title="Unicode Test">
      <introduction speaker="narrator">日本語テスト</introduction>
      <dialogue>
        <utterance speaker="A">量子力学の基礎</utterance>
      </dialogue>
      <conclusion speaker="narrator">まとめ</conclusion>
    </dialogue-section>
  </chapter>
</dialogue-book>"""
        result = parse_dialogue_xml(xml_unicode)
        assert len(result) == 1
        assert "量子力学" in result[0]["utterances"][0]["text"]

    def test_parse_section_without_introduction(self) -> None:
        """introductionがないセクションも処理できる。"""
        _require_module()
        xml_no_intro = """\
<dialogue-book>
  <chapter number="1">
    <dialogue-section number="1.1" title="No Intro">
      <dialogue>
        <utterance speaker="A">発話のみ</utterance>
      </dialogue>
      <conclusion speaker="narrator">結論</conclusion>
    </dialogue-section>
  </chapter>
</dialogue-book>"""
        result = parse_dialogue_xml(xml_no_intro)
        assert len(result) == 1
        # introductionがない場合、空文字列またはNoneが返る
        intro = result[0].get("introduction", {})
        intro_text = intro.get("text", "") if isinstance(intro, dict) else ""
        assert intro_text == "" or intro is None

    def test_parse_from_file(self, tmp_path: Path) -> None:
        """ファイルパスからXMLをパースできる。"""
        _require_module()
        xml_file = tmp_path / "dialogue.xml"
        xml_file.write_text(SAMPLE_DIALOGUE_XML, encoding="utf-8")
        result = parse_dialogue_xml(str(xml_file))
        assert len(result) >= 1


# ===========================================================================
# T051: 話者別スタイルID取得 get_style_id() のテスト
# ===========================================================================


class TestGetStyleId:
    """get_style_id()の動作テスト。"""

    def test_narrator_default_style_id(self) -> None:
        """ナレーターのデフォルトスタイルIDは13。"""
        _require_module()
        assert get_style_id("narrator") == 13

    def test_speaker_a_default_style_id(self) -> None:
        """博士（A）のデフォルトスタイルIDは67。"""
        _require_module()
        assert get_style_id("A") == 11

    def test_speaker_b_default_style_id(self) -> None:
        """助手（B）のデフォルトスタイルIDは2。"""
        _require_module()
        assert get_style_id("B") == 2

    def test_custom_style_id_mapping(self) -> None:
        """カスタムのスタイルIDマッピングを指定できる。"""
        _require_module()
        custom_mapping = {"narrator": 10, "A": 20, "B": 30}
        assert get_style_id("narrator", style_mapping=custom_mapping) == 10
        assert get_style_id("A", style_mapping=custom_mapping) == 20
        assert get_style_id("B", style_mapping=custom_mapping) == 30

    def test_unknown_speaker_raises(self) -> None:
        """未知の話者IDでValueErrorが発生する。"""
        _require_module()
        with pytest.raises((ValueError, KeyError)):
            get_style_id("unknown_speaker")

    def test_empty_speaker_raises(self) -> None:
        """空文字列の話者IDでエラーが発生する。"""
        _require_module()
        with pytest.raises((ValueError, KeyError)):
            get_style_id("")

    def test_none_speaker_raises(self) -> None:
        """Noneの話者IDでエラーが発生する。"""
        _require_module()
        with pytest.raises((TypeError, ValueError, KeyError)):
            get_style_id(None)  # type: ignore[arg-type]

    def test_case_sensitive(self) -> None:
        """話者IDは大文字小文字を区別する。"""
        _require_module()
        with pytest.raises((ValueError, KeyError)):
            get_style_id("a")


# ===========================================================================
# T051b: チャプター番号抽出 get_chapter_number() のテスト
# ===========================================================================


class TestGetChapterNumber:
    """get_chapter_number()の動作テスト。"""

    def test_extract_from_section_number(self) -> None:
        """セクション番号 '2.1' からチャプター番号 '2' を抽出する。"""
        _require_module()
        assert get_chapter_number("2.1") == "2"

    def test_extract_from_multi_digit_section(self) -> None:
        """セクション番号 '12.3' からチャプター番号 '12' を抽出する。"""
        _require_module()
        assert get_chapter_number("12.3") == "12"

    def test_no_dot_returns_whole_number(self) -> None:
        """ドットがない場合はそのまま返す。"""
        _require_module()
        assert get_chapter_number("3") == "3"

    def test_empty_string_returns_zero(self) -> None:
        """空文字列の場合は '0' を返す。"""
        _require_module()
        assert get_chapter_number("") == "0"

    def test_multiple_dots(self) -> None:
        """複数のドットがある場合は最初の部分のみ返す。"""
        _require_module()
        assert get_chapter_number("1.2.3") == "1"


# ===========================================================================
# T051c: TTS可能テキスト判定 is_speakable_text() のテスト
# ===========================================================================


class TestIsSpeakableText:
    """is_speakable_text()の動作テスト。"""

    def test_japanese_hiragana(self) -> None:
        """ひらがなを含むテキストはTrue。"""
        _require_module()
        assert is_speakable_text("これはテストです") is True

    def test_japanese_katakana(self) -> None:
        """カタカナを含むテキストはTrue。"""
        _require_module()
        assert is_speakable_text("テスト") is True

    def test_japanese_kanji(self) -> None:
        """漢字を含むテキストはTrue。"""
        _require_module()
        assert is_speakable_text("日本語") is True

    def test_only_symbols(self) -> None:
        """記号のみのテキストはFalse。"""
        _require_module()
        assert is_speakable_text("=") is False
        assert is_speakable_text("===") is False
        assert is_speakable_text("...") is False

    def test_only_ascii(self) -> None:
        """ASCII文字のみのテキストはFalse。"""
        _require_module()
        assert is_speakable_text("ABC") is False
        assert is_speakable_text("123") is False

    def test_empty_string(self) -> None:
        """空文字列はFalse。"""
        _require_module()
        assert is_speakable_text("") is False

    def test_mixed_with_japanese(self) -> None:
        """日本語を含む混合テキストはTrue。"""
        _require_module()
        assert is_speakable_text("Test テスト") is True
        assert is_speakable_text("=== 見出し ===") is True


# ===========================================================================
# T052: 発話単位音声生成 synthesize_utterance() のテスト
# ===========================================================================


class TestSynthesizeUtterance:
    """synthesize_utterance()の動作テスト。"""

    def _mock_synthesizer(self) -> MagicMock:
        """WAVバイト列を返すモックシンセサイザーを生成する。"""
        mock = MagicMock()
        sample_rate = 24000
        samples = np.zeros(int(sample_rate * 0.1), dtype=np.float32)
        mock.synthesize.return_value = _create_wav_bytes(samples, sample_rate)
        return mock

    def test_synthesize_returns_audio_data(self) -> None:
        """発話テキストから音声データ（numpy配列）が返される。"""
        _require_module()
        result = synthesize_utterance(
            text="テストの発話です",
            speaker_id="A",
            synthesizer=self._mock_synthesizer(),
        )
        assert result is not None
        assert isinstance(result, tuple)
        waveform, sr = result
        assert isinstance(waveform, np.ndarray)
        assert isinstance(sr, int)

    def test_synthesize_uses_correct_style_id_for_a(self) -> None:
        """博士（A）のスタイルID=67でVOICEVOXが呼ばれる。"""
        _require_module()
        mock = self._mock_synthesizer()
        synthesize_utterance(text="テスト", speaker_id="A", synthesizer=mock)
        mock.synthesize.assert_called_once()
        call_args = mock.synthesize.call_args
        # style_id が 67 で呼ばれることを確認
        style_id_used = call_args.kwargs.get("style_id", call_args.args[1] if len(call_args.args) > 1 else None)
        assert style_id_used == 11

    def test_synthesize_uses_correct_style_id_for_b(self) -> None:
        """助手（B）のスタイルID=2でVOICEVOXが呼ばれる。"""
        _require_module()
        mock = self._mock_synthesizer()
        synthesize_utterance(text="テスト", speaker_id="B", synthesizer=mock)
        mock.synthesize.assert_called_once()
        call_args = mock.synthesize.call_args
        style_id_used = call_args.kwargs.get("style_id", call_args.args[1] if len(call_args.args) > 1 else None)
        assert style_id_used == 2

    def test_synthesize_narrator(self) -> None:
        """ナレーターの発話を合成できる。"""
        _require_module()
        result = synthesize_utterance(
            text="導入のテキストです",
            speaker_id="narrator",
            synthesizer=self._mock_synthesizer(),
        )
        assert result is not None
        waveform, _ = result
        assert len(waveform) > 0

    def test_synthesize_empty_text_raises(self) -> None:
        """空テキストでエラーが発生する。"""
        _require_module()
        with pytest.raises((ValueError, Exception)):
            synthesize_utterance(
                text="",
                speaker_id="A",
                synthesizer=self._mock_synthesizer(),
            )

    def test_synthesize_none_text_raises(self) -> None:
        """Noneテキストでエラーが発生する。"""
        _require_module()
        with pytest.raises((TypeError, ValueError)):
            synthesize_utterance(
                text=None,  # type: ignore[arg-type]
                speaker_id="A",
                synthesizer=self._mock_synthesizer(),
            )

    def test_synthesize_unknown_speaker_raises(self) -> None:
        """未知の話者IDでエラーが発生する。"""
        _require_module()
        with pytest.raises((ValueError, KeyError)):
            synthesize_utterance(
                text="テスト",
                speaker_id="unknown",
                synthesizer=self._mock_synthesizer(),
            )

    def test_synthesize_with_special_characters(self) -> None:
        """特殊文字を含むテキストも処理できる。"""
        _require_module()
        result = synthesize_utterance(
            text="O(n^2)の計算量とは、例えば100要素で10,000回の処理です。",
            speaker_id="A",
            synthesizer=self._mock_synthesizer(),
        )
        assert result is not None

    def test_synthesize_long_text(self) -> None:
        """長いテキスト（1000文字以上）も処理できる。"""
        _require_module()
        long_text = "テスト文章です。" * 200  # 約1600文字
        result = synthesize_utterance(
            text=long_text,
            speaker_id="B",
            synthesizer=self._mock_synthesizer(),
        )
        assert result is not None

    def test_synthesize_with_custom_speed(self) -> None:
        """速度パラメータを指定して合成できる。"""
        _require_module()
        result = synthesize_utterance(
            text="テスト",
            speaker_id="A",
            synthesizer=self._mock_synthesizer(),
            speed_scale=1.2,
        )
        assert result is not None


# ===========================================================================
# T053: セクション音声結合 concatenate_section_audio() のテスト
# ===========================================================================


class TestConcatenateSectionAudio:
    """concatenate_section_audio()の動作テスト。"""

    def _make_segment(
        self,
        duration_samples: int = 24000,
        sample_rate: int = 24000,
        amplitude: float = 0.5,
        speaker: str = "A",
    ) -> tuple[np.ndarray, int, str]:
        """テスト用音声セグメントを生成する。"""
        return (np.ones(duration_samples, dtype=np.float32) * amplitude, sample_rate, speaker)

    def test_concatenate_two_segments_different_speakers(self) -> None:
        """異なる話者の2つのセグメントは無音を挟んで結合される。"""
        _require_module()
        sr = 24000
        seg1 = self._make_segment(sr, sr, 0.5, "A")
        seg2 = self._make_segment(sr, sr, 0.3, "B")

        result_waveform, result_sr = concatenate_section_audio([seg1, seg2])
        assert result_sr == sr
        # 結合後は2つのセグメント + 間の無音を含む
        assert len(result_waveform) > sr * 2

    def test_concatenate_two_segments_same_speaker(self) -> None:
        """同一話者の2つのセグメントは無音なしで結合される。"""
        _require_module()
        sr = 24000
        seg1 = self._make_segment(sr, sr, 0.5, "A")
        seg2 = self._make_segment(sr, sr, 0.3, "A")

        result_waveform, result_sr = concatenate_section_audio([seg1, seg2])
        assert result_sr == sr
        # 同一話者なので無音なし = ちょうど2つのセグメント分
        assert len(result_waveform) == sr * 2

    def test_concatenate_single_segment(self) -> None:
        """単一セグメントでもそのまま返される。"""
        _require_module()
        sr = 24000
        seg = self._make_segment(sr, sr, 0.5)

        result_waveform, result_sr = concatenate_section_audio([seg])
        assert result_sr == sr
        assert len(result_waveform) >= sr

    def test_concatenate_empty_list_raises(self) -> None:
        """空リストでエラーが発生する。"""
        _require_module()
        with pytest.raises((ValueError, IndexError)):
            concatenate_section_audio([])

    def test_concatenate_preserves_sample_rate(self) -> None:
        """サンプルレートが保持される。"""
        _require_module()
        sr = 44100
        seg1 = self._make_segment(1000, sr, speaker="A")
        seg2 = self._make_segment(1000, sr, speaker="B")

        _, result_sr = concatenate_section_audio([seg1, seg2])
        assert result_sr == sr

    def test_concatenate_with_silence_duration(self) -> None:
        """無音間隔の長さを指定できる（話者が異なる場合）。"""
        _require_module()
        sr = 24000
        seg1 = self._make_segment(1000, sr, speaker="A")
        seg2 = self._make_segment(1000, sr, speaker="B")

        result_default, _ = concatenate_section_audio([seg1, seg2])
        result_long, _ = concatenate_section_audio([seg1, seg2], silence_duration=1.0)
        assert len(result_long) > len(result_default)

    def test_concatenate_many_segments_alternating_speakers(self) -> None:
        """多数のセグメント（交互話者）を結合できる。"""
        _require_module()
        sr = 24000
        speakers = ["A", "B"] * 8  # 16個の交互セグメント
        segments = [self._make_segment(100, sr, i * 0.05, speakers[i]) for i in range(15)]

        result_waveform, result_sr = concatenate_section_audio(segments)
        assert result_sr == sr
        assert len(result_waveform) > 100 * 15

    def test_concatenate_returns_numpy_array(self) -> None:
        """返り値の波形がnumpy配列である。"""
        _require_module()
        seg = self._make_segment(1000, 24000)

        result_waveform, _ = concatenate_section_audio([seg])
        assert isinstance(result_waveform, np.ndarray)

    def test_concatenate_output_to_file(self, tmp_path: Path) -> None:
        """結合結果をファイルに保存できる。"""
        _require_module()
        sr = 24000
        seg1 = self._make_segment(sr, sr, 0.5, "A")
        seg2 = self._make_segment(sr, sr, 0.3, "B")
        output_file = tmp_path / "output.wav"

        concatenate_section_audio([seg1, seg2], output_path=output_file)
        assert output_file.exists()
        assert output_file.stat().st_size > 0


# ===========================================================================
# T054: CLI引数パース parse_args() のテスト
# ===========================================================================


class TestParseArgs:
    """parse_args()のCLI引数パーステスト。"""

    def test_required_input_argument(self) -> None:
        """--input は必須引数である。"""
        _require_module()
        with pytest.raises(SystemExit):
            parse_args([])

    def test_input_short_flag(self) -> None:
        """短縮形 -i で入力ファイルを指定できる。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml"])
        assert args.input == "dialogue.xml"

    def test_input_long_flag(self) -> None:
        """長形式 --input で入力ファイルを指定できる。"""
        _require_module()
        args = parse_args(["--input", "dialogue.xml"])
        assert args.input == "dialogue.xml"

    def test_output_default(self) -> None:
        """--output のデフォルトは './output'。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml"])
        assert args.output == "./output"

    def test_output_custom(self) -> None:
        """--output でカスタム出力ディレクトリを指定できる。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml", "-o", "/tmp/out"])
        assert args.output == "/tmp/out"

    def test_narrator_style_default(self) -> None:
        """--narrator-style のデフォルトは 13。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml"])
        assert args.narrator_style == 13

    def test_narrator_style_custom(self) -> None:
        """--narrator-style でカスタム値を指定できる。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml", "--narrator-style", "10"])
        assert args.narrator_style == 10

    def test_speaker_a_style_default(self) -> None:
        """--speaker-a-style のデフォルトは 67。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml"])
        assert args.speaker_a_style == 11

    def test_speaker_a_style_custom(self) -> None:
        """--speaker-a-style でカスタム値を指定できる。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml", "--speaker-a-style", "20"])
        assert args.speaker_a_style == 20

    def test_speaker_b_style_default(self) -> None:
        """--speaker-b-style のデフォルトは 2。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml"])
        assert args.speaker_b_style == 2

    def test_speaker_b_style_custom(self) -> None:
        """--speaker-b-style でカスタム値を指定できる。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml", "--speaker-b-style", "5"])
        assert args.speaker_b_style == 5

    def test_speed_default(self) -> None:
        """--speed のデフォルトは 1.0。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml"])
        assert args.speed == 1.0

    def test_speed_custom(self) -> None:
        """--speed でカスタム速度を指定できる。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml", "--speed", "1.5"])
        assert args.speed == 1.5

    def test_voicevox_dir_default(self) -> None:
        """--voicevox-dir のデフォルトは './voicevox_core'。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml"])
        assert args.voicevox_dir == "./voicevox_core"

    def test_voicevox_dir_custom(self) -> None:
        """--voicevox-dir でカスタムパスを指定できる。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml", "--voicevox-dir", "/opt/vv"])
        assert args.voicevox_dir == "/opt/vv"

    def test_acceleration_mode_default(self) -> None:
        """--acceleration-mode のデフォルトは 'AUTO'。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml"])
        assert args.acceleration_mode == "AUTO"

    def test_acceleration_mode_custom(self) -> None:
        """--acceleration-mode でカスタム値を指定できる。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml", "--acceleration-mode", "CPU"])
        assert args.acceleration_mode == "CPU"

    def test_all_options_combined(self) -> None:
        """全オプションを同時に指定できる。"""
        _require_module()
        args = parse_args(
            [
                "-i",
                "input.xml",
                "-o",
                "out_dir",
                "--narrator-style",
                "10",
                "--speaker-a-style",
                "20",
                "--speaker-b-style",
                "30",
                "--speed",
                "0.8",
                "--voicevox-dir",
                "/vv",
                "--acceleration-mode",
                "GPU",
            ]
        )
        assert args.input == "input.xml"
        assert args.output == "out_dir"
        assert args.narrator_style == 10
        assert args.speaker_a_style == 20
        assert args.speaker_b_style == 30
        assert args.speed == 0.8
        assert args.voicevox_dir == "/vv"
        assert args.acceleration_mode == "GPU"

    def test_dict_source_default(self) -> None:
        """--dict-source のデフォルトは None。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml"])
        assert args.dict_source is None

    def test_dict_source_custom(self) -> None:
        """--dict-source でカスタムパスを指定できる。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml", "--dict-source", "book.xml"])
        assert args.dict_source == "book.xml"


# ===========================================================================
# T055: 読み辞書初期化 init_readings() のテスト
# ===========================================================================


class TestInitReadings:
    """init_readings()の辞書初期化テスト。"""

    def test_init_with_none_path(self) -> None:
        """Noneパス指定時は空辞書で初期化される。"""
        _require_module()
        # Should not raise
        init_readings(None)

    def test_init_with_nonexistent_path(self) -> None:
        """存在しないパス指定時は空辞書で初期化される。"""
        _require_module()
        # Should not raise
        init_readings(Path("/nonexistent/file.xml"))


# ===========================================================================
# T056: テキストへの読み適用 apply_readings_to_text() のテスト
# ===========================================================================


class TestApplyReadingsToText:
    """apply_readings_to_text()のテスト。"""

    def test_number_normalization(self) -> None:
        """数字が読み仮名に変換される。"""
        _require_module()
        # Reset readings to empty
        init_readings(None)
        result = apply_readings_to_text("第3章")
        # Number normalization should convert 3 to reading
        assert "3" not in result or "さん" in result or "だいさん" in result

    def test_static_reading_rules(self) -> None:
        """静的な読み辞書のルールが適用される。"""
        _require_module()
        init_readings(None)
        result = apply_readings_to_text("SREの基本")
        # SRE should be converted (check that original is transformed)
        assert "SRE" not in result or "エス" in result

    def test_empty_text(self) -> None:
        """空文字列は空文字列を返す。"""
        _require_module()
        init_readings(None)
        result = apply_readings_to_text("")
        assert result == ""

    def test_plain_japanese(self) -> None:
        """平文の日本語はそのまま返される。"""
        _require_module()
        init_readings(None)
        result = apply_readings_to_text("これはテストです")
        # Plain Japanese should pass through (possibly with punctuation changes)
        assert "テスト" in result


# ===========================================================================
# T057: 効果音挿入テスト (Issue #55)
# ===========================================================================


try:
    from src.dialogue_pipeline import process_dialogue_sections
except ImportError:
    process_dialogue_sections = None  # type: ignore[assignment]


SAMPLE_MULTI_CHAPTER_XML = """\
<dialogue-book>
  <dialogue-section number="1.1" title="セクション1-1">
    <introduction speaker="narrator">導入1-1</introduction>
    <dialogue>
      <utterance speaker="A">発話A1-1</utterance>
    </dialogue>
    <conclusion speaker="narrator">結論1-1</conclusion>
  </dialogue-section>
  <dialogue-section number="1.2" title="セクション1-2">
    <introduction speaker="narrator">導入1-2</introduction>
    <dialogue>
      <utterance speaker="A">発話A1-2</utterance>
    </dialogue>
    <conclusion speaker="narrator">結論1-2</conclusion>
  </dialogue-section>
  <dialogue-section number="2.1" title="セクション2-1">
    <introduction speaker="narrator">導入2-1</introduction>
    <dialogue>
      <utterance speaker="A">発話A2-1</utterance>
    </dialogue>
    <conclusion speaker="narrator">結論2-1</conclusion>
  </dialogue-section>
</dialogue-book>"""


class TestSoundEffectInsertion:
    """効果音挿入機能のテスト (Issue #55)."""

    def _mock_synthesizer(self) -> MagicMock:
        """WAVバイト列を返すモックシンセサイザーを生成する。"""
        mock = MagicMock()
        sample_rate = 24000
        samples = np.ones(int(sample_rate * 0.1), dtype=np.float32) * 0.3
        mock.synthesize.return_value = _create_wav_bytes(samples, sample_rate)
        return mock

    def _make_sound(self, value: float = 0.5, duration: float = 0.05) -> np.ndarray:
        """テスト用効果音配列を生成する。"""
        return np.ones(int(24000 * duration), dtype=np.float32) * value

    def test_chapter_sound_inserted_at_chapter_start(self, tmp_path: Path) -> None:
        """チャプターの先頭にチャプター効果音が挿入される。"""
        _require_module()
        sections = parse_dialogue_xml(SAMPLE_MULTI_CHAPTER_XML)
        chapter_sound = self._make_sound(0.9)

        generated = process_dialogue_sections(
            sections=sections,
            synthesizer=self._mock_synthesizer(),
            output_dir=tmp_path,
            chapter_sound=chapter_sound,
        )
        # 2チャプター分のファイルが生成される
        assert len(generated) == 2

    def test_section_sound_inserted_at_non_first_section(self, tmp_path: Path) -> None:
        """チャプター内の2番目以降のセクションにセクション効果音が挿入される。"""
        _require_module()
        sections = parse_dialogue_xml(SAMPLE_MULTI_CHAPTER_XML)
        section_sound = self._make_sound(0.7)

        generated = process_dialogue_sections(
            sections=sections,
            synthesizer=self._mock_synthesizer(),
            output_dir=tmp_path,
            section_sound=section_sound,
        )
        assert len(generated) == 2

    def test_both_sounds_inserted(self, tmp_path: Path) -> None:
        """チャプター効果音とセクション効果音が両方挿入される。"""
        _require_module()
        sections = parse_dialogue_xml(SAMPLE_MULTI_CHAPTER_XML)
        chapter_sound = self._make_sound(0.9)
        section_sound = self._make_sound(0.7)

        generated = process_dialogue_sections(
            sections=sections,
            synthesizer=self._mock_synthesizer(),
            output_dir=tmp_path,
            chapter_sound=chapter_sound,
            section_sound=section_sound,
        )
        assert len(generated) == 2
        # 各ファイルが存在し、サイズが0でない
        for path in generated:
            assert path.exists()
            assert path.stat().st_size > 0

    def test_no_sound_backward_compatible(self, tmp_path: Path) -> None:
        """効果音なしの場合、従来通り動作する（後方互換性）。"""
        _require_module()
        sections = parse_dialogue_xml(SAMPLE_MULTI_CHAPTER_XML)

        generated = process_dialogue_sections(
            sections=sections,
            synthesizer=self._mock_synthesizer(),
            output_dir=tmp_path,
        )
        assert len(generated) == 2

    def test_parse_args_chapter_sound_default(self) -> None:
        """--chapter-sound のデフォルトは assets/sounds/chapter.mp3。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml"])
        assert args.chapter_sound == "assets/sounds/chapter.mp3"

    def test_parse_args_section_sound_default(self) -> None:
        """--section-sound のデフォルトは assets/sounds/section.mp3。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml"])
        assert args.section_sound == "assets/sounds/section.mp3"

    def test_parse_args_chapter_sound_custom(self) -> None:
        """--chapter-sound でカスタムパスを指定できる。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml", "--chapter-sound", "/tmp/ch.mp3"])
        assert args.chapter_sound == "/tmp/ch.mp3"

    def test_parse_args_section_sound_custom(self) -> None:
        """--section-sound でカスタムパスを指定できる。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml", "--section-sound", "/tmp/sec.mp3"])
        assert args.section_sound == "/tmp/sec.mp3"

    def test_parse_args_no_chapter_sound(self) -> None:
        """--no-chapter-sound でチャプター効果音を無効化できる。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml", "--no-chapter-sound"])
        assert args.chapter_sound is None

    def test_parse_args_no_section_sound(self) -> None:
        """--no-section-sound でセクション効果音を無効化できる。"""
        _require_module()
        args = parse_args(["-i", "dialogue.xml", "--no-section-sound"])
        assert args.section_sound is None

    def test_chapter_sound_increases_audio_length(self, tmp_path: Path) -> None:
        """チャプター効果音挿入により音声ファイルのサイズが増加する。"""
        _require_module()
        sections = parse_dialogue_xml(SAMPLE_MULTI_CHAPTER_XML)
        chapter_sound = self._make_sound(0.9, duration=1.0)

        path_no_sound = tmp_path / "no_sound"
        path_with_sound = tmp_path / "with_sound"

        process_dialogue_sections(
            sections,
            self._mock_synthesizer(),
            path_no_sound,
        )
        process_dialogue_sections(
            sections,
            self._mock_synthesizer(),
            path_with_sound,
            chapter_sound=chapter_sound,
        )

        size_no = (path_no_sound / "chapter_001.wav").stat().st_size
        size_with = (path_with_sound / "chapter_001.wav").stat().st_size
        assert size_with > size_no
