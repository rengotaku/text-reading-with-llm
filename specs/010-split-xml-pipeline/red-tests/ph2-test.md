# Phase 2 RED Tests: テキストクリーニング単独実行

**Date**: 2026-02-23
**Status**: RED (FAIL確認済み)
**User Story**: US1 - テキストクリーニング単独実行

## サマリー

| 項目 | 値 |
|------|-----|
| 作成テスト数 | 22 |
| FAIL数 | 22 |
| テストファイル | tests/test_text_cleaner_cli.py |

## FAILテスト一覧

| テストファイル | テストメソッド | 期待動作 |
|--------------|--------------|----------|
| tests/test_text_cleaner_cli.py | TestParseArgsInputRequired::test_parse_args_function_exists | parse_args 関数が存在する |
| tests/test_text_cleaner_cli.py | TestParseArgsInputRequired::test_parse_args_no_args_exits | 引数なしで SystemExit(2) |
| tests/test_text_cleaner_cli.py | TestParseArgsInputRequired::test_parse_args_accepts_input_long | --input を受け付ける |
| tests/test_text_cleaner_cli.py | TestParseArgsInputRequired::test_parse_args_accepts_input_short | -i 短縮形を受け付ける |
| tests/test_text_cleaner_cli.py | TestParseArgsOutputOption::test_output_default | --output デフォルトは ./output |
| tests/test_text_cleaner_cli.py | TestParseArgsOutputOption::test_output_custom | --output カスタム値 |
| tests/test_text_cleaner_cli.py | TestParseArgsOutputOption::test_output_short_flag | -o 短縮形 |
| tests/test_text_cleaner_cli.py | TestParseArgsNoTtsOptions::test_no_style_id_option | --style-id は未サポート |
| tests/test_text_cleaner_cli.py | TestParseArgsNoTtsOptions::test_no_speed_option | --speed は未サポート |
| tests/test_text_cleaner_cli.py | TestMainGeneratesCleanedText::test_main_function_exists | main 関数が存在する |
| tests/test_text_cleaner_cli.py | TestMainGeneratesCleanedText::test_main_creates_cleaned_text_file | cleaned_text.txt 生成 |
| tests/test_text_cleaner_cli.py | TestMainGeneratesCleanedText::test_main_cleaned_text_not_empty | 空でないファイル生成 |
| tests/test_text_cleaner_cli.py | TestMainGeneratesCleanedText::test_main_no_tts_processing | WAV ファイル未生成 |
| tests/test_text_cleaner_cli.py | TestMainGeneratesCleanedText::test_main_cleaned_text_contains_chapter_markers | 章区切りマーカー含む |
| tests/test_text_cleaner_cli.py | TestMainOverwritesExistingFile::test_main_overwrites_existing_cleaned_text | 既存ファイル上書き |
| tests/test_text_cleaner_cli.py | TestErrorHandling::test_file_not_found_raises_error | FileNotFoundError 発生 |
| tests/test_text_cleaner_cli.py | TestErrorHandling::test_file_not_found_with_sys_exit | SystemExit(1) 発生 |
| tests/test_text_cleaner_cli.py | TestErrorHandling::test_invalid_xml_raises_error | ParseError 発生 |
| tests/test_text_cleaner_cli.py | TestErrorHandling::test_empty_xml_no_crash | 空 XML でクラッシュしない |
| tests/test_text_cleaner_cli.py | TestOutputDirectoryCreation::test_output_directory_created_automatically | ディレクトリ自動作成 |
| tests/test_text_cleaner_cli.py | TestOutputDirectoryCreation::test_output_uses_hash_based_subdirectory | ハッシュベースサブディレクトリ |
| tests/test_text_cleaner_cli.py | TestOutputDirectoryCreation::test_existing_output_directory_not_error | 既存ディレクトリでエラーなし |

## 実装ヒント

- `parse_args()`: argparse で --input (必須), --output (デフォルト ./output) を実装。TTS 関連オプションは不要。
- `main()`: xml2_pipeline.py の L133-175 のロジックを抽出。parse_book2_xml -> init_for_content -> get_content_hash -> output_dir 作成 -> clean_page_text 適用 -> cleaned_text.txt 保存。
- ハッシュベースディレクトリ: `get_content_hash()` で combined_text からハッシュ計算、output_dir / hash でサブディレクトリ作成。
- エラーハンドリング: FileNotFoundError (存在しないファイル), ParseError (不正 XML)。
- 見出し処理: heading の末尾句点処理 (.rstrip + "。" 追加) を忘れずに。
- CHAPTER_MARKER / SECTION_MARKER の除去後にクリーニング適用。
- エッジケース: 空 XML (content_items が空) の場合は早期リターン。

## make test 出力 (抜粋)

```
FAILED tests/test_text_cleaner_cli.py::TestParseArgsInputRequired::test_parse_args_function_exists - ImportError: cannot import name 'parse_args'
FAILED tests/test_text_cleaner_cli.py::TestMainGeneratesCleanedText::test_main_function_exists - ImportError: cannot import name 'main'
FAILED tests/test_text_cleaner_cli.py::TestErrorHandling::test_file_not_found_raises_error - ImportError: cannot import name 'main'
FAILED tests/test_text_cleaner_cli.py::TestOutputDirectoryCreation::test_output_directory_created_automatically - ImportError: cannot import name 'main'
...
22 failed in 0.03s
```
