# Phase 4 RED Tests: ISBN括弧・ラベル削除と空白正規化

**Date**: 2026-02-22
**Status**: RED (FAIL確認済み)
**User Story**: US3 - ISBN・書籍メタ情報の適切な処理

## サマリー

| 項目 | 値 |
|------|-----|
| 作成テスト数 | 15 |
| FAIL数 | 13 |
| PASS数(既存) | 20 |
| テストファイル | tests/test_isbn_cleaning.py |

## FAILテスト一覧

| テストファイル | テストメソッド | 期待動作 |
|--------------|--------------|----------|
| tests/test_isbn_cleaning.py | test_parenthetical_isbn_fullwidth_brackets | 全角括弧内ISBN「（ISBN: 978-...）」を括弧ごと削除 |
| tests/test_isbn_cleaning.py | test_parenthetical_isbn_halfwidth_brackets | 半角括弧内ISBN「(ISBN: 978-...)」を括弧ごと削除 |
| tests/test_isbn_cleaning.py | test_parenthetical_isbn_no_space_after_colon | コロン後スペースなし「（ISBN:978-...）」を括弧ごと削除 |
| tests/test_isbn_cleaning.py | test_parenthetical_isbn_10_digit | ISBN-10「（ISBN: 4-7981-8771-X）」を括弧ごと削除 |
| tests/test_isbn_cleaning.py | test_parenthetical_isbn_without_label | ラベルなし括弧内ISBN「（978-...）」を括弧ごと削除 |
| tests/test_isbn_cleaning.py | test_isbn_with_colon_label | 「ISBN: 978-...」ラベル付きISBNを完全削除 |
| tests/test_isbn_cleaning.py | test_isbn10_with_label | 「ISBN-10: 4-...」ラベル付きISBNを完全削除 |
| tests/test_isbn_cleaning.py | test_isbn13_with_label | 「ISBN-13: 978-...」ラベル付きISBNを完全削除 |
| tests/test_isbn_cleaning.py | test_isbn_label_in_sentence | 文中のISBN:ラベル付きパターンを削除 |
| tests/test_isbn_cleaning.py | test_isbn_label_at_beginning | 文頭のISBN:ラベル付きパターンを削除し先頭空白正規化 |
| tests/test_isbn_cleaning.py | test_double_space_after_isbn_removal | 二重スペースを正規化（単一スペースまたは削除） |
| tests/test_isbn_cleaning.py | test_multiple_spaces_collapse | 複数スペースを単一スペースに正規化 |
| tests/test_isbn_cleaning.py | test_fullwidth_space_normalization | 全角スペースも正規化対象 |

## テストクラス構成

### TestCleanIsbnParentheticalRemoval (5テスト: 5 FAIL)
括弧ごとISBNを削除するテスト。全角・半角括弧、ラベル有無、ISBN-10対応。

### TestCleanIsbnLabelRemoval (5テスト: 5 FAIL)
「ISBN:」「ISBN-10:」「ISBN-13:」ラベル付きISBNを完全削除するテスト。

### TestCleanIsbnSpaceNormalization (5テスト: 3 FAIL, 2 PASS)
ISBN削除後の空白正規化テスト。二重スペース、複数スペース、全角スペースの正規化。
- PASS: `test_leading_space_after_isbn_removal`（strip()で対応可能なため）
- PASS: `test_trailing_space_after_isbn_removal`（strip()で対応可能なため）

## 実装ヒント

- `_clean_isbn()`: 現在の `ISBN_PATTERN.sub("", text)` を拡張して括弧・ラベル対応パターンを追加
- 新規パターン `ISBN_WITH_CONTEXT_PATTERN`: 括弧（全角・半角）内のISBN、ラベル付きISBN（ISBN:, ISBN-10:, ISBN-13:）を検出
- 空白正規化: ISBN削除後に二重以上のスペース（半角・全角）を正規化する処理を追加
- 処理順序: 括弧付きISBN削除 → ラベル付きISBN削除 → 裸のISBN削除 → 空白正規化

## make test 出力 (抜粋)

```
FAILED tests/test_isbn_cleaning.py::TestCleanIsbnParentheticalRemoval::test_parenthetical_isbn_fullwidth_brackets - AssertionError
FAILED tests/test_isbn_cleaning.py::TestCleanIsbnParentheticalRemoval::test_parenthetical_isbn_halfwidth_brackets - AssertionError
FAILED tests/test_isbn_cleaning.py::TestCleanIsbnParentheticalRemoval::test_parenthetical_isbn_no_space_after_colon - AssertionError
FAILED tests/test_isbn_cleaning.py::TestCleanIsbnParentheticalRemoval::test_parenthetical_isbn_10_digit - AssertionError
FAILED tests/test_isbn_cleaning.py::TestCleanIsbnParentheticalRemoval::test_parenthetical_isbn_without_label - AssertionError
FAILED tests/test_isbn_cleaning.py::TestCleanIsbnLabelRemoval::test_isbn_with_colon_label - AssertionError
FAILED tests/test_isbn_cleaning.py::TestCleanIsbnLabelRemoval::test_isbn10_with_label - AssertionError
FAILED tests/test_isbn_cleaning.py::TestCleanIsbnLabelRemoval::test_isbn13_with_label - AssertionError
FAILED tests/test_isbn_cleaning.py::TestCleanIsbnLabelRemoval::test_isbn_label_in_sentence - AssertionError
FAILED tests/test_isbn_cleaning.py::TestCleanIsbnLabelRemoval::test_isbn_label_at_beginning - AssertionError
FAILED tests/test_isbn_cleaning.py::TestCleanIsbnSpaceNormalization::test_double_space_after_isbn_removal - AssertionError
FAILED tests/test_isbn_cleaning.py::TestCleanIsbnSpaceNormalization::test_multiple_spaces_collapse - AssertionError
FAILED tests/test_isbn_cleaning.py::TestCleanIsbnSpaceNormalization::test_fullwidth_space_normalization - AssertionError
13 failed, 20 passed in 0.07s
```
