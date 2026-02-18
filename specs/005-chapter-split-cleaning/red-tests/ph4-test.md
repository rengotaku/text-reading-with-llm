# Phase 4 RED Tests: cleaned_text.txt の品質向上

**Date**: 2026-02-18
**Status**: RED (FAIL確認済み)
**User Story**: US3 - cleaned_text.txt の品質向上

## サマリー

| 項目 | 値 |
|------|-----|
| 作成テスト数 | 8 |
| FAIL数 | 8 |
| テストファイル | tests/test_xml2_pipeline.py |

## FAILテスト一覧

| テストファイル | テストメソッド | 期待動作 |
|--------------|--------------|----------|
| tests/test_xml2_pipeline.py | test_cleaned_text_does_not_contain_url | cleaned_text.txt に URL が含まれない（clean_page_text() 適用） |
| tests/test_xml2_pipeline.py | test_cleaned_text_does_not_contain_parenthetical_english | cleaned_text.txt に括弧内英語が含まれない |
| tests/test_xml2_pipeline.py | test_cleaned_text_numbers_converted_to_kana | cleaned_text.txt の数字がカナに変換されている |
| tests/test_xml2_pipeline.py | test_cleaned_text_isbn_removed | cleaned_text.txt に ISBN が含まれない |
| tests/test_xml2_pipeline.py | test_cleaned_text_has_chapter_separator_format | cleaned_text.txt に === Chapter N: Title === 形式の章区切りがある |
| tests/test_xml2_pipeline.py | test_cleaned_text_chapter_separator_contains_title | 章区切り行にタイトルが含まれる |
| tests/test_xml2_pipeline.py | test_cleaned_text_paragraph_text_is_cleaned | 段落テキスト全体が clean_page_text() でクリーニングされている |
| tests/test_xml2_pipeline.py | test_cleaned_text_no_item_type_labels | === paragraph === のような item_type ラベルが含まれない |

## 実装ヒント

- `main()` 関数の cleaned_text.txt 出力部分（L468-478）を修正
  - 各 item.text に `clean_page_text()` を適用してから出力
  - `=== {item_type} ===` ラベルを廃止し、`=== Chapter N: Title ===` 形式の章区切りに変更
- chapter 区切りの挿入:
  - chapter_number が変わるタイミングで `=== Chapter N: Title ===` を挿入
  - chapter タイトルは HeadingInfo から取得
- マーカー処理:
  - CHAPTER_MARKER / SECTION_MARKER は clean_page_text() 適用前に除去
  - 表示用の `[章]` `[節]` は clean_page_text() 適用後に不要

## make test 出力 (抜粋)

```
FAILED tests/test_xml2_pipeline.py::TestCleanedTextFileContainsCleanedContent::test_cleaned_text_does_not_contain_url - AssertionError
FAILED tests/test_xml2_pipeline.py::TestCleanedTextFileContainsCleanedContent::test_cleaned_text_does_not_contain_parenthetical_english - AssertionError
FAILED tests/test_xml2_pipeline.py::TestCleanedTextFileContainsCleanedContent::test_cleaned_text_numbers_converted_to_kana - AssertionError
FAILED tests/test_xml2_pipeline.py::TestCleanedTextFileContainsCleanedContent::test_cleaned_text_isbn_removed - AssertionError
FAILED tests/test_xml2_pipeline.py::TestCleanedTextFileHasChapterMarkers::test_cleaned_text_has_chapter_separator_format - AssertionError
FAILED tests/test_xml2_pipeline.py::TestCleanedTextFileHasChapterMarkers::test_cleaned_text_chapter_separator_contains_title - AssertionError
FAILED tests/test_xml2_pipeline.py::TestCleanedTextFileHasChapterMarkers::test_cleaned_text_paragraph_text_is_cleaned - AssertionError
FAILED tests/test_xml2_pipeline.py::TestCleanedTextFileHasChapterMarkers::test_cleaned_text_no_item_type_labels - AssertionError
8 failed, 443 passed in 1.03s
```
