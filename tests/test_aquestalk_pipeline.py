"""Tests for AquesTalk TTS pipeline integration.

Phase 2 RED Tests - US1: XML から AquesTalk 音声生成
Tests for aquestalk_pipeline.py command-line interface and error handling.

Target functions:
- src/aquestalk_pipeline.py::parse_args()
- src/aquestalk_pipeline.py::main()

Follows same patterns as tests/test_xml_pipeline.py (VOICEVOX version).

AquesTalk10 specifications:
- Sample rate: 16000Hz
- Default parameters: speed=100, voice=100, pitch=100
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.aquestalk_pipeline import parse_args, main


# Fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_BOOK_XML = FIXTURES_DIR / "sample_book.xml"


# ============================================================
# T013: Test file structure (this file)
# ============================================================


# ============================================================
# T014: test_parse_args
# ============================================================

class TestParseArgsRequiredInput:
    """Test --input argument is required."""

    def test_parse_args_requires_input(self):
        """--input 引数がないとエラー"""
        with pytest.raises(SystemExit) as exc_info:
            parse_args([])

        # argparse exits with code 2 for missing required argument
        assert exc_info.value.code == 2, (
            f"Missing --input should exit with code 2, got {exc_info.value.code}"
        )

    def test_parse_args_accepts_input_long(self):
        """--input 引数を受け付ける"""
        args = parse_args(["--input", str(SAMPLE_BOOK_XML)])

        assert args.input == str(SAMPLE_BOOK_XML), (
            f"--input should be parsed, got {args.input}"
        )

    def test_parse_args_accepts_input_short(self):
        """-i 短縮形を受け付ける"""
        args = parse_args(["-i", str(SAMPLE_BOOK_XML)])

        assert args.input == str(SAMPLE_BOOK_XML), (
            f"-i should be parsed, got {args.input}"
        )


class TestParseArgsDefaults:
    """Test default values for optional arguments."""

    def test_output_default(self):
        """--output のデフォルトは ./output"""
        args = parse_args(["-i", str(SAMPLE_BOOK_XML)])

        assert args.output == "./output", (
            f"--output default should be './output', got {args.output}"
        )

    def test_start_page_default(self):
        """--start-page のデフォルトは 1"""
        args = parse_args(["-i", str(SAMPLE_BOOK_XML)])

        assert args.start_page == 1, (
            f"--start-page default should be 1, got {args.start_page}"
        )

    def test_end_page_default(self):
        """--end-page のデフォルトは None"""
        args = parse_args(["-i", str(SAMPLE_BOOK_XML)])

        assert args.end_page is None, (
            f"--end-page default should be None, got {args.end_page}"
        )

    def test_speed_default(self):
        """--speed のデフォルトは 100 (AquesTalk10)"""
        args = parse_args(["-i", str(SAMPLE_BOOK_XML)])

        assert args.speed == 100, (
            f"--speed default should be 100, got {args.speed}"
        )

    def test_voice_default(self):
        """--voice のデフォルトは 100 (AquesTalk10)"""
        args = parse_args(["-i", str(SAMPLE_BOOK_XML)])

        assert args.voice == 100, (
            f"--voice default should be 100, got {args.voice}"
        )

    def test_pitch_default(self):
        """--pitch のデフォルトは 100 (AquesTalk10)"""
        args = parse_args(["-i", str(SAMPLE_BOOK_XML)])

        assert args.pitch == 100, (
            f"--pitch default should be 100, got {args.pitch}"
        )


class TestParseArgsCustomValues:
    """Test custom values for optional arguments."""

    def test_output_custom(self):
        """--output にカスタム値を設定"""
        args = parse_args(["-i", str(SAMPLE_BOOK_XML), "--output", "/tmp/audio"])

        assert args.output == "/tmp/audio", (
            f"--output should be '/tmp/audio', got {args.output}"
        )

    def test_output_short(self):
        """-o 短縮形を受け付ける"""
        args = parse_args(["-i", str(SAMPLE_BOOK_XML), "-o", "/tmp/audio"])

        assert args.output == "/tmp/audio", (
            f"-o should be parsed, got {args.output}"
        )

    def test_start_page_custom(self):
        """--start-page にカスタム値を設定"""
        args = parse_args(["-i", str(SAMPLE_BOOK_XML), "--start-page", "5"])

        assert args.start_page == 5, (
            f"--start-page should be 5, got {args.start_page}"
        )

    def test_end_page_custom(self):
        """--end-page にカスタム値を設定"""
        args = parse_args(["-i", str(SAMPLE_BOOK_XML), "--end-page", "10"])

        assert args.end_page == 10, (
            f"--end-page should be 10, got {args.end_page}"
        )

    def test_speed_custom(self):
        """--speed にカスタム値を設定 (AquesTalk10: 50-300)"""
        args = parse_args(["-i", str(SAMPLE_BOOK_XML), "--speed", "150"])

        assert args.speed == 150, (
            f"--speed should be 150, got {args.speed}"
        )

    def test_voice_custom(self):
        """--voice にカスタム値を設定 (AquesTalk10: 0-200)"""
        args = parse_args(["-i", str(SAMPLE_BOOK_XML), "--voice", "80"])

        assert args.voice == 80, (
            f"--voice should be 80, got {args.voice}"
        )

    def test_pitch_custom(self):
        """--pitch にカスタム値を設定 (AquesTalk10: 50-200)"""
        args = parse_args(["-i", str(SAMPLE_BOOK_XML), "--pitch", "120"])

        assert args.pitch == 120, (
            f"--pitch should be 120, got {args.pitch}"
        )


# ============================================================
# T015: test_main_generates_audio
# ============================================================

class TestMainGeneratesAudio:
    """Test main() generates audio files."""

    @patch("src.aquestalk_pipeline.AquesTalkSynthesizer")
    def test_main_creates_output_directory(self, mock_synthesizer_class, tmp_path):
        """main() は出力ディレクトリを作成する"""
        # Setup mock
        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = b"\x00" * 1000  # Dummy audio
        mock_synthesizer_class.return_value = mock_synthesizer

        output_dir = tmp_path / "output"

        with patch("src.aquestalk_pipeline.init_for_content"):
            with patch("src.aquestalk_pipeline.clean_page_text", return_value="テスト"):
                main([
                    "--input", str(SAMPLE_BOOK_XML),
                    "--output", str(output_dir),
                ])

        assert output_dir.exists(), (
            f"Output directory should be created: {output_dir}"
        )

    @patch("src.aquestalk_pipeline.AquesTalkSynthesizer")
    def test_main_generates_page_wav_files(self, mock_synthesizer_class, tmp_path):
        """main() はページごとの WAV ファイルを生成する"""
        # Setup mock
        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = b"\x00" * 1000
        mock_synthesizer_class.return_value = mock_synthesizer

        output_dir = tmp_path / "output"

        with patch("src.aquestalk_pipeline.init_for_content"):
            with patch("src.aquestalk_pipeline.clean_page_text", return_value="テスト"):
                main([
                    "--input", str(SAMPLE_BOOK_XML),
                    "--output", str(output_dir),
                ])

        # Check for pages directory and WAV files
        pages_dir = output_dir / "pages"
        if pages_dir.exists():
            wav_files = list(pages_dir.glob("*.wav"))
            assert len(wav_files) > 0, (
                f"Should generate WAV files in pages directory"
            )

    @patch("src.aquestalk_pipeline.AquesTalkSynthesizer")
    def test_main_generates_book_wav(self, mock_synthesizer_class, tmp_path):
        """main() は結合済み book.wav を生成する"""
        # Setup mock
        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = b"\x00" * 1000
        mock_synthesizer_class.return_value = mock_synthesizer

        output_dir = tmp_path / "output"

        with patch("src.aquestalk_pipeline.init_for_content"):
            with patch("src.aquestalk_pipeline.clean_page_text", return_value="テスト"):
                main([
                    "--input", str(SAMPLE_BOOK_XML),
                    "--output", str(output_dir),
                ])

        # Check for book.wav (may be in a subdirectory based on hash)
        book_wavs = list(output_dir.rglob("book.wav"))
        assert len(book_wavs) > 0, (
            f"Should generate book.wav, found: {list(output_dir.rglob('*'))}"
        )


# ============================================================
# T016: test_page_range_filtering
# ============================================================

class TestPageRangeFiltering:
    """Test page range filtering with --start-page and --end-page."""

    @patch("src.aquestalk_pipeline.AquesTalkSynthesizer")
    def test_start_page_filters_pages(self, mock_synthesizer_class, tmp_path):
        """--start-page でページをフィルタリング"""
        # Setup mock
        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = b"\x00" * 1000
        mock_synthesizer_class.return_value = mock_synthesizer

        output_dir = tmp_path / "output"

        with patch("src.aquestalk_pipeline.init_for_content"):
            with patch("src.aquestalk_pipeline.clean_page_text", return_value="テスト"):
                main([
                    "--input", str(SAMPLE_BOOK_XML),
                    "--output", str(output_dir),
                    "--start-page", "2",
                ])

        # Page 1 should not be generated
        pages_dir = list(output_dir.rglob("pages"))
        if pages_dir:
            page1_files = list(pages_dir[0].glob("*0001*"))
            assert len(page1_files) == 0, (
                f"Page 1 should be filtered out with --start-page 2"
            )

    @patch("src.aquestalk_pipeline.AquesTalkSynthesizer")
    def test_end_page_filters_pages(self, mock_synthesizer_class, tmp_path):
        """--end-page でページをフィルタリング"""
        # Setup mock
        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = b"\x00" * 1000
        mock_synthesizer_class.return_value = mock_synthesizer

        output_dir = tmp_path / "output"

        with patch("src.aquestalk_pipeline.init_for_content"):
            with patch("src.aquestalk_pipeline.clean_page_text", return_value="テスト"):
                main([
                    "--input", str(SAMPLE_BOOK_XML),
                    "--output", str(output_dir),
                    "--end-page", "1",
                ])

        # Pages after 1 should not be generated
        pages_dir = list(output_dir.rglob("pages"))
        if pages_dir:
            page2_files = list(pages_dir[0].glob("*0002*"))
            assert len(page2_files) == 0, (
                f"Page 2 should be filtered out with --end-page 1"
            )

    @patch("src.aquestalk_pipeline.AquesTalkSynthesizer")
    def test_page_range_combination(self, mock_synthesizer_class, tmp_path):
        """--start-page と --end-page の組み合わせ"""
        # Setup mock
        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = b"\x00" * 1000
        mock_synthesizer_class.return_value = mock_synthesizer

        output_dir = tmp_path / "output"

        with patch("src.aquestalk_pipeline.init_for_content"):
            with patch("src.aquestalk_pipeline.clean_page_text", return_value="テスト"):
                main([
                    "--input", str(SAMPLE_BOOK_XML),
                    "--output", str(output_dir),
                    "--start-page", "2",
                    "--end-page", "2",
                ])

        # Only page 2 should be generated
        pages_dir = list(output_dir.rglob("pages"))
        if pages_dir:
            page1_files = list(pages_dir[0].glob("*0001*"))
            page3_files = list(pages_dir[0].glob("*0003*"))
            assert len(page1_files) == 0, "Page 1 should be filtered out"
            assert len(page3_files) == 0, "Page 3 should be filtered out"


# ============================================================
# T017: test_file_not_found_error
# ============================================================

class TestFileNotFoundError:
    """Test error handling for non-existent input files."""

    def test_file_not_found_raises_error(self):
        """存在しないファイルでエラー"""
        non_existent = "/tmp/non_existent_aquestalk_book.xml"

        with pytest.raises(FileNotFoundError) as exc_info:
            main(["--input", non_existent])

        assert non_existent in str(exc_info.value), (
            f"Error message should contain file path: {exc_info.value}"
        )

    def test_file_not_found_error_message(self):
        """エラーメッセージにファイルパスを含む"""
        non_existent = "/tmp/does_not_exist_aquestalk_12345.xml"

        with pytest.raises(FileNotFoundError) as exc_info:
            main(["--input", non_existent])

        error_msg = str(exc_info.value)
        assert "does_not_exist_aquestalk_12345.xml" in error_msg, (
            f"Error message should contain filename: {error_msg}"
        )


class TestInvalidXmlError:
    """Test error handling for invalid XML files."""

    def test_invalid_xml_raises_parse_error(self, tmp_path):
        """不正な XML でパースエラー"""
        invalid_xml = tmp_path / "invalid.xml"
        invalid_xml.write_text("<book><page>unclosed")

        # Should raise xml.etree.ElementTree.ParseError or wrap it
        with pytest.raises(Exception) as exc_info:
            main(["--input", str(invalid_xml)])

        # Accept either ParseError or a custom exception wrapping it
        error_type = type(exc_info.value).__name__
        assert "ParseError" in error_type or "XML" in str(exc_info.value).upper(), (
            f"Should raise parse error for invalid XML, got {error_type}: {exc_info.value}"
        )

    def test_empty_file_raises_error(self, tmp_path):
        """空ファイルでエラー"""
        empty_xml = tmp_path / "empty.xml"
        empty_xml.write_text("")

        with pytest.raises(Exception) as exc_info:
            main(["--input", str(empty_xml)])

        # Empty file should cause parse error
        error_type = type(exc_info.value).__name__
        error_msg = str(exc_info.value)
        assert "ParseError" in error_type or "no element" in error_msg.lower() or "empty" in error_msg.lower(), (
            f"Should raise error for empty file, got {error_type}: {error_msg}"
        )

    def test_non_xml_content_raises_error(self, tmp_path):
        """XML でない内容でエラー"""
        non_xml = tmp_path / "not_xml.xml"
        non_xml.write_text("This is not XML content, just plain text.")

        with pytest.raises(Exception) as exc_info:
            main(["--input", str(non_xml)])

        error_type = type(exc_info.value).__name__
        assert "ParseError" in error_type or "XML" in str(exc_info.value).upper(), (
            f"Should raise parse error for non-XML content, got {error_type}: {exc_info.value}"
        )


# ============================================================
# Phase 3: User Story 2 - 見出し効果音の挿入 (Priority: P2)
# ============================================================


# ============================================================
# T035: test_load_heading_sound
# ============================================================

class TestLoadHeadingSound:
    """Test load_heading_sound() function for loading and resampling audio."""

    def test_load_heading_sound_returns_numpy_array(self, tmp_path):
        """load_heading_sound() は numpy 配列を返す"""
        from src.aquestalk_pipeline import load_heading_sound
        import numpy as np

        # Create a test WAV file with 44100Hz sample rate
        test_wav = tmp_path / "test_sound.wav"
        import soundfile as sf
        # Create a simple sine wave at 44100Hz
        duration = 0.5
        sr_original = 44100
        t = np.linspace(0, duration, int(sr_original * duration), False)
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)
        sf.write(str(test_wav), audio, sr_original)

        result = load_heading_sound(test_wav)

        assert isinstance(result, np.ndarray), (
            f"load_heading_sound should return numpy array, got {type(result)}"
        )

    def test_load_heading_sound_resamples_to_16khz(self, tmp_path):
        """load_heading_sound() は 16kHz にリサンプリングする"""
        from src.aquestalk_pipeline import load_heading_sound
        from src.aquestalk_client import AQUESTALK_SAMPLE_RATE
        import numpy as np
        import soundfile as sf

        # Create a test WAV file with 44100Hz sample rate
        test_wav = tmp_path / "test_sound.wav"
        duration = 1.0
        sr_original = 44100
        t = np.linspace(0, duration, int(sr_original * duration), False)
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)
        sf.write(str(test_wav), audio, sr_original)

        result = load_heading_sound(test_wav, target_sr=AQUESTALK_SAMPLE_RATE)

        # At 16kHz, 1 second should have approximately 16000 samples
        expected_samples = int(duration * AQUESTALK_SAMPLE_RATE)
        tolerance = 100  # Allow some tolerance for resampling
        assert abs(len(result) - expected_samples) < tolerance, (
            f"Should resample to 16kHz ({expected_samples} samples), "
            f"got {len(result)} samples"
        )

    def test_load_heading_sound_converts_stereo_to_mono(self, tmp_path):
        """load_heading_sound() はステレオをモノラルに変換する"""
        from src.aquestalk_pipeline import load_heading_sound
        import numpy as np
        import soundfile as sf

        # Create a stereo WAV file
        test_wav = tmp_path / "stereo_sound.wav"
        duration = 0.5
        sr = 16000
        t = np.linspace(0, duration, int(sr * duration), False)
        left = 0.5 * np.sin(2 * np.pi * 440 * t)
        right = 0.5 * np.sin(2 * np.pi * 880 * t)
        stereo_audio = np.column_stack([left, right])
        sf.write(str(test_wav), stereo_audio, sr)

        result = load_heading_sound(test_wav)

        # Result should be 1D (mono)
        assert len(result.shape) == 1, (
            f"Should convert stereo to mono (1D array), got shape {result.shape}"
        )

    def test_load_heading_sound_normalizes_volume(self, tmp_path):
        """load_heading_sound() は音量を正規化する"""
        from src.aquestalk_pipeline import load_heading_sound
        import numpy as np
        import soundfile as sf

        # Create a loud WAV file
        test_wav = tmp_path / "loud_sound.wav"
        duration = 0.5
        sr = 16000
        t = np.linspace(0, duration, int(sr * duration), False)
        audio = 1.0 * np.sin(2 * np.pi * 440 * t)  # Full amplitude
        sf.write(str(test_wav), audio, sr)

        result = load_heading_sound(test_wav)

        # Max amplitude should be around 0.5 (50% volume as per implementation)
        max_amplitude = np.max(np.abs(result))
        assert max_amplitude <= 0.6, (
            f"Should normalize volume (max ~0.5), got max amplitude {max_amplitude}"
        )


# ============================================================
# T036: test_heading_sound_insertion
# ============================================================

class TestHeadingSoundInsertion:
    """Test that heading sound is inserted before heading segments."""

    @patch("src.aquestalk_pipeline.AquesTalkSynthesizer")
    def test_heading_sound_inserted_before_heading(self, mock_synthesizer_class, tmp_path):
        """見出しの前に効果音が挿入される"""
        import numpy as np
        import soundfile as sf
        from src.aquestalk_pipeline import process_pages_with_heading_sound
        from src.aquestalk_client import AquesTalkSynthesizer, AQUESTALK_SAMPLE_RATE
        from src.text_cleaner import Page
        from src.xml_parser import HEADING_MARKER

        # Setup mock synthesizer
        mock_synthesizer = MagicMock()
        # Return valid WAV data
        def mock_synthesize(text, speed=None):
            duration = 0.1
            t = np.linspace(0, duration, int(AQUESTALK_SAMPLE_RATE * duration), False)
            waveform = 0.3 * np.sin(2 * np.pi * 440 * t)
            import io
            with io.BytesIO() as buffer:
                sf.write(buffer, waveform, AQUESTALK_SAMPLE_RATE, format="WAV")
                return buffer.getvalue()
        mock_synthesizer.synthesize.side_effect = mock_synthesize
        mock_synthesizer_class.return_value = mock_synthesizer

        # Create heading sound
        heading_sound = 0.5 * np.ones(1600, dtype=np.float32)  # 0.1 sec at 16kHz

        # Create test page with HEADING_MARKER
        pages = [Page(number=1, text=f"段落テキスト{HEADING_MARKER}見出しテキスト")]

        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create mock args
        args = MagicMock()
        args.speed = 100

        # Process with heading sound
        wav_files = process_pages_with_heading_sound(
            pages=pages,
            synthesizer=mock_synthesizer,
            output_dir=output_dir,
            args=args,
            heading_sound=heading_sound,
        )

        # Verify that page WAV was created
        assert len(wav_files) > 0, "Should generate WAV files"

        # Read the generated WAV and check that heading sound is included
        page_wav = wav_files[0]
        audio, sr = sf.read(str(page_wav))

        # Audio should be longer than just synthesized text (includes heading sound)
        assert len(audio) > 0, "Generated audio should not be empty"

    @patch("src.aquestalk_pipeline.AquesTalkSynthesizer")
    def test_no_heading_sound_when_not_specified(self, mock_synthesizer_class, tmp_path):
        """--heading-sound 未指定時は効果音なし"""
        import numpy as np
        import soundfile as sf
        from src.aquestalk_pipeline import process_pages_with_heading_sound
        from src.aquestalk_client import AQUESTALK_SAMPLE_RATE
        from src.text_cleaner import Page
        from src.xml_parser import HEADING_MARKER

        # Setup mock synthesizer
        mock_synthesizer = MagicMock()
        def mock_synthesize(text, speed=None):
            duration = 0.1
            t = np.linspace(0, duration, int(AQUESTALK_SAMPLE_RATE * duration), False)
            waveform = 0.3 * np.sin(2 * np.pi * 440 * t)
            import io
            with io.BytesIO() as buffer:
                sf.write(buffer, waveform, AQUESTALK_SAMPLE_RATE, format="WAV")
                return buffer.getvalue()
        mock_synthesizer.synthesize.side_effect = mock_synthesize
        mock_synthesizer_class.return_value = mock_synthesizer

        # Create test page with HEADING_MARKER
        pages = [Page(number=1, text=f"段落{HEADING_MARKER}見出し")]

        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        args = MagicMock()
        args.speed = 100

        # Process WITHOUT heading sound (None)
        wav_files = process_pages_with_heading_sound(
            pages=pages,
            synthesizer=mock_synthesizer,
            output_dir=output_dir,
            args=args,
            heading_sound=None,  # No heading sound
        )

        assert len(wav_files) > 0, "Should still generate WAV files without heading sound"

    @patch("src.aquestalk_pipeline.AquesTalkSynthesizer")
    def test_heading_sound_not_inserted_before_first_segment(self, mock_synthesizer_class, tmp_path):
        """最初のセグメント（見出しマーカー前）には効果音を挿入しない"""
        import numpy as np
        import soundfile as sf
        from src.aquestalk_pipeline import process_pages_with_heading_sound
        from src.aquestalk_client import AQUESTALK_SAMPLE_RATE
        from src.text_cleaner import Page
        from src.xml_parser import HEADING_MARKER

        # Setup mock synthesizer with call tracking
        mock_synthesizer = MagicMock()
        synthesize_calls = []
        def mock_synthesize(text, speed=None):
            synthesize_calls.append(text)
            duration = 0.1
            t = np.linspace(0, duration, int(AQUESTALK_SAMPLE_RATE * duration), False)
            waveform = 0.3 * np.sin(2 * np.pi * 440 * t)
            import io
            with io.BytesIO() as buffer:
                sf.write(buffer, waveform, AQUESTALK_SAMPLE_RATE, format="WAV")
                return buffer.getvalue()
        mock_synthesizer.synthesize.side_effect = mock_synthesize
        mock_synthesizer_class.return_value = mock_synthesizer

        # Create heading sound (0.1 sec)
        heading_sound = 0.5 * np.ones(1600, dtype=np.float32)

        # Create test page: first segment is before any heading marker
        pages = [Page(number=1, text=f"最初の段落{HEADING_MARKER}見出し")]

        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        args = MagicMock()
        args.speed = 100

        wav_files = process_pages_with_heading_sound(
            pages=pages,
            synthesizer=mock_synthesizer,
            output_dir=output_dir,
            args=args,
            heading_sound=heading_sound,
        )

        # The synthesizer should be called for both segments
        assert len(synthesize_calls) >= 2, (
            f"Should synthesize at least 2 segments, got {len(synthesize_calls)}"
        )


# ============================================================
# T037: test_heading_speed_adjustment
# ============================================================

class TestHeadingSpeedAdjustment:
    """Test that heading segments use speed=80 for emphasis."""

    def test_heading_synthesized_with_speed_80(self, tmp_path):
        """見出しセグメントは speed=80 でゆっくり読まれる"""
        import numpy as np
        import soundfile as sf
        from src.aquestalk_pipeline import process_pages_with_heading_sound
        from src.aquestalk_client import AquesTalkSynthesizer, AquesTalkConfig, AQUESTALK_SAMPLE_RATE
        from src.text_cleaner import Page
        from src.xml_parser import HEADING_MARKER

        # Track speed parameter for each synthesize call
        synthesize_speeds = []

        # Create synthesizer that tracks the speed used
        class TrackingSpeedSynthesizer:
            def __init__(self, config: AquesTalkConfig):
                self.config = config
                self._initialized = True

            def initialize(self):
                pass

            def synthesize(self, text: str, speed: int | None = None) -> bytes:
                # Record which speed was used
                actual_speed = speed if speed is not None else self.config.speed
                synthesize_speeds.append(actual_speed)

                duration = 0.1
                t = np.linspace(0, duration, int(AQUESTALK_SAMPLE_RATE * duration), False)
                waveform = 0.3 * np.sin(2 * np.pi * 440 * t)
                import io
                with io.BytesIO() as buffer:
                    sf.write(buffer, waveform, AQUESTALK_SAMPLE_RATE, format="WAV")
                    return buffer.getvalue()

        config = AquesTalkConfig(speed=100)  # Normal speed is 100
        synthesizer = TrackingSpeedSynthesizer(config)

        # Create test page with heading
        pages = [Page(number=1, text=f"通常段落{HEADING_MARKER}見出しテキスト")]

        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        args = MagicMock()
        args.speed = 100

        # Process pages - heading should use speed=80
        process_pages_with_heading_sound(
            pages=pages,
            synthesizer=synthesizer,
            output_dir=output_dir,
            args=args,
            heading_sound=None,
        )

        # The second synthesize call (for heading) should use speed=80
        assert len(synthesize_speeds) >= 2, (
            f"Should synthesize at least 2 segments, got {len(synthesize_speeds)}"
        )

        # First segment (paragraph) should use normal speed (100)
        assert synthesize_speeds[0] == 100, (
            f"Paragraph should use speed=100, got {synthesize_speeds[0]}"
        )

        # Second segment (heading) should use slow speed (80)
        assert synthesize_speeds[1] == 80, (
            f"Heading should use speed=80 for emphasis, got {synthesize_speeds[1]}"
        )

    def test_normal_segment_uses_user_specified_speed(self, tmp_path):
        """通常セグメントはユーザー指定の速度を使用"""
        import numpy as np
        import soundfile as sf
        from src.aquestalk_pipeline import process_pages_with_heading_sound
        from src.aquestalk_client import AquesTalkConfig, AQUESTALK_SAMPLE_RATE
        from src.text_cleaner import Page

        synthesize_speeds = []

        class TrackingSpeedSynthesizer:
            def __init__(self, config: AquesTalkConfig):
                self.config = config
                self._initialized = True

            def initialize(self):
                pass

            def synthesize(self, text: str, speed: int | None = None) -> bytes:
                actual_speed = speed if speed is not None else self.config.speed
                synthesize_speeds.append(actual_speed)

                duration = 0.1
                t = np.linspace(0, duration, int(AQUESTALK_SAMPLE_RATE * duration), False)
                waveform = 0.3 * np.sin(2 * np.pi * 440 * t)
                import io
                with io.BytesIO() as buffer:
                    sf.write(buffer, waveform, AQUESTALK_SAMPLE_RATE, format="WAV")
                    return buffer.getvalue()

        # User specifies speed=150
        config = AquesTalkConfig(speed=150)
        synthesizer = TrackingSpeedSynthesizer(config)

        # Page with only normal text (no heading marker)
        pages = [Page(number=1, text="通常の段落テキスト")]

        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        args = MagicMock()
        args.speed = 150

        process_pages_with_heading_sound(
            pages=pages,
            synthesizer=synthesizer,
            output_dir=output_dir,
            args=args,
            heading_sound=None,
        )

        # Normal segment should use user-specified speed (150)
        assert len(synthesize_speeds) >= 1, "Should synthesize at least 1 segment"
        assert synthesize_speeds[0] == 150, (
            f"Normal segment should use user speed=150, got {synthesize_speeds[0]}"
        )


# ============================================================
# T038: test_heading_sound_file_not_found_warning
# ============================================================

class TestHeadingSoundFileNotFoundWarning:
    """Test warning when heading sound file is not found."""

    @patch("src.aquestalk_pipeline.AquesTalkSynthesizer")
    def test_warning_when_heading_sound_not_found(self, mock_synthesizer_class, tmp_path, caplog):
        """効果音ファイルが見つからない場合は警告を表示"""
        import logging

        # Setup mock synthesizer
        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = b"\x00" * 1000
        mock_synthesizer_class.return_value = mock_synthesizer

        output_dir = tmp_path / "output"
        non_existent_sound = "/tmp/non_existent_heading_sound_12345.mp3"

        with patch("src.aquestalk_pipeline.init_for_content"):
            with patch("src.aquestalk_pipeline.clean_page_text", return_value="テスト"):
                with caplog.at_level(logging.WARNING):
                    main([
                        "--input", str(SAMPLE_BOOK_XML),
                        "--output", str(output_dir),
                        "--heading-sound", non_existent_sound,
                    ])

        # Should log a warning about missing file
        warning_found = any(
            "not found" in record.message.lower() or
            "heading" in record.message.lower()
            for record in caplog.records
            if record.levelno >= logging.WARNING
        )
        assert warning_found, (
            f"Should warn when heading sound file not found. "
            f"Log records: {[r.message for r in caplog.records]}"
        )

    @patch("src.aquestalk_pipeline.AquesTalkSynthesizer")
    def test_continues_without_heading_sound_when_file_not_found(self, mock_synthesizer_class, tmp_path):
        """効果音ファイルが見つからなくても処理を続行"""
        # Setup mock synthesizer
        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = b"\x00" * 1000
        mock_synthesizer_class.return_value = mock_synthesizer

        output_dir = tmp_path / "output"
        non_existent_sound = "/tmp/non_existent_heading_sound_67890.mp3"

        with patch("src.aquestalk_pipeline.init_for_content"):
            with patch("src.aquestalk_pipeline.clean_page_text", return_value="テスト"):
                # Should NOT raise an exception
                main([
                    "--input", str(SAMPLE_BOOK_XML),
                    "--output", str(output_dir),
                    "--heading-sound", non_existent_sound,
                ])

        # Verify output was still created
        assert output_dir.exists(), "Output should be created even without heading sound"

    def test_parse_args_accepts_heading_sound_option(self):
        """--heading-sound オプションを受け付ける"""
        args = parse_args([
            "-i", str(SAMPLE_BOOK_XML),
            "--heading-sound", "/path/to/sound.mp3",
        ])

        assert args.heading_sound == "/path/to/sound.mp3", (
            f"Should parse --heading-sound option, got {args.heading_sound}"
        )

    def test_parse_args_heading_sound_default_is_none(self):
        """--heading-sound のデフォルトは None"""
        args = parse_args(["-i", str(SAMPLE_BOOK_XML)])

        assert args.heading_sound is None, (
            f"--heading-sound default should be None, got {args.heading_sound}"
        )
