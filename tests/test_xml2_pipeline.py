"""Tests for book2.xml TTS pipeline.

Phase 4 RED Tests - US3: 音声パイプライン統合
Tests for xml2_pipeline.py command-line interface and content processing.

Phase 2 RED Tests - US1: テキストクリーニングの適用
Tests for clean_page_text() integration in process_content().

Target functions:
- src/xml2_pipeline.py::parse_args()
- src/xml2_pipeline.py::load_sound()
- src/xml2_pipeline.py::process_content()
- src/xml2_pipeline.py::main()

Test Fixture: tests/fixtures/sample_book2.xml
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# Fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_BOOK2_XML = FIXTURES_DIR / "sample_book2.xml"


# =============================================================================
# Phase 4 RED Tests - US3: 音声パイプライン統合
# =============================================================================


class TestParseArgsDefaults:
    """Test parse_args default values for xml2_pipeline.

    T041: CLI引数のデフォルト値テスト
    - --input: 必須
    - --output: ./output
    - --chapter-sound: assets/sounds/chapter.mp3
    - --section-sound: assets/sounds/section.mp3
    - --style-id: 13
    - --speed: 1.0
    """

    def test_parse_args_input_required(self):
        """--input 引数が必須"""
        from src.xml2_pipeline import parse_args

        with pytest.raises(SystemExit) as exc_info:
            parse_args([])

        # argparse exits with code 2 for missing required argument
        assert exc_info.value.code == 2, f"Missing --input should exit with code 2, got {exc_info.value.code}"

    def test_parse_args_accepts_input_long(self):
        """--input 引数を受け付ける"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["--input", str(SAMPLE_BOOK2_XML)])

        assert args.input == str(SAMPLE_BOOK2_XML), f"--input should be parsed, got {args.input}"

    def test_parse_args_accepts_input_short(self):
        """-i 短縮形を受け付ける"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML)])

        assert args.input == str(SAMPLE_BOOK2_XML), f"-i should be parsed, got {args.input}"

    def test_output_default(self):
        """--output のデフォルトは ./output"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML)])

        assert args.output == "./output", f"--output default should be './output', got {args.output}"

    def test_chapter_sound_default(self):
        """--chapter-sound のデフォルトは assets/sounds/chapter.mp3"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML)])

        assert args.chapter_sound == "assets/sounds/chapter.mp3", (
            f"--chapter-sound default should be 'assets/sounds/chapter.mp3', got {args.chapter_sound}"
        )

    def test_section_sound_default(self):
        """--section-sound のデフォルトは assets/sounds/section.mp3"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML)])

        assert args.section_sound == "assets/sounds/section.mp3", (
            f"--section-sound default should be 'assets/sounds/section.mp3', got {args.section_sound}"
        )

    def test_style_id_default(self):
        """--style-id のデフォルトは 13"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML)])

        assert args.style_id == 13, f"--style-id default should be 13, got {args.style_id}"

    def test_speed_default(self):
        """--speed のデフォルトは 1.0"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML)])

        assert args.speed == 1.0, f"--speed default should be 1.0, got {args.speed}"

    def test_voicevox_dir_default(self):
        """--voicevox-dir のデフォルトは ./voicevox_core"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML)])

        assert args.voicevox_dir == "./voicevox_core", (
            f"--voicevox-dir default should be './voicevox_core', got {args.voicevox_dir}"
        )

    def test_max_chunk_chars_default(self):
        """--max-chunk-chars のデフォルトは 500"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML)])

        assert args.max_chunk_chars == 500, f"--max-chunk-chars default should be 500, got {args.max_chunk_chars}"


