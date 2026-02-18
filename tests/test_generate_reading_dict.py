"""Tests for generate_reading_dict.py XML support.

Phase 2 RED Tests - US1: XMLファイルから読み辞書を生成
Tests for main() XML branch logic in generate_reading_dict.py.

Target functions:
- src/generate_reading_dict.py::main()

Test Fixture: tests/fixtures/dict_test_book.xml
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.xml2_parser import ContentItem, HeadingInfo


# Fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"
DICT_TEST_BOOK_XML = FIXTURES_DIR / "dict_test_book.xml"


# =============================================================================
# Phase 2 RED Tests - US1: XMLファイルから読み辞書を生成
# =============================================================================


class TestXmlInputCallsParseBook2Xml:
    """T010: XMLファイル入力時に parse_book2_xml() が呼ばれることをテスト"""

    @patch("src.generate_reading_dict.generate_readings_batch")
    @patch("src.generate_reading_dict.extract_technical_terms")
    @patch("src.generate_reading_dict.save_dict")
    @patch("src.generate_reading_dict.load_dict")
    @patch("src.generate_reading_dict.get_dict_path")
    def test_xml_input_calls_parse_book2_xml(
        self,
        mock_get_dict_path,
        mock_load_dict,
        mock_save_dict,
        mock_extract_terms,
        mock_gen_readings,
        tmp_path,
    ):
        """XML入力時にparse_book2_xmlが呼ばれ、split_into_pagesは呼ばれない"""
        mock_get_dict_path.return_value = tmp_path / "readings.json"
        mock_load_dict.return_value = {}
        mock_extract_terms.return_value = ["API", "REST"]
        mock_gen_readings.return_value = {"API": "エーピーアイ", "REST": "レスト"}

        with patch("src.generate_reading_dict.parse_book2_xml") as mock_parse_xml, \
             patch("src.generate_reading_dict.split_into_pages") as mock_split_pages, \
             patch("sys.argv", ["prog", str(DICT_TEST_BOOK_XML)]):

            mock_parse_xml.return_value = [
                ContentItem(item_type="paragraph", text="REST API test", chapter_number=1),
            ]

            from src.generate_reading_dict import main
            main()

            mock_parse_xml.assert_called_once_with(DICT_TEST_BOOK_XML)
            mock_split_pages.assert_not_called()

    @patch("src.generate_reading_dict.generate_readings_batch")
    @patch("src.generate_reading_dict.extract_technical_terms")
    @patch("src.generate_reading_dict.save_dict")
    @patch("src.generate_reading_dict.load_dict")
    @patch("src.generate_reading_dict.get_dict_path")
    def test_md_input_does_not_call_parse_book2_xml(
        self,
        mock_get_dict_path,
        mock_load_dict,
        mock_save_dict,
        mock_extract_terms,
        mock_gen_readings,
        tmp_path,
    ):
        """MD入力時にparse_book2_xmlは呼ばれず、split_into_pagesが呼ばれる"""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\nSome API content", encoding="utf-8")

        mock_get_dict_path.return_value = tmp_path / "readings.json"
        mock_load_dict.return_value = {}
        mock_extract_terms.return_value = ["API"]
        mock_gen_readings.return_value = {"API": "エーピーアイ"}

        with patch("src.generate_reading_dict.parse_book2_xml") as mock_parse_xml, \
             patch("sys.argv", ["prog", str(md_file)]):

            from src.generate_reading_dict import main
            main()

            mock_parse_xml.assert_not_called()


class TestXmlChapterGroupingAndTermExtraction:
    """T011: ContentItemのチャプター単位グループ化と用語抽出をテスト"""

    @patch("src.generate_reading_dict.generate_readings_batch")
    @patch("src.generate_reading_dict.save_dict")
    @patch("src.generate_reading_dict.load_dict")
    @patch("src.generate_reading_dict.get_dict_path")
    def test_xml_groups_by_chapter_and_extracts_terms(
        self,
        mock_get_dict_path,
        mock_load_dict,
        mock_save_dict,
        mock_gen_readings,
        tmp_path,
    ):
        """XMLのContentItemがチャプター単位でグループ化され、各グループから用語抽出される"""
        mock_get_dict_path.return_value = tmp_path / "readings.json"
        mock_load_dict.return_value = {}
        mock_gen_readings.return_value = {
            "API": "エーピーアイ",
            "REST": "レスト",
            "Docker": "ドッカー",
        }

        items = [
            ContentItem(item_type="heading", text="第1章、API Design。",
                        heading_info=HeadingInfo(level=1, number="1", title="API Design"),
                        chapter_number=1),
            ContentItem(item_type="paragraph", text="REST API design follows HTTP protocol.",
                        chapter_number=1),
            ContentItem(item_type="heading", text="第2章、Infrastructure。",
                        heading_info=HeadingInfo(level=1, number="2", title="Infrastructure"),
                        chapter_number=2),
            ContentItem(item_type="paragraph", text="Docker containers enable deployment.",
                        chapter_number=2),
        ]

        with patch("src.generate_reading_dict.parse_book2_xml", return_value=items), \
             patch("src.generate_reading_dict.extract_technical_terms") as mock_extract, \
             patch("sys.argv", ["prog", str(DICT_TEST_BOOK_XML)]):

            mock_extract.side_effect = [
                ["API", "REST", "HTTP"],  # chapter 1 terms
                ["Docker"],               # chapter 2 terms
            ]

            from src.generate_reading_dict import main
            main()

            # extract_technical_terms should be called once per chapter group
            assert mock_extract.call_count == 2, (
                f"extract_technical_terms should be called 2 times (once per chapter), "
                f"got {mock_extract.call_count}"
            )

    @patch("src.generate_reading_dict.generate_readings_batch")
    @patch("src.generate_reading_dict.save_dict")
    @patch("src.generate_reading_dict.load_dict")
    @patch("src.generate_reading_dict.get_dict_path")
    def test_xml_combined_text_per_chapter(
        self,
        mock_get_dict_path,
        mock_load_dict,
        mock_save_dict,
        mock_gen_readings,
        tmp_path,
    ):
        """同一チャプターのContentItemのテキストが結合されてextract_technical_termsに渡される"""
        mock_get_dict_path.return_value = tmp_path / "readings.json"
        mock_load_dict.return_value = {}
        mock_gen_readings.return_value = {"API": "エーピーアイ"}

        items = [
            ContentItem(item_type="paragraph", text="First paragraph about API.",
                        chapter_number=1),
            ContentItem(item_type="paragraph", text="Second paragraph about REST.",
                        chapter_number=1),
        ]

        with patch("src.generate_reading_dict.parse_book2_xml", return_value=items), \
             patch("src.generate_reading_dict.extract_technical_terms") as mock_extract, \
             patch("sys.argv", ["prog", str(DICT_TEST_BOOK_XML)]):

            mock_extract.return_value = ["API", "REST"]

            from src.generate_reading_dict import main
            main()

            # The combined text for chapter 1 should contain both paragraphs
            call_args = mock_extract.call_args[0][0]
            assert "First paragraph about API." in call_args, (
                "Combined text should contain first paragraph"
            )
            assert "Second paragraph about REST." in call_args, (
                "Combined text should contain second paragraph"
            )

    @patch("src.generate_reading_dict.generate_readings_batch")
    @patch("src.generate_reading_dict.save_dict")
    @patch("src.generate_reading_dict.load_dict")
    @patch("src.generate_reading_dict.get_dict_path")
    def test_xml_all_terms_collected_across_chapters(
        self,
        mock_get_dict_path,
        mock_load_dict,
        mock_save_dict,
        mock_gen_readings,
        tmp_path,
    ):
        """複数チャプターから抽出された用語が全て収集される"""
        mock_get_dict_path.return_value = tmp_path / "readings.json"
        mock_load_dict.return_value = {}
        mock_gen_readings.return_value = {
            "API": "エーピーアイ",
            "Docker": "ドッカー",
        }

        items = [
            ContentItem(item_type="paragraph", text="API text", chapter_number=1),
            ContentItem(item_type="paragraph", text="Docker text", chapter_number=2),
        ]

        with patch("src.generate_reading_dict.parse_book2_xml", return_value=items), \
             patch("src.generate_reading_dict.extract_technical_terms") as mock_extract, \
             patch("sys.argv", ["prog", str(DICT_TEST_BOOK_XML)]):

            mock_extract.side_effect = [["API"], ["Docker"]]

            from src.generate_reading_dict import main
            main()

            # generate_readings_batch should receive all terms from all chapters
            call_args = mock_gen_readings.call_args[0][0]
            assert "API" in call_args, "All terms should include API from chapter 1"
            assert "Docker" in call_args, "All terms should include Docker from chapter 2"


class TestXmlDictSavePath:
    """T012: XML入力で辞書ファイルが正しいパスに保存されることをテスト"""

    @patch("src.generate_reading_dict.generate_readings_batch")
    @patch("src.generate_reading_dict.extract_technical_terms")
    @patch("src.generate_reading_dict.load_dict")
    @patch("src.generate_reading_dict.get_dict_path")
    def test_xml_dict_saved_via_save_dict(
        self,
        mock_get_dict_path,
        mock_load_dict,
        mock_extract_terms,
        mock_gen_readings,
        tmp_path,
    ):
        """XML入力で生成された辞書がsave_dictを通じて保存される"""
        dict_path = tmp_path / "readings.json"
        mock_get_dict_path.return_value = dict_path
        mock_load_dict.return_value = {}
        mock_extract_terms.return_value = ["API"]
        mock_gen_readings.return_value = {"API": "エーピーアイ"}

        items = [
            ContentItem(item_type="paragraph", text="API text", chapter_number=1),
        ]

        with patch("src.generate_reading_dict.parse_book2_xml", return_value=items), \
             patch("src.generate_reading_dict.save_dict") as mock_save, \
             patch("sys.argv", ["prog", str(DICT_TEST_BOOK_XML)]):

            from src.generate_reading_dict import main
            main()

            mock_save.assert_called_once()
            saved_readings = mock_save.call_args[0][0]
            saved_input_path = mock_save.call_args[0][1]

            assert "API" in saved_readings, "Saved dict should contain generated readings"
            assert saved_readings["API"] == "エーピーアイ"
            assert saved_input_path == DICT_TEST_BOOK_XML, (
                "save_dict should receive the XML input path"
            )

    @patch("src.generate_reading_dict.generate_readings_batch")
    @patch("src.generate_reading_dict.extract_technical_terms")
    @patch("src.generate_reading_dict.load_dict")
    def test_xml_get_dict_path_called_with_xml_input(
        self,
        mock_load_dict,
        mock_extract_terms,
        mock_gen_readings,
        tmp_path,
    ):
        """get_dict_pathがXML入力パスで呼ばれること"""
        mock_load_dict.return_value = {}
        mock_extract_terms.return_value = ["API"]
        mock_gen_readings.return_value = {"API": "エーピーアイ"}

        items = [
            ContentItem(item_type="paragraph", text="API text", chapter_number=1),
        ]

        with patch("src.generate_reading_dict.parse_book2_xml", return_value=items), \
             patch("src.generate_reading_dict.save_dict"), \
             patch("src.generate_reading_dict.get_dict_path") as mock_get_path, \
             patch("sys.argv", ["prog", str(DICT_TEST_BOOK_XML)]):

            mock_get_path.return_value = tmp_path / "readings.json"

            from src.generate_reading_dict import main
            main()

            mock_get_path.assert_called_once_with(DICT_TEST_BOOK_XML)


class TestXmlMergeOption:
    """T013: --mergeオプションがXML入力で動作することをテスト"""

    @patch("src.generate_reading_dict.generate_readings_batch")
    @patch("src.generate_reading_dict.extract_technical_terms")
    @patch("src.generate_reading_dict.save_dict")
    @patch("src.generate_reading_dict.get_dict_path")
    def test_xml_merge_combines_existing_and_new(
        self,
        mock_get_dict_path,
        mock_save_dict,
        mock_extract_terms,
        mock_gen_readings,
        tmp_path,
    ):
        """--mergeオプション指定時、既存辞書と新規エントリが統合される"""
        dict_path = tmp_path / "readings.json"
        mock_get_dict_path.return_value = dict_path
        mock_extract_terms.return_value = ["API", "Docker"]
        mock_gen_readings.return_value = {"Docker": "ドッカー"}

        existing_dict = {"API": "エーピーアイ"}

        items = [
            ContentItem(item_type="paragraph", text="API and Docker text", chapter_number=1),
        ]

        with patch("src.generate_reading_dict.parse_book2_xml", return_value=items), \
             patch("src.generate_reading_dict.load_dict", return_value=existing_dict), \
             patch("sys.argv", ["prog", str(DICT_TEST_BOOK_XML), "--merge"]):

            from src.generate_reading_dict import main
            main()

            # save_dict should be called with merged dict
            mock_save_dict.assert_called_once()
            saved = mock_save_dict.call_args[0][0]
            assert "API" in saved, "Merged dict should contain existing entry 'API'"
            assert saved["API"] == "エーピーアイ"
            assert "Docker" in saved, "Merged dict should contain new entry 'Docker'"
            assert saved["Docker"] == "ドッカー"

    @patch("src.generate_reading_dict.generate_readings_batch")
    @patch("src.generate_reading_dict.extract_technical_terms")
    @patch("src.generate_reading_dict.save_dict")
    @patch("src.generate_reading_dict.get_dict_path")
    def test_xml_merge_skips_existing_terms(
        self,
        mock_get_dict_path,
        mock_save_dict,
        mock_extract_terms,
        mock_gen_readings,
        tmp_path,
    ):
        """--mergeで既存辞書にある用語はLLMに再送信されない"""
        dict_path = tmp_path / "readings.json"
        mock_get_dict_path.return_value = dict_path
        mock_extract_terms.return_value = ["API", "Docker"]
        mock_gen_readings.return_value = {"Docker": "ドッカー"}

        existing_dict = {"API": "エーピーアイ"}

        items = [
            ContentItem(item_type="paragraph", text="API and Docker", chapter_number=1),
        ]

        with patch("src.generate_reading_dict.parse_book2_xml", return_value=items), \
             patch("src.generate_reading_dict.load_dict", return_value=existing_dict), \
             patch("sys.argv", ["prog", str(DICT_TEST_BOOK_XML), "--merge"]):

            from src.generate_reading_dict import main
            main()

            # generate_readings_batch should only receive new terms (not "API")
            call_args = mock_gen_readings.call_args[0][0]
            assert "API" not in call_args, (
                "Existing term 'API' should not be sent to LLM again"
            )
            assert "Docker" in call_args, (
                "New term 'Docker' should be sent to LLM"
            )
