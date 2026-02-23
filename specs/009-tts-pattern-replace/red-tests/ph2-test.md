# Phase 2 RED Tests: US1 - URL含有テキストの自然な読み上げ

**Date**: 2026-02-22
**Status**: RED (FAIL確認済み)
**User Story**: US1 - URL含有テキストの自然な読み上げ

## サマリー

| 項目 | 値 |
|------|-----|
| 作成テスト数 | 22 (更新8 + 新規4 = 変更12, 既存維持10) |
| FAIL数 | 11 |
| テストファイル | tests/test_url_cleaning.py |

## FAILテスト一覧

| テストファイル | テストメソッド | 期待動作 |
|--------------|--------------|----------|
| tests/test_url_cleaning.py | test_clean_urls_url_as_link_text_replaced_with_website | URLリンクテキスト → 「ウェブサイト」に置換 |
| tests/test_url_cleaning.py | test_clean_urls_url_as_link_text_with_path | パス付きURLリンクテキスト → 「ウェブサイト」に置換 |
| tests/test_url_cleaning.py | test_clean_urls_bare_url_replaced_with_website | 裸URL → 「ウェブサイト」に置換 |
| tests/test_url_cleaning.py | test_clean_urls_bare_url_http | HTTP URL → 「ウェブサイト」に置換 |
| tests/test_url_cleaning.py | test_clean_urls_bare_url_with_fragment | フラグメント付きURL → 「ウェブサイト」に置換 |
| tests/test_url_cleaning.py | test_clean_urls_mixed_markdown_and_bare | 混在URL処理で裸URL部分が「ウェブサイト」に置換 |
| tests/test_url_cleaning.py | test_clean_urls_multiple_bare_urls | 複数裸URLがそれぞれ「ウェブサイト」に置換 |
| tests/test_url_cleaning.py | test_clean_urls_multiple_consecutive_bare_urls | 連続する裸URLが個別に「ウェブサイト」に置換 |
| tests/test_url_cleaning.py | test_clean_urls_bare_url_followed_by_period | URL後の句点保持、URL部分は「ウェブサイト」に置換 |
| tests/test_url_cleaning.py | test_clean_urls_bare_url_followed_by_comma | URL後の読点保持、URL部分は「ウェブサイト」に置換 |
| tests/test_url_cleaning.py | test_clean_urls_bare_url_at_end_of_sentence | 文末URLが「ウェブサイト」に置換 |

## 変更内容

### 更新したテスト (期待値変更: "" → "ウェブサイト")

1. **TestCleanUrlsUrlAsLinkText** (2テスト): URLがリンクテキストの場合、削除ではなく「ウェブサイト」に置換
2. **TestCleanUrlsBareUrl** (3テスト): 裸URLを削除ではなく「ウェブサイト」に置換
3. **TestCleanUrlsMultipleUrls** (2テスト): 混在・複数の裸URLをそれぞれ「ウェブサイト」に置換
4. **TestCleanUrlsIdempotent** (1テスト): 処理済みテキストの冪等性テスト更新

### 新規追加テスト

1. **test_clean_urls_multiple_consecutive_bare_urls**: 連続する複数裸URLの個別置換
2. **TestCleanUrlsTrailingPunctuation** (3テスト): URL直後の句読点保持確認

## 実装ヒント

- `_clean_urls()` の `replace_markdown_link` 内: `URL_TEXT_PATTERN.match(link_text)` の場合 `return ""` → `return "ウェブサイト"`
- `_clean_urls()` の裸URL処理: `BARE_URL_PATTERN.sub("", text)` → `BARE_URL_PATTERN.sub("ウェブサイト", text)`
- エッジケース: 句読点はURL正規表現のマッチ範囲外なので自動的に保持される

## make test 出力 (抜粋)

```
FAILED tests/test_url_cleaning.py::TestCleanUrlsUrlAsLinkText::test_clean_urls_url_as_link_text_replaced_with_website - AssertionError
FAILED tests/test_url_cleaning.py::TestCleanUrlsUrlAsLinkText::test_clean_urls_url_as_link_text_with_path - AssertionError
FAILED tests/test_url_cleaning.py::TestCleanUrlsBareUrl::test_clean_urls_bare_url_replaced_with_website - AssertionError
FAILED tests/test_url_cleaning.py::TestCleanUrlsBareUrl::test_clean_urls_bare_url_http - AssertionError
FAILED tests/test_url_cleaning.py::TestCleanUrlsBareUrl::test_clean_urls_bare_url_with_fragment - AssertionError
FAILED tests/test_url_cleaning.py::TestCleanUrlsMultipleUrls::test_clean_urls_mixed_markdown_and_bare - AssertionError
FAILED tests/test_url_cleaning.py::TestCleanUrlsMultipleUrls::test_clean_urls_multiple_bare_urls - AssertionError
FAILED tests/test_url_cleaning.py::TestCleanUrlsMultipleUrls::test_clean_urls_multiple_consecutive_bare_urls - AssertionError
FAILED tests/test_url_cleaning.py::TestCleanUrlsTrailingPunctuation::test_clean_urls_bare_url_followed_by_period - AssertionError
FAILED tests/test_url_cleaning.py::TestCleanUrlsTrailingPunctuation::test_clean_urls_bare_url_followed_by_comma - AssertionError
FAILED tests/test_url_cleaning.py::TestCleanUrlsTrailingPunctuation::test_clean_urls_bare_url_at_end_of_sentence - AssertionError
11 failed, 11 passed in 0.05s
```
