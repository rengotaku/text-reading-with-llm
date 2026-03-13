# Phase 5 RED Tests: CLI統合 & Makefile

**Date**: 2026-03-14
**Status**: RED (FAIL verified)
**User Story**: CLI統合 - dialogue_converter.py のCLI実装

## Summary

| Item | Value |
|------|-------|
| 作成テスト数 | 53 |
| 失敗テスト数 | 53 |
| テストファイル | tests/test_dialogue_converter.py |
| 失敗理由 | ImportError: parse_args, main が未実装 |

## 失敗テスト一覧

### T072: CLI引数パーステスト（34テスト）

| テストクラス | テストメソッド | 期待動作 |
|-------------|--------------|---------|
| TestConverterParseArgsRequired | test_no_args_raises_system_exit | 引数なしでSystemExit |
| TestConverterParseArgsRequired | test_input_is_required | --input未指定でSystemExit |
| TestConverterParseArgsInput | test_input_short_flag | -i でファイル指定 |
| TestConverterParseArgsInput | test_input_long_flag | --input でファイル指定 |
| TestConverterParseArgsInput | test_input_with_path | パス付きファイル指定 |
| TestConverterParseArgsInput | test_input_with_spaces_in_path | スペース含むパス |
| TestConverterParseArgsOutput | test_output_default | デフォルト './output' |
| TestConverterParseArgsOutput | test_output_short_flag | -o で出力先指定 |
| TestConverterParseArgsOutput | test_output_long_flag | --output で出力先指定 |
| TestConverterParseArgsModel | test_model_default | デフォルト 'gpt-oss:20b' |
| TestConverterParseArgsModel | test_model_short_flag | -m でモデル指定 |
| TestConverterParseArgsModel | test_model_long_flag | --model でモデル指定 |
| TestConverterParseArgsNumeric | test_max_chars_default | デフォルト 3500 |
| TestConverterParseArgsNumeric | test_max_chars_custom | カスタム値指定 |
| TestConverterParseArgsNumeric | test_max_chars_is_int | int型であること |
| TestConverterParseArgsNumeric | test_split_threshold_default | デフォルト 4000 |
| TestConverterParseArgsNumeric | test_split_threshold_custom | カスタム値指定 |
| TestConverterParseArgsNumeric | test_num_predict_default | デフォルト 1500 |
| TestConverterParseArgsNumeric | test_num_predict_custom | カスタム値指定 |
| TestConverterParseArgsChapterSection | test_chapter_default_none | デフォルト None |
| TestConverterParseArgsChapterSection | test_chapter_short_flag | -c で指定 |
| TestConverterParseArgsChapterSection | test_chapter_long_flag | --chapter で指定 |
| TestConverterParseArgsChapterSection | test_chapter_is_int | int型であること |
| TestConverterParseArgsChapterSection | test_section_default_none | デフォルト None |
| TestConverterParseArgsChapterSection | test_section_short_flag | -s で指定 |
| TestConverterParseArgsChapterSection | test_section_long_flag | --section で指定 |
| TestConverterParseArgsDryRun | test_dry_run_default_false | デフォルト False |
| TestConverterParseArgsDryRun | test_dry_run_flag | --dry-run で True |
| TestConverterParseArgsCombined | test_all_options_combined | 全オプション同時指定 |
| TestConverterParseArgsCombined | test_minimal_required_only | 必須のみでデフォルト値確認 |
| TestConverterParseArgsEdgeCases | test_invalid_max_chars_type | 不正型でSystemExit |
| TestConverterParseArgsEdgeCases | test_invalid_chapter_type | 不正型でSystemExit |
| TestConverterParseArgsEdgeCases | test_unknown_argument | 未知引数でSystemExit |
| TestConverterParseArgsEdgeCases | test_empty_input_string | 空文字列入力を受付 |

### T073: main() 統合テスト（19テスト）

