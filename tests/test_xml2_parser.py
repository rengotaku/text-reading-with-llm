"""Tests for book2.xml parser.

Phase 2 RED Tests - US1: 新XMLフォーマットの基本パース
Tests for parse_book2_xml() function and related data classes.

Target functions:
- src/xml2_parser.py::parse_book2_xml()
- src/xml2_parser.py::ContentItem dataclass
- src/xml2_parser.py::HeadingInfo dataclass

Test Fixture: tests/fixtures/sample_book2.xml
"""

from pathlib import Path

import pytest

from src.xml2_parser import (
    ContentItem,
    HeadingInfo,
    parse_book2_xml,
    CHAPTER_MARKER,
    SECTION_MARKER,
)

# Phase 3: format_heading_text はまだ実装されていない
# RED フェーズではインポートが失敗することを想定
try:
    from src.xml2_parser import format_heading_text
except ImportError:
    format_heading_text = None


# Fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_BOOK2_XML = FIXTURES_DIR / "sample_book2.xml"


# =============================================================================
# Phase 2 RED Tests - US1: 新XMLフォーマットの基本パース
# =============================================================================


class TestParseBook2XmlReturnsList:
    """Test parse_book2_xml returns list of ContentItem objects."""

    def test_parse_book2_xml_returns_list(self):
        """parse_book2_xml は list を返す"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        assert isinstance(result, list), (
            f"parse_book2_xml should return a list, got {type(result)}"
        )

    def test_parse_book2_xml_returns_content_item_instances(self):
        """返却リストの各要素が ContentItem インスタンス"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        assert len(result) > 0, "Sample XML should contain at least one content item"
        for item in result:
            assert isinstance(item, ContentItem), (
                f"Each element should be ContentItem, got {type(item)}"
            )

    def test_parse_book2_xml_with_pathlib_path(self):
        """pathlib.Path を受け付ける"""
        path = Path(SAMPLE_BOOK2_XML)
        result = parse_book2_xml(path)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_parse_book2_xml_with_string_path(self):
        """文字列パスを受け付ける"""
        path = str(SAMPLE_BOOK2_XML)
        result = parse_book2_xml(path)

        assert isinstance(result, list)
        assert len(result) > 0


class TestParseBook2XmlSkipsToc:
    """Test parse_book2_xml skips <toc> section."""

    def test_toc_content_not_in_result(self):
        """<toc> セクションの内容は結果に含まれない"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        # sample_book2.xml の toc には "First Chapter", "First Section" などがある
        # これらは本文の heading にも存在するので、toc 特有の属性で確認
        all_texts = " ".join(item.text for item in result)

        # toc entry のタイトルが ContentItem として抽出されていないことを確認
        # (heading として本文から抽出されるのは OK)
        # toc entry には number 属性があるが、item_type が "toc_entry" のものがないことを確認
        item_types = {item.item_type for item in result}
        assert "toc_entry" not in item_types, (
            f"toc entries should not be extracted, found item_types: {item_types}"
        )

    def test_toc_section_completely_skipped(self):
        """<toc> セクション全体がスキップされる"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        # ContentItem の数を確認（toc がスキップされていれば適切な数になる）
        # sample_book2.xml の本文構成:
        # - heading level=1 x2 (chapter 1, 2)
        # - heading level=2 x2 (section 1.1, 1.2)
        # - heading level=3 x1 (subsection 1.2.1)
        # - paragraph x7 (readAloud=true のみ)
        # - list items x3
        # front-matter のコンテンツは含まれない
        assert len(result) > 0, "Should have content items from main body"


class TestParseBook2XmlSkipsFrontMatter:
    """Test parse_book2_xml skips <front-matter> section."""

    def test_front_matter_paragraph_not_in_result(self):
        """<front-matter> 内の paragraph は結果に含まれない"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        all_texts = " ".join(item.text for item in result)

        # sample_book2.xml の front-matter には "This is front matter text." がある
        assert "front matter text" not in all_texts.lower(), (
            f"front-matter paragraph should be skipped: found in '{all_texts[:200]}...'"
        )

    def test_front_matter_heading_not_in_result(self):
        """<front-matter> 内の heading は結果に含まれない"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        all_texts = " ".join(item.text for item in result)

        # sample_book2.xml の front-matter には "Front Matter Heading" がある
        assert "Front Matter Heading" not in all_texts, (
            f"front-matter heading should be skipped: found in '{all_texts[:200]}...'"
        )


