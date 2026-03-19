# Phase 6 Output: Polish & クロスカッティング

**Date**: 2026-03-14
**Status**: Completed
**User Story**: Polish - 全体品質向上・Makefile統合

## 実行タスク

- [x] T082 セットアップ分析を読む: specs/041-book-dialogue-conversion/tasks/ph1-output.md
- [x] T083 前フェーズ出力を読む: specs/041-book-dialogue-conversion/tasks/ph5-output.md
- [x] T084 [P] Makefile に dialogue-convert, dialogue-tts, dialogue ターゲットを追加: Makefile
- [x] T085 [P] pyproject.toml に新規モジュールの除外設定を追加: pyproject.toml
- [x] T086 [P] コードの型アノテーション確認と修正: src/dialogue_converter.py, src/dialogue_pipeline.py
- [x] T087 quickstart.md の検証を実行: specs/041-book-dialogue-conversion/quickstart.md
- [x] T088 `make lint` でリントエラーがないことを確認
- [x] T089 `make test` ですべてのテストがパスすることを確認
- [x] T090 `make coverage` でカバレッジ70%以上を確認
- [x] T091 Edit: specs/041-book-dialogue-conversion/tasks/ph6-output.md

## 変更ファイル

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| Makefile | 変更 | dialogue-convert, dialogue-tts, dialogue ターゲットを追加 |
| pyproject.toml | 変更 | src/dialogue_pipeline.py を PLC0415 除外リストに追加 |
| src/dialogue_converter.py | 変更 | parse_book2_xml をトップレベルインポートに移動、ollama_chat_func の型を Callable[..., Any] \| None に変更、None ガード追加 |
| specs/041-book-dialogue-conversion/tasks.md | 変更 | Phase 6 タスクを完了済みに更新 |

## 実装内容

### Makefile 追加ターゲット

| ターゲット | 内容 |
|------------|------|
| `dialogue-convert` | LLM で書籍 XML を対話形式に変換（INPUT 必須） |
| `dialogue-tts` | output/dialogue_book.xml から複数話者 TTS 生成 |
| `dialogue` | dialogue-convert → gen-dict → clean-text → dialogue-tts の全パイプライン |

使用例:
```bash
make dialogue-convert INPUT=data/book2.xml
make dialogue-tts
make dialogue INPUT=data/book2.xml
```

### pyproject.toml 変更

`src/dialogue_pipeline.py` を `[tool.ruff.lint.per-file-ignores]` の PLC0415 除外リストに追加。
`voicevox_client` の関数内インポートは重いオプション依存のため意図的なもの。

### 型アノテーション修正（src/dialogue_converter.py）

- `from src.xml_parser import ContentItem, parse_book2_xml` をトップレベルへ移動（PLC0415 対応）
- `ollama_chat_func` の型を `Any` → `Callable[..., Any] | None` に変更（mypy 対応）
- `analyze_structure()` と `generate_dialogue()` に `ollama_chat_func is None` ガードを追加

## テスト結果

```
============================= test session starts ==============================
collecting ... collected 828 items

828 passed in 4.93s
==============================
```

**全体テスト**: 828件 PASS

## リント・型チェック結果

```
ruff check .        All checks passed!
ruff format --check . 42 files already formatted
mypy src/           Success: no issues found in 18 source files
```

## カバレッジ結果

```
TOTAL   1885  420  78%
Required test coverage of 70% reached. Total coverage: 77.72%
```

**カバレッジ**: 77.72% (目標: 70% 達成)

## 発見された課題

1. **`make coverage` 終了時の `corrupted double-linked list` エラー**: テスト自体は全件 PASS であり、カバレッジ計測後のプロセス終了時のメモリエラー。既存の問題であり本 Phase のスコープ外。

## 次フェーズへの引き継ぎ

Phase 6 は最終フェーズ（Polish）であり、全 User Story の実装が完了。

**完成した機能**:
- `src/dialogue_converter.py`: 書籍 XML → 対話形式 XML 変換（CLI 付き）
- `src/dialogue_pipeline.py`: 対話形式 XML → 複数話者音声生成（CLI 付き）
- `make dialogue-convert INPUT=<file>`: 対話変換コマンド
- `make dialogue-tts`: 複数話者 TTS コマンド
- `make dialogue INPUT=<file>`: 全パイプライン実行コマンド

**エントリーポイント**:
- `python -m src.dialogue_converter -i <xml> -o <dir> [--model <model>] [--dry-run]`
- `python -m src.dialogue_pipeline -i <dialogue_xml> -o <dir> [--narrator-style N] [--speaker-a-style N] [--speaker-b-style N]`
