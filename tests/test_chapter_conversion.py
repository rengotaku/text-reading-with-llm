"""Tests for chapter conversion functionality.

Phase 3 RED Tests - US2: Chapter X -> 第X章 変換
Tests for _clean_chapter function that converts Chapter X patterns to 第X章.
"""

from src.text_cleaner import _clean_chapter


class TestCleanChapterBasic:
    """Test basic Chapter X -> 第X章 conversion"""

    def test_clean_chapter_basic(self):
        """Chapter 5 を 第5章 に変換"""
        input_text = "Chapter 5 を参照"
        expected = "第5章 を参照"

        result = _clean_chapter(input_text)

        assert result == expected, f"Chapter X は第X章に変換されるべき: got '{result}', expected '{expected}'"

    def test_clean_chapter_double_digit(self):
        """2桁の章番号の変換"""
        input_text = "Chapter 12 について説明します"
        expected = "第12章 について説明します"

        result = _clean_chapter(input_text)

        assert result == expected

    def test_clean_chapter_single_digit(self):
        """1桁の章番号の変換"""
        input_text = "Chapter 1 から始めましょう"
        expected = "第1章 から始めましょう"

        result = _clean_chapter(input_text)

        assert result == expected

    def test_clean_chapter_large_number(self):
        """大きな章番号の変換"""
        input_text = "Chapter 100 は最終章です"
        expected = "第100章 は最終章です"

        result = _clean_chapter(input_text)

        assert result == expected


class TestCleanChapterCaseInsensitive:
    """Test case-insensitive matching: chapter, CHAPTER, Chapter"""

    def test_clean_chapter_lowercase(self):
        """小文字 chapter も変換"""
        input_text = "chapter 12 を読んでください"
        expected = "第12章 を読んでください"

        result = _clean_chapter(input_text)

        assert result == expected, f"小文字 chapter も変換されるべき: got '{result}', expected '{expected}'"

    def test_clean_chapter_uppercase(self):
        """大文字 CHAPTER も変換"""
        input_text = "CHAPTER 1 は概要です"
        expected = "第1章 は概要です"

        result = _clean_chapter(input_text)

        assert result == expected

    def test_clean_chapter_mixed_case(self):
        """混合ケース cHaPtEr も変換"""
        input_text = "cHaPtEr 3 を確認"
        expected = "第3章 を確認"

        result = _clean_chapter(input_text)

        assert result == expected


class TestCleanChapterMultiple:
    """Test multiple Chapter patterns in single text"""

    def test_clean_chapter_multiple(self):
        """複数の Chapter を同時に変換"""
        input_text = "Chapter 1 と Chapter 2 を比較してください"
        expected = "第1章 と 第2章 を比較してください"

        result = _clean_chapter(input_text)

        assert result == expected


class TestCleanChapterEdgeCases:
    """Edge cases for chapter conversion"""

    def test_clean_chapter_empty_string(self):
        """空文字列の処理"""
        result = _clean_chapter("")
        assert result == ""

    def test_clean_chapter_no_match(self):
        """マッチしないテキストは変化しない"""
        input_text = "これは通常のテキストです"
        result = _clean_chapter(input_text)
        assert result == input_text

    def test_clean_chapter_without_number(self):
        """Chapter の後に数字がない場合は変換しない"""
        input_text = "This chapter discusses the topic"
        expected = "This chapter discusses the topic"

        result = _clean_chapter(input_text)

        assert result == expected

    def test_clean_chapter_idempotent(self):
        """処理済みテキストを再処理しても変化しない"""
        input_text = "第5章を確認"
        result = _clean_chapter(input_text)
        assert result == input_text