class TestParseBook2XmlExtractsParagraphs:
    """Test parse_book2_xml extracts <paragraph> elements."""

    def test_extract_paragraph_text(self):
        """paragraph テキストを抽出する"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        # paragraph item_type を持つ ContentItem を抽出
        paragraphs = [item for item in result if item.item_type == "paragraph"]

        assert len(paragraphs) > 0, "Should extract at least one paragraph"

    def test_paragraph_text_content(self):
        """paragraph のテキスト内容が正しい"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        all_texts = " ".join(item.text for item in result)

        # sample_book2.xml の本文 paragraph
        assert "first paragraph of chapter 1" in all_texts.lower(), (
            f"First chapter paragraph should be extracted: '{all_texts[:200]}...'"
        )

    def test_paragraph_item_type(self):
        """paragraph の item_type が "paragraph" """
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        paragraphs = [item for item in result if item.item_type == "paragraph"]

        for para in paragraphs:
            assert para.item_type == "paragraph", (
                f"Paragraph item_type should be 'paragraph', got '{para.item_type}'"
            )

    def test_paragraph_has_no_heading_info(self):
        """paragraph には heading_info がない"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        paragraphs = [item for item in result if item.item_type == "paragraph"]

        for para in paragraphs:
            assert para.heading_info is None, (
                f"Paragraph should have no heading_info, got {para.heading_info}"
            )

    def test_multiple_paragraphs_extracted(self):
        """複数の paragraph が抽出される"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        paragraphs = [item for item in result if item.item_type == "paragraph"]

        # sample_book2.xml には readAloud="true" の paragraph が 6 つある
        # (front-matter の 1 つを除く)
        assert len(paragraphs) >= 5, (
            f"Should extract at least 5 paragraphs, got {len(paragraphs)}"
        )