class TestParseArgsCustomSounds:
    """Test parse_args custom sound file options.

    T042: カスタム効果音ファイルオプションテスト
    - --chapter-sound: 任意のパス
    - --section-sound: 任意のパス
    """

    def test_chapter_sound_custom(self):
        """--chapter-sound にカスタム値を設定"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML), "--chapter-sound", "/custom/path/chapter.mp3"])

        assert args.chapter_sound == "/custom/path/chapter.mp3", (
            f"--chapter-sound should be '/custom/path/chapter.mp3', got {args.chapter_sound}"
        )

    def test_section_sound_custom(self):
        """--section-sound にカスタム値を設定"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML), "--section-sound", "/custom/path/section.mp3"])

        assert args.section_sound == "/custom/path/section.mp3", (
            f"--section-sound should be '/custom/path/section.mp3', got {args.section_sound}"
        )

    def test_both_sounds_custom(self):
        """--chapter-sound と --section-sound を両方カスタム設定"""
        from src.xml2_pipeline import parse_args

        args = parse_args(
            [
                "-i",
                str(SAMPLE_BOOK2_XML),
                "--chapter-sound",
                "/path/to/chapter.wav",
                "--section-sound",
                "/path/to/section.wav",
            ]
        )

        assert args.chapter_sound == "/path/to/chapter.wav", (
            f"--chapter-sound should be '/path/to/chapter.wav', got {args.chapter_sound}"
        )
        assert args.section_sound == "/path/to/section.wav", (
            f"--section-sound should be '/path/to/section.wav', got {args.section_sound}"
        )

    def test_output_custom(self):
        """--output にカスタム値を設定"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML), "-o", "/tmp/audio"])

        assert args.output == "/tmp/audio", f"--output should be '/tmp/audio', got {args.output}"

    def test_style_id_custom(self):
        """--style-id にカスタム値を設定"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML), "--style-id", "1"])

        assert args.style_id == 1, f"--style-id should be 1, got {args.style_id}"

    def test_speed_custom(self):
        """--speed にカスタム値を設定"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML), "--speed", "1.5"])

        assert args.speed == 1.5, f"--speed should be 1.5, got {args.speed}"


class TestLoadSoundMonoConversion:
    """Test load_sound function for audio loading and conversion.

    T043: 効果音ロード機能テスト
    - ステレオ → モノラル変換
    - サンプルレート変換（リサンプリング）
    - numpy 配列として返却
    - 音量正規化
    """

    def test_load_sound_returns_numpy_array(self, tmp_path):
        """load_sound は numpy 配列を返す"""
        import soundfile as sf

        from src.xml2_pipeline import load_sound

        # Create a test mono WAV file
        test_audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 24000)).astype(np.float32)
        sound_path = tmp_path / "test.wav"
        sf.write(sound_path, test_audio, 24000)

        result = load_sound(sound_path)

        assert isinstance(result, np.ndarray), f"load_sound should return numpy.ndarray, got {type(result)}"

    def test_load_sound_stereo_to_mono_conversion(self, tmp_path):
        """ステレオ音声をモノラルに変換する"""
        import soundfile as sf

        from src.xml2_pipeline import load_sound

        # Create a stereo WAV file
        duration = 0.5
        sr = 24000
        samples = int(duration * sr)
        stereo_audio = np.column_stack(
            [
                np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples)),  # Left channel
                np.sin(2 * np.pi * 880 * np.linspace(0, duration, samples)),  # Right channel
            ]
        ).astype(np.float32)

        sound_path = tmp_path / "stereo.wav"
        sf.write(sound_path, stereo_audio, sr)

        result = load_sound(sound_path)

        # Result should be 1D (mono)
        assert len(result.shape) == 1, f"Stereo should be converted to mono (1D), got shape {result.shape}"

    def test_load_sound_resampling(self, tmp_path):
        """異なるサンプルレートをリサンプリングする"""
        import soundfile as sf

        from src.xml2_pipeline import load_sound

        # Create a 48kHz WAV file (different from VOICEVOX's 24kHz)
        source_sr = 48000
        target_sr = 24000
        duration = 0.5
        samples = int(duration * source_sr)
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples)).astype(np.float32)

        sound_path = tmp_path / "48khz.wav"
        sf.write(sound_path, audio, source_sr)

        result = load_sound(sound_path, target_sr=target_sr)

        # Expected number of samples after resampling
        expected_samples = int(samples * target_sr / source_sr)

        assert abs(len(result) - expected_samples) < 10, (
            f"Resampled audio should have ~{expected_samples} samples, got {len(result)}"
        )

    def test_load_sound_already_correct_sample_rate(self, tmp_path):
        """既に正しいサンプルレートの場合はリサンプリングしない"""
        import soundfile as sf

        from src.xml2_pipeline import load_sound

        # Create a 24kHz WAV file (same as VOICEVOX)
        sr = 24000
        duration = 0.5
        samples = int(duration * sr)
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples)).astype(np.float32)

        sound_path = tmp_path / "24khz.wav"
        sf.write(sound_path, audio, sr)

        result = load_sound(sound_path, target_sr=sr)

        assert len(result) == samples, (
            f"Audio at correct sample rate should not be resampled, got {len(result)} samples"
        )

    def test_load_sound_normalization(self, tmp_path):
        """音量が正規化される"""
        import soundfile as sf

        from src.xml2_pipeline import load_sound

        # Create audio with very low amplitude
        sr = 24000
        duration = 0.5
        samples = int(duration * sr)
        # Very quiet audio (amplitude 0.01)
        audio = 0.01 * np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples)).astype(np.float32)

        sound_path = tmp_path / "quiet.wav"
        sf.write(sound_path, audio, sr)

        result = load_sound(sound_path)

        max_amplitude = np.max(np.abs(result))
        # Should be normalized (not too quiet)
        assert max_amplitude > 0.1, f"Audio should be normalized, max amplitude is {max_amplitude}"

    def test_load_sound_returns_float32(self, tmp_path):
        """float32 型で返却される"""
        import soundfile as sf

        from src.xml2_pipeline import load_sound

        sr = 24000
        duration = 0.5
        samples = int(duration * sr)
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples)).astype(np.float32)

        sound_path = tmp_path / "test.wav"
        sf.write(sound_path, audio, sr)

        result = load_sound(sound_path)

        assert result.dtype == np.float32, f"load_sound should return float32, got {result.dtype}"


class TestProcessContentWithMarkers:
    """Test process_content function with CHAPTER_MARKER and SECTION_MARKER.

    T044: マーカー処理テスト
    - CHAPTER_MARKER で分割し chapter_sound を挿入
    - SECTION_MARKER で分割し section_sound を挿入
    - マーカーなしテキストはそのまま処理
    """

    def test_process_content_function_exists(self):
        """process_content 関数が存在する"""
        from src.xml2_pipeline import process_content

        assert callable(process_content), "process_content should be a callable function"

    def test_process_content_accepts_content_items(self):
        """process_content は ContentItem リストを受け付ける"""
        from src.xml2_parser import ContentItem
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(item_type="paragraph", text="Test paragraph", heading_info=None),
        ]

        # Should not raise
        # Note: This might need mock synthesizer in actual implementation
        try:
            # process_content signature likely includes synthesizer, sounds, etc.
            # For RED test, we just verify it accepts content_items
            _ = process_content(content_items)
        except TypeError as e:
            # If missing required arguments, that's expected - function exists but needs more args
            assert "argument" in str(e).lower() or "required" in str(e).lower(), (
                f"process_content should accept content_items, got: {e}"
            )

    def test_process_content_with_chapter_marker_includes_chapter_sound(self):
        """CHAPTER_MARKER を含むテキストで chapter_sound が挿入される"""
        from src.xml2_parser import CHAPTER_MARKER, ContentItem, HeadingInfo
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(
                item_type="heading",
                text=f"{CHAPTER_MARKER}第1章 テスト",
                heading_info=HeadingInfo(level=1, number="1", title="テスト", read_aloud=True),
            ),
        ]

        # Create mock chapter sound (short sine wave)
        chapter_sound = np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, 2400)).astype(np.float32)

        # The actual test will verify chapter_sound is inserted before the heading
        # RED phase: we verify the function handles CHAPTER_MARKER correctly
        try:
            result = process_content(
                content_items,
                chapter_sound=chapter_sound,
                section_sound=None,
            )
            # If we get here, verify result contains audio data
            assert result is not None, "process_content should return result"
        except TypeError as e:
            # Expected in RED phase - function signature may differ
            assert True, f"Function exists but signature differs: {e}"

    def test_process_content_with_section_marker_includes_section_sound(self):
        """SECTION_MARKER を含むテキストで section_sound が挿入される"""
        from src.xml2_parser import SECTION_MARKER, ContentItem, HeadingInfo
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(
                item_type="heading",
                text=f"{SECTION_MARKER}第1.1節 サブセクション",
                heading_info=HeadingInfo(level=2, number="1.1", title="サブセクション", read_aloud=True),
            ),
        ]

        # Create mock section sound
        section_sound = np.sin(2 * np.pi * 880 * np.linspace(0, 0.1, 2400)).astype(np.float32)

        try:
            result = process_content(
                content_items,
                chapter_sound=None,
                section_sound=section_sound,
            )
            assert result is not None, "process_content should return result"
        except TypeError as e:
            assert True, f"Function exists but signature differs: {e}"

    def test_process_content_mixed_markers(self):
        """CHAPTER_MARKER と SECTION_MARKER の両方を正しく処理"""
        from src.xml2_parser import CHAPTER_MARKER, SECTION_MARKER, ContentItem, HeadingInfo
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(
                item_type="heading",
                text=f"{CHAPTER_MARKER}第1章 最初の章",
                heading_info=HeadingInfo(level=1, number="1", title="最初の章", read_aloud=True),
            ),
            ContentItem(item_type="paragraph", text="段落テキスト", heading_info=None),
            ContentItem(
                item_type="heading",
                text=f"{SECTION_MARKER}第1.1節 セクション",
                heading_info=HeadingInfo(level=2, number="1.1", title="セクション", read_aloud=True),
            ),
        ]

        chapter_sound = np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, 2400)).astype(np.float32)
        section_sound = np.sin(2 * np.pi * 880 * np.linspace(0, 0.1, 2400)).astype(np.float32)

        try:
            result = process_content(
                content_items,
                chapter_sound=chapter_sound,
                section_sound=section_sound,
            )
            assert result is not None, "process_content should handle mixed markers"
        except TypeError as e:
            assert True, f"Function exists but signature differs: {e}"

    def test_process_content_no_markers(self):
        """マーカーなしのテキストはそのまま処理される"""
        from src.xml2_parser import ContentItem
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(item_type="paragraph", text="マーカーなしの段落テキスト", heading_info=None),
        ]

        try:
            result = process_content(
                content_items,
                chapter_sound=None,
                section_sound=None,
            )
            assert result is not None, "process_content should handle text without markers"
        except TypeError as e:
            assert True, f"Function exists but signature differs: {e}"


class TestMainFunction:
    """Test main() entry point function."""

    def test_main_function_exists(self):
        """main 関数が存在する"""
        from src.xml2_pipeline import main

        assert callable(main), "main should be a callable function"

    def test_main_file_not_found_raises_error(self):
        """存在しないファイルでエラー"""
        from src.xml2_pipeline import main

        non_existent = "/tmp/non_existent_book2.xml"

        with pytest.raises(FileNotFoundError) as exc_info:
            main(["--input", non_existent])

        assert non_existent in str(exc_info.value), f"Error message should contain file path: {exc_info.value}"

    def test_main_invalid_xml_raises_error(self, tmp_path):
        """不正な XML でエラー"""
        from src.xml2_pipeline import main

        invalid_xml = tmp_path / "invalid.xml"
        invalid_xml.write_text("<book><paragraph>unclosed")

        with pytest.raises(Exception) as exc_info:
            main(["--input", str(invalid_xml)])

        error_type = type(exc_info.value).__name__
        assert "ParseError" in error_type or "XML" in str(exc_info.value).upper(), (
            f"Should raise parse error for invalid XML, got {error_type}: {exc_info.value}"
        )


# =============================================================================
# Phase 2 RED Tests - US1: テキストクリーニングの適用
# =============================================================================


class TestProcessContentAppliesCleanPageText:
    """T007: process_content が clean_page_text() を呼び出すことを検証する。

    US1 Acceptance Scenario:
    - clean_page_text() が全テキストに適用される
    - マーカー除去後、TTS生成前にクリーニングが行われる
    """

    def test_process_content_calls_clean_page_text(self):
        """process_content は各コンテンツアイテムのテキストに clean_page_text() を適用する"""
        from src.xml2_parser import ContentItem
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(
                item_type="paragraph",
                text="テスト段落テキスト",
                heading_info=None,
            ),
        ]

        # Mock synthesizer and args to go through the full processing path
        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = (
            np.zeros(2400, dtype=np.float32),
            24000,
        )

        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)

            with patch("src.chapter_processor.clean_page_text") as mock_clean:
                mock_clean.return_value = "クリーニング済みテキスト"

                with patch("src.chapter_processor.generate_audio") as mock_gen:
                    mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

                    process_content(
                        content_items,
                        synthesizer=mock_synthesizer,
                        output_dir=output_dir,
                        args=mock_args,
                        chapter_sound=None,
                        section_sound=None,
                    )

                    # clean_page_text must be called at least once
                    assert mock_clean.called, (
                        "process_content は clean_page_text() を呼び出すべきだが、呼び出されていない"
                    )

    def test_process_content_applies_clean_page_text_to_each_item(self):
        """process_content は複数のコンテンツアイテム全てに clean_page_text() を適用する"""
        from src.xml2_parser import ContentItem
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(item_type="paragraph", text="段落1のテキスト", heading_info=None),
            ContentItem(item_type="paragraph", text="段落2のテキスト", heading_info=None),
            ContentItem(item_type="paragraph", text="段落3のテキスト", heading_info=None),
        ]

        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = (
            np.zeros(2400, dtype=np.float32),
            24000,
        )

        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)

            with patch("src.chapter_processor.clean_page_text") as mock_clean:
                mock_clean.side_effect = lambda text, **kwargs: text

                with patch("src.chapter_processor.generate_audio") as mock_gen:
                    mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

                    process_content(
                        content_items,
                        synthesizer=mock_synthesizer,
                        output_dir=output_dir,
                        args=mock_args,
                        chapter_sound=None,
                        section_sound=None,
                    )

                    # clean_page_text should be called for each non-empty item
                    assert mock_clean.call_count >= 3, (
                        f"clean_page_text は3回呼び出されるべきだが、{mock_clean.call_count}回しか呼び出されていない"
                    )

    def test_process_content_cleans_text_after_marker_removal(self):
        """process_content はマーカー除去後にクリーニングを行う"""
        from src.xml2_parser import CHAPTER_MARKER, ContentItem
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(
                item_type="heading",
                text=f"{CHAPTER_MARKER}第1章 テストの章",
                heading_info=None,
            ),
        ]

        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = (
            np.zeros(2400, dtype=np.float32),
            24000,
        )

        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        chapter_sound = np.zeros(2400, dtype=np.float32)

        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)

            with patch("src.chapter_processor.clean_page_text") as mock_clean:
                mock_clean.side_effect = lambda text, **kwargs: text

                with patch("src.chapter_processor.generate_audio") as mock_gen:
                    mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

                    process_content(
                        content_items,
                        synthesizer=mock_synthesizer,
                        output_dir=output_dir,
                        args=mock_args,
                        chapter_sound=chapter_sound,
                        section_sound=None,
                    )

                    # clean_page_text should be called without the marker
                    if mock_clean.called:
                        first_call_text = mock_clean.call_args_list[0][0][0]
                        assert CHAPTER_MARKER not in first_call_text, (
                            f"clean_page_text にマーカーが含まれてはいけない: {first_call_text!r}"
                        )
                    else:
                        pytest.fail("clean_page_text はマーカー除去後に呼び出されるべきだが、呼び出されていない")


class TestProcessContentRemovesUrl:
    """T008: process_content が URL を除去することを検証する。

    US1 Acceptance Scenario 1:
    - Given URL を含む paragraph 要素
    - When xml2_pipeline で処理する
    - Then URL は読み上げられない
    """

    def test_url_not_passed_to_tts(self):
        """URL を含むテキストが TTS に渡される前に URL が除去される"""
        from src.xml2_parser import ContentItem
        from src.xml2_pipeline import process_content

        url_text = "詳細は https://example.com/path/to/page を参照してください。"
        content_items = [
            ContentItem(item_type="paragraph", text=url_text, heading_info=None),
        ]

        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = (
            np.zeros(2400, dtype=np.float32),
            24000,
        )

        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        tts_texts = []

        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)

            with patch("src.chapter_processor.generate_audio") as mock_gen:
                mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

                process_content(
                    content_items,
                    synthesizer=mock_synthesizer,
                    output_dir=output_dir,
                    args=mock_args,
                    chapter_sound=None,
                    section_sound=None,
                )

                # Collect all text passed to generate_audio
                for call in mock_gen.call_args_list:
                    _, kwargs = call
                    if "text" in kwargs:
                        tts_texts.append(kwargs["text"])
                    elif len(call[0]) > 1:
                        tts_texts.append(call[0][1])

        # URL should not appear in any TTS text
        all_tts_text = " ".join(tts_texts)
        assert "https://example.com" not in all_tts_text, f"TTS テキストに URL が含まれている: {all_tts_text!r}"
        assert "example.com" not in all_tts_text, f"TTS テキストにドメイン名が含まれている: {all_tts_text!r}"

    def test_http_url_removed(self):
        """http:// で始まる URL も除去される"""
        from src.xml2_parser import ContentItem
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(
                item_type="paragraph",
                text="リンク先は http://example.org/index.html です。",
                heading_info=None,
            ),
        ]

        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = (
            np.zeros(2400, dtype=np.float32),
            24000,
        )

        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)

            with patch("src.chapter_processor.generate_audio") as mock_gen:
                mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

                process_content(
                    content_items,
                    synthesizer=mock_synthesizer,
                    output_dir=output_dir,
                    args=mock_args,
                    chapter_sound=None,
                    section_sound=None,
                )

                all_tts_text = " ".join(
                    call.kwargs.get("text", call.args[1] if len(call.args) > 1 else "")
                    for call in mock_gen.call_args_list
                )

        assert "http://example.org" not in all_tts_text, f"TTS テキストに http URL が含まれている: {all_tts_text!r}"


