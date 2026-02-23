"""Tests for number prefix cleaning functionality.

Phase 3 RED Tests - US2: No.X -> ナンバーX 変換
Tests for _clean_number_prefix function that converts No.X patterns to ナンバーX.
"""

from src.text_cleaner import _clean_number_prefix


class TestCleanNumberPrefixBasic:
    """Test basic No.X -> ナンバーX conversion"""

    def test_clean_number_prefix_basic(self):
        """No.21 を ナンバー21 に変換"""
        input_text = "詳細は No.21 で説明します"
        expected = "詳細は ナンバー21 で説明します"

        result = _clean_number_prefix(input_text)

        assert result == expected, f"No.X はナンバーX に変換されるべき: got '{result}', expected '{expected}'"

    def test_clean_number_prefix_attached_to_word(self):
        """製品No.123 のように単語に続く場合も変換"""
        input_text = "製品No.123を確認"
        expected = "製品ナンバー123を確認"

        result = _clean_number_prefix(input_text)

        assert result == expected

    def test_clean_number_prefix_large_number(self):
        """大きな番号の変換"""
        input_text = "No.1000を参照してください"
        expected = "ナンバー1000を参照してください"

        result = _clean_number_prefix(input_text)

        assert result == expected

    def test_clean_number_prefix_single_digit(self):
        """1桁の番号の変換"""
        input_text = "No.5が最も重要です"
        expected = "ナンバー5が最も重要です"

        result = _clean_number_prefix(input_text)

        assert result == expected


class TestCleanNumberPrefixCaseInsensitive:
    """Test case-insensitive matching: no., NO., No."""

    def test_clean_number_prefix_lowercase(self):
        """小文字 no. も変換"""
        input_text = "no.5を参照"
        expected = "ナンバー5を参照"

        result = _clean_number_prefix(input_text)

        assert result == expected, f"小文字 no. も変換されるべき: got '{result}', expected '{expected}'"

    def test_clean_number_prefix_uppercase(self):
        """大文字 NO. も変換"""
        input_text = "NO.100を確認してください"
        expected = "ナンバー100を確認してください"

        result = _clean_number_prefix(input_text)

        assert result == expected

    def test_clean_number_prefix_mixed_case(self):
        """混合ケース nO. も変換"""
        input_text = "nO.42は特別です"
        expected = "ナンバー42は特別です"

        result = _clean_number_prefix(input_text)

        assert result == expected


class TestCleanNumberPrefixNoNumber:
    """Test No. without number: should not be replaced"""

    def test_clean_number_prefix_no_number_after_dot(self):
        """No. の後に数字がない場合は置換しない"""
        input_text = "No. を参照してください"
        expected = "No. を参照してください"

        result = _clean_number_prefix(input_text)

        assert result == expected, f"No. の後に数字がない場合は変換しないべき: got '{result}', expected '{expected}'"

    def test_clean_number_prefix_no_followed_by_text(self):
        """No. の後にテキストが続く場合は置換しない"""
        input_text = "No.abc は無効です"
        expected = "No.abc は無効です"

        result = _clean_number_prefix(input_text)

        assert result == expected


class TestCleanNumberPrefixMultiple:
    """Test multiple No.X patterns in single text"""

    def test_clean_number_prefix_multiple(self):
        """複数の No.X を同時に変換"""
        input_text = "No.1 と No.2 を比較してください"
        expected = "ナンバー1 と ナンバー2 を比較してください"

        result = _clean_number_prefix(input_text)

        assert result == expected


class TestCleanNumberPrefixEdgeCases:
    """Edge cases for number prefix cleaning"""

    def test_clean_number_prefix_empty_string(self):
        """空文字列の処理"""
        result = _clean_number_prefix("")
        assert result == ""

    def test_clean_number_prefix_no_match(self):
        """マッチしないテキストは変化しない"""
        input_text = "これは通常のテキストです"
        result = _clean_number_prefix(input_text)
        assert result == input_text

    def test_clean_number_prefix_idempotent(self):
        """処理済みテキストを再処理しても変化しない"""
        input_text = "ナンバー21を確認"
        result = _clean_number_prefix(input_text)
        assert result == input_text
