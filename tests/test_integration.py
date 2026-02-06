"""Integration tests for text cleaning pipeline.

Phase 9 RED Tests - パイプライン統合
Tests for verifying all cleaning functions are properly integrated
into clean_page_text() and normalize_punctuation().

Target functions:
- src/text_cleaner.py::clean_page_text()
- src/punctuation_normalizer.py::normalize_punctuation()
"""

import pytest

from src.text_cleaner import clean_page_text
from src.punctuation_normalizer import normalize_punctuation


class TestCleanPageTextIntegration:
    """Test that clean_page_text integrates all cleaning functions."""

    def test_clean_page_text_all_features(self):
        """複合テキストに対して全変換が適用される（URL + ISBN + 括弧 + 参照 + コロン + 鉤括弧）"""
        input_text = """詳細は[こちら](https://example.com)を参照。
ISBN978-4-87311-865-8
トイル（Toil）について。
図2.1と表3.4を参照。
目的：システムの改善
「重要な」ポイント"""

        result = clean_page_text(input_text)

        # URL処理: Markdownリンクのテキストのみ残る
        assert "https://" not in result, (
            f"URL should be removed: got '{result}'"
        )
        assert "こちら" in result or "参照" in result, (
            f"Link text 'こちら' should remain: got '{result}'"
        )

        # ISBN処理: 削除される
        assert "ISBN" not in result, (
            f"ISBN should be removed: got '{result}'"
        )
        assert "978-4-87311-865-8" not in result, (
            f"ISBN number should be removed: got '{result}'"
        )

        # 括弧処理: 英語括弧が除去される
        assert "（Toil）" not in result, (
            f"Parenthetical English should be removed: got '{result}'"
        )
        assert "(Toil)" not in result, (
            f"Parenthetical English should be removed: got '{result}'"
        )
        # トイル is converted to kana by MeCab, but the term should exist
        # Check that English parenthetical is removed

        # 参照正規化: 図2.1 → ず2の1 (読み仮名形式)
        assert "図2.1" not in result, (
            f"Figure reference should be normalized: got '{result}'"
        )
        assert "表3.4" not in result, (
            f"Table reference should be normalized: got '{result}'"
        )
        # After number normalization, digits become Japanese
        # Check that patterns are converted (ず, ひょう prefixes exist)

        # コロン変換: ：→ は、
        assert "：" not in result, (
            f"Full-width colon should be converted: got '{result}'"
        )
        # Note: After colon conversion, 目的：→ 目的は、

        # 鉤括弧変換: 「」→ 読点
        assert "「" not in result, (
            f"Opening bracket should be converted: got '{result}'"
        )
        assert "」" not in result, (
            f"Closing bracket should be converted: got '{result}'"
        )

    def test_clean_page_text_url_integration(self):
        """clean_page_text が URL を正しく処理する"""
        input_text = "サイト[SRE NEXT](https://sre-next.dev/)を参照してください"

        result = clean_page_text(input_text)

        assert "https://" not in result, (
            f"URL should be removed: got '{result}'"
        )
        # After MeCab conversion, text becomes kana
        # Just verify URL is gone

    def test_clean_page_text_isbn_integration(self):
        """clean_page_text が ISBN を正しく削除する"""
        input_text = "この本はISBN978-4-297-15072-3で購入できます"

        result = clean_page_text(input_text)

        assert "ISBN" not in result, (
            f"ISBN should be removed: got '{result}'"
        )
        assert "978" not in result, (
            f"ISBN number should be removed: got '{result}'"
        )

    def test_clean_page_text_parenthetical_integration(self):
        """clean_page_text が括弧付き英語を正しく除去する"""
        input_text = "SRE（Site Reliability Engineering）の実践"

        result = clean_page_text(input_text)

        assert "（Site Reliability Engineering）" not in result, (
            f"Parenthetical English should be removed: got '{result}'"
        )

    def test_clean_page_text_reference_integration(self):
        """clean_page_text が図表参照を正しく変換する"""
        input_text = "図1.2と表2.3を参照"

        result = clean_page_text(input_text)

        # References should be converted to reading form
        assert "図1.2" not in result, (
            f"Figure reference should be normalized: got '{result}'"
        )
        assert "表2.3" not in result, (
            f"Table reference should be normalized: got '{result}'"
        )
        # After conversion: ず1の2, ひょう2の3
        # Then number normalization converts digits


class TestCleanPageTextProcessingOrder:
    """Test that processing order is correct."""

    def test_clean_page_text_url_before_reference(self):
        """URL処理が参照正規化より先に行われる"""
        # URL containing figure pattern should be removed, not normalized
        input_text = "図解は[こちら](https://example.com/図2.1)を参照"

        result = clean_page_text(input_text)

        # URL should be completely removed
        assert "https://" not in result
        assert "example.com" not in result

    def test_clean_page_text_isbn_before_reference(self):
        """ISBN処理が参照正規化より先に行われる"""
        input_text = "ISBN978-4-87311-865-8の図2.1を参照"

        result = clean_page_text(input_text)

        # ISBN should be removed
        assert "ISBN" not in result
        # Figure reference should be normalized
        assert "図2.1" not in result

    def test_clean_page_text_parenthetical_after_url(self):
        """括弧処理がURL処理より後に行われる"""
        input_text = "[トイル（Toil）](https://example.com)について"

        result = clean_page_text(input_text)

        # URL should be removed, leaving link text
        assert "https://" not in result
        # Parenthetical English in link text should be removed
        assert "（Toil）" not in result