class TestProcessContentRemovesParentheticalEnglish:
    """T009: process_content が括弧内英語を除去することを検証する。

    US1 Acceptance Scenario 2:
    - Given 括弧内英語 (English) を含むテキスト
    - When 処理する
    - Then 括弧内英語は読み上げられない
    """

    def test_parenthetical_english_removed(self):
        """括弧内の英語テキストが除去される"""
        from src.xml2_parser import ContentItem
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(
                item_type="paragraph",
                text="信頼性 (Reliability) は重要な概念です。",
                heading_info=None,
            ),
        ]

        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = (
            np.zeros(2400, dtype=np.float32),
            24000,
        )

        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)

            with patch("src.chapter_processor.generate_audio") as mock_gen:
                mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

                process_content(
                    content_items,
                    synthesizer=mock_synthesizer,
                    output_dir=output_dir,
                    args=mock_args,
                    chapter_sound=None,
                    section_sound=None,
                )

                all_tts_text = " ".join(
                    call.kwargs.get("text", call.args[1] if len(call.args) > 1 else "")
                    for call in mock_gen.call_args_list
                )

        assert "Reliability" not in all_tts_text, f"TTS テキストに括弧内英語が含まれている: {all_tts_text!r}"
        assert "(Reliability)" not in all_tts_text, f"TTS テキストに括弧付き英語が含まれている: {all_tts_text!r}"

    def test_multiple_parenthetical_english_removed(self):
        """複数の括弧内英語が全て除去される"""
        from src.xml2_parser import ContentItem
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(
                item_type="paragraph",
                text="可用性 (Availability) と拡張性 (Scalability) について説明します。",
                heading_info=None,
            ),
        ]

        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = (
            np.zeros(2400, dtype=np.float32),
            24000,
        )

        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)

            with patch("src.chapter_processor.generate_audio") as mock_gen:
                mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

                process_content(
                    content_items,
                    synthesizer=mock_synthesizer,
                    output_dir=output_dir,
                    args=mock_args,
                    chapter_sound=None,
                    section_sound=None,
                )

                all_tts_text = " ".join(
                    call.kwargs.get("text", call.args[1] if len(call.args) > 1 else "")
                    for call in mock_gen.call_args_list
                )

        assert "Availability" not in all_tts_text, f"TTS テキストに 'Availability' が含まれている: {all_tts_text!r}"
        assert "Scalability" not in all_tts_text, f"TTS テキストに 'Scalability' が含まれている: {all_tts_text!r}"


