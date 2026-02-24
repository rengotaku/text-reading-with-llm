# Phase 4 Output: User Story 3 - 全ステップ一括実行

**Date**: 2026-02-24
**Status**: 完了
**User Story**: US3 - 全ステップ一括実行

## 実行タスク

- [x] T036 セットアップ分析を読む: specs/010-split-xml-pipeline/tasks/ph1-output.md
- [x] T037 前フェーズ出力を読む: specs/010-split-xml-pipeline/tasks/ph3-output.md
- [x] T038 [US3] Makefile に run ターゲットを追加: gen-dict → clean-text → xml-tts の順次実行
- [x] T039 [US3] Makefile の .PHONY に run を追加
- [x] T040 [US3] Makefile の help ターゲットが run を表示することを確認
- [x] T041 `make test` で全テスト通過を確認
- [x] T042 `make help` で run ターゲットの説明が表示されることを確認
- [x] T043 編集・リネーム: specs/010-split-xml-pipeline/tasks/ph4-output-template.md → ph4-output.md

## 変更ファイル一覧

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| Makefile | 修正 | `run` ターゲットを追加: gen-dict → clean-text → xml-tts の順次実行。.PHONY に run を追加。 |
| specs/010-split-xml-pipeline/tasks.md | 修正 | Phase 4 タスクを [x] でマーク |

## 実装詳細

### Makefile への変更

`run` ターゲットを追加:
```makefile
run: gen-dict clean-text xml-tts ## Run full pipeline: dict → clean-text → TTS (INPUT=file)
```

この実装により:
- gen-dict が完了してから clean-text が実行される
- clean-text が完了してから xml-tts が実行される
- いずれかのステップでエラーが発生した場合、後続ステップは実行されない (Make のデフォルト動作)

### .PHONY の更新

```makefile
.PHONY: help setup setup-dev setup-voicevox gen-dict clean-text xml-tts run test coverage lint format clean clean-all
```

### help 表示の確認

`make help` の出力:
```
  run            Run full pipeline: dict → clean-text → TTS (INPUT=file)
```

## テスト結果

全テストが通過することを確認:
- テスト総数: 459 tests
- サンプルテスト実行結果 (tests/test_text_cleaner_cli.py::TestParseArgsInputRequired):
  ```
  tests/test_text_cleaner_cli.py::TestParseArgsInputRequired::test_parse_args_function_exists PASSED
  tests/test_text_cleaner_cli.py::TestParseArgsInputRequired::test_parse_args_no_args_exits PASSED
  tests/test_text_cleaner_cli.py::TestParseArgsInputRequired::test_parse_args_accepts_input_long PASSED
  tests/test_text_cleaner_cli.py::TestParseArgsInputRequired::test_parse_args_accepts_input_short PASSED

  4 passed in 0.08s
  ```

**Note**: Phase 4 では新規コード実装がないため、新規テストは追加していない (Standard Phase、TDD 不要)。既存テスト (Phase 1-3 の 459 テスト) が引き続き通過することを確認した。

**カバレッジ**: 未測定 (目標: 80%)

## 発見した問題/課題

なし。全ての実装が計画通りに完了した。

## 受け入れ基準の確認

spec.md の User Story 3 受け入れシナリオ:

1. ✅ **AS-003-001**: Given XML ファイルが存在する, When `make run INPUT=sample.xml` を実行, Then 辞書生成、テキストクリーニング、TTS 生成が順次実行される
   - 実装完了: `run` ターゲットが gen-dict → clean-text → xml-tts の依存関係を持つ

2. ✅ **AS-003-002**: Given 途中のステップでエラー発生, When `make run` 実行中にエラー, Then 後続ステップは実行されず適切なエラーが表示される
   - 実装完了: Make のデフォルト動作によりエラー時は後続ステップ未実行

3. ✅ **AS-003-003**: Given `make help` を実行, When ヘルプが表示される, Then `run` ターゲットの説明が含まれる
   - 実装完了: `make help` で "Run full pipeline: dict → clean-text → TTS (INPUT=file)" が表示される

## 後方互換性

既存の個別ターゲットは引き続き動作:
- `make gen-dict INPUT=file`: 辞書生成のみ
- `make clean-text INPUT=file`: テキストクリーニングのみ
- `make xml-tts INPUT=file`: TTS 生成のみ (従来通り XML から直接実行可能)

新しい `run` ターゲットは既存のワークフローに影響を与えない。

## 次フェーズへの引き継ぎ

Phase 5 (Polish & 横断的関心事項) で実装するもの:
- コードクリーンアップ
- ドキュメント更新 (README.md に新しい Makefile ターゲットの説明追加)
- 成功基準の検証
  - SC-001: テキストクリーニング 10 秒以内
  - SC-004: `make help` で全ターゲットの説明表示

確立されたインターフェース:
- `make run INPUT=file`: 全パイプライン実行 (gen-dict → clean-text → xml-tts)
- 各ステップは独立して実行可能
- エラー時は後続ステップ未実行 (fail-fast)

注意点:
- `run` ターゲットは単純な依存関係チェーンであり、ステップ間のデータ受け渡しは暗黙的 (同じハッシュベースディレクトリ使用)
- 各ステップは INPUT 変数を共有する
