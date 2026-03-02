"""Tests for xml2_pipeline.py - Integration tests"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
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


class TestMainFunction:
    """Test main() entry point function."""

    def test_main_function_exists(self):
        """main 関数が存在する"""
        from src.xml2_pipeline import main

        assert callable(main), "main should be a callable function"

    def test_main_file_not_found_raises_error(self, mock_pid_management):
        """存在しないファイルでエラー"""
        from src.xml2_pipeline import main

        non_existent = "/tmp/non_existent_book2.xml"

        with pytest.raises(FileNotFoundError) as exc_info:
            main(["--input", non_existent])

        assert non_existent in str(exc_info.value), f"Error message should contain file path: {exc_info.value}"

    def test_main_invalid_xml_raises_error(self, tmp_path, mock_pid_management):
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


class TestMainWithCleanedTextSkipsCleaning:
    """T025: --cleaned-text 指定時のテキストクリーニングスキップテストを追加。

    US2 要件:
    - --cleaned-text 指定時は XML パースは行うが、テキストクリーニングをスキップ
    - 指定ファイルの内容を cleaned_text として使用
    - TTS 生成は通常通り実行される
    """

    def test_main_with_cleaned_text_skips_text_cleaning(self, tmp_path, mock_pid_management):
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

    def test_main_with_cleaned_text_does_not_overwrite_file(self, tmp_path, mock_pid_management):
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

    def test_cleaned_text_file_not_found_raises_error(self, mock_pid_management):
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

    def test_cleaned_text_file_not_found_error_message_is_descriptive(self, mock_pid_management):
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

    def test_main_without_cleaned_text_runs_cleaning(self, tmp_path, mock_pid_management):
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

    def test_main_without_cleaned_text_generates_cleaned_text_file(self, tmp_path, mock_pid_management):
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