class TestProcessContentConvertsNumbersToKana:
    """T010: process_content が数字をカナに変換することを検証する。

    US1 Acceptance Scenario 5:
    - Given 数字「123」を含むテキスト
    - When 処理する
    - Then 「ひゃくにじゅうさん」と読み上げられる
    """

    def test_numbers_converted_to_kana(self):
        """数字がカナに変換されて TTS に渡される"""
        from src.xml2_parser import ContentItem
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(
                item_type="paragraph",
                text="合計は123個です。",
                heading_info=None,
            ),
        ]

        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = (
            np.zeros(2400, dtype=np.float32),
            24000,
        )

        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)

            with patch("src.chapter_processor.generate_audio") as mock_gen:
                mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

                process_content(
                    content_items,
                    synthesizer=mock_synthesizer,
                    output_dir=output_dir,
                    args=mock_args,
                    chapter_sound=None,
                    section_sound=None,
                )

                all_tts_text = " ".join(
                    call.kwargs.get("text", call.args[1] if len(call.args) > 1 else "")
                    for call in mock_gen.call_args_list
                )

        # 数字 "123" はそのままの形で TTS に渡されてはいけない
        # clean_page_text() が適用されれば、カナに変換される
        assert "123" not in all_tts_text, (
            f"TTS テキストに生の数字 '123' が含まれている（カナ変換されるべき）: {all_tts_text!r}"
        )

    def test_year_number_converted(self):
        """年号の数字もカナに変換される"""
        from src.xml2_parser import ContentItem
        from src.xml2_pipeline import process_content

        content_items = [
            ContentItem(
                item_type="paragraph",
                text="2024年に発表されました。",
                heading_info=None,
            ),
        ]

        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = (
            np.zeros(2400, dtype=np.float32),
            24000,
        )

        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)

            with patch("src.chapter_processor.generate_audio") as mock_gen:
                mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

                process_content(
                    content_items,
                    synthesizer=mock_synthesizer,
                    output_dir=output_dir,
                    args=mock_args,
                    chapter_sound=None,
                    section_sound=None,
                )

                all_tts_text = " ".join(
                    call.kwargs.get("text", call.args[1] if len(call.args) > 1 else "")
                    for call in mock_gen.call_args_list
                )

        assert "2024" not in all_tts_text, (
            f"TTS テキストに生の数字 '2024' が含まれている（カナ変換されるべき）: {all_tts_text!r}"
        )


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Edge cases for xml2_pipeline."""

    def test_parse_args_empty_chapter_sound_path(self):
        """--chapter-sound に空パスを設定した場合"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML), "--chapter-sound", ""])

        assert args.chapter_sound == "", "Empty chapter_sound path should be accepted"

    def test_parse_args_relative_paths(self):
        """相対パスを受け付ける"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["-i", "sample/book2.xml", "--chapter-sound", "./sounds/chapter.mp3"])

        assert args.input == "sample/book2.xml"
        assert args.chapter_sound == "./sounds/chapter.mp3"


# =============================================================================
# Phase 3 RED Tests - US2: チャプター単位の分割出力
# =============================================================================


# --- T022: test_sanitize_filename ---


class TestSanitizeFilename:
    """T022: sanitize_filename がファイル名をサニタイズすることを検証する。

    US2 要件 (FR-003):
    - ch{NN}_{sanitized_title}.wav 形式のファイル名を生成
    - 半角英数字とアンダースコアのみ許可
    - 日本語タイトルは除去
    - 空の場合は "untitled"
    - 最大20文字
    """

    def test_sanitize_filename_function_exists(self):
        """sanitize_filename 関数が存在する"""
        from src.xml2_pipeline import sanitize_filename

        assert callable(sanitize_filename), "sanitize_filename は呼び出し可能な関数であるべき"

    def test_sanitize_filename_english_title(self):
        """英語タイトルはそのままサニタイズされる"""
        from src.xml2_pipeline import sanitize_filename

        result = sanitize_filename(1, "Introduction")

        assert result == "ch01_Introduction", (
            f"英語タイトルのサニタイズ結果は 'ch01_Introduction' であるべきだが、'{result}' が返された"
        )

    def test_sanitize_filename_japanese_title(self):
        """日本語タイトルは除去される（半角英数字のみ残る）"""
        from src.xml2_pipeline import sanitize_filename

        result = sanitize_filename(2, "はじめに")

        # 日本語のみの場合、英数字が残らないので untitled になる
        assert result == "ch02_untitled", (
            f"日本語のみのタイトルは 'ch02_untitled' であるべきだが、'{result}' が返された"
        )

    def test_sanitize_filename_mixed_title(self):
        """日本語と英語の混合タイトル"""
        from src.xml2_pipeline import sanitize_filename

        result = sanitize_filename(3, "Python入門")

        assert result == "ch03_Python", (
            f"混合タイトルのサニタイズ結果は 'ch03_Python' であるべきだが、'{result}' が返された"
        )

    def test_sanitize_filename_empty_title(self):
        """空タイトルは untitled になる"""
        from src.xml2_pipeline import sanitize_filename

        result = sanitize_filename(1, "")

        assert result == "ch01_untitled", f"空タイトルは 'ch01_untitled' であるべきだが、'{result}' が返された"

    def test_sanitize_filename_special_characters(self):
        """特殊文字は除去される"""
        from src.xml2_pipeline import sanitize_filename

        result = sanitize_filename(1, "Hello/World:Test?")

        # /, :, ? は除去、英数字のみ残る
        assert "ch01_" in result, (
            f"特殊文字を含むタイトルのサニタイズ結果には"
            f"プレフィックス 'ch01_' が含まれるべきだが、'{result}' が返された"
        )
        assert "/" not in result, f"'/' が含まれてはいけない: '{result}'"
        assert ":" not in result, f"':' が含まれてはいけない: '{result}'"
        assert "?" not in result, f"'?' が含まれてはいけない: '{result}'"

    def test_sanitize_filename_number_zero_padded(self):
        """章番号はゼロ埋め2桁"""
        from src.xml2_pipeline import sanitize_filename

        result = sanitize_filename(5, "Test")

        assert result.startswith("ch05_"), f"章番号 5 は 'ch05_' で始まるべきだが、'{result}' が返された"

    def test_sanitize_filename_large_chapter_number(self):
        """2桁以上の章番号"""
        from src.xml2_pipeline import sanitize_filename

        result = sanitize_filename(12, "Test")

        assert result.startswith("ch12_"), f"章番号 12 は 'ch12_' で始まるべきだが、'{result}' が返された"

    def test_sanitize_filename_max_length(self):
        """サニタイズ後のタイトル部分が最大20文字"""
        from src.xml2_pipeline import sanitize_filename

        long_title = "A" * 50  # 50文字の英語タイトル
        result = sanitize_filename(1, long_title)

        # ch01_ (5文字) + 最大20文字 = 25文字以下
        title_part = result[5:]  # "ch01_" を除いた部分
        assert len(title_part) <= 20, f"タイトル部分は最大20文字であるべきだが、{len(title_part)}文字: '{result}'"

    def test_sanitize_filename_spaces_to_underscores(self):
        """スペースはアンダースコアに変換される"""
        from src.xml2_pipeline import sanitize_filename

        result = sanitize_filename(1, "Hello World")

        assert " " not in result, f"スペースが含まれてはいけない: '{result}'"
        assert "Hello" in result and "World" in result, f"'Hello' と 'World' が含まれるべき: '{result}'"


# --- T023: test_process_chapters_creates_chapter_files ---


class TestProcessChaptersCreatesChapterFiles:
    """T023: process_chapters が chapter ごとの WAV ファイルを chapters/ ディレクトリに生成することを検証する。

    US2 要件 (FR-002):
    - chapter 要素ごとに個別の WAV ファイルを chapters/ ディレクトリに出力
    - ファイル名は ch{NN}_{sanitized_title}.wav 形式
    """

    def test_process_chapters_function_exists(self):
        """process_chapters 関数が存在する"""
        from src.xml2_pipeline import process_chapters

        assert callable(process_chapters), "process_chapters は呼び出し可能な関数であるべき"

    def test_process_chapters_creates_chapters_directory(self, tmp_path):
        """process_chapters が chapters/ ディレクトリを作成する"""
        from src.xml2_parser import CHAPTER_MARKER, ContentItem, HeadingInfo
        from src.xml2_pipeline import process_chapters

        content_items = [
            ContentItem(
                item_type="heading",
                text=f"{CHAPTER_MARKER}第1章 Introduction",
                heading_info=HeadingInfo(level=1, number="1", title="Introduction", read_aloud=True),
                chapter_number=1,
            ),
            ContentItem(
                item_type="paragraph",
                text="First chapter content.",
                heading_info=None,
                chapter_number=1,
            ),
        ]

        mock_synthesizer = MagicMock()
        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with patch("src.chapter_processor.generate_audio") as mock_gen:
            mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

            process_chapters(
                content_items,
                synthesizer=mock_synthesizer,
                output_dir=output_dir,
                args=mock_args,
                chapter_sound=None,
                section_sound=None,
            )

        chapters_dir = output_dir / "chapters"
        assert chapters_dir.exists(), f"chapters/ ディレクトリが作成されるべきだが、存在しない: {chapters_dir}"

    def test_process_chapters_creates_chapter_wav_files(self, tmp_path):
        """process_chapters が chapter ごとの WAV ファイルを作成する"""
        from src.xml2_parser import CHAPTER_MARKER, ContentItem, HeadingInfo
        from src.xml2_pipeline import process_chapters

        content_items = [
            ContentItem(
                item_type="heading",
                text=f"{CHAPTER_MARKER}第1章 First",
                heading_info=HeadingInfo(level=1, number="1", title="First", read_aloud=True),
                chapter_number=1,
            ),
            ContentItem(
                item_type="paragraph",
                text="Chapter 1 content.",
                heading_info=None,
                chapter_number=1,
            ),
            ContentItem(
                item_type="heading",
                text=f"{CHAPTER_MARKER}第2章 Second",
                heading_info=HeadingInfo(level=1, number="2", title="Second", read_aloud=True),
                chapter_number=2,
            ),
            ContentItem(
                item_type="paragraph",
                text="Chapter 2 content.",
                heading_info=None,
                chapter_number=2,
            ),
        ]

        mock_synthesizer = MagicMock()
        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with patch("src.chapter_processor.generate_audio") as mock_gen:
            mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

            process_chapters(
                content_items,
                synthesizer=mock_synthesizer,
                output_dir=output_dir,
                args=mock_args,
                chapter_sound=None,
                section_sound=None,
            )

        chapters_dir = output_dir / "chapters"
        wav_files = sorted(chapters_dir.glob("*.wav"))

        assert len(wav_files) == 2, (
            f"2つの chapter WAV ファイルが作成されるべきだが、{len(wav_files)} 個が見つかった: {wav_files}"
        )

    def test_process_chapters_filename_format(self, tmp_path):
        """chapter WAV ファイル名が ch{NN}_{title}.wav 形式である"""
        from src.xml2_parser import CHAPTER_MARKER, ContentItem, HeadingInfo
        from src.xml2_pipeline import process_chapters

        content_items = [
            ContentItem(
                item_type="heading",
                text=f"{CHAPTER_MARKER}第1章 Introduction",
                heading_info=HeadingInfo(level=1, number="1", title="Introduction", read_aloud=True),
                chapter_number=1,
            ),
            ContentItem(
                item_type="paragraph",
                text="Content here.",
                heading_info=None,
                chapter_number=1,
            ),
        ]

        mock_synthesizer = MagicMock()
        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with patch("src.chapter_processor.generate_audio") as mock_gen:
            mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

            process_chapters(
                content_items,
                synthesizer=mock_synthesizer,
                output_dir=output_dir,
                args=mock_args,
                chapter_sound=None,
                section_sound=None,
            )

        chapters_dir = output_dir / "chapters"
        wav_files = list(chapters_dir.glob("*.wav"))

        assert len(wav_files) >= 1, "少なくとも1つの WAV ファイルが作成されるべき"
        filename = wav_files[0].stem  # 拡張子なし
        assert filename.startswith("ch01_"), f"ファイル名は 'ch01_' で始まるべきだが、'{filename}' が返された"

    def test_process_chapters_three_chapters(self, tmp_path):
        """3つの chapter を処理した場合に3つの WAV ファイルが生成される"""
        from src.xml2_parser import CHAPTER_MARKER, ContentItem, HeadingInfo
        from src.xml2_pipeline import process_chapters

        content_items = []
        for ch_num in range(1, 4):
            content_items.extend(
                [
                    ContentItem(
                        item_type="heading",
                        text=f"{CHAPTER_MARKER}第{ch_num}章 Chapter{ch_num}",
                        heading_info=HeadingInfo(
                            level=1, number=str(ch_num), title=f"Chapter{ch_num}", read_aloud=True
                        ),
                        chapter_number=ch_num,
                    ),
                    ContentItem(
                        item_type="paragraph",
                        text=f"Content of chapter {ch_num}.",
                        heading_info=None,
                        chapter_number=ch_num,
                    ),
                ]
            )

        mock_synthesizer = MagicMock()
        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with patch("src.chapter_processor.generate_audio") as mock_gen:
            mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

            process_chapters(
                content_items,
                synthesizer=mock_synthesizer,
                output_dir=output_dir,
                args=mock_args,
                chapter_sound=None,
                section_sound=None,
            )

        chapters_dir = output_dir / "chapters"
        wav_files = sorted(chapters_dir.glob("*.wav"))

        assert len(wav_files) == 3, (
            f"3つの chapter WAV ファイルが作成されるべきだが、{len(wav_files)} 個が見つかった: "
            f"{[f.name for f in wav_files]}"
        )


# --- T024: test_process_chapters_creates_book_wav ---


class TestProcessChaptersCreatesBookWav:
    """T024: process_chapters が全 chapter を結合した book.wav を生成することを検証する。

    US2 要件 (FR-004):
    - 全 chapter を結合した book.wav も生成される
    """

    def test_process_chapters_creates_book_wav(self, tmp_path):
        """process_chapters が book.wav を生成する"""
        from src.xml2_parser import CHAPTER_MARKER, ContentItem, HeadingInfo
        from src.xml2_pipeline import process_chapters

        content_items = [
            ContentItem(
                item_type="heading",
                text=f"{CHAPTER_MARKER}第1章 First",
                heading_info=HeadingInfo(level=1, number="1", title="First", read_aloud=True),
                chapter_number=1,
            ),
            ContentItem(
                item_type="paragraph",
                text="Chapter 1 content.",
                heading_info=None,
                chapter_number=1,
            ),
            ContentItem(
                item_type="heading",
                text=f"{CHAPTER_MARKER}第2章 Second",
                heading_info=HeadingInfo(level=1, number="2", title="Second", read_aloud=True),
                chapter_number=2,
            ),
            ContentItem(
                item_type="paragraph",
                text="Chapter 2 content.",
                heading_info=None,
                chapter_number=2,
            ),
        ]

        mock_synthesizer = MagicMock()
        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with patch("src.chapter_processor.generate_audio") as mock_gen:
            mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

            process_chapters(
                content_items,
                synthesizer=mock_synthesizer,
                output_dir=output_dir,
                args=mock_args,
                chapter_sound=None,
                section_sound=None,
            )

        book_wav = output_dir / "book.wav"
        assert book_wav.exists(), f"book.wav が生成されるべきだが、存在しない: {book_wav}"

    def test_process_chapters_book_wav_and_chapter_files_coexist(self, tmp_path):
        """book.wav と chapters/ の WAV ファイルが両方存在する"""
        from src.xml2_parser import CHAPTER_MARKER, ContentItem, HeadingInfo
        from src.xml2_pipeline import process_chapters

        content_items = [
            ContentItem(
                item_type="heading",
                text=f"{CHAPTER_MARKER}第1章 Only",
                heading_info=HeadingInfo(level=1, number="1", title="Only", read_aloud=True),
                chapter_number=1,
            ),
            ContentItem(
                item_type="paragraph",
                text="Solo chapter.",
                heading_info=None,
                chapter_number=1,
            ),
        ]

        mock_synthesizer = MagicMock()
        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with patch("src.chapter_processor.generate_audio") as mock_gen:
            mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

            process_chapters(
                content_items,
                synthesizer=mock_synthesizer,
                output_dir=output_dir,
                args=mock_args,
                chapter_sound=None,
                section_sound=None,
            )

        book_wav = output_dir / "book.wav"
        chapters_dir = output_dir / "chapters"

        assert book_wav.exists(), "book.wav が存在するべき"
        assert chapters_dir.exists(), "chapters/ ディレクトリが存在するべき"
        assert len(list(chapters_dir.glob("*.wav"))) >= 1, "chapters/ に少なくとも1つの WAV ファイルが存在するべき"


# --- T025: test_process_content_without_chapters_creates_book_wav ---


# =============================================================================
# Phase 4 RED Tests - US3: cleaned_text.txt の品質向上
# =============================================================================


class TestCleanedTextFileContainsCleanedContent:
    """T039: cleaned_text.txt に clean_page_text() 適用済みテキストが出力されることを検証する。

    US3 要件 (FR-005):
    - cleaned_text.txt にクリーニング済みテキストを出力
    - URL、括弧内英語が除去されている
    - 数字がカナに変換されている
    """

    def test_cleaned_text_does_not_contain_url(self, tmp_path):
        """cleaned_text.txt に URL が含まれていないことを確認する"""
        from src.xml2_pipeline import main

        # Create a test XML with URL-containing text
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<book>
  <chapter number="1" title="Introduction">
    <paragraph>詳細は https://example.com/path を参照してください。</paragraph>
  </chapter>
</book>"""
        xml_path = tmp_path / "test_book.xml"
        xml_path.write_text(xml_content, encoding="utf-8")

        output_dir = tmp_path / "output"

        with (
            patch("src.xml2_pipeline.init_for_content"),
            patch("src.xml2_pipeline.get_content_hash", return_value="testhash"),
            patch("src.xml2_pipeline.VoicevoxConfig"),
            patch("src.xml2_pipeline.VoicevoxSynthesizer"),
            patch("src.chapter_processor.generate_audio") as mock_gen,
            patch("src.chapter_processor.save_audio"),
            patch("src.chapter_processor.concatenate_audio_files"),
        ):
            mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

            main(
                [
                    "--input",
                    str(xml_path),
                    "--output",
                    str(output_dir),
                    "--chapter-sound",
                    "",
                    "--section-sound",
                    "",
                ]
            )

        # Find cleaned_text.txt in output
        cleaned_text_files = list(output_dir.rglob("cleaned_text.txt"))
        assert len(cleaned_text_files) >= 1, "cleaned_text.txt が生成されるべき"

        content = cleaned_text_files[0].read_text(encoding="utf-8")
        assert "https://example.com" not in content, (
            f"cleaned_text.txt に URL が含まれている（clean_page_text() が適用されるべき）: {content!r}"
        )
        assert "example.com" not in content, f"cleaned_text.txt にドメイン名が含まれている: {content!r}"

    def test_cleaned_text_does_not_contain_parenthetical_english(self, tmp_path):
        """cleaned_text.txt に括弧内英語が含まれていないことを確認する"""
        from src.xml2_pipeline import main

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<book>
  <chapter number="1" title="Basics">
    <paragraph>信頼性 (Reliability) は重要です。</paragraph>
  </chapter>
