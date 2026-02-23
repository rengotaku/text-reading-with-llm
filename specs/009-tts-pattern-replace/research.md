# Research: TTS前処理パターン置換

**Date**: 2026-02-22
**Feature**: 009-tts-pattern-replace

## 1. URL置換パターン

### Decision
裸のURL（`www.`や`https://`で始まる文字列）を「ウェブサイト」に置換する。

### Rationale
- Issue #13 の A案を採用
- 単純削除では「詳細は を参照」のように文が不自然になる
- 「ウェブサイト」は汎用的で文脈に依存しない

### Alternatives Considered
| 案 | 内容 | 却下理由 |
|----|------|----------|
| 削除のみ | URLを完全削除 | 文が不自然になる |
| ドメイン名読み | 「イグザンプル ドット コム」 | TTSで不自然、元の問題と同じ |
| 文脈ごと削除 | URL含む文全体を削除 | 情報損失が大きい |

### Implementation Pattern
```python
# 既存の BARE_URL_PATTERN を修正
# Before: BARE_URL_PATTERN.sub("", text)
# After:  BARE_URL_PATTERN.sub("ウェブサイト", text)
```

---

## 2. No.X → ナンバーX 変換

### Decision
`No.X` 形式（大文字小文字不問）を「ナンバーX」に変換する。数字部分は後続の `normalize_numbers()` で日本語読みに変換される。

### Rationale
- ユーザー指定: 章番号専用変換ではなく汎用的な置換
- 「ナンバー」は日本語として自然
- 文脈（章番号、製品番号、順位）に関係なく適用可能

### Alternatives Considered
| 案 | 内容 | 却下理由 |
|----|------|----------|
| 章番号変換 | No.21 → だいにじゅういっしょう | 章番号以外の用途で不適切 |
| 削除 | No.21 → 21 | 文脈情報の損失 |
| そのまま | TTSに任せる | 「エヌオー」と読まれて不自然 |

### Implementation Pattern
```python
NUMBER_PREFIX_PATTERN = re.compile(r"No\.(\d+)", re.IGNORECASE)
# "No.21" → "ナンバー21" → (normalize_numbers) → "ナンバーにじゅういち"
```

---

## 3. Chapter X → だいXしょう 変換

### Decision
`Chapter X` 形式を「だいXしょう」に変換する。

### Rationale
- 英語の "Chapter" は日本語読み上げで不自然
- 「だいXしょう」は日本語として標準的な章番号表現
- 既存の `number_normalizer.py` に「第N章」パターンがあり、一貫性を保つ

### Alternatives Considered
| 案 | 内容 | 却下理由 |
|----|------|----------|
| チャプターX | カタカナ化 | 「だいXしょう」の方が日本語として自然 |
| 削除 | Chapter を削除 | 文脈情報の損失 |

### Implementation Pattern
```python
CHAPTER_PATTERN = re.compile(r"Chapter\s+(\d+)", re.IGNORECASE)
# "Chapter 5" → "第5章" → (normalize_numbers in number_normalizer) → "だいごしょう"
```

---

## 4. 処理順序

### Decision
新規関数は `clean_page_text()` 内で以下の順序で実行:
1. `_clean_urls()` - URL置換 (修正)
2. `_clean_isbn()` - ISBN削除 (既存)
3. `_clean_number_prefix()` - No.X → ナンバーX (新規)
4. `_clean_chapter()` - Chapter X → 第X章 (新規)
5. (既存の処理続行)
6. `normalize_numbers()` - 数値の日本語化 (既存)

### Rationale
- No.X と Chapter X は数値正規化の前に処理する必要がある
- 「ナンバー21」→「ナンバーにじゅういち」の流れを確保
- 「第5章」→「だいごしょう」は既存パターンで処理される

---

## 5. 既存コードとの整合性

### 確認事項
- [x] `_clean_urls()` の現在の動作: 削除のみ → 置換に変更必要
- [x] `ISBN_PATTERN` の動作: 削除のみ → 変更不要
- [x] `number_normalizer.py` の「第N章」パターン: 既存 → そのまま利用

### 影響範囲
- `src/text_cleaner.py`: 関数修正・追加
- `tests/test_url_cleaning.py`: テスト修正・追加
- 新規テストファイル: 2つ (`test_number_prefix.py`, `test_chapter_conversion.py`)

---

## Summary

| パターン | 変換 | 実装方法 |
|----------|------|----------|
| `www.example.com` | ウェブサイト | `_clean_urls()` 修正 |
| `https://...` | ウェブサイト | `_clean_urls()` 修正 |
| `No.21` | ナンバー21 | `_clean_number_prefix()` 新規 |
| `Chapter 5` | 第5章 | `_clean_chapter()` 新規 |
| ISBN | 削除 | 既存のまま |

すべての NEEDS CLARIFICATION は解決済み。
