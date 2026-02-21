---
status: completed
created: 2026-02-22
branch: quick/001-009-llm-warmup
issue: "#9"
---

# 009-llm-warmup

## 概要

`make gen-dict` 実行時、Ollamaモデルの初回ロードでバッチ1が必ずタイムアウトで失敗する問題を修正。ウォームアップリクエストを追加してモデルロード完了を待つ。

## ゴール

- [x] ウォームアップ機能の追加により、バッチ1のタイムアウト失敗を防止
- [x] モデルロード待ち時間を明示的にログ出力

## スコープ外

- ollama_chat のリトライロジック変更
- バッチサイズ最適化
- 他モジュールへの影響

## 前提条件

- 既存の `ollama_chat()` を再利用
- `generate_readings_batch()` の構造は維持

---

## 実装タスク

### Phase 1: ウォームアップ関数追加

- [x] T001 [src/generate_reading_dict.py] `_warmup_model(model, timeout)` 関数を追加
  - 最小限のリクエスト（"ping"）を送信
  - timeout はデフォルト 300秒（モデルロード考慮）
  - ログ出力: "Warming up model: {model}" → "Model ready"

### Phase 2: 呼び出し統合

- [x] T002 [src/generate_reading_dict.py] `generate_readings_batch()` 先頭で `_warmup_model()` を呼び出し
  - 最初のバッチ処理前に1回だけ実行

### Phase 3: テスト・確認

- [x] T003 [tests/test_generate_reading_dict.py] ウォームアップ関数のユニットテスト追加
  - `_warmup_model()` がリクエストを送信することを確認（mock）
- [ ] T004 動作確認: `make gen-dict` でバッチ1が成功することを確認

---

## リスク

| レベル | 内容 |
|-------|------|
| LOW   | ウォームアップで300秒使用するが、モデルがロード済みなら数秒で完了 |

---

## 完了条件

- [x] 全タスク完了
- [x] テスト通過
- [ ] `make gen-dict` でバッチ1成功確認（手動確認）
