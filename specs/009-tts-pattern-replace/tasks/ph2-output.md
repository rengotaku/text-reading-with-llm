# Phase 2 Output: US1 - URL含有テキストの自然な読み上げ

**Date**: 2026-02-22
**Status**: 完了
**User Story**: US1 - URL含有テキストの自然な読み上げ

## 実行タスク

- [x] T014 Read RED tests: specs/009-tts-pattern-replace/red-tests/ph2-test.md
- [x] T015 [US1] Modify `_clean_urls()` in src/text_cleaner.py: BARE_URL_PATTERN.sub("ウェブサイト", text)
- [x] T016 [US1] Modify `_clean_urls()` in src/text_cleaner.py: URL-as-link-text → "ウェブサイト"
- [x] T017 Verify `make test` PASS (GREEN)
- [x] T018 Verify `make test` passes all tests (回帰なし)
- [x] T019 Generate phase output: specs/009-tts-pattern-replace/tasks/ph2-output.md

## 変更ファイル一覧

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| src/text_cleaner.py | 修正 | `_clean_urls()` を修正: URL削除 → 「ウェブサイト」置換 |
| tests/test_url_cleaning.py | 既存 | RED Phase で期待値を "" → "ウェブサイト" に変更済み |
| specs/009-tts-pattern-replace/tasks.md | 修正 | T014-T019 をチェック済みに更新 |

## 実装詳細

### src/text_cleaner.py の変更

#### 変更前（L119-L140）

```python
def _clean_urls(text: str) -> str:
    """Remove URLs from text for TTS.

    - Markdown links: Keep link text, remove URL
    - URL as link text: Remove entirely
    - Bare URLs: Remove entirely
    """

    # Step 1: Handle Markdown links
    def replace_markdown_link(match):
        link_text = match.group(1)
        # If link text is a URL, remove entirely
        if URL_TEXT_PATTERN.match(link_text):
            return ""
        return link_text

    text = MARKDOWN_LINK_PATTERN.sub(replace_markdown_link, text)

    # Step 2: Remove bare URLs
    text = BARE_URL_PATTERN.sub("", text)

    return text
```

#### 変更後（L119-L140）

```python
def _clean_urls(text: str) -> str:
    """Replace URLs with 'ウェブサイト' for TTS.

    - Markdown links: Keep link text, remove URL
    - URL as link text: Replace with 'ウェブサイト'
    - Bare URLs: Replace with 'ウェブサイト'
    """

    # Step 1: Handle Markdown links
    def replace_markdown_link(match):
        link_text = match.group(1)
        # If link text is a URL, replace with 'ウェブサイト'
        if URL_TEXT_PATTERN.match(link_text):
            return "ウェブサイト"
        return link_text

    text = MARKDOWN_LINK_PATTERN.sub(replace_markdown_link, text)

    # Step 2: Replace bare URLs with 'ウェブサイト'
    text = BARE_URL_PATTERN.sub("ウェブサイト", text)

    return text
```

**変更箇所**:
1. Line 132: `return ""` → `return "ウェブサイト"`
2. Line 138: `BARE_URL_PATTERN.sub("", text)` → `BARE_URL_PATTERN.sub("ウェブサイト", text)`
3. Docstring 更新: "Remove" → "Replace"

## テスト結果

### URL cleaning tests (22 tests)