class TestCleanPageTextIdempotent:
    """Test that clean_page_text is idempotent."""

    def test_clean_page_text_idempotent_basic(self):
        """再処理しても結果が同一"""
        input_text = """詳細は[こちら](https://example.com)を参照。
ISBN978-4-87311-865-8
トイル（Toil）について。"""

        first_pass = clean_page_text(input_text)
        second_pass = clean_page_text(first_pass)

        assert first_pass == second_pass, (
            f"clean_page_text should be idempotent: "
            f"first='{first_pass}', second='{second_pass}'"
        )

    def test_clean_page_text_idempotent_complex(self):
        """複雑な入力でも再処理で結果同一"""
        input_text = """図2.1と表3.4を参照。
目的：システムの改善
「重要な」ポイント
注1.2と注2.3も確認。"""

        first_pass = clean_page_text(input_text)
        second_pass = clean_page_text(first_pass)

        assert first_pass == second_pass, (
            f"clean_page_text should be idempotent: "
            f"first='{first_pass}', second='{second_pass}'"
        )

    def test_clean_page_text_idempotent_url_markdown(self):
        """URL処理後の再処理で結果同一"""
        input_text = "[SRE NEXT](https://sre-next.dev/)を参照"

        first_pass = clean_page_text(input_text)
        second_pass = clean_page_text(first_pass)

        assert first_pass == second_pass


class TestNormalizePunctuationIntegration:
    """Test that normalize_punctuation integrates all rules."""

    def test_normalize_punctuation_all_rules(self):
        """normalize_punctuation が全ルールを統合する"""
        input_text = """目的：システム改善
「重要な」ポイント
これは問題ではありません"""

        result = normalize_punctuation(input_text)

        # コロン変換: ：→ は、
        assert "：" not in result, (
            f"Full-width colon should be converted: got '{result}'"
        )
        assert "目的は、" in result, (
            f"Colon should be converted to は、: got '{result}'"
        )

        # 鉤括弧変換: 「」→ 読点
        assert "「" not in result, (
            f"Opening bracket should be converted: got '{result}'"
        )
        assert "」" not in result, (
            f"Closing bracket should be converted: got '{result}'"
        )

        # 除外パターン: ではありません に読点を入れない
        assert "では、ありません" not in result, (
            f"No comma should be inserted in ではありません: got '{result}'"
        )

    def test_normalize_punctuation_colon_conversion(self):
        """コロン変換が正しく動作する"""
        input_text = "目的：テスト実行"

        result = normalize_punctuation(input_text)

        assert "目的は、" in result, (
            f"Colon should be converted to は、: got '{result}'"
        )
        assert "：" not in result

    def test_normalize_punctuation_bracket_conversion(self):
        """鉤括弧変換が正しく動作する"""
        input_text = "これは「テスト」です"

        result = normalize_punctuation(input_text)

        assert "「" not in result
        assert "」" not in result
        assert "、テスト、" in result, (
            f"Brackets should be converted to commas: got '{result}'"
        )

    def test_normalize_punctuation_exclusion_patterns(self):
        """除外パターンが正しく動作する"""
        input_text = "問題ではありません"

        result = normalize_punctuation(input_text)

        assert "では、" not in result, (
            f"No comma after では in exclusion pattern: got '{result}'"
        )

    def test_normalize_punctuation_combined_example(self):
        """複合例での統合テスト"""
        input_text = "目的：「テスト」ではない問題"

        result = normalize_punctuation(input_text)

        # コロン変換
        assert "：" not in result
        # 鉤括弧変換
        assert "「" not in result
        assert "」" not in result
        # 除外パターン
        assert "では、ない" not in result


class TestIntegrationEdgeCases:
    """Test edge cases for integration."""

    def test_empty_input(self):
        """空入力の処理"""
        assert clean_page_text("") == ""
        assert normalize_punctuation("") == ""

    def test_whitespace_only(self):
        """空白のみの入力"""
        assert clean_page_text("   \n\n   ") == ""
        assert normalize_punctuation("   \n\n   ") == "   \n\n   "

    def test_no_special_patterns(self):
        """特殊パターンがない普通のテキスト"""
        input_text = "これは普通のテキストです"

        # clean_page_text applies MeCab conversion
        result_clean = clean_page_text(input_text)
        assert result_clean  # Should produce some output

        # normalize_punctuation should not change much
        result_punct = normalize_punctuation(input_text)
        # May have comma insertion after は
        assert result_punct  # Should produce some output

    def test_multiple_urls_and_references(self):
        """複数のURLと参照が混在"""
        input_text = """[リンク1](https://a.com)と[リンク2](https://b.com)を参照。
図1.1、図1.2、表2.1を確認。"""

        result = clean_page_text(input_text)

        assert "https://" not in result
        assert "図1.1" not in result
        assert "図1.2" not in result
        assert "表2.1" not in result

    def test_unicode_characters(self):
        """Unicode文字を含むテキスト"""
        input_text = "特殊文字：★☆◆◇を含むテキスト「引用」です"

        result = normalize_punctuation(input_text)

        assert "：" not in result
        assert "「" not in result
        assert "」" not in result
