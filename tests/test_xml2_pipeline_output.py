"""Tests for xml2_pipeline.py - Output file generation tests"""

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
    from unittest.mock import MagicMock

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
