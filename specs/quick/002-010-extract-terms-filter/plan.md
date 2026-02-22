---
status: completed
created: 2026-02-22
branch: quick/002-010-extract-terms-filter
issue: "#10"
---

# 010-extract-terms-filter

## 概要

`extract_technical_terms()` の正規表現が広すぎて URL・ISBN・一般語などのノイズが抽出される問題を修正。フィルタ関数を追加して不要パターンを除外する。

## ゴール

- [x] URL（www.*, http*）が除外される
- [x] ISBN（ISBN978-...）が除外される
- [x] 章番号（No.21 等）が除外される
- [x] 一般英語ストップワード（and, of, in 等）が除外される
- [x] 2文字以下の小文字のみ（eb, cm 等）が除外される

## スコープ外

- 正規表現自体の変更（フィルタ追加のみ）
- 既存 readings.json のクリーンアップ（--merge で再生成すれば解決）

## 前提条件

- 既存の `extract_technical_terms()` をベースに拡張
- 既存テストは mock しているため影響なし

---

## 実装タスク

### Phase 1: テスト作成 (TDD RED)

- [x] T001 [tests/test_llm_reading_generator.py] `_should_exclude()` フィルタ関数のユニットテスト追加
- [x] T002 [tests/test_llm_reading_generator.py] `extract_technical_terms()` のフィルタ適用テスト追加

### Phase 2: 実装 (TDD GREEN)

- [x] T003 [src/llm_reading_generator.py] STOP_WORDS 定数を定義
- [x] T004 [src/llm_reading_generator.py] `_should_exclude()` ヘルパー関数を追加
- [x] T005 [src/llm_reading_generator.py] `extract_technical_terms()` にフィルタを統合

### Phase 3: 確認

- [x] T006 全テスト通過確認 (`make test`)
- [x] T007 ruff lint/format 確認 (`make lint`)

---

## リスク

| レベル | 内容 |
|-------|------|
| LOW | 過剰フィルタで有効な term が除外される可能性 → テストで検証 |
| LOW | ストップワードリストの不足 → 必要に応じて追加可能 |

---

## 技術詳細

### 除外パターン

```python
STOP_WORDS = {
    "and", "or", "of", "in", "if", "on", "the", "to", "is", "it",
    "at", "by", "for", "an", "as", "do", "no", "so", "up", "we",
    "he", "be", "https", "http"
}

def _should_exclude(term: str) -> bool:
    if term.lower() in STOP_WORDS:
        return True
    if term.startswith(("www.", "http")):
        return True
    if term.startswith("ISBN"):
        return True
    if re.match(r"^No\.\d", term):
        return True
    if len(term) <= 2 and term.islower():
        return True
    return False
```

---

## 完了条件

- [x] 全タスク完了
- [x] テスト通過 (新規テスト含む)
- [x] ruff lint/format 通過
