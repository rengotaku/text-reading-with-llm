# Contract: text_cleaner.py API

**Date**: 2026-02-06
**Module**: `src/text_cleaner.py`

## 新規関数インターフェース

### _clean_urls(text: str) -> str

URL関連のクリーニングを行う。

**Parameters**:
- `text` (str): 入力テキスト

**Returns**:
- `str`: URLが処理されたテキスト

**Processing Order**:
1. `[URL](URL)` 形式（リンクテキストがURL）→ 完全削除
2. `[text](URL)` 形式 → リンクテキストのみ残す
3. 裸のURL → 完全削除

**Examples**:
```python
>>> _clean_urls("[SRE NEXT](https://sre-next.dev/)")
"SRE NEXT"

>>> _clean_urls("[https://example.com](https://example.com)")
""

>>> _clean_urls("詳細は https://example.com を参照")
"詳細は  を参照"
```

---

### _clean_isbn(text: str) -> str

ISBN番号を削除する。

**Parameters**:
- `text` (str): 入力テキスト

**Returns**:
- `str`: ISBNが削除されたテキスト

**Examples**:
```python
>>> _clean_isbn("ISBN978-4-297-15072-3")
""

>>> _clean_isbn("本書 ISBN 978-4-297-15072-3 は...")
"本書  は..."
```

---

### _clean_parenthetical_english(text: str) -> str

括弧付き英語表記を除去し、日本語部分のみ残す。

**Parameters**:
- `text` (str): 入力テキスト

**Returns**:
- `str`: 括弧内英語が除去されたテキスト

**Examples**:
```python
>>> _clean_parenthetical_english("トイル（Toil）の削減")
"トイルの削減"

>>> _clean_parenthetical_english("SRE（Site Reliability Engineering）")
"SRE"

>>> _clean_parenthetical_english("API（アプリケーション...）")  # 日本語含む
"API（アプリケーション...）"  # 変換しない
```

---

### _normalize_references(text: str) -> str

図表・注釈参照を読み仮名形式に変換する。

**Parameters**:
- `text` (str): 入力テキスト

**Returns**:
- `str`: 参照が読み仮名に変換されたテキスト

**Examples**:
```python
>>> _normalize_references("図2.1に示す")
"ずにてんいちに示す"

>>> _normalize_references("表1.2を参照")
"ひょういちてんにを参照"

>>> _normalize_references("注1.6の説明")
"ちゅういちてんろくの説明"
```

---

## 変更関数インターフェース

### clean_page_text(text: str) -> str (Modified)

**変更点**: 新規関数を処理パイプラインに追加

**New Processing Order**:
```python
# 1. 既存のMarkdownクリーニング
# 2. NEW: URL処理
text = _clean_urls(text)
# 3. NEW: ISBN処理
text = _clean_isbn(text)
# 4. NEW: 括弧付き英語除去
text = _clean_parenthetical_english(text)
# 5. NEW: 参照正規化
text = _normalize_references(text)
# 6. normalize_punctuation() (modified)
# 7. normalize_numbers()
# 8. apply_reading_rules()
# 9. apply_llm_readings()
# 10. convert_to_kana()
```