class TestParseBook2XmlRespectsReadAloudFalse:
    """Test parse_book2_xml respects readAloud='false' attribute."""

    def test_skip_paragraph_with_read_aloud_false(self):
        """readAloud='false' の paragraph はスキップする"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        all_texts = " ".join(item.text for item in result)

        # sample_book2.xml には "This paragraph should be skipped." がある
        assert "should be skipped" not in all_texts.lower(), (
            f"Paragraph with readAloud='false' should be skipped: '{all_texts}'"
        )

    def test_include_paragraph_with_read_aloud_true(self):
        """readAloud='true' の paragraph は抽出する"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        all_texts = " ".join(item.text for item in result)

        # sample_book2.xml の readAloud="true" paragraph
        assert "second paragraph" in all_texts.lower(), (
            f"Paragraph with readAloud='true' should be extracted: '{all_texts[:200]}...'"
        )

    def test_default_read_aloud_is_true(self):
        """readAloud 属性がない要素はデフォルトで抽出する"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        # list item には readAloud 属性がないが、抽出される
        list_items = [item for item in result if item.item_type == "list_item"]

        assert len(list_items) > 0, (
            "Elements without readAloud attribute should be extracted (default true)"
        )


class TestParseBook2XmlExtractsListItems:
    """Test parse_book2_xml extracts <list>/<item> elements."""

    def test_extract_list_items(self):
        """list 内の item テキストを抽出する"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        list_items = [item for item in result if item.item_type == "list_item"]

        assert len(list_items) > 0, "Should extract at least one list item"

    def test_list_item_text_content(self):
        """list item のテキスト内容が正しい"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        all_texts = " ".join(item.text for item in result)

        # sample_book2.xml の list items
        assert "List item one" in all_texts, (
            f"List item one should be extracted: '{all_texts[:200]}...'"
        )
        assert "List item two" in all_texts, (
            f"List item two should be extracted: '{all_texts[:200]}...'"
        )
        assert "List item three" in all_texts, (
            f"List item three should be extracted: '{all_texts[:200]}...'"
        )

    def test_list_item_count(self):
        """list item の数が正しい"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        list_items = [item for item in result if item.item_type == "list_item"]

        # sample_book2.xml には 3 つの list items がある
        assert len(list_items) == 3, (
            f"Should extract 3 list items, got {len(list_items)}"
        )

    def test_list_item_type(self):
        """list item の item_type が "list_item" """
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        list_items = [item for item in result if item.item_type == "list_item"]

        for item in list_items:
            assert item.item_type == "list_item", (
                f"List item item_type should be 'list_item', got '{item.item_type}'"
            )

    def test_list_items_preserve_order(self):
        """list item の順序が保持される"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        list_items = [item for item in result if item.item_type == "list_item"]
        list_texts = [item.text for item in list_items]

        assert "List item one" in list_texts[0], (
            f"First list item should be 'List item one', got '{list_texts[0]}'"
        )
        assert "List item two" in list_texts[1], (
            f"Second list item should be 'List item two', got '{list_texts[1]}'"
        )
        assert "List item three" in list_texts[2], (
            f"Third list item should be 'List item three', got '{list_texts[2]}'"
        )


# =============================================================================
# Data Class Tests
# =============================================================================


class TestContentItemDataclass:
    """Test ContentItem dataclass structure."""

    def test_content_item_has_item_type(self):
        """ContentItem に item_type フィールドがある"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)
        first_item = result[0]

        assert hasattr(first_item, "item_type"), (
            "ContentItem should have 'item_type' attribute"
        )
        assert isinstance(first_item.item_type, str), (
            f"item_type should be str, got {type(first_item.item_type)}"
        )

    def test_content_item_has_text(self):
        """ContentItem に text フィールドがある"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)
        first_item = result[0]

        assert hasattr(first_item, "text"), (
            "ContentItem should have 'text' attribute"
        )
        assert isinstance(first_item.text, str), (
            f"text should be str, got {type(first_item.text)}"
        )

    def test_content_item_has_heading_info(self):
        """ContentItem に heading_info フィールドがある"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)
        first_item = result[0]

        assert hasattr(first_item, "heading_info"), (
            "ContentItem should have 'heading_info' attribute"
        )


class TestHeadingInfoDataclass:
    """Test HeadingInfo dataclass structure."""

    def test_heading_info_has_level(self):
        """HeadingInfo に level フィールドがある"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)
        headings = [item for item in result if item.item_type == "heading"]

        assert len(headings) > 0, "Should have at least one heading"
        heading = headings[0]

        assert heading.heading_info is not None, (
            "Heading should have heading_info"
        )
        assert hasattr(heading.heading_info, "level"), (
            "HeadingInfo should have 'level' attribute"
        )
        assert isinstance(heading.heading_info.level, int), (
            f"level should be int, got {type(heading.heading_info.level)}"
        )

    def test_heading_info_has_number(self):
        """HeadingInfo に number フィールドがある"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)
        headings = [item for item in result if item.item_type == "heading"]

        heading = headings[0]

        assert hasattr(heading.heading_info, "number"), (
            "HeadingInfo should have 'number' attribute"
        )
        assert isinstance(heading.heading_info.number, str), (
            f"number should be str, got {type(heading.heading_info.number)}"
        )

    def test_heading_info_has_title(self):
        """HeadingInfo に title フィールドがある"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)
        headings = [item for item in result if item.item_type == "heading"]

        heading = headings[0]

        assert hasattr(heading.heading_info, "title"), (
            "HeadingInfo should have 'title' attribute"
        )
        assert isinstance(heading.heading_info.title, str), (
            f"title should be str, got {type(heading.heading_info.title)}"
        )

    def test_heading_info_has_read_aloud(self):
        """HeadingInfo に read_aloud フィールドがある"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)
        headings = [item for item in result if item.item_type == "heading"]

        heading = headings[0]

        assert hasattr(heading.heading_info, "read_aloud"), (
            "HeadingInfo should have 'read_aloud' attribute"
        )
        assert isinstance(heading.heading_info.read_aloud, bool), (
            f"read_aloud should be bool, got {type(heading.heading_info.read_aloud)}"
        )


