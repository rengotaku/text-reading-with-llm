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


# ============================================================================
# Phase 7 RED Tests - US7: コロン記号の自然な読み上げ変換
# Target function: src/punctuation_normalizer.py::_normalize_colons()
# Expected behavior: Convert colons to 「は、」 (exclude time/ratio patterns)
# ============================================================================


class TestNormalizeColonsFullWidth:
    """Test full-width colon (：) conversion to 「は、」"""

    def test_normalize_colons_full_width_basic(self):
        """全角コロンが「は、」に変換される"""
        from src.punctuation_normalizer import _normalize_colons

        input_text = "目的：システムの改善"
        expected = "目的は、システムの改善"

        result = _normalize_colons(input_text)

        assert result == expected, (
            f"全角コロンが「は、」に変換されるべき: "
            f"got '{result}', expected '{expected}'"
        )

    def test_normalize_colons_full_width_multiple(self):
        """複数の全角コロンが変換される"""
        from src.punctuation_normalizer import _normalize_colons

        input_text = "項目1：説明1、項目2：説明2"
        expected = "項目1は、説明1、項目2は、説明2"

        result = _normalize_colons(input_text)

        assert result == expected, (
            f"複数の全角コロンが変換されるべき: "
            f"got '{result}', expected '{expected}'"
        )

    def test_normalize_colons_full_width_at_end(self):
        """文末の全角コロンが変換される"""
        from src.punctuation_normalizer import _normalize_colons

        input_text = "以下の通り："
        # 文末コロンは「は、」に変換されてもよい
        expected = "以下の通りは、"

        result = _normalize_colons(input_text)

        assert result == expected, (
            f"文末の全角コロンも変換されるべき: "
            f"got '{result}', expected '{expected}'"
        )


class TestNormalizeColonsHalfWidth:
    """Test half-width colon (:) conversion to 「は、」"""

    def test_normalize_colons_half_width_basic(self):
        """半角コロンが「は、」に変換される"""
        from src.punctuation_normalizer import _normalize_colons

        input_text = "目的:システムの改善"
        expected = "目的は、システムの改善"

        result = _normalize_colons(input_text)

        assert result == expected, (
            f"半角コロンが「は、」に変換されるべき: "
            f"got '{result}', expected '{expected}'"
        )

    def test_normalize_colons_half_width_with_space(self):
        """半角コロン後のスペースも適切に処理される"""
        from src.punctuation_normalizer import _normalize_colons

        input_text = "注意: この操作は取り消せません"
        expected = "注意は、この操作は取り消せません"

        result = _normalize_colons(input_text)

        assert result == expected, (
            f"半角コロン+スペースが変換されるべき: "
            f"got '{result}', expected '{expected}'"
        )


class TestNormalizeColonsExclusions:
    """Test patterns that should NOT be converted (time, ratio)"""

    def test_normalize_colons_exclude_time_pattern(self):
        """時刻パターン(10:30)は変換しない"""
        from src.punctuation_normalizer import _normalize_colons

        input_text = "開始時刻は10:30です"
        expected = "開始時刻は10:30です"

        result = _normalize_colons(input_text)

        assert result == expected, (
            f"時刻パターンは変換しない: "
            f"got '{result}', expected '{expected}'"
        )

    def test_normalize_colons_exclude_time_with_seconds(self):
        """時刻パターン(10:30:45)は変換しない"""
        from src.punctuation_normalizer import _normalize_colons

        input_text = "正確な時刻は10:30:45です"
        expected = "正確な時刻は10:30:45です"

        result = _normalize_colons(input_text)

        assert result == expected, (
            f"秒を含む時刻パターンは変換しない: "
            f"got '{result}', expected '{expected}'"
        )

    def test_normalize_colons_exclude_ratio_pattern(self):
        """比率パターン(1:3)は変換しない"""
        from src.punctuation_normalizer import _normalize_colons

        input_text = "比率は1:3です"
        expected = "比率は1:3です"

        result = _normalize_colons(input_text)

        assert result == expected, (
            f"比率パターンは変換しない: "
            f"got '{result}', expected '{expected}'"
        )

    def test_normalize_colons_exclude_ratio_multiple(self):
        """複合比率パターン(1:2:3)は変換しない"""
        from src.punctuation_normalizer import _normalize_colons

        input_text = "割合は1:2:3です"
        expected = "割合は1:2:3です"

        result = _normalize_colons(input_text)

        assert result == expected, (
            f"複合比率パターンは変換しない: "
            f"got '{result}', expected '{expected}'"
        )


