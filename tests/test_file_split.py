"""Tests for xml2_pipeline.py file split verification.

Phase 3 RED Tests - US3: xml2_pipeline.py ファイル分割の検証
分割後の各モジュールが正しくimport可能であり、後方互換性が維持されていることを確認する。

テスト対象:
- T027: src/process_manager.py のimport互換性
- T028: src/chapter_processor.py のimport互換性
- T029: src/xml2_pipeline.py のre-export動作
- T030: 各ファイルの行数上限（600行以下）
"""

from pathlib import Path

# プロジェクトルートパス
PROJECT_ROOT = Path(__file__).parent.parent


class TestProcessManagerImport:
    """T027: src/process_manager.py のimport互換性テスト。

    process_manager.py が独立モジュールとしてimport可能であり、
    期待される関数が全て定義されていることを確認する。
    """

    def test_process_manager_module_importable(self):
        """process_manager モジュールが import 可能であることを確認する。"""
        import src.process_manager  # noqa: F401

    def test_process_manager_has_get_pid_file_path(self):
        """process_manager に get_pid_file_path 関数が存在することを確認する。"""
        from src.process_manager import get_pid_file_path

        assert callable(get_pid_file_path), "get_pid_file_path は callable でなければならない"

    def test_process_manager_has_kill_existing_process(self):
        """process_manager に kill_existing_process 関数が存在することを確認する。"""
        from src.process_manager import kill_existing_process

        assert callable(kill_existing_process), "kill_existing_process は callable でなければならない"

    def test_process_manager_has_write_pid_file(self):
        """process_manager に write_pid_file 関数が存在することを確認する。"""
        from src.process_manager import write_pid_file

        assert callable(write_pid_file), "write_pid_file は callable でなければならない"

    def test_process_manager_has_cleanup_pid_file(self):
        """process_manager に cleanup_pid_file 関数が存在することを確認する。"""
        from src.process_manager import cleanup_pid_file

        assert callable(cleanup_pid_file), "cleanup_pid_file は callable でなければならない"

    def test_process_manager_file_exists(self):
        """src/process_manager.py ファイルが存在することを確認する。"""
        filepath = PROJECT_ROOT / "src" / "process_manager.py"
        assert filepath.exists(), f"{filepath} が存在しない"


class TestChapterProcessorImport:
    """T028: src/chapter_processor.py のimport互換性テスト。

    chapter_processor.py が独立モジュールとしてimport可能であり、
    期待される関数が全て定義されていることを確認する。
    """

    def test_chapter_processor_module_importable(self):
        """chapter_processor モジュールが import 可能であることを確認する。"""
        import src.chapter_processor  # noqa: F401

    def test_chapter_processor_has_sanitize_filename(self):
        """chapter_processor に sanitize_filename 関数が存在することを確認する。"""
        from src.chapter_processor import sanitize_filename

        assert callable(sanitize_filename), "sanitize_filename は callable でなければならない"

    def test_chapter_processor_has_load_sound(self):
        """chapter_processor に load_sound 関数が存在することを確認する。"""
        from src.chapter_processor import load_sound

        assert callable(load_sound), "load_sound は callable でなければならない"

    def test_chapter_processor_has_process_chapters(self):
        """chapter_processor に process_chapters 関数が存在することを確認する。"""
        from src.chapter_processor import process_chapters

        assert callable(process_chapters), "process_chapters は callable でなければならない"

    def test_chapter_processor_has_process_content(self):
        """chapter_processor に process_content 関数が存在することを確認する。"""
        from src.chapter_processor import process_content

        assert callable(process_content), "process_content は callable でなければならない"

    def test_chapter_processor_file_exists(self):
        """src/chapter_processor.py ファイルが存在することを確認する。"""
        filepath = PROJECT_ROOT / "src" / "chapter_processor.py"
        assert filepath.exists(), f"{filepath} が存在しない"


