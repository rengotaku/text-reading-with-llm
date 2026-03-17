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
        concatenate_section_audio,
        get_style_id,
        parse_args,
        parse_dialogue_xml,
        synthesize_utterance,
    )

    _MODULE_AVAILABLE = True
except ImportError:
    _MODULE_AVAILABLE = False
    Speaker = None  # type: ignore[assignment,misc]
    concatenate_section_audio = None  # type: ignore[assignment]
    get_style_id = None  # type: ignore[assignment]
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
        self, duration_samples: int = 24000, sample_rate: int = 24000, amplitude: float = 0.5
    ) -> tuple[np.ndarray, int]:
        """テスト用音声セグメントを生成する。"""
        return (np.ones(duration_samples, dtype=np.float32) * amplitude, sample_rate)

    def test_concatenate_two_segments(self) -> None:
        """2つの音声セグメントを結合できる。"""
        _require_module()
        sr = 24000
        seg1 = self._make_segment(sr, sr, 0.5)
        seg2 = self._make_segment(sr, sr, 0.3)

        result_waveform, result_sr = concatenate_section_audio([seg1, seg2])
        assert result_sr == sr
        # 結合後は2つのセグメント + 間の無音を含む
        assert len(result_waveform) > sr * 2

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
        seg1 = self._make_segment(1000, sr)
        seg2 = self._make_segment(1000, sr)

        _, result_sr = concatenate_section_audio([seg1, seg2])
        assert result_sr == sr

    def test_concatenate_with_silence_duration(self) -> None:
        """無音間隔の長さを指定できる。"""
        _require_module()
        sr = 24000
        seg1 = self._make_segment(1000, sr)
        seg2 = self._make_segment(1000, sr)

        result_default, _ = concatenate_section_audio([seg1, seg2])
        result_long, _ = concatenate_section_audio([seg1, seg2], silence_duration=1.0)
        assert len(result_long) > len(result_default)

    def test_concatenate_many_segments(self) -> None:
        """多数のセグメント（15個）を結合できる。"""
        _require_module()
        sr = 24000
        segments = [self._make_segment(100, sr, i * 0.05) for i in range(15)]

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
        seg1 = self._make_segment(sr, sr, 0.5)
        seg2 = self._make_segment(sr, sr, 0.3)
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