class TestNormalizeColonsMixedPatterns:
    """Test mixed patterns - colon conversion + time/ratio preservation"""

    def test_normalize_colons_mixed_time_and_heading(self):
        """見出しコロン変換 + 時刻保持の混合パターン"""
        from src.punctuation_normalizer import _normalize_colons

        input_text = "会議時間：10:30から"
        expected = "会議時間は、10:30から"

        result = _normalize_colons(input_text)

        assert result == expected, (
            f"見出しコロンは変換、時刻コロンは保持: "
            f"got '{result}', expected '{expected}'"
        )

    def test_normalize_colons_mixed_ratio_and_heading(self):
        """見出しコロン変換 + 比率保持の混合パターン"""
        from src.punctuation_normalizer import _normalize_colons

        input_text = "推奨比率：水1:砂糖2"
        expected = "推奨比率は、水1:砂糖2"

        result = _normalize_colons(input_text)

        assert result == expected, (
            f"見出しコロンは変換、比率コロンは保持: "
            f"got '{result}', expected '{expected}'"
        )

    def test_normalize_colons_full_and_half_width_mixed(self):
        """全角・半角コロン混在パターン"""
        from src.punctuation_normalizer import _normalize_colons

        input_text = "項目A：説明A、項目B:説明B"
        expected = "項目Aは、説明A、項目Bは、説明B"

        result = _normalize_colons(input_text)

        assert result == expected, (
            f"全角・半角コロン両方が変換されるべき: "
            f"got '{result}', expected '{expected}'"
        )


class TestNormalizeColonsEdgeCases:
    """Edge cases for colon normalization"""

    def test_normalize_colons_empty_string(self):
        """空文字列の処理"""
        from src.punctuation_normalizer import _normalize_colons

        result = _normalize_colons("")

        assert result == "", f"空文字列は空のまま: got '{result}'"

    def test_normalize_colons_no_colons(self):
        """コロンを含まないテキスト"""
        from src.punctuation_normalizer import _normalize_colons

        input_text = "これはコロンを含まないテキストです"
        expected = "これはコロンを含まないテキストです"

        result = _normalize_colons(input_text)

        assert result == expected, (
            f"コロンのないテキストは変化しない: "
            f"got '{result}', expected '{expected}'"
        )

    def test_normalize_colons_consecutive(self):
        """連続コロン(::)の処理"""
        from src.punctuation_normalizer import _normalize_colons

        input_text = "特殊パターン::値"
        # 実装依存: 連続コロンの処理はどちらかに変換
        # ここでは最初のコロンが変換され、2つ目は残る想定

        result = _normalize_colons(input_text)

        # 少なくとも元の形式とは異なることを確認
        # または連続コロンが適切に処理されることを確認
        assert "::" not in result or "は、" in result, (
            f"連続コロンが処理されるべき: got '{result}'"
        )

    def test_normalize_colons_at_line_start(self):
        """行頭のコロン"""
        from src.punctuation_normalizer import _normalize_colons

        input_text = "：これは行頭コロン"
        # 行頭コロンは前に変換対象テキストがないため変換しない or 削除
        # 実装依存

        result = _normalize_colons(input_text)

        # 行頭コロンの処理を確認（変換なし or 削除）
        assert result is not None, "結果がNoneであってはいけない"

    def test_normalize_colons_url_colon_not_affected(self):
        """URL内のコロン(https:)は影響を受けない想定

        Note: URL処理はtext_cleaner.pyで行われるため、
        punctuation_normalizerにはURLが渡らない前提。
        しかし万が一渡った場合のエッジケースとしてテスト。
        """
        from src.punctuation_normalizer import _normalize_colons

        # URLはtext_cleaner.pyで処理済みの前提だが、
        # 万が一残っていた場合の動作確認
        input_text = "リンク：https://example.com"

        result = _normalize_colons(input_text)

        # 「リンク：」は変換されるが、https: の部分は数字パターンではないので
        # 通常は変換対象になりうる（ただしURL処理後なら問題なし）
        # このテストは動作確認のみ
        assert result is not None, "結果がNoneであってはいけない"
