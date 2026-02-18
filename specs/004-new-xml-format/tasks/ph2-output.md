# Phase 2 Output: User Story 1 - 新XMLフォーマットの基本パース

**Date**: 2026-02-18
**Status**: 完了
**User Story**: US1 - 新XMLフォーマットの基本パース

## 実行タスク

- [x] T016 Read RED tests: specs/004-new-xml-format/red-tests/ph2-test.md
- [x] T017 [P] [US1] Create dataclasses HeadingInfo, ContentItem in src/xml2_parser.py
- [x] T018 [P] [US1] Create constants CHAPTER_MARKER, SECTION_MARKER in src/xml2_parser.py
- [x] T019 [US1] Implement parse_book2_xml() in src/xml2_parser.py
- [x] T020 [US1] Implement _should_read_aloud() helper in src/xml2_parser.py
- [x] T021 Verify `make test` PASS (GREEN)
- [x] T022 Verify `make test` passes all tests (no regressions)
- [x] T023 Edit and rename: specs/004-new-xml-format/tasks/ph2-output-template.md → ph2-output.md

## 変更ファイル一覧

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| src/xml2_parser.py | 新規 | book2.xml パーサー実装（ContentItem, HeadingInfo, parse_book2_xml, _should_read_aloud） |

## 実装詳細

### src/xml2_parser.py

**データクラス**:
- `HeadingInfo`: 見出し情報（level, number, title, read_aloud）
- `ContentItem`: コンテンツ単位（item_type, text, heading_info）

**マーカー定数**:
- `CHAPTER_MARKER = "\uE001"`: Unicode Private Use Area
- `SECTION_MARKER = "\uE002"`: Unicode Private Use Area

**関数**:
- `parse_book2_xml(xml_path)`: book2.xml をパースして ContentItem リストを返却
  - `<toc>`, `<front-matter>`, `<metadata>` セクションをスキップ
  - `readAloud="false"` の要素をスキップ
  - 空テキストの要素をスキップ
  - `<heading>`, `<paragraph>`, `<list>/<item>` を処理
- `_should_read_aloud(elem)`: readAloud 属性チェック（既存実装を参考）

## テスト結果

```
============================= test session starts ==============================
platform linux -- Python 3.13.11, pytest-9.0.2, pluggy-1.6.0
collected 354 items

tests/test_xml2_parser.py::TestParseBook2XmlReturnsList::test_parse_book2_xml_returns_list PASSED
tests/test_xml2_parser.py::TestParseBook2XmlReturnsList::test_parse_book2_xml_returns_content_item_instances PASSED
tests/test_xml2_parser.py::TestParseBook2XmlReturnsList::test_parse_book2_xml_with_pathlib_path PASSED
tests/test_xml2_parser.py::TestParseBook2XmlReturnsList::test_parse_book2_xml_with_string_path PASSED
tests/test_xml2_parser.py::TestParseBook2XmlSkipsToc::test_toc_content_not_in_result PASSED
tests/test_xml2_parser.py::TestParseBook2XmlSkipsToc::test_toc_section_completely_skipped PASSED
tests/test_xml2_parser.py::TestParseBook2XmlSkipsFrontMatter::test_front_matter_paragraph_not_in_result PASSED
tests/test_xml2_parser.py::TestParseBook2XmlSkipsFrontMatter::test_front_matter_heading_not_in_result PASSED
tests/test_xml2_parser.py::TestParseBook2XmlExtractsParagraphs::test_extract_paragraph_text PASSED
tests/test_xml2_parser.py::TestParseBook2XmlExtractsParagraphs::test_paragraph_text_content PASSED
tests/test_xml2_parser.py::TestParseBook2XmlExtractsParagraphs::test_paragraph_item_type PASSED
tests/test_xml2_parser.py::TestParseBook2XmlExtractsParagraphs::test_paragraph_has_no_heading_info PASSED
tests/test_xml2_parser.py::TestParseBook2XmlExtractsParagraphs::test_multiple_paragraphs_extracted PASSED
tests/test_xml2_parser.py::TestParseBook2XmlRespectsReadAloudFalse::test_skip_paragraph_with_read_aloud_false PASSED
tests/test_xml2_parser.py::TestParseBook2XmlRespectsReadAloudFalse::test_include_paragraph_with_read_aloud_true PASSED
tests/test_xml2_parser.py::TestParseBook2XmlRespectsReadAloudFalse::test_default_read_aloud_is_true PASSED
tests/test_xml2_parser.py::TestParseBook2XmlExtractsListItems::test_extract_list_items PASSED
tests/test_xml2_parser.py::TestParseBook2XmlExtractsListItems::test_list_item_text_content PASSED
tests/test_xml2_parser.py::TestParseBook2XmlExtractsListItems::test_list_item_count PASSED
tests/test_xml2_parser.py::TestParseBook2XmlExtractsListItems::test_list_item_type PASSED
tests/test_xml2_parser.py::TestParseBook2XmlExtractsListItems::test_list_items_preserve_order PASSED
tests/test_xml2_parser.py::TestContentItemDataclass::test_content_item_has_item_type PASSED
tests/test_xml2_parser.py::TestContentItemDataclass::test_content_item_has_text PASSED
tests/test_xml2_parser.py::TestContentItemDataclass::test_content_item_has_heading_info PASSED
tests/test_xml2_parser.py::TestHeadingInfoDataclass::test_heading_info_has_level PASSED
tests/test_xml2_parser.py::TestHeadingInfoDataclass::test_heading_info_has_number PASSED
tests/test_xml2_parser.py::TestHeadingInfoDataclass::test_heading_info_has_title PASSED
tests/test_xml2_parser.py::TestHeadingInfoDataclass::test_heading_info_has_read_aloud PASSED
tests/test_xml2_parser.py::TestMarkerConstants::test_chapter_marker_defined PASSED
tests/test_xml2_parser.py::TestMarkerConstants::test_section_marker_defined PASSED
tests/test_xml2_parser.py::TestEdgeCases::test_empty_paragraph_skipped PASSED
tests/test_xml2_parser.py::TestEdgeCases::test_text_is_not_empty PASSED
tests/test_xml2_parser.py::TestEdgeCases::test_document_order_preserved PASSED

============================== 33 passed, 0 failed ==============================
```

**結果**: 全 354 テストが PASS（US1 の新規テスト 33 件を含む）

**カバレッジ**: 既存テスト + 新規テスト全て GREEN

## 発見した問題/課題

特になし。全テストが PASS し、既存テストへの影響もありません。

## 次フェーズへの引き継ぎ

Phase 3 (US2 - 見出し速度調整) で実装するもの:

**実装済み基盤**:
- `HeadingInfo`: 見出し情報データクラス（level, number, title, read_aloud）
- `ContentItem`: コンテンツ単位データクラス（item_type, text, heading_info）
- `CHAPTER_MARKER`, `SECTION_MARKER`: マーカー定数

**次 Phase の実装対象**:
- `format_heading_text()`: 見出し整形関数（「第N章」「第N.N節」形式）
- `parse_book2_xml()` の heading 処理拡張:
  - heading 要素に level に応じたマーカー（CHAPTER_MARKER/SECTION_MARKER）を付与
  - `format_heading_text()` で見出しテキストを整形
  - ContentItem.text にマーカー + 整形済みテキストを設定

**注意点**:
- heading 要素は level 属性で chapter（level=1）と section（level=2+）を判定
- book2.xml の本文 heading 要素には number 属性がない（toc の entry には存在）
- Phase 3 では heading の number 抽出ロジックも追加が必要
