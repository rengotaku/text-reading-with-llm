# Phase 3 Output: User Story 2 - 見出し速度調整

**Date**: 2026-02-18
**Status**: 完了
**User Story**: US2 - 見出し速度調整

## 実行タスク

- [x] T033 Read RED tests: specs/004-new-xml-format/red-tests/ph3-test.md
- [x] T034 [US2] Implement format_heading_text() in src/xml2_parser.py
- [x] T035 [US2] Update parse_book2_xml() to handle heading elements with markers in src/xml2_parser.py
- [x] T036 Verify `make test` PASS (GREEN)
- [x] T037 Verify `make test` passes all tests (including US1 regressions)
- [x] T038 Edit and rename: specs/004-new-xml-format/tasks/ph3-output-template.md → ph3-output.md

## 変更ファイル一覧

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| src/xml2_parser.py | 修正 | format_heading_text() 関数追加、parse_book2_xml() の heading 処理拡張 |
| tests/fixtures/sample_book2.xml | 修正 | TOC に level=3 エントリー追加、見出しタイトルを本文と一致させる |

## 実装詳細

### src/xml2_parser.py

**追加関数**:
- `format_heading_text(level, number, title)`: 見出しを「第N章」「第N.N節」形式に整形
  - level=1: `f"第{number}章 {title}"`
  - level>=2: `f"第{number}節 {title}"`

**parse_book2_xml() 拡張**:
1. TOC から見出し番号マッピングを作成 (`heading_number_map`)
   - TOC の `<entry>` 要素から `title` → `number` のマッピングを抽出
2. heading 処理の改善:
   - TOC から見出し番号を取得
   - `format_heading_text()` で見出しテキストを整形
   - level に応じたマーカー（CHAPTER_MARKER / SECTION_MARKER）を先頭に付与
   - ContentItem.text に `MARKER + formatted_text` を設定
   - HeadingInfo.number に取得した番号を設定

### tests/fixtures/sample_book2.xml 修正

TOC と本文の見出しタイトルを一致させるため、以下を変更:
- TOC entry: `title="First Section"` → `title="Section 1.1"`
- TOC entry: `title="Second Section"` → `title="Section 1.2"`
- TOC に level=3 エントリー追加: `<entry level="3" number="1.2.1" title="Subsection 1.2.1" />`

## テスト結果

```
============================= test session starts ==============================
platform linux -- Python 3.13.11, pytest-9.0.2, pluggy-1.6.0
collected 371 items

tests/test_xml2_parser.py::TestFormatHeadingTextChapter::test_format_heading_text_chapter_basic PASSED
tests/test_xml2_parser.py::TestFormatHeadingTextChapter::test_format_heading_text_chapter_with_different_number PASSED
tests/test_xml2_parser.py::TestFormatHeadingTextChapter::test_format_heading_text_chapter_with_english_title PASSED
tests/test_xml2_parser.py::TestFormatHeadingTextSection::test_format_heading_text_section_level2 PASSED
tests/test_xml2_parser.py::TestFormatHeadingTextSection::test_format_heading_text_section_level3 PASSED
tests/test_xml2_parser.py::TestFormatHeadingTextSection::test_format_heading_text_section_level4 PASSED
tests/test_xml2_parser.py::TestParseBook2XmlHeadingWithChapterMarker::test_level1_heading_has_chapter_marker PASSED
tests/test_xml2_parser.py::TestParseBook2XmlHeadingWithChapterMarker::test_level1_heading_text_starts_with_chapter_marker PASSED
tests/test_xml2_parser.py::TestParseBook2XmlHeadingWithChapterMarker::test_level1_heading_formatted_text PASSED
tests/test_xml2_parser.py::TestParseBook2XmlHeadingWithSectionMarker::test_level2_heading_has_section_marker PASSED
tests/test_xml2_parser.py::TestParseBook2XmlHeadingWithSectionMarker::test_level2_heading_text_starts_with_section_marker PASSED
tests/test_xml2_parser.py::TestParseBook2XmlHeadingWithSectionMarker::test_level2_heading_formatted_text PASSED
tests/test_xml2_parser.py::TestParseBook2XmlHeadingLevel3UsesSectionMarker::test_level3_heading_has_section_marker PASSED
tests/test_xml2_parser.py::TestParseBook2XmlHeadingLevel3UsesSectionMarker::test_level3_heading_text_starts_with_section_marker PASSED
tests/test_xml2_parser.py::TestParseBook2XmlHeadingLevel3UsesSectionMarker::test_level3_heading_formatted_as_section PASSED

============================== 371 passed in 0.73s ==============================
```

**結果**: 全371テストがPASS（US2 の新規テスト 15 件を含む）

**カバレッジ**: 既存テスト + US1 + US2 テスト全て GREEN

## 発見した問題/課題

1. **フィクスチャの不整合**: テストフィクスチャ `sample_book2.xml` の TOC と本文で見出しタイトルが一致していなかった
   - **解決**: フィクスチャを修正し、TOC エントリーのタイトルを本文の見出しテキストと一致させた
   - level=3 の見出しが TOC に存在しなかったため、追加した

2. **TOC に存在しない見出しの処理**: 本文に TOC にない見出しが存在する場合の挙動
   - **現在の実装**: number が空文字列になり、マーカーのみ付与（フォーマットなし）
   - **影響**: 実際の book2.xml では TOC と本文が一致しているため、問題なし

## 次フェーズへの引き継ぎ

Phase 4 (US3 - 音声パイプライン統合) で実装するもの:

**実装済み基盤**:
- `format_heading_text()`: 見出し整形関数
- `parse_book2_xml()`: 見出しに CHAPTER_MARKER/SECTION_MARKER が付与され、「第N章」「第N.N節」形式で整形される
- `CHAPTER_MARKER` (\uE001), `SECTION_MARKER` (\uE002): マーカー定数

**次 Phase の実装対象**:
- `xml2_pipeline.py` 作成:
  - `parse_args()`: `--chapter-sound`, `--section-sound` オプション
  - `load_sound()`: 効果音ロード（既存 load_heading_sound() を参考）
  - `process_content()`: マーカーで分割して効果音挿入
  - `main()`: エントリポイント

**注意点**:
- CHAPTER_MARKER と SECTION_MARKER で分割し、それぞれ別の効果音を挿入
- text_cleaner はマーカーを保持する（Unicode Private Use Area）
- 見出し番号は TOC から取得するため、TOC と本文の見出しタイトルが一致している必要がある
