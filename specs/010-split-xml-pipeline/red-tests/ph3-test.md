# Phase 3 RED Tests: User Story 2 - 既存テキストから TTS 生成

**Date**: 2026-02-24
**Status**: RED (FAIL確認済み)
**User Story**: US2 - 既存テキストから TTS 生成

## サマリー

| 項目 | 値 |
|------|-----|
| 作成テスト数 | 10 |
| FAIL数 | 8 |
| PASS数 (後方互換) | 2 |
| テストファイル | tests/test_xml2_pipeline.py |

## FAILテスト一覧

| テストファイル | テストメソッド | 期待動作 |
|--------------|--------------|----------|
| tests/test_xml2_pipeline.py | TestParseArgsCleanedTextOption::test_cleaned_text_option_accepted | --cleaned-text オプションがパースされ、ファイルパスが格納される |
| tests/test_xml2_pipeline.py | TestParseArgsCleanedTextOption::test_cleaned_text_option_default_is_none | --cleaned-text 未指定時は None がデフォルト |
| tests/test_xml2_pipeline.py | TestParseArgsCleanedTextOption::test_cleaned_text_option_with_relative_path | 相対パスを --cleaned-text に指定できる |
| tests/test_xml2_pipeline.py | TestParseArgsCleanedTextOption::test_cleaned_text_option_coexists_with_other_options | --cleaned-text と --speed, --style-id を同時指定できる |
| tests/test_xml2_pipeline.py | TestMainWithCleanedTextSkipsCleaning::test_main_with_cleaned_text_skips_text_cleaning | --cleaned-text 指定時は clean_page_text() が呼び出されない |
| tests/test_xml2_pipeline.py | TestMainWithCleanedTextSkipsCleaning::test_main_with_cleaned_text_does_not_overwrite_file | --cleaned-text 指定時は既存ファイルが上書きされない |
| tests/test_xml2_pipeline.py | TestCleanedTextFileNotFound::test_cleaned_text_file_not_found_raises_error | 存在しないファイルを --cleaned-text に指定すると FileNotFoundError |
| tests/test_xml2_pipeline.py | TestCleanedTextFileNotFound::test_cleaned_text_file_not_found_error_message_is_descriptive | エラーメッセージにファイルパスが含まれる |

## PASSテスト一覧 (後方互換性)

| テストファイル | テストメソッド | 理由 |
|--------------|--------------|------|
| tests/test_xml2_pipeline.py | TestBackwardCompatibilityWithoutCleanedText::test_main_without_cleaned_text_runs_cleaning | 既存動作（clean_page_text 呼び出し）は変更なし |
| tests/test_xml2_pipeline.py | TestBackwardCompatibilityWithoutCleanedText::test_main_without_cleaned_text_generates_cleaned_text_file | 既存動作（cleaned_text.txt 生成）は変更なし |

## 実装ヒント

- `parse_args()`: `parser.add_argument("--cleaned-text", default=None, ...)` を追加
- `main()`: `parsed.cleaned_text` が None でない場合、テキストクリーニング処理（L134-175）をスキップ
- `main()`: `parsed.cleaned_text` ファイルが存在しない場合は FileNotFoundError を送出
- エッジケース: `--cleaned-text` と `--input` の両方が必要（XML パースは TTS 処理に必要）

## make test 出力 (抜粋)

```
FAILED tests/test_xml2_pipeline.py::TestParseArgsCleanedTextOption::test_cleaned_text_option_accepted - SystemExit: 2
FAILED tests/test_xml2_pipeline.py::TestParseArgsCleanedTextOption::test_cleaned_text_option_default_is_none - AttributeError: 'Namespace' object has no attribute 'cleaned_text'
FAILED tests/test_xml2_pipeline.py::TestParseArgsCleanedTextOption::test_cleaned_text_option_with_relative_path - SystemExit: 2
FAILED tests/test_xml2_pipeline.py::TestParseArgsCleanedTextOption::test_cleaned_text_option_coexists_with_other_options - SystemExit: 2
FAILED tests/test_xml2_pipeline.py::TestMainWithCleanedTextSkipsCleaning::test_main_with_cleaned_text_skips_text_cleaning - SystemExit: 2
FAILED tests/test_xml2_pipeline.py::TestMainWithCleanedTextSkipsCleaning::test_main_with_cleaned_text_does_not_overwrite_file - SystemExit: 2
FAILED tests/test_xml2_pipeline.py::TestCleanedTextFileNotFound::test_cleaned_text_file_not_found_raises_error - SystemExit: 2
FAILED tests/test_xml2_pipeline.py::TestCleanedTextFileNotFound::test_cleaned_text_file_not_found_error_message_is_descriptive - SystemExit: 2
8 failed, 2 passed (新規テストのみ)
既存テスト: 69 passed (リグレッションなし)
```
