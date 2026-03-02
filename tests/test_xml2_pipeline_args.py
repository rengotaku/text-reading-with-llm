"""Tests for xml2_pipeline.py - Argument parsing tests"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_BOOK2_XML = FIXTURES_DIR / "sample_book2.xml"


# Fixture to prevent PID file and atexit state leaks across tests
@pytest.fixture
def mock_pid_management(monkeypatch):
    """Mock PID file management to prevent atexit accumulation and file conflicts."""
    import atexit

    mock_get_pid = MagicMock(return_value=Path(f"/tmp/test_pid_{id(monkeypatch)}.pid"))
    mock_kill = MagicMock(return_value=False)
    mock_write = MagicMock()
    mock_atexit = MagicMock()

    import src.xml2_pipeline

    monkeypatch.setattr(src.xml2_pipeline, "get_pid_file_path", mock_get_pid)
    monkeypatch.setattr(src.xml2_pipeline, "kill_existing_process", mock_kill)
    monkeypatch.setattr(src.xml2_pipeline, "write_pid_file", mock_write)
    monkeypatch.setattr(atexit, "register", mock_atexit)

    yield


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