class TestXml2PipelineReExport:
    """T029: xml2_pipeline.py のre-export動作テスト。

    ファイル分割後も xml2_pipeline.py 経由でのimportが動作し、
    後方互換性が維持されていることを確認する。
    """

    def test_reexport_get_pid_file_path(self):
        """xml2_pipeline 経由で get_pid_file_path がimport可能であることを確認する。"""
        from src.xml2_pipeline import get_pid_file_path

        assert callable(get_pid_file_path), "get_pid_file_path は xml2_pipeline から import 可能でなければならない"

    def test_reexport_kill_existing_process(self):
        """xml2_pipeline 経由で kill_existing_process がimport可能であることを確認する。"""
        from src.xml2_pipeline import kill_existing_process

        assert callable(kill_existing_process), (
            "kill_existing_process は xml2_pipeline から import 可能でなければならない"
        )

    def test_reexport_write_pid_file(self):
        """xml2_pipeline 経由で write_pid_file がimport可能であることを確認する。"""
        from src.xml2_pipeline import write_pid_file

        assert callable(write_pid_file), "write_pid_file は xml2_pipeline から import 可能でなければならない"

    def test_reexport_cleanup_pid_file(self):
        """xml2_pipeline 経由で cleanup_pid_file がimport可能であることを確認する。"""
        from src.xml2_pipeline import cleanup_pid_file

        assert callable(cleanup_pid_file), "cleanup_pid_file は xml2_pipeline から import 可能でなければならない"

    def test_reexport_sanitize_filename(self):
        """xml2_pipeline 経由で sanitize_filename がimport可能であることを確認する。"""
        from src.xml2_pipeline import sanitize_filename

        assert callable(sanitize_filename), "sanitize_filename は xml2_pipeline から import 可能でなければならない"

    def test_reexport_load_sound(self):
        """xml2_pipeline 経由で load_sound がimport可能であることを確認する。"""
        from src.xml2_pipeline import load_sound

        assert callable(load_sound), "load_sound は xml2_pipeline から import 可能でなければならない"

    def test_reexport_process_chapters(self):
        """xml2_pipeline 経由で process_chapters がimport可能であることを確認する。"""
        from src.xml2_pipeline import process_chapters

        assert callable(process_chapters), "process_chapters は xml2_pipeline から import 可能でなければならない"

    def test_reexport_process_content(self):
        """xml2_pipeline 経由で process_content がimport可能であることを確認する。"""
        from src.xml2_pipeline import process_content

        assert callable(process_content), "process_content は xml2_pipeline から import 可能でなければならない"

    def test_reexport_parse_args(self):
        """xml2_pipeline 経由で parse_args がimport可能であることを確認する。"""
        from src.xml2_pipeline import parse_args

        assert callable(parse_args), "parse_args は xml2_pipeline から import 可能でなければならない"

    def test_reexport_main(self):
        """xml2_pipeline 経由で main がimport可能であることを確認する。"""
        from src.xml2_pipeline import main

        assert callable(main), "main は xml2_pipeline から import 可能でなければならない"

    def test_reexport_origin_process_manager(self):
        """re-export された PID管理関数が process_manager モジュール由来であることを確認する。"""
        from src.process_manager import get_pid_file_path as original
        from src.xml2_pipeline import get_pid_file_path as reexported

        assert original is reexported, (
            "xml2_pipeline.get_pid_file_path は process_manager からのre-exportでなければならない"
        )

    def test_reexport_origin_chapter_processor(self):
        """re-export された音声処理関数が chapter_processor モジュール由来であることを確認する。"""
        from src.chapter_processor import sanitize_filename as original
        from src.xml2_pipeline import sanitize_filename as reexported

        assert original is reexported, (
            "xml2_pipeline.sanitize_filename は chapter_processor からのre-exportでなければならない"
        )


class TestFileSizeLimit:
    """T030: 各ファイルの行数上限テスト（600行以下確認）。

    分割後の全ファイルが600行以下であることを確認する。
    """

    LINE_LIMIT = 600

    @staticmethod
    def _count_lines(filepath: Path) -> int:
        """ファイルの行数をカウントする。"""
        return len(filepath.read_text(encoding="utf-8").splitlines())

    def test_xml2_pipeline_line_count(self):
        """src/xml2_pipeline.py が600行以下であることを確認する。"""
        filepath = PROJECT_ROOT / "src" / "xml2_pipeline.py"
        assert filepath.exists(), f"{filepath} が存在しない"
        line_count = self._count_lines(filepath)
        assert line_count <= self.LINE_LIMIT, f"src/xml2_pipeline.py は {line_count} 行（上限: {self.LINE_LIMIT} 行）"

    def test_process_manager_line_count(self):
        """src/process_manager.py が600行以下であることを確認する。"""
        filepath = PROJECT_ROOT / "src" / "process_manager.py"
        assert filepath.exists(), f"{filepath} が存在しない"
        line_count = self._count_lines(filepath)
        assert line_count <= self.LINE_LIMIT, f"src/process_manager.py は {line_count} 行（上限: {self.LINE_LIMIT} 行）"

    def test_chapter_processor_line_count(self):
        """src/chapter_processor.py が600行以下であることを確認する。"""
        filepath = PROJECT_ROOT / "src" / "chapter_processor.py"
        assert filepath.exists(), f"{filepath} が存在しない"
        line_count = self._count_lines(filepath)
        assert line_count <= self.LINE_LIMIT, (
            f"src/chapter_processor.py は {line_count} 行（上限: {self.LINE_LIMIT} 行）"
        )
