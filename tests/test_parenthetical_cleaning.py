"""Tests for parenthetical English term cleaning.

Phase 5 RED Tests - US5: 括弧付き用語の重複読み防止
Tests for _clean_parenthetical_english function that removes English terms in parentheses.
"""

import pytest

from src.text_cleaner import _clean_parenthetical_english


class TestCleanParentheticalFullWidth:
    """Test full-width parentheses with English: トイル（Toil） -> トイル"""

    def test_clean_parenthetical_english_full_width_basic(self):
        """全角括弧内の英語を削除"""
        input_text = "トイル（Toil）について"
        expected = "トイルについて"

        result = _clean_parenthetical_english(input_text)

        assert result == expected, (
            f"全角括弧内の英語表記は削除されるべき: "
            f"got '{result}', expected '{expected}'"
        )

    def test_clean_parenthetical_english_full_width_multi_word(self):
        """複数単語の英語を削除"""
        input_text = "SRE（Site Reliability Engineering）に関する"
        expected = "SREに関する"

        result = _clean_parenthetical_english(input_text)

        assert result == expected

    def test_clean_parenthetical_english_full_width_with_space(self):
        """括弧前後にスペースがある場合"""
        input_text = "可観測性 （Observability） について"
        expected = "可観測性  について"

        result = _clean_parenthetical_english(input_text)

        assert result == expected


class TestCleanParentheticalHalfWidth:
    """Test half-width parentheses with English: トイル(Toil) -> トイル"""

    def test_clean_parenthetical_english_half_width_basic(self):
        """半角括弧内の英語を削除"""
        input_text = "トイル(Toil)について"
        expected = "トイルについて"

        result = _clean_parenthetical_english(input_text)

        assert result == expected, (
            f"半角括弧内の英語表記は削除されるべき: "
            f"got '{result}', expected '{expected}'"
        )

    def test_clean_parenthetical_english_half_width_multi_word(self):
        """半角括弧内の複数単語英語を削除"""
        input_text = "API(Application Programming Interface)とは"
        expected = "APIとは"

        result = _clean_parenthetical_english(input_text)

        assert result == expected

    def test_clean_parenthetical_english_half_width_with_hyphen(self):
        """ハイフン付き英語を削除"""
        input_text = "ゼロトラスト(Zero-Trust)モデル"
        expected = "ゼロトラストモデル"

        result = _clean_parenthetical_english(input_text)

        assert result == expected


class TestCleanParentheticalPreserve:
    """Test preservation of Japanese content in parentheses"""

    def test_clean_parenthetical_preserve_japanese(self):
        """括弧内が日本語の場合は保持"""
        input_text = "SRE（サイト信頼性エンジニアリング）の役割"
        expected = "SRE（サイト信頼性エンジニアリング）の役割"

        result = _clean_parenthetical_english(input_text)

        assert result == expected, (
            f"括弧内が日本語の場合は保持されるべき: "
            f"got '{result}', expected '{expected}'"
        )

    def test_clean_parenthetical_preserve_hiragana(self):
        """ひらがなのみの括弧内容は保持"""
        input_text = "例えば（たとえば）のように"
        expected = "例えば（たとえば）のように"

        result = _clean_parenthetical_english(input_text)

        assert result == expected

    def test_clean_parenthetical_preserve_katakana(self):
        """カタカナのみの括弧内容は保持"""
        input_text = "API（エーピーアイ）と呼ばれる"
        expected = "API（エーピーアイ）と呼ばれる"

        result = _clean_parenthetical_english(input_text)

        assert result == expected

    def test_clean_parenthetical_preserve_mixed_japanese_english(self):
        """日本語と英語が混在する場合は保持"""
        input_text = "システム（System 管理）の設計"
        expected = "システム（System 管理）の設計"

        result = _clean_parenthetical_english(input_text)

        assert result == expected


