# Phase 4 Output

## 作業概要
- User Story 4 - ISBN・書籍情報の簡略化の実装完了
- FAIL テスト 18 件を PASS させた
- ISBN番号（ISBN-10/ISBN-13、ハイフンあり/なし）を検出・削除する機能を実装

## 修正ファイル一覧
- `src/text_cleaner.py` - ISBN処理機能を追加
  - `ISBN_PATTERN` 定数を追加（ISBN-10/ISBN-13パターンに対応）
  - `_clean_isbn()` 関数を実装（ISBNを削除）

## 実装詳細

### ISBN_PATTERN 定数

ISBN-13とISBN-10の両方に対応する正規表現パターンを定義:

- ISBN-13: `978` または `979` で始まる13桁の数字（ハイフンあり/なし）
- ISBN-10: 10桁の数字（最後の文字は `X` または `x` も可）
- 大文字小文字混在対応: `ISBN`, `isbn`, `Isbn` など
- スペース区切り対応: `ISBN 978-...` のようなパターン

### _clean_isbn() 関数

```python
def _clean_isbn(text: str) -> str:
    """Remove ISBN numbers from text for TTS.

    Removes all ISBN patterns (ISBN-10 and ISBN-13, with or without hyphens).
    """
    return ISBN_PATTERN.sub("", text)
```

## テスト結果

全57テスト PASS（新規18テスト + 既存39テスト）:

### 新規テスト（18件）
- ISBN-13 ハイフン付き/スペース区切り: 4件
- 文中ISBN削除: 3件
- ISBN-10 処理: 3件
- 複数ISBN処理: 2件
- 大文字小文字混在: 3件
- 冪等性・エッジケース: 3件

### 既存テスト（39件）
- US1 URL処理: 21件
- US2/3 参照正規化: 18件

## 注意点

### 次 Phase で必要な情報

Phase 5では括弧付き英語表記の処理を実装:
- 「トイル（Toil）」→「トイル」
- 全角括弧 `（）` と半角括弧 `()` の両方に対応
- 括弧内が日本語の場合は保持（除外条件）

### 統合について

現状 `_clean_isbn()` は独立した関数として実装済み。Phase 9で `clean_page_text()` パイプラインに統合される予定。

## 実装のミス・課題

特になし。すべてのテストが PASS し、リグレッションもなし。
