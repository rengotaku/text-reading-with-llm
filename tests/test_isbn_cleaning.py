"""Tests for ISBN cleaning functionality.

Phase 4 RED Tests - US4: ISBN・書籍情報の簡略化
Tests for _clean_isbn function that removes ISBN numbers from text.
"""

from src.text_cleaner import _clean_isbn


class TestCleanIsbnWithHyphens:
    """Test ISBN with hyphens: ISBN978-4-87311-865-8 -> removed"""

    def test_clean_isbn_with_hyphens_basic(self):
        """ハイフン区切りのISBN番号を完全削除"""
        input_text = "ISBN978-4-87311-865-8"
        expected = ""

        result = _clean_isbn(input_text)

        assert result == expected, f"ISBN番号は完全に削除されるべき: got '{result}', expected '{expected}'"

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

        assert result == expected, f"スペース区切りISBNも完全に削除されるべき: got '{result}', expected '{expected}'"

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

        assert result == expected, f"文中のISBNが削除されるべき: got '{result}', expected '{expected}'"

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

        assert result == expected, f"ハイフンなしISBNも削除されるべき: got '{result}', expected '{expected}'"

    def test_clean_isbn_10_digit(self):
        """ISBN-10形式（旧形式）を削除"""
        input_text = "ISBN4-87311-865-X"
        expected = ""

        result = _clean_isbn(input_text)

        assert result == expected, f"ISBN-10形式も削除されるべき: got '{result}', expected '{expected}'"

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

        assert result == expected, f"複数のISBNを正しく削除すべき: got '{result}', expected '{expected}'"

    def test_clean_isbn_preserve_other_numbers(self):
        """ISBN以外の数字は保持"""
        input_text = "ISBN978-4-87311-865-8 価格3000円"
        expected = " 価格3000円"

        result = _clean_isbn(input_text)

        assert result == expected, f"ISBN以外の数字は保持されるべき: got '{result}', expected '{expected}'"

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

        assert result == expected, f"ISBNのないテキストは変化すべきでない: got '{result}', expected '{expected}'"

    def test_clean_isbn_idempotent_already_processed(self):
        """処理済みテキストを再処理しても変化しない"""
        original = "ISBN978-4-87311-865-8の本"
        first_pass = _clean_isbn(original)
        second_pass = _clean_isbn(first_pass)

        assert first_pass == second_pass, (
            f"冪等性が保証されるべき: first pass: '{first_pass}', second pass: '{second_pass}'"
        )

    def test_clean_isbn_empty_string(self):
        """空文字列の処理"""
        result = _clean_isbn("")
        assert result == ""

    def test_clean_isbn_whitespace_only(self):
        """空白のみのテキスト"""
        result = _clean_isbn("   ")
        assert result == "   "


class TestCleanIsbnParentheticalRemoval:
    """Test parenthetical ISBN removal: 括弧ごとISBNを削除 (US3 Phase 4)"""

    def test_parenthetical_isbn_fullwidth_brackets(self):
        """全角括弧内のISBNを括弧ごと削除"""
        input_text = "この本（ISBN: 978-4-7981-8771-6）は良書です"
        expected = "この本は良書です"

        result = _clean_isbn(input_text)

        assert result == expected, f"括弧ごとISBNが削除されるべき: got '{result}', expected '{expected}'"

    def test_parenthetical_isbn_halfwidth_brackets(self):
        """半角括弧内のISBNを括弧ごと削除"""
        input_text = "この本(ISBN: 978-4-7981-8771-6)は良書です"
        expected = "この本は良書です"

        result = _clean_isbn(input_text)

        assert result == expected, f"半角括弧でも括弧ごと削除されるべき: got '{result}', expected '{expected}'"

    def test_parenthetical_isbn_no_space_after_colon(self):
        """コロン後スペースなしでも括弧ごと削除"""
        input_text = "この本（ISBN:978-4-7981-8771-6）は良書です"
        expected = "この本は良書です"

        result = _clean_isbn(input_text)

        assert result == expected

    def test_parenthetical_isbn_10_digit(self):
        """ISBN-10を括弧ごと削除"""
        input_text = "参考書（ISBN: 4-7981-8771-X）を読んでください"
        expected = "参考書を読んでください"

        result = _clean_isbn(input_text)

        assert result == expected

    def test_parenthetical_isbn_without_label(self):
        """ラベルなしでISBNのみ括弧内にある場合も削除"""
        input_text = "この本（978-4-7981-8771-6）は良書です"
        expected = "この本は良書です"

        result = _clean_isbn(input_text)

        assert result == expected


