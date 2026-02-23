# Phase 3 RED Tests: 番号表記の自然な読み上げ

**Date**: 2026-02-22
**Status**: RED (FAIL確認済み)
**User Story**: US2 - 番号表記の自然な読み上げ

## サマリー

| 項目 | 値 |
|------|-----|
| 作成テスト数 | 24 |
| FAIL数 | 24 (ImportError: 関数未実装) |
| テストファイル | tests/test_number_prefix.py, tests/test_chapter_conversion.py |

## FAILテスト一覧

| テストファイル | テストメソッド | 期待動作 |
|--------------|--------------|----------|
| tests/test_number_prefix.py | test_clean_number_prefix_basic | No.21 -> ナンバー21 |
| tests/test_number_prefix.py | test_clean_number_prefix_attached_to_word | 製品No.123 -> 製品ナンバー123 |
| tests/test_number_prefix.py | test_clean_number_prefix_large_number | No.1000 -> ナンバー1000 |
| tests/test_number_prefix.py | test_clean_number_prefix_single_digit | No.5 -> ナンバー5 |
| tests/test_number_prefix.py | test_clean_number_prefix_lowercase | no.5 -> ナンバー5 |
| tests/test_number_prefix.py | test_clean_number_prefix_uppercase | NO.100 -> ナンバー100 |
| tests/test_number_prefix.py | test_clean_number_prefix_mixed_case | nO.42 -> ナンバー42 |
| tests/test_number_prefix.py | test_clean_number_prefix_no_number_after_dot | No. 後に数字なし -> 変換しない |
| tests/test_number_prefix.py | test_clean_number_prefix_no_followed_by_text | No.abc -> 変換しない |
| tests/test_number_prefix.py | test_clean_number_prefix_multiple | 複数 No.X を同時変換 |
| tests/test_number_prefix.py | test_clean_number_prefix_empty_string | 空文字列 -> 空文字列 |
| tests/test_number_prefix.py | test_clean_number_prefix_no_match | マッチなし -> 変化なし |
| tests/test_number_prefix.py | test_clean_number_prefix_idempotent | 処理済みテキスト -> 変化なし |
| tests/test_chapter_conversion.py | test_clean_chapter_basic | Chapter 5 -> 第5章 |
| tests/test_chapter_conversion.py | test_clean_chapter_double_digit | Chapter 12 -> 第12章 |
| tests/test_chapter_conversion.py | test_clean_chapter_single_digit | Chapter 1 -> 第1章 |
| tests/test_chapter_conversion.py | test_clean_chapter_large_number | Chapter 100 -> 第100章 |
| tests/test_chapter_conversion.py | test_clean_chapter_lowercase | chapter 12 -> 第12章 |
| tests/test_chapter_conversion.py | test_clean_chapter_uppercase | CHAPTER 1 -> 第1章 |
| tests/test_chapter_conversion.py | test_clean_chapter_mixed_case | cHaPtEr 3 -> 第3章 |
| tests/test_chapter_conversion.py | test_clean_chapter_multiple | 複数 Chapter を同時変換 |
| tests/test_chapter_conversion.py | test_clean_chapter_empty_string | 空文字列 -> 空文字列 |
| tests/test_chapter_conversion.py | test_clean_chapter_no_match | マッチなし -> 変化なし |
| tests/test_chapter_conversion.py | test_clean_chapter_without_number | Chapter 後に数字なし -> 変換しない |
| tests/test_chapter_conversion.py | test_clean_chapter_idempotent | 処理済みテキスト -> 変化なし |

## 実装ヒント

- `_clean_number_prefix(text: str) -> str`: `NUMBER_PREFIX_PATTERN = re.compile(r"No\.(\d+)", re.IGNORECASE)` を使い `ナンバー\1` に置換
- `_clean_chapter(text: str) -> str`: `CHAPTER_PATTERN = re.compile(r"Chapter\s+(\d+)", re.IGNORECASE)` を使い `第\1章` に置換
- エッジケース: No./Chapter の後に数字がない場合は置換しない
- 大文字小文字不問 (`re.IGNORECASE`)
- `clean_page_text()` への統合: `_clean_isbn()` の後、`_normalize_references()` の前に配置

## make test 出力 (抜粋)

```
ERROR tests/test_chapter_conversion.py - ImportError: cannot import name '_clean_chapter' from 'src.text_cleaner'
ERROR tests/test_number_prefix.py - ImportError: cannot import name '_clean_number_prefix' from 'src.text_cleaner'
2 errors in 0.21s
```