class TestCleanParentheticalAlphabetTerm:
    """Test alphabet term with English explanation removal"""

    def test_clean_parenthetical_alphabet_term_basic(self):
        """アルファベット用語後の括弧付き英語を削除"""
        input_text = "SLI（Service Level Indicator）を測定"
        expected = "SLIを測定"

        result = _clean_parenthetical_english(input_text)

        assert result == expected, (
            f"アルファベット用語の括弧付き英語も削除されるべき: "
            f"got '{result}', expected '{expected}'"
        )

    def test_clean_parenthetical_alphabet_term_lowercase(self):
        """小文字アルファベット用語の処理"""
        input_text = "npm（Node Package Manager）を使用"
        expected = "npmを使用"

        result = _clean_parenthetical_english(input_text)

        assert result == expected

    def test_clean_parenthetical_alphabet_with_numbers(self):
        """数字を含むアルファベット用語"""
        input_text = "OAuth2（Open Authorization 2.0）の認証"
        expected = "OAuth2の認証"

        result = _clean_parenthetical_english(input_text)

        assert result == expected


class TestCleanParentheticalEdgeCases:
    """Edge cases and special scenarios"""

    def test_clean_parenthetical_mixed_content(self):
        """英語のみ削除、日本語は保持の混在"""
        input_text = "API（Application Programming Interface）とSRE（サイト信頼性）"
        expected = "APIとSRE（サイト信頼性）"

        result = _clean_parenthetical_english(input_text)

        assert result == expected, (
            f"英語括弧のみ削除、日本語括弧は保持: "
            f"got '{result}', expected '{expected}'"
        )

    def test_clean_parenthetical_numbers_with_japanese(self):
        """数字+日本語の括弧内容は保持"""
        input_text = "Chapter1（第1章）を読む"
        expected = "Chapter1（第1章）を読む"

        result = _clean_parenthetical_english(input_text)

        assert result == expected, (
            f"数字+日本語は保持されるべき: "
            f"got '{result}', expected '{expected}'"
        )

    def test_clean_parenthetical_multiple_english(self):
        """複数の英語括弧を削除"""
        input_text = "トイル（Toil）とエラーバジェット（Error Budget）"
        expected = "トイルとエラーバジェット"

        result = _clean_parenthetical_english(input_text)

        assert result == expected, (
            f"複数の英語括弧を正しく削除すべき: "
            f"got '{result}', expected '{expected}'"
        )

    def test_clean_parenthetical_empty_parens(self):
        """空括弧は保持"""
        input_text = "テスト（）終了"
        expected = "テスト（）終了"

        result = _clean_parenthetical_english(input_text)

        assert result == expected, (
            f"空括弧は保持されるべき: "
            f"got '{result}', expected '{expected}'"
        )

    def test_clean_parenthetical_empty_half_width_parens(self):
        """半角空括弧は保持"""
        input_text = "テスト()終了"
        expected = "テスト()終了"

        result = _clean_parenthetical_english(input_text)

        assert result == expected

    def test_clean_parenthetical_numbers_only(self):
        """数字のみの括弧内容は保持"""
        input_text = "バージョン（1.0）について"
        expected = "バージョン（1.0）について"

        result = _clean_parenthetical_english(input_text)

        assert result == expected

    def test_clean_parenthetical_punctuation_in_english(self):
        """英語内のピリオド・カンマを含む"""
        input_text = "例（e.g., example）として"
        expected = "例として"

        result = _clean_parenthetical_english(input_text)

        assert result == expected


class TestCleanParentheticalIdempotent:
    """Test idempotency: processing already-cleaned text"""

    def test_clean_parenthetical_idempotent_no_parens(self):
        """括弧のないテキストは変化しない"""
        input_text = "これは括弧を含まないテキストです"
        expected = "これは括弧を含まないテキストです"

        result = _clean_parenthetical_english(input_text)

        assert result == expected, (
            f"括弧のないテキストは変化すべきでない: "
            f"got '{result}', expected '{expected}'"
        )

    def test_clean_parenthetical_idempotent_already_processed(self):
        """処理済みテキストを再処理しても変化しない"""
        original = "トイル（Toil）の削減"
        first_pass = _clean_parenthetical_english(original)
        second_pass = _clean_parenthetical_english(first_pass)

        assert first_pass == second_pass, (
            f"冪等性が保証されるべき: "
            f"first pass: '{first_pass}', second pass: '{second_pass}'"
        )

    def test_clean_parenthetical_empty_string(self):
        """空文字列の処理"""
        result = _clean_parenthetical_english("")
        assert result == ""

    def test_clean_parenthetical_whitespace_only(self):
        """空白のみのテキスト"""
        result = _clean_parenthetical_english("   ")
        assert result == "   "
