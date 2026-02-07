"""Tests for XML book parser.

Phase 2 RED Tests - US1: XML ファイルを TTS パイプラインに読み込む
Tests for parse_book_xml() function and related utilities.

Target functions:
- src/xml_parser.py::parse_book_xml()
- src/xml_parser.py::XmlPage dataclass
- src/xml_parser.py::Figure dataclass
- src/xml_parser.py::to_page()
"""

from pathlib import Path

import pytest

from src.xml_parser import Figure, XmlPage, parse_book_xml, to_page
from src.text_cleaner import Page


# Fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_BOOK_XML = FIXTURES_DIR / "sample_book.xml"


class TestParseBookXmlReturnsPages:
    """Test parse_book_xml returns list of XmlPage objects."""

    def test_parse_book_xml_returns_list(self):
        """parse_book_xml は XmlPage のリストを返す"""
        result = parse_book_xml(SAMPLE_BOOK_XML)

        assert isinstance(result, list), (
            f"parse_book_xml should return a list, got {type(result)}"
        )

    def test_parse_book_xml_returns_xmlpage_instances(self):
        """返却リストの各要素が XmlPage インスタンス"""
        result = parse_book_xml(SAMPLE_BOOK_XML)

        assert len(result) > 0, "Sample XML should contain at least one page"
        for page in result:
            assert isinstance(page, XmlPage), (
                f"Each element should be XmlPage, got {type(page)}"
            )

    def test_parse_book_xml_page_count(self):
        """sample_book.xml には 3 ページ含まれる"""
        result = parse_book_xml(SAMPLE_BOOK_XML)

        assert len(result) == 3, (
            f"sample_book.xml should have 3 pages, got {len(result)}"
        )


class TestXmlPageHasNumberAndText:
    """Test XmlPage dataclass has required fields."""

    def test_xmlpage_has_number(self):
        """XmlPage に number フィールドがある"""
        result = parse_book_xml(SAMPLE_BOOK_XML)
        first_page = result[0]

        assert hasattr(first_page, "number"), (
            "XmlPage should have 'number' attribute"
        )
        assert first_page.number == 1, (
            f"First page number should be 1, got {first_page.number}"
        )

    def test_xmlpage_has_content_text(self):
        """XmlPage に content_text フィールドがある"""
        result = parse_book_xml(SAMPLE_BOOK_XML)
        first_page = result[0]

        assert hasattr(first_page, "content_text"), (
            "XmlPage should have 'content_text' attribute"
        )
        assert isinstance(first_page.content_text, str), (
            f"content_text should be str, got {type(first_page.content_text)}"
        )

    def test_xmlpage_has_announcement(self):
        """XmlPage に announcement フィールドがある"""
        result = parse_book_xml(SAMPLE_BOOK_XML)
        first_page = result[0]

        assert hasattr(first_page, "announcement"), (
            "XmlPage should have 'announcement' attribute"
        )
        assert first_page.announcement == "1ページ", (
            f"First page announcement should be '1ページ', got '{first_page.announcement}'"
        )

    def test_xmlpage_has_figures(self):
        """XmlPage に figures フィールドがある"""
        result = parse_book_xml(SAMPLE_BOOK_XML)
        first_page = result[0]

        assert hasattr(first_page, "figures"), (
            "XmlPage should have 'figures' attribute"
        )
        assert isinstance(first_page.figures, list), (
            f"figures should be a list, got {type(first_page.figures)}"
        )

    def test_xmlpage_has_source_file(self):
        """XmlPage に source_file フィールドがある"""
        result = parse_book_xml(SAMPLE_BOOK_XML)
        first_page = result[0]

        assert hasattr(first_page, "source_file"), (
            "XmlPage should have 'source_file' attribute"
        )
        assert first_page.source_file == "page_0001.png", (
            f"First page source_file should be 'page_0001.png', got '{first_page.source_file}'"
        )


class TestExtractParagraphText:
    """Test paragraph text extraction from content."""

    def test_extract_paragraph_text_single(self):
        """単一の paragraph テキストを抽出"""
        result = parse_book_xml(SAMPLE_BOOK_XML)
        first_page = result[0]

        assert "これはテスト用のパラグラフです" in first_page.content_text, (
            f"First paragraph text should be extracted: got '{first_page.content_text}'"
        )

    def test_extract_paragraph_text_multiple(self):
        """複数の paragraph テキストを抽出"""
        result = parse_book_xml(SAMPLE_BOOK_XML)
        first_page = result[0]

        assert "2つ目のパラグラフ" in first_page.content_text, (
            f"Second paragraph text should be extracted: got '{first_page.content_text}'"
        )

    def test_extract_paragraph_preserves_order(self):
        """paragraph の順序が保持される"""
        result = parse_book_xml(SAMPLE_BOOK_XML)
        first_page = result[0]

        first_para_pos = first_page.content_text.find("これはテスト用のパラグラフです")
        second_para_pos = first_page.content_text.find("2つ目のパラグラフ")

        assert first_para_pos < second_para_pos, (
            f"Paragraph order should be preserved: "
            f"first at {first_para_pos}, second at {second_para_pos}"
        )