# =============================================================================
# Constants Tests
# =============================================================================


class TestMarkerConstants:
    """Test marker constants exist."""

    def test_chapter_marker_defined(self):
        """CHAPTER_MARKER が定義されている"""
        assert CHAPTER_MARKER is not None, "CHAPTER_MARKER should be defined"
        assert isinstance(CHAPTER_MARKER, str), (
            f"CHAPTER_MARKER should be str, got {type(CHAPTER_MARKER)}"
        )
        assert CHAPTER_MARKER == "\uE001", (
            f"CHAPTER_MARKER should be '\\uE001', got {repr(CHAPTER_MARKER)}"
        )

    def test_section_marker_defined(self):
        """SECTION_MARKER が定義されている"""
        assert SECTION_MARKER is not None, "SECTION_MARKER should be defined"
        assert isinstance(SECTION_MARKER, str), (
            f"SECTION_MARKER should be str, got {type(SECTION_MARKER)}"
        )
        assert SECTION_MARKER == "\uE002", (
            f"SECTION_MARKER should be '\\uE002', got {repr(SECTION_MARKER)}"
        )


# =============================================================================
# Edge Cases
# =============================================================================


# =============================================================================
# Phase 3 RED Tests - US2: 見出し速度調整
# =============================================================================


class TestFormatHeadingTextChapter:
    """Test format_heading_text for chapter (level=1)."""

    def test_format_heading_text_chapter_basic(self):
        """level=1 で「第N章、タイトル」形式になる"""
        assert format_heading_text is not None, (
            "format_heading_text function should be implemented in src/xml2_parser.py"
        )
        result = format_heading_text(level=1, number="1", title="はじめに")

        assert result == "第1章、はじめに。", (
            f"Chapter format should be '第1章、はじめに。', got '{result}'"
        )

    def test_format_heading_text_chapter_with_different_number(self):
        """level=1 で異なる章番号を処理"""
        assert format_heading_text is not None, (
            "format_heading_text function should be implemented in src/xml2_parser.py"
        )
        result = format_heading_text(level=1, number="3", title="実装")

        assert result == "第3章、実装。", (
            f"Chapter format should be '第3章、実装。', got '{result}'"
        )

    def test_format_heading_text_chapter_with_english_title(self):
        """level=1 で英語タイトル"""
        assert format_heading_text is not None, (
            "format_heading_text function should be implemented in src/xml2_parser.py"
        )
        result = format_heading_text(level=1, number="1", title="Introduction")

        assert result == "第1章、Introduction。", (
            f"Chapter format should be '第1章、Introduction。', got '{result}'"
        )


class TestFormatHeadingTextSection:
    """Test format_heading_text for section (level>=2)."""

    def test_format_heading_text_section_level2(self):
        """level=2 で「XのY節、タイトル」形式になる"""
        assert format_heading_text is not None, (
            "format_heading_text function should be implemented in src/xml2_parser.py"
        )
        result = format_heading_text(level=2, number="1.1", title="概要")

        assert result == "1の1節、概要。", (
            f"Section format should be '1の1節、概要。', got '{result}'"
        )

    def test_format_heading_text_section_level3(self):
        """level=3 でも「XのY節、タイトル」形式になる"""
        assert format_heading_text is not None, (
            "format_heading_text function should be implemented in src/xml2_parser.py"
        )
        result = format_heading_text(level=3, number="1.2.1", title="詳細")

        assert result == "1の2.1節、詳細。", (
            f"Section format should be '1の2.1節、詳細。', got '{result}'"
        )

    def test_format_heading_text_section_level4(self):
        """level=4 でも「XのY節、タイトル」形式になる"""
        assert format_heading_text is not None, (
            "format_heading_text function should be implemented in src/xml2_parser.py"
        )
        result = format_heading_text(level=4, number="1.2.1.1", title="補足")

        assert result == "1の2.1.1節、補足。", (
            f"Section format should be '1の2.1.1節、補足。', got '{result}'"
        )


