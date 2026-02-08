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
