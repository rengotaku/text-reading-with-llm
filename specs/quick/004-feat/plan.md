---
status: completed
created: 2026-03-01
branch: quick/004-feat
issue: "#31"
---

# feat: 既存コードへの型ヒント追加

## 概要

mypy 導入時に段階的導入設定（`disallow_untyped_defs = false`）を採用した。
`--disallow-untyped-defs` で検出される 13 箇所に型ヒントを追加し、`ignore_errors` override を削除する。

## ゴール

- [x] 13 箇所の関数に型ヒントを追加
- [x] `ignore_errors = true` の override を削除（voicevox_client のみ残す）
- [x] `mypy src/ --disallow-untyped-defs` がエラー 0 で通過

## スコープ外

- pyproject.toml の `disallow_untyped_defs = true` への変更（今回は手動チェックで確認）
- 新規テストの追加

## 前提条件

- PR #30 で mypy 導入済み
- 現状 `mypy src/` はエラー 0（ignore_errors 適用中）

---

## 実装タスク

### Phase 1: 型ヒント追加（8ファイル13箇所）

- [x] T001 [src/punctuation_normalizer.py:146] 関数に型ヒント追加
- [x] T002 [src/xml2_parser.py:124,236] 2 関数に型ヒント追加
- [x] T003 [src/xml2_pipeline.py:51,94] 2 関数に型ヒント追加
- [x] T004 [src/text_cleaner_cli.py:24,60] 2 関数に型ヒント追加
- [x] T005 [src/text_cleaner.py:168] 関数に型ヒント追加
- [x] T006 [src/process_manager.py:74,84] 2 関数に戻り値型追加
- [x] T007 [src/llm_reading_generator.py:81] 関数に型ヒント追加
- [x] T008 [src/chapter_processor.py:83,246] 2 関数に型ヒント追加

### Phase 2: pyproject.toml 更新 + 検証

- [x] T009 [pyproject.toml] ignore_errors override を削除（voicevox_client のみ残す）
- [x] T010 `mypy src/ --disallow-untyped-defs` でエラー 0 を確認
- [x] T011 既存テスト通過確認

---

## リスク

| レベル | 内容 |
|-------|------|
| LOW | 型推論できない複雑な型は `Any` で対応 |

---

## 完了条件

- [x] 全タスク完了
- [x] `mypy src/ --disallow-untyped-defs` エラー 0
- [x] 既存テスト通過
