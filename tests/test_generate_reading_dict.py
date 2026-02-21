"""Tests for generate_reading_dict.py XML support.

Phase 2 RED Tests - US1: XMLファイルから読み辞書を生成
Phase 3 RED Tests - US2: Markdownファイルの既存動作維持 + エッジケース
Tests for main() XML branch logic in generate_reading_dict.py.

Target functions:
- src/generate_reading_dict.py::main()

Test Fixtures:
- tests/fixtures/dict_test_book.xml
- tests/fixtures/dict_test_empty.xml
- tests/fixtures/dict_test_invalid.xml
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.xml2_parser import ContentItem, HeadingInfo

# Fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"
DICT_TEST_BOOK_XML = FIXTURES_DIR / "dict_test_book.xml"
DICT_TEST_EMPTY_XML = FIXTURES_DIR / "dict_test_empty.xml"
DICT_TEST_INVALID_XML = FIXTURES_DIR / "dict_test_invalid.xml"


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

        with (
            patch("src.generate_reading_dict.parse_book2_xml") as mock_parse_xml,
            patch("src.generate_reading_dict.split_into_pages") as mock_split_pages,
            patch("sys.argv", ["prog", str(DICT_TEST_BOOK_XML)]),
        ):
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

        with (
            patch("src.generate_reading_dict.parse_book2_xml") as mock_parse_xml,
            patch("sys.argv", ["prog", str(md_file)]),
        ):
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
            ContentItem(
                item_type="heading",
                text="第1章、API Design。",
                heading_info=HeadingInfo(level=1, number="1", title="API Design"),
                chapter_number=1,
            ),
            ContentItem(item_type="paragraph", text="REST API design follows HTTP protocol.", chapter_number=1),
            ContentItem(
                item_type="heading",
                text="第2章、Infrastructure。",
                heading_info=HeadingInfo(level=1, number="2", title="Infrastructure"),
                chapter_number=2,
            ),
            ContentItem(item_type="paragraph", text="Docker containers enable deployment.", chapter_number=2),
        ]

        with (
            patch("src.generate_reading_dict.parse_book2_xml", return_value=items),
            patch("src.generate_reading_dict.extract_technical_terms") as mock_extract,
            patch("sys.argv", ["prog", str(DICT_TEST_BOOK_XML)]),
        ):
            mock_extract.side_effect = [
                ["API", "REST", "HTTP"],  # chapter 1 terms
                ["Docker"],  # chapter 2 terms
            ]

            from src.generate_reading_dict import main

            main()

            # extract_technical_terms should be called once per chapter group
            assert mock_extract.call_count == 2, (
                f"extract_technical_terms should be called 2 times (once per chapter), got {mock_extract.call_count}"
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
            ContentItem(item_type="paragraph", text="First paragraph about API.", chapter_number=1),
            ContentItem(item_type="paragraph", text="Second paragraph about REST.", chapter_number=1),
        ]

        with (
            patch("src.generate_reading_dict.parse_book2_xml", return_value=items),
            patch("src.generate_reading_dict.extract_technical_terms") as mock_extract,
            patch("sys.argv", ["prog", str(DICT_TEST_BOOK_XML)]),
        ):
            mock_extract.return_value = ["API", "REST"]

            from src.generate_reading_dict import main

            main()

            # The combined text for chapter 1 should contain both paragraphs
            call_args = mock_extract.call_args[0][0]
            assert "First paragraph about API." in call_args, "Combined text should contain first paragraph"
            assert "Second paragraph about REST." in call_args, "Combined text should contain second paragraph"

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

        with (
            patch("src.generate_reading_dict.parse_book2_xml", return_value=items),
            patch("src.generate_reading_dict.extract_technical_terms") as mock_extract,
            patch("sys.argv", ["prog", str(DICT_TEST_BOOK_XML)]),
        ):
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

        with (
            patch("src.generate_reading_dict.parse_book2_xml", return_value=items),
            patch("src.generate_reading_dict.save_dict") as mock_save,
            patch("sys.argv", ["prog", str(DICT_TEST_BOOK_XML)]),
        ):
            from src.generate_reading_dict import main

            main()

            mock_save.assert_called_once()
            saved_readings = mock_save.call_args[0][0]
            saved_input_path = mock_save.call_args[0][1]

            assert "API" in saved_readings, "Saved dict should contain generated readings"
            assert saved_readings["API"] == "エーピーアイ"
            assert saved_input_path == DICT_TEST_BOOK_XML, "save_dict should receive the XML input path"

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

        with (
            patch("src.generate_reading_dict.parse_book2_xml", return_value=items),
            patch("src.generate_reading_dict.save_dict"),
            patch("src.generate_reading_dict.get_dict_path") as mock_get_path,
            patch("sys.argv", ["prog", str(DICT_TEST_BOOK_XML)]),
        ):
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

        with (
            patch("src.generate_reading_dict.parse_book2_xml", return_value=items),
            patch("src.generate_reading_dict.load_dict", return_value=existing_dict),
            patch("sys.argv", ["prog", str(DICT_TEST_BOOK_XML), "--merge"]),
        ):
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

        with (
            patch("src.generate_reading_dict.parse_book2_xml", return_value=items),
            patch("src.generate_reading_dict.load_dict", return_value=existing_dict),
            patch("sys.argv", ["prog", str(DICT_TEST_BOOK_XML), "--merge"]),
        ):
            from src.generate_reading_dict import main

            main()

            # generate_readings_batch should only receive new terms (not "API")
            call_args = mock_gen_readings.call_args[0][0]
            assert "API" not in call_args, "Existing term 'API' should not be sent to LLM again"
            assert "Docker" in call_args, "New term 'Docker' should be sent to LLM"


# =============================================================================
# Phase 3 RED Tests - US2: Markdownファイルの既存動作維持 + エッジケース
# =============================================================================


class TestMdInputUsesSplitIntoPages:
    """T024: Markdown入力時に既存フロー（split_into_pages）が使われることをテスト"""

    @patch("src.generate_reading_dict.generate_readings_batch")
    @patch("src.generate_reading_dict.extract_technical_terms")
    @patch("src.generate_reading_dict.save_dict")
    @patch("src.generate_reading_dict.load_dict")
    @patch("src.generate_reading_dict.get_dict_path")
    def test_md_input_calls_split_into_pages(
        self,
        mock_get_dict_path,
        mock_load_dict,
        mock_save_dict,
        mock_extract_terms,
        mock_gen_readings,
        tmp_path,
    ):
        """MD入力時にsplit_into_pagesが呼ばれ、ページ単位でextract_technical_termsが適用される"""
        md_file = tmp_path / "test_book.md"
        md_file.write_text(
            "# Chapter 1\nSome API content\n\n---\n\n# Chapter 2\nDocker usage\n",
            encoding="utf-8",
        )

        mock_get_dict_path.return_value = tmp_path / "readings.json"
        mock_load_dict.return_value = {}
        mock_extract_terms.return_value = ["API"]
        mock_gen_readings.return_value = {"API": "エーピーアイ"}

        with (
            patch("src.generate_reading_dict.split_into_pages") as mock_split,
            patch("sys.argv", ["prog", str(md_file)]),
        ):
            # split_into_pages returns Page objects with .text attribute
            page1 = MagicMock()
            page1.text = "Chapter 1 Some API content"
            page2 = MagicMock()
            page2.text = "Chapter 2 Docker usage"
            mock_split.return_value = [page1, page2]

            from src.generate_reading_dict import main

            main()

            mock_split.assert_called_once()
            assert mock_extract_terms.call_count == 2, (
                f"extract_technical_terms should be called once per page (2 pages), got {mock_extract_terms.call_count}"
            )

    @patch("src.generate_reading_dict.generate_readings_batch")
    @patch("src.generate_reading_dict.extract_technical_terms")
    @patch("src.generate_reading_dict.save_dict")
    @patch("src.generate_reading_dict.load_dict")
    @patch("src.generate_reading_dict.get_dict_path")
    def test_md_input_does_not_call_parse_book2_xml_explicit(
        self,
        mock_get_dict_path,
        mock_load_dict,
        mock_save_dict,
        mock_extract_terms,
        mock_gen_readings,
        tmp_path,
    ):
        """MD入力時にparse_book2_xmlが呼ばれないことを明示的に確認"""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\nSome content with API terms\n", encoding="utf-8")

        mock_get_dict_path.return_value = tmp_path / "readings.json"
        mock_load_dict.return_value = {}
        mock_extract_terms.return_value = ["API"]
        mock_gen_readings.return_value = {"API": "エーピーアイ"}

        with (
            patch("src.generate_reading_dict.parse_book2_xml") as mock_parse_xml,
            patch("sys.argv", ["prog", str(md_file)]),
        ):
            from src.generate_reading_dict import main

            main()

            mock_parse_xml.assert_not_called()


class TestUnsupportedExtensionError:
    """T025: 未対応拡張子（.txt 等）でエラー終了することをテスト"""

    def test_txt_extension_exits_with_error(self, tmp_path):
        """拡張子.txtのファイルを指定した場合、sys.exit(1)で終了する"""
        txt_file = tmp_path / "book.txt"
        txt_file.write_text("Some text content", encoding="utf-8")

        with patch("sys.argv", ["prog", str(txt_file)]):
            from src.generate_reading_dict import main

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1, (
                f"Expected exit code 1 for unsupported extension, got {exc_info.value.code}"
            )

    def test_csv_extension_exits_with_error(self, tmp_path):
        """拡張子.csvのファイルを指定した場合もsys.exit(1)で終了する"""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("col1,col2\nval1,val2", encoding="utf-8")

        with patch("sys.argv", ["prog", str(csv_file)]):
            from src.generate_reading_dict import main

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1, (
                f"Expected exit code 1 for unsupported .csv extension, got {exc_info.value.code}"
            )

    def test_unsupported_extension_logs_error_message(self, tmp_path):
        """未対応拡張子の場合、エラーメッセージにサポート対象拡張子が含まれる"""
        txt_file = tmp_path / "book.txt"
        txt_file.write_text("Some content", encoding="utf-8")

        with patch("sys.argv", ["prog", str(txt_file)]), patch("src.generate_reading_dict.logger") as mock_logger:
            from src.generate_reading_dict import main

            with pytest.raises(SystemExit):
                main()

            # logger.error should be called with message about unsupported extension
            mock_logger.error.assert_called()
            error_msg = mock_logger.error.call_args[0][0]
            assert (
                "Unsupported" in error_msg
                or "unsupported" in error_msg.lower()
                or ".xml" in str(mock_logger.error.call_args)
                or ".md" in str(mock_logger.error.call_args)
            ), f"Error message should mention supported extensions, got: {mock_logger.error.call_args}"


class TestEmptyXmlGeneratesEmptyDict:
    """T026: 空XMLファイル（テキストなし）で空辞書が生成されることをテスト"""

    @patch("src.generate_reading_dict.generate_readings_batch")
    @patch("src.generate_reading_dict.save_dict")
    @patch("src.generate_reading_dict.load_dict")
    @patch("src.generate_reading_dict.get_dict_path")
    def test_empty_xml_no_terms_extracted(
        self,
        mock_get_dict_path,
        mock_load_dict,
        mock_save_dict,
        mock_gen_readings,
        tmp_path,
    ):
        """テキストコンテンツのないXMLファイルでは用語が抽出されない"""
        mock_get_dict_path.return_value = tmp_path / "readings.json"
        mock_load_dict.return_value = {}

        with (
            patch("src.generate_reading_dict.parse_book2_xml", return_value=[]),
            patch("src.generate_reading_dict.extract_technical_terms") as mock_extract,
            patch("sys.argv", ["prog", str(DICT_TEST_EMPTY_XML)]),
        ):
            from src.generate_reading_dict import main

            main()

            # extract_technical_terms should not be called when there are no items
            mock_extract.assert_not_called()

    @patch("src.generate_reading_dict.generate_readings_batch")
    @patch("src.generate_reading_dict.save_dict")
    @patch("src.generate_reading_dict.load_dict")
    @patch("src.generate_reading_dict.get_dict_path")
    def test_empty_xml_does_not_call_llm(
        self,
        mock_get_dict_path,
        mock_load_dict,
        mock_save_dict,
        mock_gen_readings,
        tmp_path,
    ):
        """空XMLの場合、LLM呼び出し（generate_readings_batch）が行われない"""
        mock_get_dict_path.return_value = tmp_path / "readings.json"
        mock_load_dict.return_value = {}

        with (
            patch("src.generate_reading_dict.parse_book2_xml", return_value=[]),
            patch("src.generate_reading_dict.extract_technical_terms"),
            patch("sys.argv", ["prog", str(DICT_TEST_EMPTY_XML)]),
        ):
            from src.generate_reading_dict import main

            main()

            mock_gen_readings.assert_not_called()

    @patch("src.generate_reading_dict.generate_readings_batch")
    @patch("src.generate_reading_dict.load_dict")
    @patch("src.generate_reading_dict.get_dict_path")
    def test_empty_xml_normal_exit(
        self,
        mock_get_dict_path,
        mock_load_dict,
        mock_gen_readings,
        tmp_path,
    ):
        """空XMLファイルは正常終了する（sys.exit(1)しない）"""
        mock_get_dict_path.return_value = tmp_path / "readings.json"
        mock_load_dict.return_value = {}

        with (
            patch("src.generate_reading_dict.parse_book2_xml", return_value=[]),
            patch("src.generate_reading_dict.extract_technical_terms"),
            patch("src.generate_reading_dict.save_dict"),
            patch("sys.argv", ["prog", str(DICT_TEST_EMPTY_XML)]),
        ):
            from src.generate_reading_dict import main

            # Should not raise SystemExit
            main()


class TestInvalidXmlErrorExit:
    """T027: 不正なXMLファイルでエラー終了することをテスト"""

    def test_malformed_xml_exits_with_error(self, tmp_path):
        """不正なXMLファイルを指定した場合、sys.exit(1)で終了する"""
        with patch("sys.argv", ["prog", str(DICT_TEST_INVALID_XML)]):
            from src.generate_reading_dict import main

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1, f"Expected exit code 1 for malformed XML, got {exc_info.value.code}"

    def test_malformed_xml_logs_error(self, tmp_path):
        """不正なXMLファイルの場合、エラーメッセージがログに出力される"""
        with (
            patch("sys.argv", ["prog", str(DICT_TEST_INVALID_XML)]),
            patch("src.generate_reading_dict.logger") as mock_logger,
        ):
            from src.generate_reading_dict import main

            with pytest.raises(SystemExit):
                main()

            mock_logger.error.assert_called()

    def test_xml_parse_error_caught_gracefully(self, tmp_path):
        """XMLパースエラーがキャッチされ、未処理例外として伝播しない"""
        import xml.etree.ElementTree as ET

        with (
            patch("src.generate_reading_dict.parse_book2_xml") as mock_parse,
            patch("sys.argv", ["prog", str(DICT_TEST_BOOK_XML)]),
            patch("src.generate_reading_dict.get_dict_path") as mock_get_path,
            patch("src.generate_reading_dict.load_dict", return_value={}),
        ):
            mock_get_path.return_value = tmp_path / "readings.json"
            mock_parse.side_effect = ET.ParseError("invalid XML")

            from src.generate_reading_dict import main

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1, f"Expected exit code 1 for XML parse error, got {exc_info.value.code}"


class TestChapterNumberNoneContentItem:
    """T028: チャプター番号なしのContentItemも用語抽出対象になることをテスト"""

    @patch("src.generate_reading_dict.generate_readings_batch")
    @patch("src.generate_reading_dict.save_dict")
    @patch("src.generate_reading_dict.load_dict")
    @patch("src.generate_reading_dict.get_dict_path")
    def test_none_chapter_items_are_included_in_extraction(
        self,
        mock_get_dict_path,
        mock_load_dict,
        mock_save_dict,
        mock_gen_readings,
        tmp_path,
    ):
        """chapter_number=NoneのContentItemからも用語が抽出される"""
        mock_get_dict_path.return_value = tmp_path / "readings.json"
        mock_load_dict.return_value = {}
        mock_gen_readings.return_value = {"API": "エーピーアイ", "REST": "レスト"}

        items = [
            ContentItem(item_type="paragraph", text="API design patterns", chapter_number=None),
            ContentItem(item_type="paragraph", text="REST architecture", chapter_number=1),
        ]

        with (
            patch("src.generate_reading_dict.parse_book2_xml", return_value=items),
            patch("src.generate_reading_dict.extract_technical_terms") as mock_extract,
            patch("sys.argv", ["prog", str(DICT_TEST_BOOK_XML)]),
        ):
            mock_extract.side_effect = [["API"], ["REST"]]

            from src.generate_reading_dict import main

            main()

            # extract_technical_terms should be called for BOTH groups
            # (None group + chapter 1 group)
            assert mock_extract.call_count == 2, (
                f"extract_technical_terms should be called 2 times "
                f"(once for None group, once for chapter 1), "
                f"got {mock_extract.call_count}"
            )

    @patch("src.generate_reading_dict.generate_readings_batch")
    @patch("src.generate_reading_dict.save_dict")
    @patch("src.generate_reading_dict.load_dict")
    @patch("src.generate_reading_dict.get_dict_path")
    def test_none_chapter_terms_included_in_final_result(
        self,
        mock_get_dict_path,
        mock_load_dict,
        mock_save_dict,
        mock_gen_readings,
        tmp_path,
    ):
        """chapter_number=Noneのアイテムから抽出された用語が最終結果に含まれる"""
        mock_get_dict_path.return_value = tmp_path / "readings.json"
        mock_load_dict.return_value = {}
        mock_gen_readings.return_value = {
            "GraphQL": "グラフキューエル",
            "Docker": "ドッカー",
        }

        items = [
            ContentItem(item_type="paragraph", text="GraphQL is a query language", chapter_number=None),
            ContentItem(item_type="paragraph", text="Docker containers", chapter_number=1),
        ]

        with (
            patch("src.generate_reading_dict.parse_book2_xml", return_value=items),
            patch("src.generate_reading_dict.extract_technical_terms") as mock_extract,
            patch("sys.argv", ["prog", str(DICT_TEST_BOOK_XML)]),
        ):
            mock_extract.side_effect = [["GraphQL"], ["Docker"]]

            from src.generate_reading_dict import main

            main()

            # generate_readings_batch should receive terms from all groups including None
            call_args = mock_gen_readings.call_args[0][0]
            assert "GraphQL" in call_args, "Terms from chapter_number=None items should be included"
            assert "Docker" in call_args, "Terms from numbered chapters should also be included"

    @patch("src.generate_reading_dict.generate_readings_batch")
    @patch("src.generate_reading_dict.save_dict")
    @patch("src.generate_reading_dict.load_dict")
    @patch("src.generate_reading_dict.get_dict_path")
    def test_all_none_chapter_items_grouped_together(
        self,
        mock_get_dict_path,
        mock_load_dict,
        mock_save_dict,
        mock_gen_readings,
        tmp_path,
    ):
        """複数のchapter_number=Noneアイテムが一つのグループとして扱われる"""
        mock_get_dict_path.return_value = tmp_path / "readings.json"
        mock_load_dict.return_value = {}
        mock_gen_readings.return_value = {"API": "エーピーアイ"}

        items = [
            ContentItem(item_type="paragraph", text="First ungrouped item about API", chapter_number=None),
            ContentItem(item_type="paragraph", text="Second ungrouped item about REST", chapter_number=None),
        ]

        with (
            patch("src.generate_reading_dict.parse_book2_xml", return_value=items),
            patch("src.generate_reading_dict.extract_technical_terms") as mock_extract,
            patch("sys.argv", ["prog", str(DICT_TEST_BOOK_XML)]),
        ):
            mock_extract.return_value = ["API", "REST"]

            from src.generate_reading_dict import main

            main()

            # Both None items should be in one group, so extract called once
            assert mock_extract.call_count == 1, (
                f"All chapter_number=None items should be in one group, "
                f"extract_technical_terms should be called once, "
                f"got {mock_extract.call_count}"
            )

            # Combined text should contain both items
            call_text = mock_extract.call_args[0][0]
            assert "First ungrouped item about API" in call_text, "Combined text should contain first None-chapter item"
            assert "Second ungrouped item about REST" in call_text, (
                "Combined text should contain second None-chapter item"
            )


# =============================================================================
# Phase 1 RED Tests - 009-llm-warmup: ウォームアップ関数追加
# =============================================================================


class TestWarmupModel:
    """T003: ウォームアップ関数 _warmup_model() のユニットテスト"""

    @patch("src.generate_reading_dict.ollama_chat")
    @patch("src.generate_reading_dict.logger")
    def test_warmup_model_calls_ollama_chat_with_ping(self, mock_logger, mock_ollama_chat):
        """_warmup_model()が最小限のリクエスト（ping）でollama_chat()を呼び出す"""
        from src.generate_reading_dict import _warmup_model

        test_model = "gpt-oss:20b"
        mock_ollama_chat.return_value = {"message": {"content": "pong"}}

        _warmup_model(test_model)

        # ollama_chat should be called once
        mock_ollama_chat.assert_called_once()

        # Verify call arguments
        call_args = mock_ollama_chat.call_args
        assert call_args[0][0] == test_model, "Model name should be passed to ollama_chat"

        messages = call_args[0][1]
        assert isinstance(messages, list), "Messages should be a list"
        assert len(messages) > 0, "Messages should not be empty"

    @patch("src.generate_reading_dict.ollama_chat")
    @patch("src.generate_reading_dict.logger")
    def test_warmup_model_logs_warming_up_message(self, mock_logger, mock_ollama_chat):
        """_warmup_model()が開始時に "Warming up model: {model}" をログ出力する"""
        from src.generate_reading_dict import _warmup_model

        test_model = "gpt-oss:20b"
        mock_ollama_chat.return_value = {"message": {"content": "pong"}}

        _warmup_model(test_model)

        # Check that logger.info was called with warming up message
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any("Warming up model" in str(call) and test_model in str(call) for call in log_calls), (
            f"Expected 'Warming up model: {test_model}' in logger.info calls, got: {log_calls}"
        )

    @patch("src.generate_reading_dict.ollama_chat")
    @patch("src.generate_reading_dict.logger")
    def test_warmup_model_logs_model_ready_message(self, mock_logger, mock_ollama_chat):
        """_warmup_model()が完了時に "Model ready" をログ出力する"""
        from src.generate_reading_dict import _warmup_model

        test_model = "gpt-oss:20b"
        mock_ollama_chat.return_value = {"message": {"content": "pong"}}

        _warmup_model(test_model)

        # Check that logger.info was called with model ready message
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any("Model ready" in str(call) for call in log_calls), (
            f"Expected 'Model ready' in logger.info calls, got: {log_calls}"
        )

    @patch("src.generate_reading_dict.ollama_chat")
    @patch("src.generate_reading_dict.logger")
    def test_warmup_model_default_timeout(self, mock_logger, mock_ollama_chat):
        """_warmup_model()のデフォルトタイムアウトが300秒であることを確認"""
        from src.generate_reading_dict import _warmup_model

        test_model = "gpt-oss:20b"
        mock_ollama_chat.return_value = {"message": {"content": "pong"}}

        # Call without timeout argument (should use default 300)
        _warmup_model(test_model)

        # Verify ollama_chat was called
        mock_ollama_chat.assert_called_once()

    @patch("src.generate_reading_dict.ollama_chat")
    @patch("src.generate_reading_dict.logger")
    def test_warmup_model_custom_timeout(self, mock_logger, mock_ollama_chat):
        """_warmup_model()にカスタムタイムアウトを渡せることを確認"""
        from src.generate_reading_dict import _warmup_model

        test_model = "gpt-oss:20b"
        custom_timeout = 600
        mock_ollama_chat.return_value = {"message": {"content": "pong"}}

        # Call with custom timeout
        _warmup_model(test_model, timeout=custom_timeout)

        # Verify ollama_chat was called
        mock_ollama_chat.assert_called_once()

    @patch("src.generate_reading_dict.ollama_chat")
    @patch("src.generate_reading_dict.logger")
    def test_warmup_model_handles_request_exception(self, mock_logger, mock_ollama_chat):
        """_warmup_model()がリクエスト例外を適切に処理する"""
        from src.generate_reading_dict import _warmup_model

        test_model = "gpt-oss:20b"
        mock_ollama_chat.side_effect = requests.RequestException("Connection failed")

        # Should raise exception or handle gracefully
        with pytest.raises(requests.RequestException):
            _warmup_model(test_model)
