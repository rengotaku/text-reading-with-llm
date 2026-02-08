# Phase 2 RED Tests

## Summary

- **Phase**: Phase 2 - US1 URLの除去・簡略化
- **FAIL テスト数**: 17 test methods (collected 0 due to import error)
- **テストファイル**: tests/test_url_cleaning.py

## FAIL テスト一覧

| テストファイル | テストクラス | テストメソッド | 期待動作 |
|---------------|-------------|---------------|---------|
| tests/test_url_cleaning.py | TestCleanUrlsMarkdownLink | test_clean_urls_markdown_link_basic | `[text](url)` -> `text` |
| tests/test_url_cleaning.py | TestCleanUrlsMarkdownLink | test_clean_urls_markdown_link_with_path | パス付きURLでもリンクテキスト抽出 |
| tests/test_url_cleaning.py | TestCleanUrlsUrlAsLinkText | test_clean_urls_url_as_link_text_complete_removal | `[url](url)` -> 完全削除 |
| tests/test_url_cleaning.py | TestCleanUrlsUrlAsLinkText | test_clean_urls_url_as_link_text_with_path | パス付き`[url](url)` -> 完全削除 |
| tests/test_url_cleaning.py | TestCleanUrlsBareUrl | test_clean_urls_bare_url_complete_removal | 裸URL -> 完全削除 |
| tests/test_url_cleaning.py | TestCleanUrlsBareUrl | test_clean_urls_bare_url_http | HTTP URL -> 完全削除 |
| tests/test_url_cleaning.py | TestCleanUrlsBareUrl | test_clean_urls_bare_url_with_fragment | フラグメント付きURL -> 完全削除 |
| tests/test_url_cleaning.py | TestCleanUrlsMultipleUrls | test_clean_urls_multiple_markdown_links | 複数Markdownリンク処理 |
| tests/test_url_cleaning.py | TestCleanUrlsMultipleUrls | test_clean_urls_mixed_markdown_and_bare | Markdown+裸URL混在処理 |
| tests/test_url_cleaning.py | TestCleanUrlsMultipleUrls | test_clean_urls_multiple_bare_urls | 複数裸URL処理 |
| tests/test_url_cleaning.py | TestCleanUrlsIdempotent | test_clean_urls_idempotent_no_urls | URLなしテキスト不変 |
| tests/test_url_cleaning.py | TestCleanUrlsIdempotent | test_clean_urls_idempotent_already_processed | 処理済みテキスト不変 |
| tests/test_url_cleaning.py | TestCleanUrlsIdempotent | test_clean_urls_idempotent_plain_text | プレーンテキスト不変 |
| tests/test_url_cleaning.py | TestCleanUrlsEdgeCases | test_clean_urls_empty_string | 空文字列処理 |
| tests/test_url_cleaning.py | TestCleanUrlsEdgeCases | test_clean_urls_whitespace_only | 空白のみ処理 |
| tests/test_url_cleaning.py | TestCleanUrlsEdgeCases | test_clean_urls_long_link_text | 長いリンクテキスト処理 |
| tests/test_url_cleaning.py | TestCleanUrlsEdgeCases | test_clean_urls_japanese_and_english_mixed_link_text | 日英混在リンクテキスト |
| tests/test_url_cleaning.py | TestCleanUrlsEdgeCases | test_clean_urls_url_with_japanese_characters | URL内日本語処理 |

## 実装ヒント

1. `src/text_cleaner.py` に `_clean_urls(text: str) -> str` 関数を実装
2. 処理順序:
   - Markdownリンク `[text](url)` 処理 (先に処理)
     - URLがリンクテキストの場合: 完全削除
     - 通常リンクテキスト: テキストのみ残す
   - 裸URL `https?://...` 処理 (後で処理)
     - 完全削除

3. 正規表現パターン例:
   ```python
   # Markdownリンク: [text](url)
   MARKDOWN_LINK_PATTERN = re.compile(r'\[([^\]]*)\]\(https?://[^)]+\)')

   # 裸URL
   BARE_URL_PATTERN = re.compile(r'https?://[^\s\)）」』】\]]+')
   ```

4. URLがリンクテキストかどうかの判定:
   - リンクテキストが `https?://` で始まる場合は URL と判定

5. `clean_page_text()` 内で呼び出し位置:
   - マークダウン処理後、句読点正規化前

## FAIL 出力例

```
============================= test session starts ==============================
platform linux -- Python 3.13.11, pytest-9.0.2
collecting ... collected 0 items / 1 error

==================================== ERRORS ====================================
_________________ ERROR collecting tests/test_url_cleaning.py __________________
ImportError while importing test module '/data/projects/text-reading-with-llm/tests/test_url_cleaning.py'.
tests/test_url_cleaning.py:9: in <module>
    from src.text_cleaner import _clean_urls
E   ImportError: cannot import name '_clean_urls' from 'src.text_cleaner' (/data/projects/text-reading-with-llm/src/text_cleaner.py)
=========================== short test summary info ============================
ERROR tests/test_url_cleaning.py
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.08s ===============================
```

## 次ステップ

phase-executor が以下を実行:
1. T014: RED テスト読み込み
2. T015: URL パターン定数追加
3. T016: `_clean_urls()` 関数実装
4. T017: `make test` PASS (GREEN) 確認
5. T018-T019: 検証と Phase 出力生成
