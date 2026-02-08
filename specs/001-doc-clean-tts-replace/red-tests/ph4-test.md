# Phase 4 RED Tests

## サマリー
- Phase: Phase 4 - User Story 4: ISBN・書籍情報の簡略化
- FAIL テスト数: 18
- テストファイル: tests/test_isbn_cleaning.py

## FAIL テスト一覧

| テストファイル | テストメソッド | 期待動作 |
|---------------|---------------|---------|
| tests/test_isbn_cleaning.py | test_clean_isbn_with_hyphens_basic | ISBN978-4-87311-865-8 -> "" (完全削除) |
| tests/test_isbn_cleaning.py | test_clean_isbn_with_hyphens_13_digit | ISBN979形式も削除 |
| tests/test_isbn_cleaning.py | test_clean_isbn_with_space_basic | ISBN 978-... (スペース区切り) 削除 |
| tests/test_isbn_cleaning.py | test_clean_isbn_with_multiple_spaces | 複数スペースも処理 |
| tests/test_isbn_cleaning.py | test_clean_isbn_in_sentence_basic | 文中ISBNを削除、前後テキスト保持 |
| tests/test_isbn_cleaning.py | test_clean_isbn_in_sentence_with_space | 文中スペース区切りISBN削除 |
| tests/test_isbn_cleaning.py | test_clean_isbn_at_end_of_sentence | 文末ISBN削除 |
| tests/test_isbn_cleaning.py | test_clean_isbn_no_hyphens | ハイフンなしISBN-13削除 |
| tests/test_isbn_cleaning.py | test_clean_isbn_10_digit | ISBN-10形式 (4-87311-865-X) 削除 |
| tests/test_isbn_cleaning.py | test_clean_isbn_10_digit_no_hyphens | ハイフンなしISBN-10削除 |
| tests/test_isbn_cleaning.py | test_clean_isbn_multiple | 複数ISBN -> "と" のみ残る |
| tests/test_isbn_cleaning.py | test_clean_isbn_preserve_other_numbers | ISBN以外の数字 (3000円) は保持 |
| tests/test_isbn_cleaning.py | test_clean_isbn_lowercase | 小文字isbn処理 |
| tests/test_isbn_cleaning.py | test_clean_isbn_mixed_case | 大文字小文字混在 (Isbn) 処理 |
| tests/test_isbn_cleaning.py | test_clean_isbn_idempotent_no_isbn | ISBNなしテキスト不変 |
| tests/test_isbn_cleaning.py | test_clean_isbn_idempotent_already_processed | 冪等性確認 |
| tests/test_isbn_cleaning.py | test_clean_isbn_empty_string | 空文字列処理 |
| tests/test_isbn_cleaning.py | test_clean_isbn_whitespace_only | 空白のみ処理 |

## 実装ヒント

- `src/text_cleaner.py` に `_clean_isbn(text: str) -> str` を実装
- ISBN パターン定数を追加:
  ```python
  # ISBN patterns (US4)
  # ISBN-13: 978/979 + 10 digits with optional hyphens
  # ISBN-10: 10 digits/chars with optional hyphens (last char can be X)
  ISBN_PATTERN = re.compile(
      r'[Ii][Ss][Bb][Nn]\s*'  # ISBN prefix (case insensitive)
      r'(?:'
      r'97[89][-\s]?\d[-\s]?\d{1,5}[-\s]?\d{1,7}[-\s]?\d'  # ISBN-13 with hyphens
      r'|97[89]\d{10}'  # ISBN-13 without hyphens
      r'|\d[-\s]?\d{1,5}[-\s]?\d{1,7}[-\s]?[\dXx]'  # ISBN-10 with hyphens
      r'|\d{9}[\dXx]'  # ISBN-10 without hyphens
      r')'
  )
  ```
- チェックディジット X は大文字・小文字両対応
- 大文字・小文字 ISBN 両対応 (ISBN, isbn, Isbn)

## FAIL 出力例

```
============================= test session starts ==============================
platform linux -- Python 3.13.11, pytest-9.0.2
collected 39 items / 1 error

==================================== ERRORS ====================================
_________________ ERROR collecting tests/test_isbn_cleaning.py _________________
ImportError while importing test module '/data/projects/text-reading-with-llm/tests/test_isbn_cleaning.py'.
tests/test_isbn_cleaning.py:9: in <module>
    from src.text_cleaner import _clean_isbn
E   ImportError: cannot import name '_clean_isbn' from 'src.text_cleaner'
=========================== short test summary info ============================
ERROR tests/test_isbn_cleaning.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.08s ===============================
```

## 次ステップ

phase-executor が以下を実行:
1. `_clean_isbn()` 関数を実装 (GREEN)
2. `make test` で PASS 確認
3. リグレッションなしを確認
4. `tasks/ph4-output.md` を生成