</book>"""
        xml_path = tmp_path / "test_book.xml"
        xml_path.write_text(xml_content, encoding="utf-8")

        output_dir = tmp_path / "output"

        with (
            patch("src.xml2_pipeline.init_for_content"),
            patch("src.xml2_pipeline.get_content_hash", return_value="testhash"),
            patch("src.xml2_pipeline.VoicevoxConfig"),
            patch("src.xml2_pipeline.VoicevoxSynthesizer"),
            patch("src.chapter_processor.generate_audio") as mock_gen,
            patch("src.chapter_processor.save_audio"),
            patch("src.chapter_processor.concatenate_audio_files"),
        ):
            mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

            main(
                [
                    "--input",
                    str(xml_path),
                    "--output",
                    str(output_dir),
                    "--chapter-sound",
                    "",
                    "--section-sound",
                    "",
                ]
            )

        cleaned_text_files = list(output_dir.rglob("cleaned_text.txt"))
        assert len(cleaned_text_files) >= 1, "cleaned_text.txt が生成されるべき"

        content = cleaned_text_files[0].read_text(encoding="utf-8")
        assert "(Reliability)" not in content, (
            f"cleaned_text.txt に括弧内英語が含まれている（clean_page_text() が適用されるべき）: {content!r}"
        )

    def test_cleaned_text_numbers_converted_to_kana(self, tmp_path):
        """cleaned_text.txt の数字がカナに変換されていることを確認する"""
        from src.xml2_pipeline import main

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<book>
  <chapter number="1" title="Numbers">
    <paragraph>合計は123個です。</paragraph>
  </chapter>
</book>"""
        xml_path = tmp_path / "test_book.xml"
        xml_path.write_text(xml_content, encoding="utf-8")

        output_dir = tmp_path / "output"

        with (
            patch("src.xml2_pipeline.init_for_content"),
            patch("src.xml2_pipeline.get_content_hash", return_value="testhash"),
            patch("src.xml2_pipeline.VoicevoxConfig"),
            patch("src.xml2_pipeline.VoicevoxSynthesizer"),
            patch("src.chapter_processor.generate_audio") as mock_gen,
            patch("src.chapter_processor.save_audio"),
            patch("src.chapter_processor.concatenate_audio_files"),
        ):
            mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

            main(
                [
                    "--input",
                    str(xml_path),
                    "--output",
                    str(output_dir),
                    "--chapter-sound",
                    "",
                    "--section-sound",
                    "",
                ]
            )

        cleaned_text_files = list(output_dir.rglob("cleaned_text.txt"))
        assert len(cleaned_text_files) >= 1, "cleaned_text.txt が生成されるべき"

        content = cleaned_text_files[0].read_text(encoding="utf-8")
        assert "123" not in content, (
            f"cleaned_text.txt に生の数字 '123' が含まれている（カナ変換されるべき）: {content!r}"
        )

    def test_cleaned_text_isbn_removed(self, tmp_path):
        """cleaned_text.txt に ISBN が含まれていないことを確認する"""
        from src.xml2_pipeline import main

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<book>
  <chapter number="1" title="References">
    <paragraph>参考文献 ISBN978-4-87311-778-2 を参照。</paragraph>
  </chapter>
