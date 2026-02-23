# Phase 1 Output: Setup

**Date**: 2026-02-22
**Status**: 完了

## 実行タスク

- [x] T001 Read current implementation in src/text_cleaner.py
- [x] T002 [P] Read existing URL tests in tests/test_url_cleaning.py
- [x] T003 [P] Read existing ISBN tests in tests/test_isbn_cleaning.py
- [x] T004 [P] Read number normalizer in src/number_normalizer.py
- [x] T005 Run `make test` to verify current test status (36 passed)
- [x] T006 Generate setup output

## 既存コード分析

### src/text_cleaner.py

**構造**:
- `MARKDOWN_LINK_PATTERN`: Markdownリンク `[text](url)` を検出
- `BARE_URL_PATTERN`: 裸のURL `https://...` を検出
- `URL_TEXT_PATTERN`: リンクテキストがURLかどうかを判定
- `ISBN_PATTERN`: ISBN-10/ISBN-13 を検出
- `_clean_urls()`: URLの除去処理（現状は削除のみ）
- `_clean_isbn()`: ISBNの削除処理
- `clean_page_text()`: メイン処理関数

**更新が必要な箇所**:
1. `_clean_urls()`:
   - 現在: `BARE_URL_PATTERN.sub("", text)` → 削除
   - 変更: `BARE_URL_PATTERN.sub("ウェブサイト", text)` → 置換
   - 現在: URL-as-link-text → "" → 削除
   - 変更: URL-as-link-text → "ウェブサイト" → 置換
2. `clean_page_text()`:
   - 新規関数追加: `_clean_number_prefix()`, `_clean_chapter()`
   - 処理順序: `_clean_urls()` → `_clean_isbn()` → `_clean_number_prefix()` → `_clean_chapter()`

### src/number_normalizer.py

**構造**:
- `number_to_japanese()`: 数字を日本語読みに変換
- `normalize_numbers()`: テキスト中の数字をすべて変換
- `PATTERNS`: 変換パターンリスト（第N章 → だいN... など既存）

**活用ポイント**:
- `第N章` パターンが既に存在（L486-489）: `r"第(?P<number>\d+)(?P<suffix>[章節回部編条項])"`
- `Chapter X` → `第X章` に変換後、既存の `normalize_numbers()` で `だいXしょう` になる

## 既存テスト分析

- `tests/test_url_cleaning.py`: 18テスト
  - `TestCleanUrlsMarkdownLink`: Markdownリンクからテキスト抽出
  - `TestCleanUrlsUrlAsLinkText`: URLがリンクテキストの場合の削除
  - `TestCleanUrlsBareUrl`: 裸URLの削除
  - `TestCleanUrlsMultipleUrls`: 複数URL処理
  - `TestCleanUrlsIdempotent`: 冪等性確認
  - `TestCleanUrlsEdgeCases`: エッジケース

- `tests/test_isbn_cleaning.py`: 18テスト
  - ISBN-10/ISBN-13、ハイフン有無、文中処理など

**存在しない**:
- `tests/test_number_prefix.py` → Phase 3 で新規作成
- `tests/test_chapter_conversion.py` → Phase 3 で新規作成

## 新規作成ファイル

### tests/test_number_prefix.py (Phase 3)

- `TestCleanNumberPrefix`: No.X → ナンバーX テスト
- 基本パターン、大文字小文字、文中処理

### tests/test_chapter_conversion.py (Phase 3)

- `TestCleanChapter`: Chapter X → 第X章 テスト
- 基本パターン、大文字小文字、文中処理

## 技術的決定事項

1. **URL置換文字列**: 「ウェブサイト」（research.md の A案採用）
2. **No.X 変換先**: 「ナンバーX」（汎用的、章番号専用ではない）
3. **Chapter X 変換先**: 「第X章」（既存の normalize_numbers で「だいXしょう」に変換される）
4. **処理順序**: URL → ISBN → No.X → Chapter → その他（数値正規化の前に変換必須）

## パターン定数（追加予定）

```python
# No.X パターン（大文字小文字不問）
NUMBER_PREFIX_PATTERN = re.compile(r"No\.(\d+)", re.IGNORECASE)

# Chapter X パターン（大文字小文字不問）
CHAPTER_PATTERN = re.compile(r"Chapter\s+(\d+)", re.IGNORECASE)
```

## 次フェーズへの引き継ぎ

### Phase 2 (US1: URL置換)

- `_clean_urls()` の修正: 削除 → 「ウェブサイト」置換
- 既存テスト期待値変更: `""` → `"ウェブサイト"`
- 新規テスト追加: 複数連続URL、句読点付きURL

### Phase 3 (US2: No.X/Chapter)

- `NUMBER_PREFIX_PATTERN` 定数追加
- `CHAPTER_PATTERN` 定数追加
- `_clean_number_prefix()` 関数新規作成
- `_clean_chapter()` 関数新規作成
- `clean_page_text()` に統合

### Phase 4 (US3: ISBN括弧処理)

- `_clean_isbn()` の拡張: 括弧ごと削除
- 空白正規化処理追加
