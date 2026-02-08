"""Tests for ISBN cleaning functionality.

Phase 4 RED Tests - US4: ISBN・書籍情報の簡略化
Tests for _clean_isbn function that removes ISBN numbers from text.
"""

import pytest

from src.text_cleaner import _clean_isbn


class TestCleanIsbnWithHyphens:
    """Test ISBN with hyphens: ISBN978-4-87311-865-8 -> removed"""

    def test_clean_isbn_with_hyphens_basic(self):
        """ハイフン区切りのISBN番号を完全削除"""
        input_text = "ISBN978-4-87311-865-8"
        expected = ""

        result = _clean_isbn(input_text)

        assert result == expected, (
            f"ISBN番号は完全に削除されるべき: "
            f"got '{result}', expected '{expected}'"
        )

    def test_clean_isbn_with_hyphens_13_digit(self):
        """ISBN-13形式（978または979で始まる）を削除"""
        input_text = "ISBN979-1-234-56789-0"
        expected = ""

        result = _clean_isbn(input_text)

        assert result == expected


class TestCleanIsbnWithSpace:
    """Test ISBN with space separator: ISBN 978-4-87311-865-8 -> removed"""

    def test_clean_isbn_with_space_basic(self):
        """スペース区切りのISBN番号を完全削除"""
        input_text = "ISBN 978-4-87311-865-8"
        expected = ""

        result = _clean_isbn(input_text)

        assert result == expected, (
            f"スペース区切りISBNも完全に削除されるべき: "
            f"got '{result}', expected '{expected}'"
        )

    def test_clean_isbn_with_multiple_spaces(self):
        """複数スペースがあっても処理"""
        input_text = "ISBN  978-4-87311-865-8"
        expected = ""

        result = _clean_isbn(input_text)

        assert result == expected


class TestCleanIsbnInSentence:
    """Test ISBN within sentence context"""

    def test_clean_isbn_in_sentence_basic(self):
        """文中のISBNを削除"""
        input_text = "この本はISBN978-4-87311-865-8で購入可能です"
        expected = "この本はで購入可能です"

        result = _clean_isbn(input_text)

        assert result == expected, (
            f"文中のISBNが削除されるべき: "
            f"got '{result}', expected '{expected}'"
        )

    def test_clean_isbn_in_sentence_with_space(self):
        """スペース区切りISBNを文中で削除"""
        input_text = "詳細はISBN 978-4-297-15072-3をご確認ください"
        expected = "詳細はをご確認ください"

        result = _clean_isbn(input_text)

        assert result == expected

    def test_clean_isbn_at_end_of_sentence(self):
        """文末のISBNを削除"""
        input_text = "本書のISBNはISBN978-4-87311-865-8"
        expected = "本書のISBNは"

        result = _clean_isbn(input_text)

        assert result == expected


class TestCleanIsbnEdgeCases:
    """Edge cases and special scenarios"""

    def test_clean_isbn_no_hyphens(self):
        """ハイフンなしISBN-13を削除"""
        input_text = "ISBN9784873118658"
        expected = ""

        result = _clean_isbn(input_text)

        assert result == expected, (
            f"ハイフンなしISBNも削除されるべき: "
            f"got '{result}', expected '{expected}'"
        )

    def test_clean_isbn_10_digit(self):
        """ISBN-10形式（旧形式）を削除"""
        input_text = "ISBN4-87311-865-X"
        expected = ""

        result = _clean_isbn(input_text)

        assert result == expected, (
            f"ISBN-10形式も削除されるべき: "
            f"got '{result}', expected '{expected}'"
        )

    def test_clean_isbn_10_digit_no_hyphens(self):
        """ハイフンなしISBN-10を削除"""
        input_text = "ISBN487311865X"
        expected = ""

        result = _clean_isbn(input_text)

        assert result == expected

    def test_clean_isbn_multiple(self):
        """複数のISBNを削除"""
        input_text = "ISBN978-4-87311-865-8とISBN978-4-87311-866-5"
        expected = "と"

        result = _clean_isbn(input_text)

        assert result == expected, (
            f"複数のISBNを正しく削除すべき: "
            f"got '{result}', expected '{expected}'"
        )

    def test_clean_isbn_preserve_other_numbers(self):
        """ISBN以外の数字は保持"""
        input_text = "ISBN978-4-87311-865-8 価格3000円"
        expected = " 価格3000円"

        result = _clean_isbn(input_text)

        assert result == expected, (
            f"ISBN以外の数字は保持されるべき: "
            f"got '{result}', expected '{expected}'"
        )

    def test_clean_isbn_lowercase(self):
        """小文字isbnも処理"""
        input_text = "isbn978-4-87311-865-8"
        expected = ""

        result = _clean_isbn(input_text)

        assert result == expected

    def test_clean_isbn_mixed_case(self):
        """大文字小文字混在も処理"""
        input_text = "Isbn978-4-87311-865-8"
        expected = ""

        result = _clean_isbn(input_text)

        assert result == expected


class TestCleanIsbnIdempotent:
    """Test idempotency: processing already-cleaned text"""

    def test_clean_isbn_idempotent_no_isbn(self):
        """ISBNのないテキストは変化しない"""
        input_text = "これはISBNを含まないテキストです"
        expected = "これはISBNを含まないテキストです"

        result = _clean_isbn(input_text)

        assert result == expected, (
            f"ISBNのないテキストは変化すべきでない: "
            f"got '{result}', expected '{expected}'"
        )

    def test_clean_isbn_idempotent_already_processed(self):
        """処理済みテキストを再処理しても変化しない"""
        original = "ISBN978-4-87311-865-8の本"
        first_pass = _clean_isbn(original)
        second_pass = _clean_isbn(first_pass)

        assert first_pass == second_pass, (
            f"冪等性が保証されるべき: "
            f"first pass: '{first_pass}', second pass: '{second_pass}'"
        )

    def test_clean_isbn_empty_string(self):
        """空文字列の処理"""
        result = _clean_isbn("")
        assert result == ""

    def test_clean_isbn_whitespace_only(self):
        """空白のみのテキスト"""
        result = _clean_isbn("   ")
        assert result == "   "
