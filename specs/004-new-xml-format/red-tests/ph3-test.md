# Phase 3 RED Tests: User Story 2 - 見出し速度調整

**Date**: 2026-02-18
**Status**: RED (FAIL確認済み)
**User Story**: US2 - 見出し速度調整

## サマリー

| 項目 | 値 |
|------|-----|
| 作成テスト数 | 15 |
| FAIL数 | 15 |
| テストファイル | tests/test_xml2_parser.py |

## FAILテスト一覧

| テストファイル | テストクラス | テストメソッド | 期待動作 |
|--------------|-------------|---------------|----------|
| tests/test_xml2_parser.py | TestFormatHeadingTextChapter | test_format_heading_text_chapter_basic | level=1 で「第1章 はじめに」形式 |
| tests/test_xml2_parser.py | TestFormatHeadingTextChapter | test_format_heading_text_chapter_with_different_number | level=1 で異なる章番号「第3章 実装」 |
| tests/test_xml2_parser.py | TestFormatHeadingTextChapter | test_format_heading_text_chapter_with_english_title | level=1 で英語タイトル「第1章 Introduction」 |
| tests/test_xml2_parser.py | TestFormatHeadingTextSection | test_format_heading_text_section_level2 | level=2 で「第1.1節 概要」形式 |
| tests/test_xml2_parser.py | TestFormatHeadingTextSection | test_format_heading_text_section_level3 | level=3 で「第1.2.1節 詳細」形式 |
| tests/test_xml2_parser.py | TestFormatHeadingTextSection | test_format_heading_text_section_level4 | level=4 で「第1.2.1.1節 補足」形式 |
| tests/test_xml2_parser.py | TestParseBook2XmlHeadingWithChapterMarker | test_level1_heading_has_chapter_marker | level=1 heading に CHAPTER_MARKER 付与 |
| tests/test_xml2_parser.py | TestParseBook2XmlHeadingWithChapterMarker | test_level1_heading_text_starts_with_chapter_marker | level=1 heading テキストが CHAPTER_MARKER で開始 |
| tests/test_xml2_parser.py | TestParseBook2XmlHeadingWithChapterMarker | test_level1_heading_formatted_text | level=1 heading が「第N章」形式 |
| tests/test_xml2_parser.py | TestParseBook2XmlHeadingWithSectionMarker | test_level2_heading_has_section_marker | level=2 heading に SECTION_MARKER 付与 |
| tests/test_xml2_parser.py | TestParseBook2XmlHeadingWithSectionMarker | test_level2_heading_text_starts_with_section_marker | level=2 heading テキストが SECTION_MARKER で開始 |
| tests/test_xml2_parser.py | TestParseBook2XmlHeadingWithSectionMarker | test_level2_heading_formatted_text | level=2 heading が「第N節」形式 |
| tests/test_xml2_parser.py | TestParseBook2XmlHeadingLevel3UsesSectionMarker | test_level3_heading_has_section_marker | level=3 heading に SECTION_MARKER 付与 |
| tests/test_xml2_parser.py | TestParseBook2XmlHeadingLevel3UsesSectionMarker | test_level3_heading_text_starts_with_section_marker | level=3 heading テキストが SECTION_MARKER で開始 |
| tests/test_xml2_parser.py | TestParseBook2XmlHeadingLevel3UsesSectionMarker | test_level3_heading_formatted_as_section | level=3 heading が「第N節」形式（章ではない） |

## 実装ヒント

### format_heading_text() 関数

```python
def format_heading_text(level: int, number: str, title: str) -> str:
    """Format heading for TTS.

    Args:
        level: Heading level (1=chapter, 2+=section)
        number: Heading number ("1", "1.2", etc.)
        title: Heading text

    Returns:
        "第{number}章 {title}" for level=1
        "第{number}節 {title}" for level>=2
    """
    if level == 1:
        return f"第{number}章 {title}"
    else:
        return f"第{number}節 {title}"
```

### parse_book2_xml() の heading 処理拡張

1. `format_heading_text()` を呼び出して見出しテキストを整形
2. level=1 の場合は `CHAPTER_MARKER` を先頭に付与
3. level>=2 の場合は `SECTION_MARKER` を先頭に付与
4. ContentItem.text に `MARKER + formatted_text` を設定

### 見出し番号の抽出

book2.xml の本文 `<heading>` 要素には number 属性がない。
TOC の `<entry>` 要素から番号を取得するか、または見出しの出現順で番号を生成する必要がある。