```
tests/test_url_cleaning.py::TestCleanUrlsMarkdownLink::test_clean_urls_markdown_link_basic PASSED
tests/test_url_cleaning.py::TestCleanUrlsMarkdownLink::test_clean_urls_markdown_link_with_path PASSED
tests/test_url_cleaning.py::TestCleanUrlsUrlAsLinkText::test_clean_urls_url_as_link_text_replaced_with_website PASSED
tests/test_url_cleaning.py::TestCleanUrlsUrlAsLinkText::test_clean_urls_url_as_link_text_with_path PASSED
tests/test_url_cleaning.py::TestCleanUrlsBareUrl::test_clean_urls_bare_url_replaced_with_website PASSED
tests/test_url_cleaning.py::TestCleanUrlsBareUrl::test_clean_urls_bare_url_http PASSED
tests/test_url_cleaning.py::TestCleanUrlsBareUrl::test_clean_urls_bare_url_with_fragment PASSED
tests/test_url_cleaning.py::TestCleanUrlsMultipleUrls::test_clean_urls_multiple_markdown_links PASSED
tests/test_url_cleaning.py::TestCleanUrlsMultipleUrls::test_clean_urls_mixed_markdown_and_bare PASSED
tests/test_url_cleaning.py::TestCleanUrlsMultipleUrls::test_clean_urls_multiple_bare_urls PASSED
tests/test_url_cleaning.py::TestCleanUrlsMultipleUrls::test_clean_urls_multiple_consecutive_bare_urls PASSED
tests/test_url_cleaning.py::TestCleanUrlsIdempotent::test_clean_urls_idempotent_no_urls PASSED
tests/test_url_cleaning.py::TestCleanUrlsIdempotent::test_clean_urls_idempotent_already_processed PASSED
tests/test_url_cleaning.py::TestCleanUrlsIdempotent::test_clean_urls_idempotent_plain_text PASSED
tests/test_url_cleaning.py::TestCleanUrlsTrailingPunctuation::test_clean_urls_bare_url_followed_by_period PASSED
tests/test_url_cleaning.py::TestCleanUrlsTrailingPunctuation::test_clean_urls_bare_url_followed_by_comma PASSED
tests/test_url_cleaning.py::TestCleanUrlsTrailingPunctuation::test_clean_urls_bare_url_at_end_of_sentence PASSED
tests/test_url_cleaning.py::TestCleanUrlsEdgeCases::test_clean_urls_empty_string PASSED
tests/test_url_cleaning.py::TestCleanUrlsEdgeCases::test_clean_urls_whitespace_only PASSED
tests/test_url_cleaning.py::TestCleanUrlsEdgeCases::test_clean_urls_long_link_text PASSED
tests/test_url_cleaning.py::TestCleanUrlsEdgeCases::test_clean_urls_japanese_and_english_mixed_link_text PASSED
tests/test_url_cleaning.py::TestCleanUrlsEdgeCases::test_clean_urls_url_with_japanese_characters PASSED

22 passed in 0.03s
```

### Core text cleaning tests (85 tests - no regressions)

```
tests/test_url_cleaning.py ...................... [ 25%]
tests/test_isbn_cleaning.py .................. [ 47%]
tests/test_parenthetical_cleaning.py ........................ [ 75%]
tests/test_reference_normalization.py ..................... [100%]

85 passed in 0.05s
```

**カバレッジ**: 測定なし（Phase 5 で実施予定）

## 発見した問題/課題

特になし。すべてのテストが期待通りにPASSし、回帰も発生していない。

## GREEN Phase 検証完了

- すべての RED テストが PASS に変更された（11 FAIL → 11 PASS）
- 既存テストに回帰なし（22 URL tests すべて PASS）
- 実装は最小限で、過剰実装なし

## 次フェーズへの引き継ぎ

Phase 3 (US2: 番号表記の自然な読み上げ) で実装するもの:
- `No.X` → 「ナンバーX」 変換
- `Chapter X` → 「第X章」→「だいXしょう」 変換
- 新規パターン定数: `NUMBER_PREFIX_PATTERN`, `CHAPTER_PATTERN`
- 新規関数: `_clean_number_prefix()`, `_clean_chapter()`
- `clean_page_text()` への統合（US1 の後に実行）

注意点:
- US1 の URL 置換処理は完全に独立しており、US2 と干渉しない
- 処理順序: `_clean_urls()` → `_clean_isbn()` → `_clean_number_prefix()` → `_clean_chapter()`