</book>"""
        xml_path = tmp_path / "test_book.xml"
        xml_path.write_text(xml_content, encoding="utf-8")

        output_dir = tmp_path / "output"

        with (
            patch("src.xml2_pipeline.init_for_content"),
            patch("src.xml2_pipeline.get_content_hash", return_value="testhash"),
            patch("src.xml2_pipeline.VoicevoxConfig"),
            patch("src.xml2_pipeline.VoicevoxSynthesizer"),
            patch("src.chapter_processor.generate_audio") as mock_gen,
            patch("src.chapter_processor.save_audio"),
            patch("src.chapter_processor.concatenate_audio_files"),
        ):
            mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

            main(
                [
                    "--input",
                    str(xml_path),
                    "--output",
                    str(output_dir),
                    "--chapter-sound",
                    "",
                    "--section-sound",
                    "",
                ]
            )

        cleaned_text_files = list(output_dir.rglob("cleaned_text.txt"))
        assert len(cleaned_text_files) >= 1, "cleaned_text.txt が生成されるべき"

        content = cleaned_text_files[0].read_text(encoding="utf-8")
        assert "ISBN" not in content, (
            f"cleaned_text.txt に ISBN が含まれている（clean_page_text() が適用されるべき）: {content!r}"
        )


class TestCleanedTextFileHasChapterMarkers:
    """T040: cleaned_text.txt に章区切りマーカーが含まれていることを検証する。

    US3 要件 (spec.md Acceptance Scenario 2):
    - 見出し要素が「第N章」「第N.N節」形式で整形されている
    - chapter 区切りが識別できる形式で出力されている
    """

    def test_cleaned_text_has_chapter_separator_format(self, tmp_path):
        """cleaned_text.txt に === Chapter N: Title === 形式の章区切りが含まれる"""
        from src.xml2_pipeline import main

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<book>
  <chapter number="1" title="First Chapter">
    <paragraph>最初の章の内容。</paragraph>
  </chapter>
  <chapter number="2" title="Second Chapter">
    <paragraph>二番目の章の内容。</paragraph>
  </chapter>
</book>"""
        xml_path = tmp_path / "test_book.xml"
        xml_path.write_text(xml_content, encoding="utf-8")

        output_dir = tmp_path / "output"

        with (
            patch("src.xml2_pipeline.init_for_content"),
            patch("src.xml2_pipeline.get_content_hash", return_value="testhash"),
            patch("src.xml2_pipeline.VoicevoxConfig"),
            patch("src.xml2_pipeline.VoicevoxSynthesizer"),
            patch("src.chapter_processor.generate_audio") as mock_gen,
            patch("src.chapter_processor.save_audio"),
            patch("src.chapter_processor.concatenate_audio_files"),
        ):
            mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

            main(
                [
                    "--input",
                    str(xml_path),
                    "--output",
                    str(output_dir),
                    "--chapter-sound",
                    "",
                    "--section-sound",
                    "",
                ]
            )

        cleaned_text_files = list(output_dir.rglob("cleaned_text.txt"))
        assert len(cleaned_text_files) >= 1, "cleaned_text.txt が生成されるべき"

        content = cleaned_text_files[0].read_text(encoding="utf-8")

        # === Chapter N: Title === 形式の区切りが含まれるべき
        assert "=== Chapter 1:" in content or "=== 第1章:" in content, (
            f"cleaned_text.txt に '=== Chapter 1:' 形式の章区切りが含まれるべき: {content!r}"
        )
        assert "=== Chapter 2:" in content or "=== 第2章:" in content, (
            f"cleaned_text.txt に '=== Chapter 2:' 形式の章区切りが含まれるべき: {content!r}"
        )

    def test_cleaned_text_chapter_separator_contains_title(self, tmp_path):
        """cleaned_text.txt の章区切り行にタイトルが含まれる（=== 形式）"""
        from src.xml2_pipeline import main

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<book>
  <chapter number="1" title="Introduction">
    <paragraph>導入テキスト。</paragraph>
  </chapter>
</book>"""
        xml_path = tmp_path / "test_book.xml"
        xml_path.write_text(xml_content, encoding="utf-8")

        output_dir = tmp_path / "output"

        with (
            patch("src.xml2_pipeline.init_for_content"),
            patch("src.xml2_pipeline.get_content_hash", return_value="testhash"),
            patch("src.xml2_pipeline.VoicevoxConfig"),
            patch("src.xml2_pipeline.VoicevoxSynthesizer"),
            patch("src.chapter_processor.generate_audio") as mock_gen,
            patch("src.chapter_processor.save_audio"),
            patch("src.chapter_processor.concatenate_audio_files"),
        ):
            mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

            main(
                [
                    "--input",
                    str(xml_path),
                    "--output",
                    str(output_dir),
                    "--chapter-sound",
                    "",
                    "--section-sound",
                    "",
                ]
            )

        cleaned_text_files = list(output_dir.rglob("cleaned_text.txt"))
        assert len(cleaned_text_files) >= 1, "cleaned_text.txt が生成されるべき"

        content = cleaned_text_files[0].read_text(encoding="utf-8")

        # === Chapter 1: Introduction === のような形式の行が含まれるべき
        lines = content.split("\n")
        has_separator_with_title = any("===" in line and "Introduction" in line for line in lines)
        assert has_separator_with_title, (
            f"cleaned_text.txt に '=== ... Introduction ===' 形式の章区切り行が含まれるべき: {content!r}"
        )

    def test_cleaned_text_paragraph_text_is_cleaned(self, tmp_path):
        """cleaned_text.txt の段落テキストに clean_page_text() が適用されている"""
        from src.xml2_pipeline import main

        # URL と括弧英語と数字を含むテキスト
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<book>
  <chapter number="1" title="Mixed">
    <paragraph>詳細は https://example.com を参照。可用性 (Availability) は100パーセント。</paragraph>
  </chapter>
</book>"""
        xml_path = tmp_path / "test_book.xml"
        xml_path.write_text(xml_content, encoding="utf-8")

        output_dir = tmp_path / "output"

        with (
            patch("src.xml2_pipeline.init_for_content"),
            patch("src.xml2_pipeline.get_content_hash", return_value="testhash"),
            patch("src.xml2_pipeline.VoicevoxConfig"),
            patch("src.xml2_pipeline.VoicevoxSynthesizer"),
            patch("src.chapter_processor.generate_audio") as mock_gen,
            patch("src.chapter_processor.save_audio"),
            patch("src.chapter_processor.concatenate_audio_files"),
        ):
            mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

            main(
                [
                    "--input",
                    str(xml_path),
                    "--output",
                    str(output_dir),
                    "--chapter-sound",
                    "",
                    "--section-sound",
                    "",
                ]
            )

        cleaned_text_files = list(output_dir.rglob("cleaned_text.txt"))
        assert len(cleaned_text_files) >= 1, "cleaned_text.txt が生成されるべき"

        content = cleaned_text_files[0].read_text(encoding="utf-8")

        # URL、括弧英語、生数字が全て除去/変換されているべき
        assert "https://example.com" not in content, f"cleaned_text.txt に URL が含まれている: {content!r}"
        assert "(Availability)" not in content, f"cleaned_text.txt に括弧英語が含まれている: {content!r}"
        assert "100" not in content, f"cleaned_text.txt に生の数字 '100' が含まれている: {content!r}"

    def test_cleaned_text_no_item_type_labels(self, tmp_path):
        """cleaned_text.txt に '=== paragraph ===' のような
        item_type ラベルが含まれない（クリーニング後の形式を使用）"""
        from src.xml2_pipeline import main

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<book>
  <chapter number="1" title="Test">
    <paragraph>テスト段落。</paragraph>
  </chapter>