class TestExtractHeadingText:
    """Test heading text extraction from content."""

    def test_extract_heading_text_level1(self):
        """level=1 の heading テキストを抽出"""
        result = parse_book_xml(SAMPLE_BOOK_XML)
        first_page = result[0]

        assert "テスト見出し" in first_page.content_text, (
            f"Heading text should be extracted: got '{first_page.content_text}'"
        )

    def test_extract_heading_text_chapter(self):
        """章見出しテキストを抽出"""
        result = parse_book_xml(SAMPLE_BOOK_XML)
        second_page = result[1]

        assert "第1章 はじめに" in second_page.content_text, (
            f"Chapter heading should be extracted: got '{second_page.content_text}'"
        )

    def test_heading_order_with_paragraphs(self):
        """heading と paragraph の順序が保持される"""
        result = parse_book_xml(SAMPLE_BOOK_XML)
        first_page = result[0]

        para_pos = first_page.content_text.find("これはテスト用のパラグラフです")
        heading_pos = first_page.content_text.find("テスト見出し")

        assert para_pos < heading_pos, (
            f"First paragraph should come before heading: "
            f"para at {para_pos}, heading at {heading_pos}"
        )


class TestExtractListItems:
    """Test list item extraction from content."""

    def test_extract_list_items(self):
        """list 内の item テキストを抽出"""
        result = parse_book_xml(SAMPLE_BOOK_XML)
        second_page = result[1]

        assert "項目1" in second_page.content_text, (
            f"List item 1 should be extracted: got '{second_page.content_text}'"
        )
        assert "項目2" in second_page.content_text, (
            f"List item 2 should be extracted: got '{second_page.content_text}'"
        )
        assert "項目3" in second_page.content_text, (
            f"List item 3 should be extracted: got '{second_page.content_text}'"
        )

    def test_list_items_preserve_order(self):
        """list item の順序が保持される"""
        result = parse_book_xml(SAMPLE_BOOK_XML)
        second_page = result[1]

        item1_pos = second_page.content_text.find("項目1")
        item2_pos = second_page.content_text.find("項目2")
        item3_pos = second_page.content_text.find("項目3")

        assert item1_pos < item2_pos < item3_pos, (
            f"List items should be in order: "
            f"item1 at {item1_pos}, item2 at {item2_pos}, item3 at {item3_pos}"
        )


class TestExtractPageAnnouncement:
    """Test page announcement extraction."""

    def test_extract_page_announcement_page1(self):
        """1 ページ目のアナウンスを抽出"""
        result = parse_book_xml(SAMPLE_BOOK_XML)
        first_page = result[0]

        assert first_page.announcement == "1ページ", (
            f"Page 1 announcement should be '1ページ', got '{first_page.announcement}'"
        )

    def test_extract_page_announcement_page2(self):
        """2 ページ目のアナウンスを抽出"""
        result = parse_book_xml(SAMPLE_BOOK_XML)
        second_page = result[1]

        assert second_page.announcement == "2ページ", (
            f"Page 2 announcement should be '2ページ', got '{second_page.announcement}'"
        )

    def test_extract_page_announcement_page3(self):
        """3 ページ目のアナウンスを抽出"""
        result = parse_book_xml(SAMPLE_BOOK_XML)
        third_page = result[2]

        assert third_page.announcement == "3ページ", (
            f"Page 3 announcement should be '3ページ', got '{third_page.announcement}'"
        )


class TestToPageConversion:
    """Test XmlPage to Page conversion."""

    def test_to_page_returns_page_instance(self):
        """to_page は Page インスタンスを返す"""
        xml_pages = parse_book_xml(SAMPLE_BOOK_XML)
        first_xml_page = xml_pages[0]

        result = to_page(first_xml_page)

        assert isinstance(result, Page), (
            f"to_page should return Page, got {type(result)}"
        )

    def test_to_page_preserves_number(self):
        """to_page は number を保持する"""
        xml_pages = parse_book_xml(SAMPLE_BOOK_XML)
        first_xml_page = xml_pages[0]

        result = to_page(first_xml_page)

        assert result.number == first_xml_page.number, (
            f"Page number should be preserved: "
            f"expected {first_xml_page.number}, got {result.number}"
        )

    def test_to_page_includes_announcement(self):
        """to_page は announcement をテキストに含める"""
        xml_pages = parse_book_xml(SAMPLE_BOOK_XML)
        first_xml_page = xml_pages[0]

        result = to_page(first_xml_page)

        assert "1ページ" in result.text, (
            f"Page text should include announcement: got '{result.text}'"
        )

    def test_to_page_includes_content_text(self):
        """to_page は content_text をテキストに含める"""
        xml_pages = parse_book_xml(SAMPLE_BOOK_XML)
        first_xml_page = xml_pages[0]

        result = to_page(first_xml_page)

        assert "これはテスト用のパラグラフです" in result.text, (
            f"Page text should include content: got '{result.text}'"
        )

    def test_to_page_announcement_before_content(self):
        """to_page では announcement が content より前に来る"""
        xml_pages = parse_book_xml(SAMPLE_BOOK_XML)
        first_xml_page = xml_pages[0]

        result = to_page(first_xml_page)

        announcement_pos = result.text.find("1ページ")
        content_pos = result.text.find("これはテスト用のパラグラフです")

        assert announcement_pos < content_pos, (
            f"Announcement should come before content: "
            f"announcement at {announcement_pos}, content at {content_pos}"
        )


