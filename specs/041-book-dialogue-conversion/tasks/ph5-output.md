# Phase 5 Output: CLI統合 & Makefile

**Date**: 2026-03-14
**Status**: Completed
**User Story**: CLI統合 - dialogue_converter.py のCLI実装

## 実行タスク

- [x] T076 REDテストを読む: specs/041-book-dialogue-conversion/red-tests/ph5-test.md
- [x] T077 [P] dialogue_converter.py の parse_args() を実装: src/dialogue_converter.py
- [x] T078 dialogue_converter.py の main() を実装: src/dialogue_converter.py
- [x] T079 `make test` で PASS (GREEN) を確認
- [x] T080 `make test` ですべてのテストがパスすることを確認
- [x] T081 Edit: specs/041-book-dialogue-conversion/tasks/ph5-output.md

## 変更ファイル

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| src/dialogue_converter.py | 変更 | parse_args() と main() を追加、argparse・os・pathlib をインポートに追加 |
| specs/041-book-dialogue-conversion/tasks.md | 変更 | Phase 5 タスクを完了済みに更新 |

## 実装内容

### parse_args() の引数定義

| オプション | 短縮形 | デフォルト | 型 | 説明 |
|-----------|--------|-----------|-----|------|
| --input | -i | 必須 | str | 入力XMLファイルパス |
| --output | -o | ./output | str | 出力ディレクトリ |
| --model | -m | gpt-oss:20b | str | Ollamaモデル名 |
| --max-chars | - | 3500 | int | 分割なしの最大文字数 |
| --split-threshold | - | 4000 | int | 分割閾値 |
| --num-predict | - | 1500 | int | LLMトークン上限 |
| --chapter | -c | None | int | 対象チャプター番号 |
| --section | -s | None | int | 対象セクション番号 |
| --dry-run | - | False | bool | プレビューモード |

### main() の終了コード

| コード | 条件 |
|--------|------|
| 0 | 成功（dry-run含む、セクションなしXML含む） |
| 1 | 入力ファイルエラー（存在しない/空/ディレクトリ/不正XML） |
| 2 | LLM接続エラー（ConnectionError） |
| 3 | 変換エラー（ConversionResult.success=False、予期しない例外） |

### 出力ファイル

- `dialogue_book.xml`: 全セクションの対話形式XML
- `conversion_log.json`: 変換ログ（セクションごとの成否・処理時間・文字数）

## テスト結果

```
============================= test session starts ==============================
collecting ... collected 828 items

（Phase 5 新規: 53テスト）
tests/test_dialogue_converter.py::TestConverterParseArgsRequired - 2 passed
tests/test_dialogue_converter.py::TestConverterParseArgsInput - 4 passed
tests/test_dialogue_converter.py::TestConverterParseArgsOutput - 3 passed
tests/test_dialogue_converter.py::TestConverterParseArgsModel - 3 passed
tests/test_dialogue_converter.py::TestConverterParseArgsNumeric - 7 passed
tests/test_dialogue_converter.py::TestConverterParseArgsChapterSection - 7 passed
tests/test_dialogue_converter.py::TestConverterParseArgsDryRun - 2 passed
tests/test_dialogue_converter.py::TestConverterParseArgsCombined - 2 passed
tests/test_dialogue_converter.py::TestConverterParseArgsEdgeCases - 4 passed
tests/test_dialogue_converter.py::TestConverterMainInputValidation - 3 passed
tests/test_dialogue_converter.py::TestConverterMainDryRun - 3 passed
tests/test_dialogue_converter.py::TestConverterMainSuccessPath - 4 passed
tests/test_dialogue_converter.py::TestConverterMainErrorHandling - 4 passed
tests/test_dialogue_converter.py::TestConverterMainChapterSectionFilter - 2 passed
tests/test_dialogue_converter.py::TestConverterMainEdgeCases - 3 passed

============================= 828 passed in 59.57s ==============================
```

**Phase 5 新規テスト**: 53件 PASS (100%)
**全体テスト**: 828件 PASS

## 発見された課題

1. **`parse_book2_xml` の `<heading>` 処理**: テストXMLは `<heading level="2" number="1.1">` 形式を使っているが、`parse_book2_xml` は `<heading>` タグの `number` 属性を無視しTOCマッピングを使用する。テストでは `section` フィルタの整合性確認はモック経由で行っているため問題なし。

## 次フェーズへの引き継ぎ

Phase 6（Polish & クロスカッティング）で実施する内容:

- Makefile への `dialogue-convert`, `dialogue-tts`, `dialogue` ターゲット追加
- 全モジュールのコード品質改善（型アノテーション、docstring、ログ整理）
- Phase 5で確立したインターフェース:
  - `parse_args(args: list[str] | None = None) -> argparse.Namespace`
  - `main() -> int`（終了コード 0/1/2/3）
  - 出力ファイル: `dialogue_book.xml`, `conversion_log.json`
- 注意事項: `main()` 内の `convert_section()` は実際のOllama接続が必要。統合テストにはOllama実行環境が必要
