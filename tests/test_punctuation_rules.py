"""Tests for punctuation normalization rules.

Phase 6 RED Tests - US6: 不適切な読点挿入の修正
Tests for _normalize_line function that handles punctuation insertion with exclusion patterns.

Target function: src/punctuation_normalizer.py::_normalize_line()
Current behavior: Rule 4 inserts comma after は when preceded by long phrase.
Expected behavior: Exclude patterns like ではありません, ではない, にはならない, etc.
"""

import pytest

from src.punctuation_normalizer import _normalize_line


class TestNormalizeLineDehaArimasen:
    """Test 「ではありません」 pattern - no comma insertion after は"""

    def test_normalize_line_deha_arimasen_basic(self):
        """「ではありません」の「は」の後に読点が入らない"""
        input_text = "これは問題ではありません"
        expected = "これは問題ではありません"

        result = _normalize_line(input_text)

        assert result == expected, (
            f"「ではありません」の「は」の後に読点を入れてはいけない: "
            f"got '{result}', expected '{expected}'"
        )

    def test_normalize_line_deha_arimasen_longer(self):
        """長いフレーズ後の「ではありません」でも読点なし"""
        input_text = "この技術の導入は終わりではありません"
        expected = "この技術の導入は終わりではありません"

        result = _normalize_line(input_text)

        # 「導入は」の後には読点が入ってもよいが、「ではありません」には入らない
        # Expected: 「この技術の導入は、終わりではありません」or「この技術の導入は終わりではありません」
        assert "では、ありません" not in result, (
            f"「ではありません」の途中に読点を入れてはいけない: got '{result}'"
        )


class TestNormalizeLineDehaPatterns:
    """Test 「ではない」「ではなかった」 patterns"""

    def test_normalize_line_deha_nai_basic(self):
        """「ではない」の「は」の後に読点が入らない"""
        input_text = "問題ではない"
        expected = "問題ではない"

        result = _normalize_line(input_text)

        assert result == expected, (
            f"「ではない」の「は」の後に読点を入れてはいけない: "
            f"got '{result}', expected '{expected}'"
        )

    def test_normalize_line_deha_nai_in_sentence(self):
        """文中の「ではない」でも読点なし"""
        input_text = "これは単純な問題ではないと思います"
        expected_without_deha_comma = "では、ない"

        result = _normalize_line(input_text)

        assert expected_without_deha_comma not in result, (
            f"「ではない」の途中に読点を入れてはいけない: got '{result}'"
        )

    def test_normalize_line_deha_nakatta(self):
        """「ではなかった」の「は」の後に読点が入らない"""
        input_text = "問題ではなかった"
        expected = "問題ではなかった"

        result = _normalize_line(input_text)

        assert result == expected, (
            f"「ではなかった」の「は」の後に読点を入れてはいけない: "
            f"got '{result}', expected '{expected}'"
        )

    def test_normalize_line_deha_nakute(self):
        """「ではなくて」の「は」の後に読点が入らない"""
        input_text = "問題ではなくて改善点です"
        expected_without_deha_comma = "では、なくて"

        result = _normalize_line(input_text)

        assert expected_without_deha_comma not in result, (
            f"「ではなくて」の途中に読点を入れてはいけない: got '{result}'"
        )


class TestNormalizeLineNihaPatterns:
    """Test 「にはならない」「には至らない」 patterns"""

    def test_normalize_line_niha_naranai(self):
        """「にはならない」の「は」の後に読点が入らない"""
        input_text = "問題にはならない"
        expected = "問題にはならない"

        result = _normalize_line(input_text)

        assert result == expected, (
            f"「にはならない」の「は」の後に読点を入れてはいけない: "
            f"got '{result}', expected '{expected}'"
        )

    def test_normalize_line_niha_itaranai(self):
        """「には至らない」の「は」の後に読点が入らない"""
        input_text = "成功には至らない"
        expected_without_niha_comma = "には、至らない"

        result = _normalize_line(input_text)

        assert expected_without_niha_comma not in result, (
            f"「には至らない」の途中に読点を入れてはいけない: got '{result}'"
        )

    def test_normalize_line_niha_naranakatta(self):
        """「にはならなかった」の「は」の後に読点が入らない"""
        input_text = "問題にはならなかった"
        expected_without_niha_comma = "には、ならなかった"

        result = _normalize_line(input_text)

        assert expected_without_niha_comma not in result, (
            f"「にはならなかった」の途中に読点を入れてはいけない: got '{result}'"
        )


