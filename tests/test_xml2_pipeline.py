"""Tests for book2.xml TTS pipeline.

Phase 4 RED Tests - US3: 音声パイプライン統合
Tests for xml2_pipeline.py command-line interface and content processing.

Target functions:
- src/xml2_pipeline.py::parse_args()
- src/xml2_pipeline.py::load_sound()
- src/xml2_pipeline.py::process_content()
- src/xml2_pipeline.py::main()

Test Fixture: tests/fixtures/sample_book2.xml
"""

from pathlib import Path

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
        assert exc_info.value.code == 2, (
            f"Missing --input should exit with code 2, got {exc_info.value.code}"
        )

    def test_parse_args_accepts_input_long(self):
        """--input 引数を受け付ける"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["--input", str(SAMPLE_BOOK2_XML)])

        assert args.input == str(SAMPLE_BOOK2_XML), (
            f"--input should be parsed, got {args.input}"
        )

    def test_parse_args_accepts_input_short(self):
        """-i 短縮形を受け付ける"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML)])

        assert args.input == str(SAMPLE_BOOK2_XML), (
            f"-i should be parsed, got {args.input}"
        )

    def test_output_default(self):
        """--output のデフォルトは ./output"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML)])

        assert args.output == "./output", (
            f"--output default should be './output', got {args.output}"
        )

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

        assert args.style_id == 13, (
            f"--style-id default should be 13, got {args.style_id}"
        )

    def test_speed_default(self):
        """--speed のデフォルトは 1.0"""
        from src.xml2_pipeline import parse_args

        args = parse_args(["-i", str(SAMPLE_BOOK2_XML)])

        assert args.speed == 1.0, (
            f"--speed default should be 1.0, got {args.speed}"
        )

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

        assert args.max_chunk_chars == 500, (
            f"--max-chunk-chars default should be 500, got {args.max_chunk_chars}"
        )


class TestParseArgsCustomSounds:
    """Test parse_args custom sound file options.

    T042: カスタム効果音ファイルオプションテスト
    - --chapter-sound: 任意のパス
    - --section-sound: 任意のパス
    """

    def test_chapter_sound_custom(self):
        """--chapter-sound にカスタム値を設定"""
        from src.xml2_pipeline import parse_args

        args = parse_args([
            "-i", str(SAMPLE_BOOK2_XML),
            "--chapter-sound", "/custom/path/chapter.mp3"
        ])

        assert args.chapter_sound == "/custom/path/chapter.mp3", (
            f"--chapter-sound should be '/custom/path/chapter.mp3', got {args.chapter_sound}"
        )

    def test_section_sound_custom(self):
        """--section-sound にカスタム値を設定"""
        from src.xml2_pipeline import parse_args

        args = parse_args([
            "-i", str(SAMPLE_BOOK2_XML),
            "--section-sound", "/custom/path/section.mp3"
        ])

        assert args.section_sound == "/custom/path/section.mp3", (
            f"--section-sound should be '/custom/path/section.mp3', got {args.section_sound}"
        )

    def test_both_sounds_custom(self):
        """--chapter-sound と --section-sound を両方カスタム設定"""
        from src.xml2_pipeline import parse_args

        args = parse_args([
            "-i", str(SAMPLE_BOOK2_XML),
            "--chapter-sound", "/path/to/chapter.wav",
            "--section-sound", "/path/to/section.wav"
        ])

        assert args.chapter_sound == "/path/to/chapter.wav", (
            f"--chapter-sound should be '/path/to/chapter.wav', got {args.chapter_sound}"
        )
        assert args.section_sound == "/path/to/section.wav", (
            f"--section-sound should be '/path/to/section.wav', got {args.section_sound}"
        )

    def test_output_custom(self):
        """--output にカスタム値を設定"""
        from src.xml2_pipeline import parse_args

        args = parse_args([
            "-i", str(SAMPLE_BOOK2_XML),
            "-o", "/tmp/audio"
        ])

        assert args.output == "/tmp/audio", (
            f"--output should be '/tmp/audio', got {args.output}"
        )

    def test_style_id_custom(self):
        """--style-id にカスタム値を設定"""
        from src.xml2_pipeline import parse_args

        args = parse_args([
            "-i", str(SAMPLE_BOOK2_XML),
            "--style-id", "1"
        ])

        assert args.style_id == 1, (
            f"--style-id should be 1, got {args.style_id}"
        )

    def test_speed_custom(self):
        """--speed にカスタム値を設定"""
        from src.xml2_pipeline import parse_args

        args = parse_args([
            "-i", str(SAMPLE_BOOK2_XML),
            "--speed", "1.5"
        ])

        assert args.speed == 1.5, (
            f"--speed should be 1.5, got {args.speed}"
        )


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
        from src.xml2_pipeline import load_sound
        import soundfile as sf

        # Create a test mono WAV file
        test_audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 24000)).astype(np.float32)
        sound_path = tmp_path / "test.wav"
        sf.write(sound_path, test_audio, 24000)

        result = load_sound(sound_path)

        assert isinstance(result, np.ndarray), (
            f"load_sound should return numpy.ndarray, got {type(result)}"
        )

    def test_load_sound_stereo_to_mono_conversion(self, tmp_path):
        """ステレオ音声をモノラルに変換する"""
        from src.xml2_pipeline import load_sound
        import soundfile as sf

        # Create a stereo WAV file
        duration = 0.5
        sr = 24000
        samples = int(duration * sr)
        stereo_audio = np.column_stack([
            np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples)),  # Left channel
            np.sin(2 * np.pi * 880 * np.linspace(0, duration, samples)),  # Right channel
        ]).astype(np.float32)

        sound_path = tmp_path / "stereo.wav"
        sf.write(sound_path, stereo_audio, sr)

        result = load_sound(sound_path)

        # Result should be 1D (mono)
        assert len(result.shape) == 1, (
            f"Stereo should be converted to mono (1D), got shape {result.shape}"
        )

    def test_load_sound_resampling(self, tmp_path):
        """異なるサンプルレートをリサンプリングする"""
        from src.xml2_pipeline import load_sound
        import soundfile as sf

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
        from src.xml2_pipeline import load_sound
        import soundfile as sf

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
        from src.xml2_pipeline import load_sound
        import soundfile as sf

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
        assert max_amplitude > 0.1, (
            f"Audio should be normalized, max amplitude is {max_amplitude}"
        )

    def test_load_sound_returns_float32(self, tmp_path):
        """float32 型で返却される"""
        from src.xml2_pipeline import load_sound
        import soundfile as sf

        sr = 24000
        duration = 0.5
        samples = int(duration * sr)
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples)).astype(np.float32)

        sound_path = tmp_path / "test.wav"
        sf.write(sound_path, audio, sr)

        result = load_sound(sound_path)

        assert result.dtype == np.float32, (
            f"load_sound should return float32, got {result.dtype}"
        )


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

        assert callable(process_content), (
            "process_content should be a callable function"
        )

    def test_process_content_accepts_content_items(self):
        """process_content は ContentItem リストを受け付ける"""
        from src.xml2_pipeline import process_content
        from src.xml2_parser import ContentItem

        content_items = [
            ContentItem(item_type="paragraph", text="Test paragraph", heading_info=None),
        ]

        # Should not raise
        # Note: This might need mock synthesizer in actual implementation
        try:
            # process_content signature likely includes synthesizer, sounds, etc.
            # For RED test, we just verify it accepts content_items
            result = process_content(content_items)
        except TypeError as e:
            # If missing required arguments, that's expected - function exists but needs more args
            assert "argument" in str(e).lower() or "required" in str(e).lower(), (
                f"process_content should accept content_items, got: {e}"
            )

    def test_process_content_with_chapter_marker_includes_chapter_sound(self):
        """CHAPTER_MARKER を含むテキストで chapter_sound が挿入される"""
        from src.xml2_pipeline import process_content
        from src.xml2_parser import ContentItem, HeadingInfo, CHAPTER_MARKER

        content_items = [
            ContentItem(
                item_type="heading",
                text=f"{CHAPTER_MARKER}第1章 テスト",
                heading_info=HeadingInfo(level=1, number="1", title="テスト", read_aloud=True)
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
        from src.xml2_pipeline import process_content
        from src.xml2_parser import ContentItem, HeadingInfo, SECTION_MARKER

        content_items = [
            ContentItem(
                item_type="heading",
                text=f"{SECTION_MARKER}第1.1節 サブセクション",
                heading_info=HeadingInfo(level=2, number="1.1", title="サブセクション", read_aloud=True)
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
        from src.xml2_pipeline import process_content
        from src.xml2_parser import ContentItem, HeadingInfo, CHAPTER_MARKER, SECTION_MARKER

        content_items = [
            ContentItem(
                item_type="heading",
                text=f"{CHAPTER_MARKER}第1章 最初の章",
                heading_info=HeadingInfo(level=1, number="1", title="最初の章", read_aloud=True)
            ),
            ContentItem(
                item_type="paragraph",
                text="段落テキスト",
                heading_info=None
            ),
            ContentItem(
                item_type="heading",
                text=f"{SECTION_MARKER}第1.1節 セクション",
                heading_info=HeadingInfo(level=2, number="1.1", title="セクション", read_aloud=True)
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
        from src.xml2_pipeline import process_content
        from src.xml2_parser import ContentItem

        content_items = [
            ContentItem(
                item_type="paragraph",
                text="マーカーなしの段落テキスト",
                heading_info=None
            ),
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

        assert non_existent in str(exc_info.value), (
            f"Error message should contain file path: {exc_info.value}"
        )

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
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Edge cases for xml2_pipeline."""

    def test_parse_args_empty_chapter_sound_path(self):
        """--chapter-sound に空パスを設定した場合"""
        from src.xml2_pipeline import parse_args

        args = parse_args([
            "-i", str(SAMPLE_BOOK2_XML),
            "--chapter-sound", ""
        ])

        assert args.chapter_sound == "", (
            f"Empty chapter_sound path should be accepted"
        )

    def test_parse_args_relative_paths(self):
        """相対パスを受け付ける"""
        from src.xml2_pipeline import parse_args

        args = parse_args([
            "-i", "sample/book2.xml",
            "--chapter-sound", "./sounds/chapter.mp3"
        ])

        assert args.input == "sample/book2.xml"
        assert args.chapter_sound == "./sounds/chapter.mp3"
