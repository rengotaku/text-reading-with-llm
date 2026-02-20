# Phase 3 RED Tests: US3 - xml2_pipeline.py ファイル分割

**Date**: 2026-02-21
**Status**: RED (FAIL確認済み)
**User Story**: US3 - 大規模ファイルの分割

## サマリー

| 項目 | 値 |
|------|-----|
| 作成テスト数 | 27 |
| FAIL数 | 17 |
| PASS数 | 10 (分割前の既存関数が xml2_pipeline.py に直接存在するため) |
| テストファイル | tests/test_file_split.py |

## FAILテスト一覧

| テストファイル | テストメソッド | 期待動作 |
|--------------|--------------|----------|
| tests/test_file_split.py | TestProcessManagerImport::test_process_manager_module_importable | src.process_manager モジュールが import 可能 |
| tests/test_file_split.py | TestProcessManagerImport::test_process_manager_has_get_pid_file_path | get_pid_file_path 関数が存在 |
| tests/test_file_split.py | TestProcessManagerImport::test_process_manager_has_kill_existing_process | kill_existing_process 関数が存在 |
| tests/test_file_split.py | TestProcessManagerImport::test_process_manager_has_write_pid_file | write_pid_file 関数が存在 |
| tests/test_file_split.py | TestProcessManagerImport::test_process_manager_has_cleanup_pid_file | cleanup_pid_file 関数が存在 |
| tests/test_file_split.py | TestProcessManagerImport::test_process_manager_file_exists | src/process_manager.py ファイルが存在 |
| tests/test_file_split.py | TestChapterProcessorImport::test_chapter_processor_module_importable | src.chapter_processor モジュールが import 可能 |
| tests/test_file_split.py | TestChapterProcessorImport::test_chapter_processor_has_sanitize_filename | sanitize_filename 関数が存在 |
| tests/test_file_split.py | TestChapterProcessorImport::test_chapter_processor_has_load_sound | load_sound 関数が存在 |
| tests/test_file_split.py | TestChapterProcessorImport::test_chapter_processor_has_process_chapters | process_chapters 関数が存在 |
| tests/test_file_split.py | TestChapterProcessorImport::test_chapter_processor_has_process_content | process_content 関数が存在 |
| tests/test_file_split.py | TestChapterProcessorImport::test_chapter_processor_file_exists | src/chapter_processor.py ファイルが存在 |
| tests/test_file_split.py | TestXml2PipelineReExport::test_reexport_origin_process_manager | get_pid_file_path が process_manager 由来の re-export |
| tests/test_file_split.py | TestXml2PipelineReExport::test_reexport_origin_chapter_processor | sanitize_filename が chapter_processor 由来の re-export |
| tests/test_file_split.py | TestFileSizeLimit::test_xml2_pipeline_line_count | xml2_pipeline.py が 600行以下 (現在 613行) |
| tests/test_file_split.py | TestFileSizeLimit::test_process_manager_line_count | process_manager.py が存在し 600行以下 |
| tests/test_file_split.py | TestFileSizeLimit::test_chapter_processor_line_count | chapter_processor.py が存在し 600行以下 |

## PASSテスト一覧（分割前の後方互換性テスト）

以下の10テストは、関数が現在 xml2_pipeline.py に直接定義されているためPASS。
分割後は re-export 経由でPASSする必要がある。

- test_reexport_get_pid_file_path
- test_reexport_kill_existing_process
- test_reexport_write_pid_file
- test_reexport_cleanup_pid_file
- test_reexport_sanitize_filename
- test_reexport_load_sound
- test_reexport_process_chapters
- test_reexport_process_content
- test_reexport_parse_args
- test_reexport_main

## 実装ヒント

- `src/process_manager.py`: xml2_pipeline.py から get_pid_file_path, kill_existing_process, write_pid_file, cleanup_pid_file を移動（行49-125付近）
- `src/chapter_processor.py`: xml2_pipeline.py から sanitize_filename, load_sound, process_chapters, process_content を移動（行166-470付近）
- `src/xml2_pipeline.py`: parse_args, main を残し、上記2モジュールから re-export を追加
- re-export パターン: `from src.process_manager import get_pid_file_path, ...` を xml2_pipeline.py に追加
- 各ファイルに必要な import 文を忘れずに移動すること（os, signal, re, numpy, soundfile 等）
- エッジケース: circular import に注意。process_manager と chapter_processor は相互依存しないこと

## make test 出力 (抜粋)

```
FAILED tests/test_file_split.py::TestProcessManagerImport::test_process_manager_module_importable - ModuleNotFoundError: No module named 'src.process_manager'
FAILED tests/test_file_split.py::TestProcessManagerImport::test_process_manager_has_get_pid_file_path - ModuleNotFoundError
FAILED tests/test_file_split.py::TestProcessManagerImport::test_process_manager_has_kill_existing_process - ModuleNotFoundError
FAILED tests/test_file_split.py::TestProcessManagerImport::test_process_manager_has_write_pid_file - ModuleNotFoundError
FAILED tests/test_file_split.py::TestProcessManagerImport::test_process_manager_has_cleanup_pid_file - ModuleNotFoundError
FAILED tests/test_file_split.py::TestProcessManagerImport::test_process_manager_file_exists - AssertionError
FAILED tests/test_file_split.py::TestChapterProcessorImport::test_chapter_processor_module_importable - ModuleNotFoundError: No module named 'src.chapter_processor'
FAILED tests/test_file_split.py::TestChapterProcessorImport::test_chapter_processor_has_sanitize_filename - ModuleNotFoundError
FAILED tests/test_file_split.py::TestChapterProcessorImport::test_chapter_processor_has_load_sound - ModuleNotFoundError
FAILED tests/test_file_split.py::TestChapterProcessorImport::test_chapter_processor_has_process_chapters - ModuleNotFoundError
FAILED tests/test_file_split.py::TestChapterProcessorImport::test_chapter_processor_has_process_content - ModuleNotFoundError
FAILED tests/test_file_split.py::TestChapterProcessorImport::test_chapter_processor_file_exists - AssertionError
FAILED tests/test_file_split.py::TestXml2PipelineReExport::test_reexport_origin_process_manager - ModuleNotFoundError
FAILED tests/test_file_split.py::TestXml2PipelineReExport::test_reexport_origin_chapter_processor - ModuleNotFoundError
FAILED tests/test_file_split.py::TestFileSizeLimit::test_xml2_pipeline_line_count - AssertionError: src/xml2_pipeline.py は 613 行（上限: 600 行）
FAILED tests/test_file_split.py::TestFileSizeLimit::test_process_manager_line_count - AssertionError: src/process_manager.py が存在しない
FAILED tests/test_file_split.py::TestFileSizeLimit::test_chapter_processor_line_count - AssertionError: src/chapter_processor.py が存在しない
17 failed, 10 passed in 0.11s
```