class TestParseBook2XmlHeadingWithChapterMarker:
    """Test parse_book2_xml inserts CHAPTER_MARKER for level=1 headings."""

    def test_level1_heading_has_chapter_marker(self):
        """level=1 の heading に CHAPTER_MARKER が付与される"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        # level=1 の heading を取得
        level1_headings = [
            item for item in result
            if item.item_type == "heading" and item.heading_info and item.heading_info.level == 1
        ]

        assert len(level1_headings) >= 1, "Should have at least one level=1 heading"

        for heading in level1_headings:
            assert CHAPTER_MARKER in heading.text, (
                f"Level 1 heading should contain CHAPTER_MARKER, got text: '{heading.text}'"
            )

    def test_level1_heading_text_starts_with_chapter_marker(self):
        """level=1 の heading テキストが CHAPTER_MARKER で始まる"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        level1_headings = [
            item for item in result
            if item.item_type == "heading" and item.heading_info and item.heading_info.level == 1
        ]

        for heading in level1_headings:
            assert heading.text.startswith(CHAPTER_MARKER), (
                f"Level 1 heading text should start with CHAPTER_MARKER, got: '{heading.text}'"
            )

    def test_level1_heading_formatted_text(self):
        """level=1 の heading が「第N章」形式で整形される"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        # "First Chapter" の heading を探す
        first_chapter = None
        for item in result:
            if item.item_type == "heading" and item.heading_info:
                if "First Chapter" in item.text or "第1章" in item.text:
                    first_chapter = item
                    break

        assert first_chapter is not None, "Should find 'First Chapter' heading"
        # CHAPTER_MARKER + "第1章 First Chapter" のような形式
        assert "第" in first_chapter.text and "章" in first_chapter.text, (
            f"Level 1 heading should contain '第N章', got: '{first_chapter.text}'"
        )


class TestParseBook2XmlHeadingWithSectionMarker:
    """Test parse_book2_xml inserts SECTION_MARKER for level>=2 headings."""

    def test_level2_heading_has_section_marker(self):
        """level=2 の heading に SECTION_MARKER が付与される"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        # level=2 の heading を取得
        level2_headings = [
            item for item in result
            if item.item_type == "heading" and item.heading_info and item.heading_info.level == 2
        ]

        assert len(level2_headings) >= 1, "Should have at least one level=2 heading"

        for heading in level2_headings:
            assert SECTION_MARKER in heading.text, (
                f"Level 2 heading should contain SECTION_MARKER, got text: '{heading.text}'"
            )

    def test_level2_heading_text_starts_with_section_marker(self):
        """level=2 の heading テキストが SECTION_MARKER で始まる"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        level2_headings = [
            item for item in result
            if item.item_type == "heading" and item.heading_info and item.heading_info.level == 2
        ]

        for heading in level2_headings:
            assert heading.text.startswith(SECTION_MARKER), (
                f"Level 2 heading text should start with SECTION_MARKER, got: '{heading.text}'"
            )

    def test_level2_heading_formatted_text(self):
        """level=2 の heading が「XのY節、」形式で整形される"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        # "Section 1.1" の heading を探す
        section_heading = None
        for item in result:
            if item.item_type == "heading" and item.heading_info:
                if item.heading_info.level == 2:
                    section_heading = item
                    break

        assert section_heading is not None, "Should find level=2 section heading"
        # SECTION_MARKER + "XのY節、..." のような形式 (e.g., "1の1節、")
        assert "の" in section_heading.text and "節" in section_heading.text, (
            f"Level 2 heading should contain 'XのY節', got: '{section_heading.text}'"
        )

    def test_level2_heading_does_not_have_chapter_marker(self):
        """level=2 の heading に CHAPTER_MARKER が含まれない"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        level2_headings = [
            item for item in result
            if item.item_type == "heading" and item.heading_info and item.heading_info.level == 2
        ]

        for heading in level2_headings:
            assert CHAPTER_MARKER not in heading.text, (
                f"Level 2 heading should NOT contain CHAPTER_MARKER, got: '{heading.text}'"
            )


class TestParseBook2XmlHeadingLevel3UsesSectionMarker:
    """Test parse_book2_xml inserts SECTION_MARKER for level=3 headings."""

    def test_level3_heading_has_section_marker(self):
        """level=3 の heading に SECTION_MARKER が付与される（CHAPTER_MARKER ではない）"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        # level=3 の heading を取得
        level3_headings = [
            item for item in result
            if item.item_type == "heading" and item.heading_info and item.heading_info.level == 3
        ]

        assert len(level3_headings) >= 1, "Should have at least one level=3 heading"

        for heading in level3_headings:
            assert SECTION_MARKER in heading.text, (
                f"Level 3 heading should contain SECTION_MARKER, got text: '{heading.text}'"
            )

    def test_level3_heading_does_not_have_chapter_marker(self):
        """level=3 の heading に CHAPTER_MARKER が含まれない"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        level3_headings = [
            item for item in result
            if item.item_type == "heading" and item.heading_info and item.heading_info.level == 3
        ]

        for heading in level3_headings:
            assert CHAPTER_MARKER not in heading.text, (
                f"Level 3 heading should NOT contain CHAPTER_MARKER, got: '{heading.text}'"
            )

    def test_level3_heading_text_starts_with_section_marker(self):
        """level=3 の heading テキストが SECTION_MARKER で始まる"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        level3_headings = [
            item for item in result
            if item.item_type == "heading" and item.heading_info and item.heading_info.level == 3
        ]

        for heading in level3_headings:
            assert heading.text.startswith(SECTION_MARKER), (
                f"Level 3 heading text should start with SECTION_MARKER, got: '{heading.text}'"
            )

    def test_level3_heading_formatted_as_section(self):
        """level=3 の heading が「第N節」形式で整形される（章ではない）"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        level3_headings = [
            item for item in result
            if item.item_type == "heading" and item.heading_info and item.heading_info.level == 3
        ]

        for heading in level3_headings:
            # "章" が含まれず "節" が含まれる
            assert "節" in heading.text, (
                f"Level 3 heading should contain '節', got: '{heading.text}'"
            )
            # マーカー後のテキストに "章" が含まれないことを確認
            text_after_marker = heading.text.lstrip(SECTION_MARKER)
            # "章" は "第N章" 形式のみをチェック（テキスト自体に「章」があっても OK）
            assert not text_after_marker.startswith("第") or "章" not in text_after_marker.split()[0], (
                f"Level 3 heading should not be formatted as '第N章', got: '{heading.text}'"
            )


# =============================================================================
# Phase 2 Edge Cases (existing tests)
# =============================================================================


class TestEdgeCases:
    """Edge cases for book2.xml parsing."""

    def test_empty_paragraph_skipped(self):
        """空の paragraph はスキップされる"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        paragraphs = [item for item in result if item.item_type == "paragraph"]

        for para in paragraphs:
            assert para.text.strip(), (
                f"Empty paragraphs should be skipped, found: '{para.text}'"
            )

    def test_text_is_not_empty(self):
        """抽出されたテキストは空でない"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        for item in result:
            assert item.text.strip(), (
                f"ContentItem text should not be empty: item_type={item.item_type}"
            )

    def test_document_order_preserved(self):
        """ドキュメント順序が保持される"""
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        all_texts = " ".join(item.text for item in result)

        # First Chapter が Second Chapter より前にある
        first_chapter_pos = all_texts.find("First Chapter")
        second_chapter_pos = all_texts.find("Second Chapter")

        assert first_chapter_pos < second_chapter_pos, (
            f"Document order should be preserved: "
            f"First Chapter at {first_chapter_pos}, Second Chapter at {second_chapter_pos}"
        )


# =============================================================================
# Phase 3 RED Tests - US2: チャプター単位の分割出力
# =============================================================================


# --- T020: test_content_item_has_chapter_number ---


class TestContentItemHasChapterNumber:
    """T020: ContentItem に chapter_number フィールドが存在することを検証する。

    US2 要件: ContentItem に chapter_number (int | None) フィールドを追加
    - デフォルト値は None
    - chapter 内のコンテンツには 1 以上の整数が設定される
    """

    def test_content_item_has_chapter_number_attribute(self):
        """ContentItem に chapter_number 属性が存在する"""
        item = ContentItem(
            item_type="paragraph",
            text="テスト段落",
            heading_info=None,
        )

        assert hasattr(item, "chapter_number"), (
            "ContentItem に 'chapter_number' 属性が存在するべきだが、見つからない"
        )

    def test_content_item_chapter_number_default_is_none(self):
        """ContentItem の chapter_number デフォルト値は None"""
        item = ContentItem(
            item_type="paragraph",
            text="テスト段落",
            heading_info=None,
        )

        assert item.chapter_number is None, (
            f"chapter_number のデフォルト値は None であるべきだが、{item.chapter_number!r} が返された"
        )

    def test_content_item_chapter_number_accepts_int(self):
        """ContentItem の chapter_number に整数を設定できる"""
        item = ContentItem(
            item_type="paragraph",
            text="テスト段落",
            heading_info=None,
            chapter_number=1,
        )

        assert item.chapter_number == 1, (
            f"chapter_number に 1 を設定したが、{item.chapter_number!r} が返された"
        )

    def test_content_item_chapter_number_accepts_larger_int(self):
        """ContentItem の chapter_number に大きな整数を設定できる"""
        item = ContentItem(
            item_type="paragraph",
            text="テスト段落",
            heading_info=None,
            chapter_number=99,
        )

        assert item.chapter_number == 99, (
            f"chapter_number に 99 を設定したが、{item.chapter_number!r} が返された"
        )

    def test_content_item_backward_compatible_without_chapter_number(self):
        """既存の ContentItem 作成コード（chapter_number なし）が引き続き動作する"""
        # 既存コードとの後方互換性を確認
        item = ContentItem(
            item_type="heading",
            text="見出しテキスト",
            heading_info=HeadingInfo(level=1, number="1", title="見出し", read_aloud=True),
        )

        # 既存フィールドが正常に動作する
        assert item.item_type == "heading"
        assert item.text == "見出しテキスト"
        assert item.heading_info is not None
        # chapter_number はデフォルトで None
        assert item.chapter_number is None, (
            "後方互換性: chapter_number を指定しない場合は None であるべき"
        )


# --- T021: test_parse_book2_xml_assigns_chapter_numbers ---


class TestParseBook2XmlAssignsChapterNumbers:
    """T021: parse_book2_xml が chapter 要素内のコンテンツに chapter_number を割り当てることを検証する。

    US2 要件:
    - <chapter number="N"> 内のコンテンツに chapter_number=N を設定
    - chapter 外のコンテンツは chapter_number=None
    - section は所属する chapter の chapter_number を引き継ぐ
    """

    def _create_chapter_xml(self, tmp_path):
        """テスト用の chapter を含む XML ファイルを作成する"""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<book>
    <metadata><title>Chapter Test</title></metadata>
    <toc begin="1" end="3">
        <entry level="1" number="1" title="Introduction" />
        <entry level="1" number="2" title="Main Content" />
        <entry level="1" number="3" title="Conclusion" />
    </toc>
    <chapter number="1" title="Introduction">
        <paragraph readAloud="true">First chapter paragraph one.</paragraph>
        <paragraph readAloud="true">First chapter paragraph two.</paragraph>
    </chapter>
    <chapter number="2" title="Main Content">
        <section number="2.1" title="Details">
            <paragraph readAloud="true">Section content in chapter 2.</paragraph>
        </section>
        <paragraph readAloud="true">Second chapter paragraph.</paragraph>
    </chapter>
    <chapter number="3" title="Conclusion">
        <paragraph readAloud="true">Third chapter paragraph.</paragraph>
    </chapter>
</book>"""
        xml_path = tmp_path / "chapter_test.xml"
        xml_path.write_text(xml_content, encoding="utf-8")
        return xml_path

    def test_chapter_1_items_have_chapter_number_1(self, tmp_path):
        """chapter 1 内のコンテンツの chapter_number が 1 になる"""
        xml_path = self._create_chapter_xml(tmp_path)
        result = parse_book2_xml(xml_path)

        # chapter 1 の heading と paragraph を取得
        ch1_items = [
            item for item in result
            if hasattr(item, "chapter_number") and item.chapter_number == 1
        ]

        assert len(ch1_items) >= 2, (
            f"chapter 1 には少なくとも2つのアイテム（heading + paragraph）が存在するべきだが、"
            f"{len(ch1_items)} 個しか見つからない。"
            f"全アイテムの chapter_number: {[(i.text[:30], getattr(i, 'chapter_number', 'N/A')) for i in result]}"
        )

    def test_chapter_2_items_have_chapter_number_2(self, tmp_path):
        """chapter 2 内のコンテンツの chapter_number が 2 になる"""
        xml_path = self._create_chapter_xml(tmp_path)
        result = parse_book2_xml(xml_path)

        ch2_items = [
            item for item in result
            if hasattr(item, "chapter_number") and item.chapter_number == 2
        ]

        # chapter 2 には heading + section heading + paragraph + section paragraph
        assert len(ch2_items) >= 2, (
            f"chapter 2 には少なくとも2つのアイテムが存在するべきだが、"
            f"{len(ch2_items)} 個しか見つからない。"
            f"全アイテムの chapter_number: {[(i.text[:30], getattr(i, 'chapter_number', 'N/A')) for i in result]}"
        )

    def test_chapter_3_items_have_chapter_number_3(self, tmp_path):
        """chapter 3 内のコンテンツの chapter_number が 3 になる"""
        xml_path = self._create_chapter_xml(tmp_path)
        result = parse_book2_xml(xml_path)

        ch3_items = [
            item for item in result
            if hasattr(item, "chapter_number") and item.chapter_number == 3
        ]

        assert len(ch3_items) >= 1, (
            f"chapter 3 には少なくとも1つのアイテムが存在するべきだが、"
            f"{len(ch3_items)} 個しか見つからない。"
            f"全アイテムの chapter_number: {[(i.text[:30], getattr(i, 'chapter_number', 'N/A')) for i in result]}"
        )

    def test_section_inherits_parent_chapter_number(self, tmp_path):
        """section 内のコンテンツは親 chapter の chapter_number を引き継ぐ"""
        xml_path = self._create_chapter_xml(tmp_path)
        result = parse_book2_xml(xml_path)

        # "Section content in chapter 2" は chapter 2 内の section にある
        section_items = [
            item for item in result
            if "Section content" in item.text
        ]

        assert len(section_items) >= 1, (
            "section 内の paragraph が見つからない"
        )

        for item in section_items:
            assert hasattr(item, "chapter_number"), (
                "section 内のアイテムにも chapter_number が存在するべき"
            )
            assert item.chapter_number == 2, (
                f"section 内のアイテムの chapter_number は 2 であるべきだが、"
                f"{getattr(item, 'chapter_number', 'N/A')} が返された"
            )

    def test_no_chapter_xml_has_none_chapter_number(self):
        """chapter 要素のない XML では chapter_number が None になる"""
        # sample_book2.xml には <chapter> 要素がない（<heading> を使用）
        result = parse_book2_xml(SAMPLE_BOOK2_XML)

        for item in result:
            assert hasattr(item, "chapter_number"), (
                f"ContentItem に chapter_number 属性が存在するべき: {item.text[:30]}"
            )
            assert item.chapter_number is None, (
                f"chapter 要素がない XML では chapter_number は None であるべきだが、"
                f"'{item.text[:30]}' の chapter_number が {item.chapter_number} になっている"
            )

    def test_chapter_heading_itself_has_chapter_number(self, tmp_path):
        """chapter の見出し自体にも chapter_number が設定される"""
        xml_path = self._create_chapter_xml(tmp_path)
        result = parse_book2_xml(xml_path)

        # chapter 1 の heading を探す
        ch1_headings = [
            item for item in result
            if item.item_type == "heading"
            and hasattr(item, "chapter_number")
            and item.chapter_number == 1
        ]

        assert len(ch1_headings) >= 1, (
            f"chapter 1 の heading に chapter_number=1 が設定されるべきだが、見つからない。"
            f"heading items: {[(i.text[:30], getattr(i, 'chapter_number', 'N/A')) for i in result if i.item_type == 'heading']}"
        )