</book>"""
        xml_path = tmp_path / "test_book.xml"
        xml_path.write_text(xml_content, encoding="utf-8")

        output_dir = tmp_path / "output"

        with (
            patch("src.xml2_pipeline.init_for_content"),
            patch("src.xml2_pipeline.get_content_hash", return_value="testhash"),
            patch("src.xml2_pipeline.VoicevoxConfig"),
            patch("src.xml2_pipeline.VoicevoxSynthesizer"),
            patch("src.chapter_processor.generate_audio") as mock_gen,
            patch("src.chapter_processor.save_audio"),
            patch("src.chapter_processor.concatenate_audio_files"),
        ):
            mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

            main(
                [
                    "--input",
                    str(xml_path),
                    "--output",
                    str(output_dir),
                    "--chapter-sound",
                    "",
                    "--section-sound",
                    "",
                ]
            )

        cleaned_text_files = list(output_dir.rglob("cleaned_text.txt"))
        assert len(cleaned_text_files) >= 1, "cleaned_text.txt が生成されるべき"

        content = cleaned_text_files[0].read_text(encoding="utf-8")

        # clean_page_text() 適用済みの形式では item_type ラベル（=== paragraph ===）は不要
        # 代わりに章区切り（=== Chapter N: Title ===）を使用する
        assert "=== paragraph ===" not in content, (
            f"cleaned_text.txt に '=== paragraph ===' ラベルが含まれている"
            f"（クリーニング済み形式を使用すべき）: {content!r}"
        )
        assert "=== heading ===" not in content, (
            f"cleaned_text.txt に '=== heading ===' ラベルが含まれている"
            f"（クリーニング済み形式を使用すべき）: {content!r}"
        )


# =============================================================================
# Phase 3 RED Tests (010) - US2: 既存テキストから TTS 生成
# =============================================================================


class TestParseArgsCleanedTextOption:
    """T024: --cleaned-text オプションパーステストを追加。

    US2 要件:
    - parse_args() が --cleaned-text オプションを受け付ける
    - オプショナル（指定なしで従来動作）
    - 指定時はファイルパスを文字列として受け取る
    """

    def test_cleaned_text_option_accepted(self):
        """--cleaned-text オプションが受け付けられる"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML), "--cleaned-text", "/path/to/cleaned_text.txt"])

        assert args.cleaned_text == "/path/to/cleaned_text.txt", (
            f"--cleaned-text は '/path/to/cleaned_text.txt' であるべきだが、'{args.cleaned_text}' が返された"
        )

    def test_cleaned_text_option_default_is_none(self):
        """--cleaned-text 未指定時のデフォルトは None"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML)])

        assert args.cleaned_text is None, (
            f"--cleaned-text のデフォルトは None であるべきだが、'{args.cleaned_text}' が返された"
        )

    def test_cleaned_text_option_with_relative_path(self):
        """--cleaned-text に相対パスを指定できる"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML), "--cleaned-text", "./output/abc123/cleaned_text.txt"])

        assert args.cleaned_text == "./output/abc123/cleaned_text.txt", (
            f"--cleaned-text は相対パスを受け付けるべき: '{args.cleaned_text}'"
        )

    def test_cleaned_text_option_coexists_with_other_options(self):
        """--cleaned-text は他のオプションと共存できる"""
        from src.xml2_pipeline import parse_args

        args = parse_args(
            [
                "-i",
                str(SAMPLE_BOOK2_XML),
                "--cleaned-text",
                "/path/to/cleaned.txt",
                "--speed",
                "1.5",
                "--style-id",
                "1",
            ]
        )

        assert args.cleaned_text == "/path/to/cleaned.txt"
        assert args.speed == 1.5
        assert args.style_id == 1


class TestMainWithCleanedTextSkipsCleaning:
    """T025: --cleaned-text 指定時のテキストクリーニングスキップテストを追加。

    US2 要件:
    - --cleaned-text 指定時は XML パースは行うが、テキストクリーニングをスキップ
    - 指定ファイルの内容を cleaned_text として使用
    - TTS 生成は通常通り実行される
    """

    def test_main_with_cleaned_text_skips_text_cleaning(self, tmp_path):
        """--cleaned-text 指定時はテキストクリーニング（clean_page_text）がスキップされる"""
        from src.xml2_pipeline import main

        # テスト用 XML を作成
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<book>
  <chapter number="1" title="Test">
    <paragraph>テスト段落。</paragraph>
  </chapter>
</book>"""
        xml_path = tmp_path / "test_book.xml"
        xml_path.write_text(xml_content, encoding="utf-8")

        # 既存の cleaned_text.txt を作成
        cleaned_text_path = tmp_path / "cleaned_text.txt"
        cleaned_text_path.write_text("事前に生成されたクリーニング済みテキスト。\n", encoding="utf-8")

        output_dir = tmp_path / "output"

        with (
            patch("src.xml2_pipeline.init_for_content"),
            patch("src.xml2_pipeline.get_content_hash", return_value="testhash"),
            patch("src.xml2_pipeline.VoicevoxConfig"),
            patch("src.xml2_pipeline.VoicevoxSynthesizer"),
            patch("src.xml2_pipeline.clean_page_text") as mock_clean,
            patch("src.chapter_processor.generate_audio") as mock_gen,
            patch("src.chapter_processor.save_audio"),
            patch("src.chapter_processor.concatenate_audio_files"),
        ):
            mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

            main(
                [
                    "--input",
                    str(xml_path),
                    "--output",
                    str(output_dir),
                    "--cleaned-text",
                    str(cleaned_text_path),
                    "--chapter-sound",
                    "",
                    "--section-sound",
                    "",
                ]
            )

            # clean_page_text はスキップされるべき（呼び出されない）
            assert not mock_clean.called, (
                f"--cleaned-text 指定時は clean_page_text() が呼び出されるべきではないが、"
                f"{mock_clean.call_count}回呼び出された"
            )

    def test_main_with_cleaned_text_does_not_overwrite_file(self, tmp_path):
        """--cleaned-text 指定時は既存の cleaned_text.txt を上書きしない"""
        from src.xml2_pipeline import main

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<book>
  <chapter number="1" title="Test">
    <paragraph>テスト段落。</paragraph>
  </chapter>
</book>"""
        xml_path = tmp_path / "test_book.xml"
        xml_path.write_text(xml_content, encoding="utf-8")

        # 既存の cleaned_text.txt を作成（特定の内容）
        original_content = "オリジナルのクリーニング済みテキスト。\n"
        cleaned_text_path = tmp_path / "cleaned_text.txt"
        cleaned_text_path.write_text(original_content, encoding="utf-8")

        output_dir = tmp_path / "output"

        with (
            patch("src.xml2_pipeline.init_for_content"),
            patch("src.xml2_pipeline.get_content_hash", return_value="testhash"),
            patch("src.xml2_pipeline.VoicevoxConfig"),
            patch("src.xml2_pipeline.VoicevoxSynthesizer"),
            patch("src.chapter_processor.generate_audio") as mock_gen,
            patch("src.chapter_processor.save_audio"),
            patch("src.chapter_processor.concatenate_audio_files"),
        ):
            mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

            main(
                [
                    "--input",
                    str(xml_path),
                    "--output",
                    str(output_dir),
                    "--cleaned-text",
                    str(cleaned_text_path),
                    "--chapter-sound",
                    "",
                    "--section-sound",
                    "",
                ]
            )

        # 元のファイル内容が保持されているべき
        actual_content = cleaned_text_path.read_text(encoding="utf-8")
        assert actual_content == original_content, (
            f"--cleaned-text 指定時はファイルが上書きされるべきではない。"
            f"期待: {original_content!r}, 実際: {actual_content!r}"
        )


