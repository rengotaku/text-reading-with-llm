# Phase 2 Output: User Story 1 - テキストクリーニング単独実行

**Date**: 2026-02-24
**Status**: 完了
**User Story**: US1 - テキストクリーニング単独実行

## 実行タスク

- [x] T014 RED テストを読む: specs/010-split-xml-pipeline/red-tests/ph2-test.md
- [x] T015 [P] [US1] parse_args() 関数を実装: src/text_cleaner_cli.py に argparse で --input, --output オプション
- [x] T016 [P] [US1] main() 関数を実装: src/text_cleaner_cli.py に XML パース → テキストクリーニング → cleaned_text.txt 保存
- [x] T017 [US1] Makefile に clean-text ターゲットを追加: Makefile
- [x] T018 `make test` PASS (GREEN) を確認
- [x] T019 `make test` で全テスト通過を確認（リグレッションなし）
- [x] T020 `make clean-text INPUT=tests/fixtures/sample_book2.xml` で動作確認

## 変更ファイル一覧

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| src/text_cleaner_cli.py | 新規 | XML から cleaned_text.txt を生成する CLI スクリプト。parse_args() と main() 関数を実装。xml2_pipeline.py の L133-175 のロジックを抽出。 |
| Makefile | 修正 | clean-text ターゲットを追加。.PHONY に clean-text を追加。 |
| tests/test_text_cleaner_cli.py | 修正 | test_main_cleaned_text_contains_chapter_markers テストを修正。sample_book2.xml には `<chapter>` タグがないため、テスト用に独自の XML を生成するよう変更。 |

## テスト結果

```
PYTHONPATH=/data/projects/text-reading-with-llm .venv/bin/python -m pytest tests/test_text_cleaner_cli.py -v
============================= test session starts ==============================
platform linux -- Python 3.13.11, pytest-9.0.2, pluggy-1.6.0
rootdir: /data/projects/text-reading-with-llm
configfile: pyproject.toml
plugins: cov-7.0.0
collecting ... collected 22 items

tests/test_text_cleaner_cli.py::TestParseArgsInputRequired::test_parse_args_function_exists PASSED [  4%]
tests/test_text_cleaner_cli.py::TestParseArgsInputRequired::test_parse_args_no_args_exits PASSED [  9%]
tests/test_text_cleaner_cli.py::TestParseArgsInputRequired::test_parse_args_accepts_input_long PASSED [ 13%]
tests/test_text_cleaner_cli.py::TestParseArgsInputRequired::test_parse_args_accepts_input_short PASSED [ 18%]
tests/test_text_cleaner_cli.py::TestParseArgsOutputOption::test_output_default PASSED [ 22%]
tests/test_text_cleaner_cli.py::TestParseArgsOutputOption::test_output_custom PASSED [ 27%]
tests/test_text_cleaner_cli.py::TestParseArgsOutputOption::test_output_short_flag PASSED [ 31%]
tests/test_text_cleaner_cli.py::TestParseArgsNoTtsOptions::test_no_style_id_option PASSED [ 36%]
tests/test_text_cleaner_cli.py::TestParseArgsNoTtsOptions::test_no_speed_option PASSED [ 40%]
tests/test_text_cleaner_cli.py::TestMainGeneratesCleanedText::test_main_function_exists PASSED [ 45%]
tests/test_text_cleaner_cli.py::TestMainGeneratesCleanedText::test_main_creates_cleaned_text_file PASSED [ 50%]
tests/test_text_cleaner_cli.py::TestMainGeneratesCleanedText::test_main_cleaned_text_not_empty PASSED [ 54%]
tests/test_text_cleaner_cli.py::TestMainGeneratesCleanedText::test_main_no_tts_processing PASSED [ 59%]
tests/test_text_cleaner_cli.py::TestMainGeneratesCleanedText::test_main_cleaned_text_contains_chapter_markers PASSED [ 63%]
tests/test_text_cleaner_cli.py::TestMainOverwritesExistingFile::test_main_overwrites_existing_cleaned_text PASSED [ 68%]
tests/test_text_cleaner_cli.py::TestErrorHandling::test_file_not_found_raises_error PASSED [ 72%]
tests/test_text_cleaner_cli.py::TestErrorHandling::test_file_not_found_with_sys_exit PASSED [ 77%]
tests/test_text_cleaner_cli.py::TestErrorHandling::test_invalid_xml_raises_error PASSED [ 81%]
tests/test_text_cleaner_cli.py::TestErrorHandling::test_empty_xml_no_crash PASSED [ 86%]
tests/test_text_cleaner_cli.py::TestOutputDirectoryCreation::test_output_directory_created_automatically PASSED [ 90%]
tests/test_text_cleaner_cli.py::TestOutputDirectoryCreation::test_output_uses_hash_based_subdirectory PASSED [ 95%]
tests/test_text_cleaner_cli.py::TestOutputDirectoryCreation::test_existing_output_directory_not_error PASSED [100%]

============================== 22 passed in 0.09s ==============================
```

**カバレッジ**: 未測定 (目標: 80%)

## 発見した問題/課題

1. **RED テストの不備**: test_main_cleaned_text_contains_chapter_markers テストが sample_book2.xml を使用していたが、このファイルには `<chapter>` タグがないため章区切りマーカー ("===") が生成されない。→ テスト内で独自の XML を生成するよう修正し解決。

2. **chapter_number フィールドの仕様**: xml2_parser.py の ContentItem には chapter_number フィールドがあるが、これは `<chapter>` タグを使用した XML でのみ設定される。`<heading level="1">` タグの場合は None のまま。この仕様により、章区切りマーカーの生成は XML 形式に依存する。

## 次フェーズへの引き継ぎ

Phase 3 (User Story 2 - 既存テキストから TTS 生成) で実装するもの:
- `xml2_pipeline.py` に `--cleaned-text` オプションを追加
- 指定時は XML パース・テキストクリーニングをスキップして既存の cleaned_text.txt から TTS 生成
- 後方互換性の維持（既存の動作に影響しない）

確立されたインターフェース:
- `text_cleaner_cli.py` の main() 関数: `cleaned_text.txt` を `output_dir / hash / cleaned_text.txt` に保存
- ハッシュ値は `get_content_hash(combined_text)` で計算
- Makefile の `clean-text` ターゲット: `INPUT` と `OUTPUT` 変数を受け取る

注意点:
- `init_for_content()` の呼び出しが必要（辞書初期化）
- 章区切りマーカーは `<chapter>` タグを持つ XML でのみ生成される
- エラーハンドリング: FileNotFoundError (入力ファイル不存在), ParseError (不正 XML)
