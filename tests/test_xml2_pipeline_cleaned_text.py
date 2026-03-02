"""Tests for xml2_pipeline.py - Cleaned text file tests"""

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


class TestCleanedTextFileContainsCleanedContent:
    """T039: cleaned_text.txt に clean_page_text() 適用済みテキストが出力されることを検証する。

    US3 要件 (FR-005):
    - cleaned_text.txt にクリーニング済みテキストを出力
    - URL、括弧内英語が除去されている
    - 数字がカナに変換されている
    """

    def test_cleaned_text_does_not_contain_url(self, tmp_path, mock_pid_management):
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

    def test_cleaned_text_does_not_contain_parenthetical_english(self, tmp_path, mock_pid_management):
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

    def test_cleaned_text_numbers_converted_to_kana(self, tmp_path, mock_pid_management):
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

    def test_cleaned_text_isbn_removed(self, tmp_path, mock_pid_management):
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

    def test_cleaned_text_has_chapter_separator_format(self, tmp_path, mock_pid_management):
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

    def test_cleaned_text_chapter_separator_contains_title(self, tmp_path, mock_pid_management):
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

    def test_cleaned_text_paragraph_text_is_cleaned(self, tmp_path, mock_pid_management):
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

    def test_cleaned_text_no_item_type_labels(self, tmp_path, mock_pid_management):
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