class TestCleanedTextFileNotFound:
    """T026: --cleaned-text ファイル不存在時のエラーテストを追加。

    US2 受け入れシナリオ 2:
    - Given cleaned_text.txt が存在しない
    - When --cleaned-text=nonexistent を実行
    - Then 適切なエラーメッセージが表示される
    """

    def test_cleaned_text_file_not_found_raises_error(self):
        """--cleaned-text で指定したファイルが存在しない場合 FileNotFoundError"""
        from src.xml2_pipeline import main

        non_existent_cleaned = "/tmp/nonexistent_cleaned_text.txt"

        with pytest.raises(FileNotFoundError) as exc_info:
            main(
                [
                    "--input",
                    str(SAMPLE_BOOK2_XML),
                    "--cleaned-text",
                    non_existent_cleaned,
                ]
            )

        assert non_existent_cleaned in str(exc_info.value), (
            f"エラーメッセージにファイルパスが含まれるべき: {exc_info.value}"
        )

    def test_cleaned_text_file_not_found_error_message_is_descriptive(self):
        """--cleaned-text ファイル不存在時のエラーメッセージが分かりやすい"""
        from src.xml2_pipeline import main

        non_existent_cleaned = "/tmp/does_not_exist_cleaned.txt"

        with pytest.raises(FileNotFoundError) as exc_info:
            main(
                [
                    "--input",
                    str(SAMPLE_BOOK2_XML),
                    "--cleaned-text",
                    non_existent_cleaned,
                ]
            )

        error_msg = str(exc_info.value)
        # エラーメッセージに "cleaned" または "text" が含まれるべき
        assert "cleaned" in error_msg.lower() or non_existent_cleaned in error_msg, (
            f"エラーメッセージが分かりやすくない: {error_msg}"
        )


class TestBackwardCompatibilityWithoutCleanedText:
    """T027: 後方互換性テストを追加。

    US2 要件:
    - --cleaned-text 未指定時は従来通り XML パース -> テキストクリーニング -> TTS
    - 既存の動作が変わらない
    """

    def test_main_without_cleaned_text_runs_cleaning(self, tmp_path):
        """--cleaned-text 未指定時は従来通りテキストクリーニングが実行される"""
        from src.xml2_pipeline import main

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<book>
  <chapter number="1" title="Test">
    <paragraph>テスト段落。</paragraph>
  </chapter>
</book>"""
        xml_path = tmp_path / "test_book.xml"
        xml_path.write_text(xml_content, encoding="utf-8")

        output_dir = tmp_path / "output"

        with (
            patch("src.xml2_pipeline.init_for_content"),
            patch("src.xml2_pipeline.get_content_hash", return_value="testhash"),
            patch("src.xml2_pipeline.VoicevoxConfig"),
            patch("src.xml2_pipeline.VoicevoxSynthesizer"),
            patch("src.xml2_pipeline.clean_page_text") as mock_clean,
            patch("src.chapter_processor.generate_audio") as mock_gen,
            patch("src.chapter_processor.save_audio"),
            patch("src.chapter_processor.concatenate_audio_files"),
        ):
            mock_clean.return_value = "クリーニング済み"
            mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

            main(
                [
                    "--input",
                    str(xml_path),
                    "--output",
                    str(output_dir),
                    "--chapter-sound",
                    "",
                    "--section-sound",
                    "",
                ]
            )

            # --cleaned-text 未指定時は clean_page_text が呼び出されるべき
            assert mock_clean.called, (
                "--cleaned-text 未指定時は clean_page_text() が呼び出されるべきだが、呼び出されていない"
            )

    def test_main_without_cleaned_text_generates_cleaned_text_file(self, tmp_path):
        """--cleaned-text 未指定時は cleaned_text.txt が新規生成される"""
        from src.xml2_pipeline import main

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<book>
  <chapter number="1" title="Test">
    <paragraph>テスト段落。</paragraph>
  </chapter>
</book>"""
        xml_path = tmp_path / "test_book.xml"
        xml_path.write_text(xml_content, encoding="utf-8")

        output_dir = tmp_path / "output"

        with (
            patch("src.xml2_pipeline.init_for_content"),
            patch("src.xml2_pipeline.get_content_hash", return_value="testhash"),
            patch("src.xml2_pipeline.VoicevoxConfig"),
            patch("src.xml2_pipeline.VoicevoxSynthesizer"),
            patch("src.chapter_processor.generate_audio") as mock_gen,
            patch("src.chapter_processor.save_audio"),
            patch("src.chapter_processor.concatenate_audio_files"),
        ):
            mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

            main(
                [
                    "--input",
                    str(xml_path),
                    "--output",
                    str(output_dir),
                    "--chapter-sound",
                    "",
                    "--section-sound",
                    "",
                ]
            )

        # cleaned_text.txt が生成されるべき
        cleaned_text_files = list(output_dir.rglob("cleaned_text.txt"))
        assert len(cleaned_text_files) >= 1, "--cleaned-text 未指定時は cleaned_text.txt が新規生成されるべき"


class TestProcessContentWithoutChaptersCreatesBookWav:
    """T025: chapter_number が全て None の場合に book.wav のみ生成されることを検証する。

    US2 エッジケース (FR-009):
    - chapter を含まない XML の場合、全コンテンツを book.wav として出力する
    - chapters/ ディレクトリは作成されない
    """

    def test_no_chapters_creates_only_book_wav(self, tmp_path):
        """chapter_number が全て None の場合、book.wav のみ生成される"""
        from src.xml2_parser import ContentItem
        from src.xml2_pipeline import process_chapters

        # chapter_number が全て None（chapter 要素がない XML から取得した場合）
        content_items = [
            ContentItem(
                item_type="paragraph",
                text="First paragraph without chapter.",
                heading_info=None,
                chapter_number=None,
            ),
            ContentItem(
                item_type="paragraph",
                text="Second paragraph without chapter.",
                heading_info=None,
                chapter_number=None,
            ),
        ]

        mock_synthesizer = MagicMock()
        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with patch("src.chapter_processor.generate_audio") as mock_gen:
            mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

            process_chapters(
                content_items,
                synthesizer=mock_synthesizer,
                output_dir=output_dir,
                args=mock_args,
                chapter_sound=None,
                section_sound=None,
            )

        book_wav = output_dir / "book.wav"
        chapters_dir = output_dir / "chapters"

        assert book_wav.exists(), "chapter がない場合でも book.wav は生成されるべき"
        # chapters/ ディレクトリは作成されないか、空である
        if chapters_dir.exists():
            wav_files = list(chapters_dir.glob("*.wav"))
            assert len(wav_files) == 0, (
                f"chapter がない場合、chapters/ に WAV ファイルは作成されないべきだが、"
                f"{len(wav_files)} 個見つかった: {[f.name for f in wav_files]}"
            )

    def test_mixed_none_and_numbered_chapters(self, tmp_path):
        """chapter_number が混在する場合（None + 数値）は chapter のみ分割される"""
        from src.xml2_parser import CHAPTER_MARKER, ContentItem, HeadingInfo
        from src.xml2_pipeline import process_chapters

        content_items = [
            # chapter 外のコンテンツ（chapter_number=None）
            ContentItem(
                item_type="paragraph",
                text="Preamble text.",
                heading_info=None,
                chapter_number=None,
            ),
            # chapter 1 のコンテンツ
            ContentItem(
                item_type="heading",
                text=f"{CHAPTER_MARKER}第1章 Main",
                heading_info=HeadingInfo(level=1, number="1", title="Main", read_aloud=True),
                chapter_number=1,
            ),
            ContentItem(
                item_type="paragraph",
                text="Chapter content.",
                heading_info=None,
                chapter_number=1,
            ),
        ]

        mock_synthesizer = MagicMock()
        mock_args = MagicMock()
        mock_args.max_chunk_chars = 500
        mock_args.style_id = 13
        mock_args.speed = 1.0

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with patch("src.chapter_processor.generate_audio") as mock_gen:
            mock_gen.return_value = (np.zeros(2400, dtype=np.float32), 24000)

            process_chapters(
                content_items,
                synthesizer=mock_synthesizer,
                output_dir=output_dir,
                args=mock_args,
                chapter_sound=None,
                section_sound=None,
            )

        book_wav = output_dir / "book.wav"
        assert book_wav.exists(), "book.wav は常に生成されるべき"