class TestFigureDataclass:
    """Test Figure dataclass structure."""

    def test_figure_extracted_from_page(self):
        """ページから figure が抽出される"""
        result = parse_book_xml(SAMPLE_BOOK_XML)
        first_page = result[0]

        assert len(first_page.figures) > 0, (
            f"First page should have at least one figure"
        )

    def test_figure_has_file_path(self):
        """Figure に file_path フィールドがある"""
        result = parse_book_xml(SAMPLE_BOOK_XML)
        first_page = result[0]
        first_figure = first_page.figures[0]

        assert hasattr(first_figure, "file_path"), (
            "Figure should have 'file_path' attribute"
        )
        assert first_figure.file_path == "figures/test_figure.png", (
            f"Figure file_path should be 'figures/test_figure.png', "
            f"got '{first_figure.file_path}'"
        )

    def test_figure_has_description(self):
        """Figure に description フィールドがある"""
        result = parse_book_xml(SAMPLE_BOOK_XML)
        first_page = result[0]
        first_figure = first_page.figures[0]

        assert hasattr(first_figure, "description"), (
            "Figure should have 'description' attribute"
        )
        assert first_figure.description == "テスト画像の説明文。", (
            f"Figure description should be 'テスト画像の説明文。', "
            f"got '{first_figure.description}'"
        )

    def test_figure_has_read_aloud(self):
        """Figure に read_aloud フィールドがある"""
        result = parse_book_xml(SAMPLE_BOOK_XML)
        first_page = result[0]
        first_figure = first_page.figures[0]

        assert hasattr(first_figure, "read_aloud"), (
            "Figure should have 'read_aloud' attribute"
        )
        assert first_figure.read_aloud == "optional", (
            f"Figure read_aloud should be 'optional', got '{first_figure.read_aloud}'"
        )


class TestToPageWithFigureDescription:
    """Test to_page includes figure descriptions based on readAloud."""

    def test_to_page_includes_figure_description_when_optional(self):
        """readAloud='optional' の figure description を含める"""
        xml_pages = parse_book_xml(SAMPLE_BOOK_XML)
        first_xml_page = xml_pages[0]  # Has figure with readAloud="optional"

        result = to_page(first_xml_page)

        assert "テスト画像の説明文" in result.text, (
            f"Page text should include figure description when readAloud='optional': "
            f"got '{result.text}'"
        )


class TestParseBookXmlWithPath:
    """Test parse_book_xml accepts different path types."""

    def test_parse_book_xml_with_pathlib_path(self):
        """pathlib.Path を受け付ける"""
        path = Path(SAMPLE_BOOK_XML)
        result = parse_book_xml(path)

        assert len(result) == 3

    def test_parse_book_xml_with_string_path(self):
        """文字列パスを受け付ける"""
        path = str(SAMPLE_BOOK_XML)
        result = parse_book_xml(path)

        assert len(result) == 3


class TestEdgeCases:
    """Edge cases for XML parsing."""

    def test_page_numbers_are_integers(self):
        """ページ番号が整数型"""
        result = parse_book_xml(SAMPLE_BOOK_XML)

        for page in result:
            assert isinstance(page.number, int), (
                f"Page number should be int, got {type(page.number)}"
            )

    def test_page_numbers_are_sequential(self):
        """ページ番号が 1, 2, 3 の順"""
        result = parse_book_xml(SAMPLE_BOOK_XML)

        numbers = [page.number for page in result]
        assert numbers == [1, 2, 3], (
            f"Page numbers should be [1, 2, 3], got {numbers}"
        )

    def test_content_text_is_not_empty(self):
        """content_text が空でない"""
        result = parse_book_xml(SAMPLE_BOOK_XML)

        for page in result:
            assert page.content_text.strip(), (
                f"Page {page.number} content_text should not be empty"
            )