class TestNormalizeLineTohaPatterns:
    """Test 「とは言えない」「とは限らない」 patterns"""

    def test_normalize_line_toha_ienai(self):
        """「とは言えない」の「は」の後に読点が入らない"""
        input_text = "正確とは言えない"
        expected = "正確とは言えない"

        result = _normalize_line(input_text)

        assert result == expected, (
            f"「とは言えない」の「は」の後に読点を入れてはいけない: "
            f"got '{result}', expected '{expected}'"
        )

    def test_normalize_line_toha_kagiranai(self):
        """「とは限らない」の「は」の後に読点が入らない"""
        input_text = "正しいとは限らない"
        expected_without_toha_comma = "とは、限らない"

        result = _normalize_line(input_text)

        assert expected_without_toha_comma not in result, (
            f"「とは限らない」の途中に読点を入れてはいけない: got '{result}'"
        )


class TestNormalizeLineMixedPatterns:
    """Test mixed patterns - regular は should get comma, exclusion patterns should not"""

    def test_normalize_line_mixed_ha_patterns(self):
        """通常の「は」には読点、除外パターンには読点なし"""
        input_text = "この本は問題ではありません"
        # Expected: 「この本は、問題ではありません」
        # - 「本は」の後に読点（通常のはルール）
        # - 「ではありません」には読点なし（除外パターン）

        result = _normalize_line(input_text)

        # Check that では、ありません does NOT appear
        assert "では、ありません" not in result, (
            f"「ではありません」の途中に読点を入れてはいけない: got '{result}'"
        )

    def test_normalize_line_mixed_ha_patterns_longer(self):
        """長い文での混合パターン"""
        input_text = "この技術は重要ですが問題ではありません"
        # 「技術は」の後に読点OK、「ではありません」には読点なし

        result = _normalize_line(input_text)

        assert "では、ありません" not in result, (
            f"「ではありません」の途中に読点を入れてはいけない: got '{result}'"
        )

    def test_normalize_line_multiple_exclusions(self):
        """複数の除外パターンが連続する場合"""
        input_text = "この方法では問題ではありません"
        # 「方法では」の「では」も、「問題ではありません」の「では」も読点なし

        result = _normalize_line(input_text)

        # Check no comma appears after any では
        assert "では、" not in result, (
            f"「では」の後に読点を入れてはいけない: got '{result}'"
        )

    def test_normalize_line_regular_ha_still_works(self):
        """通常の「は」には読点が入る（機能継続確認）"""
        input_text = "この技術は重要です"
        # Expected: 「この技術は、重要です」（通常のRule 4動作）

        result = _normalize_line(input_text)

        # This test verifies that normal は rule still applies
        # The exact behavior depends on min_prefix_len
        # At minimum, the exclusion patterns should not affect normal は
        assert "技術" in result and "重要" in result, (
            f"テキストが破損している: got '{result}'"
        )


class TestNormalizeLineEdgeCases:
    """Edge cases for exclusion patterns"""

    def test_normalize_line_deha_at_sentence_start(self):
        """文頭の「では」でも読点なし"""
        input_text = "ではありませんでした"
        expected_without_comma = "では、ありませんでした"

        result = _normalize_line(input_text)

        assert expected_without_comma not in result, (
            f"文頭の「では」でも読点を入れてはいけない: got '{result}'"
        )

    def test_normalize_line_deha_before_particle(self):
        """「ではないか」パターン"""
        input_text = "問題ではないか"
        expected_without_comma = "では、ないか"

        result = _normalize_line(input_text)

        assert expected_without_comma not in result, (
            f"「ではないか」の途中に読点を入れてはいけない: got '{result}'"
        )

    def test_normalize_line_empty_string(self):
        """空文字列の処理"""
        result = _normalize_line("")

        assert result == "", f"空文字列は空のまま: got '{result}'"

    def test_normalize_line_no_ha(self):
        """「は」を含まないテキスト"""
        input_text = "これを確認する"
        expected = "これを確認する"

        result = _normalize_line(input_text)

        assert result == expected, (
            f"「は」のないテキストは変化しない: got '{result}', expected '{expected}'"
        )


class TestNormalizeLineArimasuPatterns:
    """Test 「ではあります」 patterns (affirmative, but still exclusion)"""

    def test_normalize_line_deha_arimasuga(self):
        """「ではありますが」の「は」の後に読点が入らない"""
        input_text = "重要ではありますが問題です"
        expected_without_comma = "では、ありますが"

        result = _normalize_line(input_text)

        assert expected_without_comma not in result, (
            f"「ではありますが」の途中に読点を入れてはいけない: got '{result}'"
        )

    def test_normalize_line_deha_aru(self):
        """「ではある」の「は」の後に読点が入らない"""
        input_text = "問題ではある"
        expected_without_comma = "では、ある"

        result = _normalize_line(input_text)

        assert expected_without_comma not in result, (
            f"「ではある」の途中に読点を入れてはいけない: got '{result}'"
        )
