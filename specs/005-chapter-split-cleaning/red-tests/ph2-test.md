# Phase 2 RED Tests: テキストクリーニングの適用

**Date**: 2026-02-18
**Status**: RED (FAIL確認済み)
**User Story**: US1 - テキストクリーニングの適用

## サマリー

| 項目 | 値 |
|------|-----|
| 作成テスト数 | 9 |
| FAIL数 | 9 |
| PASS数（既存） | 404 |
| テストファイル | tests/test_xml2_pipeline.py |

## FAILテスト一覧

| テストファイル | テストクラス | テストメソッド | 期待動作 |
|--------------|-------------|--------------|----------|
| tests/test_xml2_pipeline.py | TestProcessContentAppliesCleanPageText | test_process_content_calls_clean_page_text | process_content が clean_page_text() を呼び出す |
| tests/test_xml2_pipeline.py | TestProcessContentAppliesCleanPageText | test_process_content_applies_clean_page_text_to_each_item | 全コンテンツアイテムに clean_page_text() が適用される |
| tests/test_xml2_pipeline.py | TestProcessContentAppliesCleanPageText | test_process_content_cleans_text_after_marker_removal | マーカー除去後にクリーニングが行われる |
| tests/test_xml2_pipeline.py | TestProcessContentRemovesUrl | test_url_not_passed_to_tts | https:// URL が TTS テキストから除去される |
| tests/test_xml2_pipeline.py | TestProcessContentRemovesUrl | test_http_url_removed | http:// URL が TTS テキストから除去される |
| tests/test_xml2_pipeline.py | TestProcessContentRemovesParentheticalEnglish | test_parenthetical_english_removed | 括弧内英語 (Reliability) が除去される |
| tests/test_xml2_pipeline.py | TestProcessContentRemovesParentheticalEnglish | test_multiple_parenthetical_english_removed | 複数の括弧内英語が全て除去される |
| tests/test_xml2_pipeline.py | TestProcessContentConvertsNumbersToKana | test_numbers_converted_to_kana | 数字 "123" がカナに変換される |
| tests/test_xml2_pipeline.py | TestProcessContentConvertsNumbersToKana | test_year_number_converted | 年号 "2024" がカナに変換される |

## テスト設計

### T007: TestProcessContentAppliesCleanPageText (3テスト)

`process_content()` 内で `clean_page_text()` が呼び出されることを検証する。
- `unittest.mock.patch` で `src.xml2_pipeline.clean_page_text` をモックし、呼び出し回数を検証
- マーカー除去後に呼び出されることを確認（CHAPTER_MARKER がクリーニング対象テキストに含まれない）

### T008: TestProcessContentRemovesUrl (2テスト)

URL を含むテキストが TTS に渡される前に除去されることを検証する。
- `generate_audio` をモックし、TTS に渡されたテキストを収集
- https:// と http:// の両方のプロトコルをテスト

### T009: TestProcessContentRemovesParentheticalEnglish (2テスト)

括弧内英語が除去されることを検証する。
- 単一の括弧英語: `信頼性 (Reliability)`
- 複数の括弧英語: `可用性 (Availability) と拡張性 (Scalability)`

### T010: TestProcessContentConvertsNumbersToKana (2テスト)

数字がカナに変換されることを検証する。
- 一般的な数字: "123" が生の形で TTS に渡されないこと
- 年号: "2024" が生の形で TTS に渡されないこと

## 実装ヒント

- `process_content()`: マーカー除去後（L196付近）、`text.strip()` の前後で `clean_page_text(text)` を呼び出す
- `clean_page_text()` は `src.text_cleaner` から既に import 済み（L29）
- clean_page_text は heading_marker パラメータを受け取るが、マーカーは既に除去済みなので不要
- 空文字列チェック（L200-201）は clean_page_text() 適用後も維持すること

## make test 出力 (抜粋)

```
FAILED tests/test_xml2_pipeline.py::TestProcessContentAppliesCleanPageText::test_process_content_calls_clean_page_text - AssertionError
FAILED tests/test_xml2_pipeline.py::TestProcessContentAppliesCleanPageText::test_process_content_applies_clean_page_text_to_each_item - AssertionError
FAILED tests/test_xml2_pipeline.py::TestProcessContentAppliesCleanPageText::test_process_content_cleans_text_after_marker_removal - Failed
FAILED tests/test_xml2_pipeline.py::TestProcessContentRemovesUrl::test_url_not_passed_to_tts - AssertionError
FAILED tests/test_xml2_pipeline.py::TestProcessContentRemovesUrl::test_http_url_removed - AssertionError
FAILED tests/test_xml2_pipeline.py::TestProcessContentRemovesParentheticalEnglish::test_parenthetical_english_removed - AssertionError
FAILED tests/test_xml2_pipeline.py::TestProcessContentRemovesParentheticalEnglish::test_multiple_parenthetical_english_removed - AssertionError
FAILED tests/test_xml2_pipeline.py::TestProcessContentConvertsNumbersToKana::test_numbers_converted_to_kana - AssertionError
FAILED tests/test_xml2_pipeline.py::TestProcessContentConvertsNumbersToKana::test_year_number_converted - AssertionError
9 failed, 404 passed in 0.89s
```
