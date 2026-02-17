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
