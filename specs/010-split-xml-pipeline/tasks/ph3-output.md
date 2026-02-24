# Phase 3 Output: User Story 2 - 既存テキストから TTS 生成

**Date**: 2026-02-24
**Status**: 完了
**User Story**: US2 - 既存テキストから TTS 生成

## 実行タスク

- [x] T030 RED テストを読む: specs/010-split-xml-pipeline/red-tests/ph3-test.md
- [x] T031 [US2] parse_args() に --cleaned-text オプションを追加: src/xml2_pipeline.py
- [x] T032 [US2] main() を修正して --cleaned-text 指定時はクリーニングスキップ: src/xml2_pipeline.py
- [x] T033 `make test` PASS (GREEN) を確認
- [x] T034 `make test` で全テスト通過を確認（US1 テスト含む）
- [x] T035 編集・リネーム: specs/010-split-xml-pipeline/tasks/ph3-output-template.md → ph3-output.md

## 変更ファイル一覧

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| src/xml2_pipeline.py | 修正 | parse_args() に --cleaned-text オプションを追加。main() を修正して --cleaned-text 指定時は既存ファイルを使用し、テキストクリーニング処理（L134-175）をスキップするように変更。 |
| specs/010-split-xml-pipeline/tasks.md | 修正 | Phase 3 タスクを [x] でマーク |

## テスト結果

Phase 3 新規テスト（10テスト）:
```
tests/test_xml2_pipeline.py::TestParseArgsCleanedTextOption::test_cleaned_text_option_accepted PASSED
tests/test_xml2_pipeline.py::TestParseArgsCleanedTextOption::test_cleaned_text_option_default_is_none PASSED
tests/test_xml2_pipeline.py::TestParseArgsCleanedTextOption::test_cleaned_text_option_with_relative_path PASSED
tests/test_xml2_pipeline.py::TestParseArgsCleanedTextOption::test_cleaned_text_option_coexists_with_other_options PASSED
tests/test_xml2_pipeline.py::TestMainWithCleanedTextSkipsCleaning::test_main_with_cleaned_text_skips_text_cleaning PASSED
tests/test_xml2_pipeline.py::TestMainWithCleanedTextSkipsCleaning::test_main_with_cleaned_text_does_not_overwrite_file PASSED
tests/test_xml2_pipeline.py::TestCleanedTextFileNotFound::test_cleaned_text_file_not_found_raises_error PASSED
tests/test_xml2_pipeline.py::TestCleanedTextFileNotFound::test_cleaned_text_file_not_found_error_message_is_descriptive PASSED
tests/test_xml2_pipeline.py::TestBackwardCompatibilityWithoutCleanedText::test_main_without_cleaned_text_runs_cleaning PASSED
tests/test_xml2_pipeline.py::TestBackwardCompatibilityWithoutCleanedText::test_main_without_cleaned_text_generates_cleaned_text_file PASSED

10 passed (Phase 3 新規テスト)
```

Phase 1 + 2 既存テスト（22テスト）:
```
tests/test_text_cleaner_cli.py: 22 passed (リグレッションなし)
```

既存 xml2_pipeline テスト（69テスト）:
```
tests/test_xml2_pipeline.py: 69 passed (Phase 3 以前のテスト、リグレッションなし)
```

**合計**: 101 passed (22 + 69 + 10)

**カバレッジ**: 未測定 (目標: 80%)

## 発見した問題/課題

なし。全てのテストが PASS し、後方互換性も維持されている。

## 実装詳細

### parse_args() への変更

`--cleaned-text` オプションを追加:
```python
parser.add_argument(
    "--cleaned-text",
    default=None,
    help="Path to existing cleaned_text.txt (skip text cleaning if provided)",
)
```

### main() への変更

`parsed.cleaned_text` が指定されている場合:
1. 指定されたファイルの存在確認 → FileNotFoundError
2. XML パース処理は実行（チャプター情報取得のため）
3. テキストクリーニング処理をスキップ
4. 指定された cleaned_text.txt を使用して TTS 生成

コード構造:
```python
if parsed.cleaned_text:
    # 既存ファイルを使用
    cleaned_text_path = Path(parsed.cleaned_text)
    if not cleaned_text_path.exists():
        raise FileNotFoundError(f"Cleaned text file not found: {parsed.cleaned_text}")
    logger.info("Using existing cleaned text: %s", cleaned_text_path)
else:
    # 従来のテキストクリーニング処理（L134-175）
    cleaned_text_path = output_dir / "cleaned_text.txt"
    with open(cleaned_text_path, "w", encoding="utf-8") as f:
        # ... テキストクリーニング処理 ...
```

### 後方互換性

`--cleaned-text` 未指定時は従来通りの動作:
- XML パース → テキストクリーニング → cleaned_text.txt 保存 → TTS 生成
- 既存のテスト（69テスト）が全て PASS

## 次フェーズへの引き継ぎ

Phase 4 (User Story 3 - 全ステップ一括実行) で実装するもの:
- Makefile に `run` ターゲットを追加: `gen-dict → clean-text → xml-tts` の順次実行
- エラー時は後続ステップ未実行
- `make help` で `run` ターゲットの説明を表示

確立されたインターフェース:
- `xml2_pipeline.py` の `--cleaned-text` オプション: 既存の cleaned_text.txt から TTS 生成
- `text_cleaner_cli.py` で生成した cleaned_text.txt を `xml2_pipeline.py --cleaned-text` で使用可能

注意点:
- Phase 4 では Makefile の `xml-tts` ターゲットは変更不要（`--cleaned-text` オプションは任意）
- `run` ターゲットでは `clean-text` の出力を `xml-tts` に渡す連携が必要