**オプション**:
1. TOC から見出しタイトル → 番号のマッピングを作成
2. 見出しカウンターを使用して自動採番

## make test 出力 (抜粋)

```
FAILED tests/test_xml2_parser.py::TestFormatHeadingTextChapter::test_format_heading_text_chapter_basic - AssertionError: format_heading_text function should be implemented in src/xml2_parser.py
FAILED tests/test_xml2_parser.py::TestFormatHeadingTextChapter::test_format_heading_text_chapter_with_different_number - AssertionError: format_heading_text function should be implemented
FAILED tests/test_xml2_parser.py::TestFormatHeadingTextChapter::test_format_heading_text_chapter_with_english_title - AssertionError: format_heading_text function should be implemented
FAILED tests/test_xml2_parser.py::TestFormatHeadingTextSection::test_format_heading_text_section_level2 - AssertionError: format_heading_text function should be implemented
FAILED tests/test_xml2_parser.py::TestFormatHeadingTextSection::test_format_heading_text_section_level3 - AssertionError: format_heading_text function should be implemented
FAILED tests/test_xml2_parser.py::TestFormatHeadingTextSection::test_format_heading_text_section_level4 - AssertionError: format_heading_text function should be implemented
FAILED tests/test_xml2_parser.py::TestParseBook2XmlHeadingWithChapterMarker::test_level1_heading_has_chapter_marker - AssertionError: Level 1 heading should contain CHAPTER_MARKER, got text: 'First Chapter'
FAILED tests/test_xml2_parser.py::TestParseBook2XmlHeadingWithChapterMarker::test_level1_heading_text_starts_with_chapter_marker - AssertionError: Level 1 heading text should start with CHAPTER_MARKER, got: 'First Chapter'
FAILED tests/test_xml2_parser.py::TestParseBook2XmlHeadingWithChapterMarker::test_level1_heading_formatted_text - AssertionError: Level 1 heading should contain '第N章', got: 'First Chapter'
FAILED tests/test_xml2_parser.py::TestParseBook2XmlHeadingWithSectionMarker::test_level2_heading_has_section_marker - AssertionError: Level 2 heading should contain SECTION_MARKER, got text: 'Section 1.1'
FAILED tests/test_xml2_parser.py::TestParseBook2XmlHeadingWithSectionMarker::test_level2_heading_text_starts_with_section_marker - AssertionError: Level 2 heading text should start with SECTION_MARKER, got: 'Section 1.1'
FAILED tests/test_xml2_parser.py::TestParseBook2XmlHeadingWithSectionMarker::test_level2_heading_formatted_text - AssertionError: Level 2 heading should contain '第N節', got: 'Section 1.1'
FAILED tests/test_xml2_parser.py::TestParseBook2XmlHeadingLevel3UsesSectionMarker::test_level3_heading_has_section_marker - AssertionError: Level 3 heading should contain SECTION_MARKER, got text: 'Subsection 1.2.1'
FAILED tests/test_xml2_parser.py::TestParseBook2XmlHeadingLevel3UsesSectionMarker::test_level3_heading_text_starts_with_section_marker - AssertionError: Level 3 heading text should start with SECTION_MARKER, got: 'Subsection 1.2.1'
FAILED tests/test_xml2_parser.py::TestParseBook2XmlHeadingLevel3UsesSectionMarker::test_level3_heading_formatted_as_section - AssertionError: Level 3 heading should contain '節', got: 'Subsection 1.2.1'
======================== 15 failed, 356 passed in 0.80s ========================
```

## 補足情報

### 現在の parse_book2_xml() heading 処理

```python
# 現在の実装（src/xml2_parser.py）
if elem.tag == "heading":
    if _should_read_aloud(elem) and elem.text:
        text = elem.text.strip()
        if text:
            level = int(elem.get("level", "1"))
            heading_info = HeadingInfo(
                level=level,
                number="",  # number は空
                title=text,
                read_aloud=True
            )
            content_items.append(ContentItem(
                item_type="heading",
                text=text,  # マーカーなし、整形なし
                heading_info=heading_info
            ))
```

### 必要な変更

1. `format_heading_text()` 関数を追加
2. TOC から見出し番号を抽出するロジックを追加
3. heading 処理で:
   - 見出し番号を取得
   - `format_heading_text()` で整形
   - level に応じたマーカー（CHAPTER_MARKER / SECTION_MARKER）を付与
   - ContentItem.text を `MARKER + formatted_text` に設定