| テストクラス | テストメソッド | 期待動作 |
|-------------|--------------|---------|
| TestConverterMainInputValidation | test_nonexistent_input_file_returns_exit_code_1 | 存在しないファイルで終了コード1 |
| TestConverterMainInputValidation | test_empty_input_path_returns_exit_code_1 | 空パスで終了コード1 |
| TestConverterMainInputValidation | test_directory_as_input_returns_exit_code_1 | ディレクトリ指定で終了コード1 |
| TestConverterMainDryRun | test_dry_run_returns_exit_code_0 | dry-runで終了コード0 |
| TestConverterMainDryRun | test_dry_run_does_not_create_output_files | dry-runで出力ファイル未作成 |
| TestConverterMainDryRun | test_dry_run_does_not_call_llm | dry-runでLLM未呼出 |
| TestConverterMainSuccessPath | test_successful_conversion_returns_exit_code_0 | 正常変換で終了コード0 |
| TestConverterMainSuccessPath | test_creates_output_directory | 出力ディレクトリ自動作成 |
| TestConverterMainSuccessPath | test_creates_dialogue_book_xml | dialogue_book.xml作成 |
| TestConverterMainSuccessPath | test_creates_conversion_log_json | conversion_log.json作成 |
| TestConverterMainErrorHandling | test_llm_connection_error_returns_exit_code_2 | LLM接続エラーで終了コード2 |
| TestConverterMainErrorHandling | test_conversion_failure_returns_exit_code_3 | 変換失敗で終了コード3 |
| TestConverterMainErrorHandling | test_xml_parse_error_returns_exit_code_1 | 不正XMLで終了コード1 |
| TestConverterMainErrorHandling | test_unexpected_exception_returns_exit_code_3 | 予期しない例外で終了コード3 |
| TestConverterMainChapterSectionFilter | test_chapter_filter_processes_only_specified_chapter | チャプターフィルタ |
| TestConverterMainChapterSectionFilter | test_section_filter_processes_only_specified_section | セクションフィルタ |
| TestConverterMainEdgeCases | test_empty_xml_no_sections | セクションなしXMLで正常終了 |
| TestConverterMainEdgeCases | test_unicode_content_in_xml | Unicode文字を含むXML処理 |
| TestConverterMainEdgeCases | test_large_xml_with_many_sections | 50セクション以上の大規模XML |

## 実装ヒント

- `parse_args(args: list[str] | None = None) -> argparse.Namespace`: argparseで引数解析。cli-spec.mdの定義に従う
- `main() -> int`: エントリーポイント。終了コード 0(成功)/1(入力エラー)/2(LLM接続エラー)/3(変換エラー)
- `--dry-run`: 変換せずに処理対象セクションを表示するプレビューモード
- `--chapter`, `--section`: extract_sections()結果をフィルタリング
- 出力ファイル: `dialogue_book.xml`（変換結果）、`conversion_log.json`（変換ログ）
- エッジケース: 存在しないファイル、不正XML、空XML、LLM接続エラー、ディレクトリ指定

## make test 出力（抜粋）

```
FAILED tests/test_dialogue_converter.py::TestConverterParseArgsRequired::test_no_args_raises_system_exit - ImportError: parse_args is not yet implemented
FAILED tests/test_dialogue_converter.py::TestConverterParseArgsInput::test_input_short_flag - ImportError: parse_args is not yet implemented
FAILED tests/test_dialogue_converter.py::TestConverterMainInputValidation::test_nonexistent_input_file_returns_exit_code_1 - ImportError: main is not yet implemented
FAILED tests/test_dialogue_converter.py::TestConverterMainDryRun::test_dry_run_returns_exit_code_0 - ImportError: main is not yet implemented
FAILED tests/test_dialogue_converter.py::TestConverterMainSuccessPath::test_successful_conversion_returns_exit_code_0 - ImportError: main is not yet implemented
FAILED tests/test_dialogue_converter.py::TestConverterMainErrorHandling::test_llm_connection_error_returns_exit_code_2 - ImportError: main is not yet implemented
...
53 failed, 775 passed in 7.39s
```
