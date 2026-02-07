"""Tests for XML TTS pipeline integration.

Phase 4 RED Tests - パイプライン統合
Tests for xml_pipeline.py command-line interface and error handling.

Target functions:
- src/xml_pipeline.py::parse_args()
- src/xml_pipeline.py::main()
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from src.xml_pipeline import parse_args, main


# Fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_BOOK_XML = FIXTURES_DIR / "sample_book.xml"


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

    def test_style_id_default(self):
        """--style-id のデフォルトは 13"""
        args = parse_args(["-i", str(SAMPLE_BOOK_XML)])

        assert args.style_id == 13, (
            f"--style-id default should be 13, got {args.style_id}"
        )

    def test_speed_default(self):
        """--speed のデフォルトは 1.0"""
        args = parse_args(["-i", str(SAMPLE_BOOK_XML)])

        assert args.speed == 1.0, (
            f"--speed default should be 1.0, got {args.speed}"
        )

    def test_voicevox_dir_default(self):
        """--voicevox-dir のデフォルトは ./voicevox_core_cuda"""
        args = parse_args(["-i", str(SAMPLE_BOOK_XML)])

        assert args.voicevox_dir == "./voicevox_core_cuda", (
            f"--voicevox-dir default should be './voicevox_core_cuda', got {args.voicevox_dir}"
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

    def test_style_id_custom(self):
        """--style-id にカスタム値を設定"""
        args = parse_args(["-i", str(SAMPLE_BOOK_XML), "--style-id", "1"])

        assert args.style_id == 1, (
            f"--style-id should be 1, got {args.style_id}"
        )

    def test_speed_custom(self):
        """--speed にカスタム値を設定"""
        args = parse_args(["-i", str(SAMPLE_BOOK_XML), "--speed", "1.5"])

        assert args.speed == 1.5, (
            f"--speed should be 1.5, got {args.speed}"
        )

    def test_voicevox_dir_custom(self):
        """--voicevox-dir にカスタム値を設定"""
        args = parse_args(["-i", str(SAMPLE_BOOK_XML), "--voicevox-dir", "/opt/voicevox"])

        assert args.voicevox_dir == "/opt/voicevox", (
            f"--voicevox-dir should be '/opt/voicevox', got {args.voicevox_dir}"
        )


class TestFileNotFoundError:
    """Test error handling for non-existent input files."""

    def test_file_not_found_raises_error(self):
        """存在しないファイルでエラー"""
        non_existent = "/tmp/non_existent_book.xml"

        with pytest.raises(FileNotFoundError) as exc_info:
            main(["--input", non_existent])

        assert non_existent in str(exc_info.value), (
            f"Error message should contain file path: {exc_info.value}"
        )

    def test_file_not_found_error_message(self):
        """エラーメッセージにファイルパスを含む"""
        non_existent = "/tmp/does_not_exist_12345.xml"

        with pytest.raises(FileNotFoundError) as exc_info:
            main(["--input", non_existent])

        error_msg = str(exc_info.value)
        assert "does_not_exist_12345.xml" in error_msg, (
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