class TestCleanIsbnLabelRemoval:
    """Test ISBN with label removal: ラベル付きISBNを完全削除 (US3 Phase 4)"""

    def test_isbn_with_colon_label(self):
        """ISBN: ラベル付きISBNを完全削除"""
        input_text = "ISBN: 978-4-7981-8771-6"
        expected = ""

        result = _clean_isbn(input_text)

        assert result == expected, f"ISBN:ラベル付きISBNは完全に削除されるべき: got '{result}', expected '{expected}'"

    def test_isbn10_with_label(self):
        """ISBN-10: ラベル付きISBNを完全削除"""
        input_text = "ISBN-10: 4-7981-8771-X"
        expected = ""

        result = _clean_isbn(input_text)

        assert result == expected, f"ISBN-10:ラベルも削除されるべき: got '{result}', expected '{expected}'"

    def test_isbn13_with_label(self):
        """ISBN-13: ラベル付きISBNを完全削除"""
        input_text = "ISBN-13: 978-4-7981-8771-6"
        expected = ""

        result = _clean_isbn(input_text)

        assert result == expected, f"ISBN-13:ラベルも削除されるべき: got '{result}', expected '{expected}'"

    def test_isbn_label_in_sentence(self):
        """文中のISBN:ラベル付きパターンを削除"""
        input_text = "書籍情報はISBN: 978-4-7981-8771-6です"
        expected = "書籍情報はです"

        result = _clean_isbn(input_text)

        assert result == expected

    def test_isbn_label_at_beginning(self):
        """文頭のISBN:ラベル付きパターンを削除"""
        input_text = "ISBN: 978-4-7981-8771-6 この本は良書です"
        expected = "この本は良書です"

        result = _clean_isbn(input_text)

        assert result.strip() == expected, (
            f"文頭のISBNラベル削除後、先頭空白も正規化されるべき: got '{result.strip()}', expected '{expected}'"
        )


class TestCleanIsbnSpaceNormalization:
    """Test space normalization after ISBN removal (US3 Phase 4)"""

    def test_double_space_after_isbn_removal(self):
        """ISBN削除後の二重スペースを正規化"""
        input_text = "この本  は良書です"
        expected = "この本は良書です"

        result = _clean_isbn(input_text)

        assert result == expected, f"二重スペースが正規化されるべき: got '{result}', expected '{expected}'"

    def test_leading_space_after_isbn_removal(self):
        """ISBN削除後の先頭スペースを除去"""
        input_text = "ISBN978-4-7981-8771-6 は良書です"
        expected = "は良書です"

        result = _clean_isbn(input_text)

        assert result.strip() == expected, (
            f"先頭スペースが正規化されるべき: got '{result.strip()}', expected '{expected}'"
        )

    def test_trailing_space_after_isbn_removal(self):
        """ISBN削除後の末尾スペースを除去"""
        input_text = "この本は ISBN978-4-7981-8771-6"
        expected = "この本は"

        result = _clean_isbn(input_text)

        assert result.strip() == expected, (
            f"末尾スペースが正規化されるべき: got '{result.strip()}', expected '{expected}'"
        )

    def test_multiple_spaces_collapse(self):
        """複数スペースを単一スペースに"""
        input_text = "この本   は   良書です"
        expected = "この本 は 良書です"

        result = _clean_isbn(input_text)

        assert result == expected, f"複数スペースが単一に正規化されるべき: got '{result}', expected '{expected}'"

    def test_fullwidth_space_normalization(self):
        """全角スペースも正規化対象"""
        input_text = "この本\u3000\u3000は良書です"
        expected = "この本は良書です"

        result = _clean_isbn(input_text)

        assert result == expected, f"全角スペースも正規化されるべき: got '{result}', expected '{expected}'"
