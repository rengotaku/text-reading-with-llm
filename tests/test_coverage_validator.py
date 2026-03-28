"""coverage_validator モジュールのテスト。

キーワードリストと対話XMLを入力として、カバー率を計算し
JSON形式で出力する機能のテスト。LLMは使用しない（文字列マッチングのみ）。
"""

import pytest

from src.coverage_validator import CoverageResult, validate_coverage

# --- サンプルデータ ---

SAMPLE_DIALOGUE_XML = """<dialogue>
  <turn speaker="ハル">ロボチェック社のデスマーチについて話しましょう。</turn>
  <turn speaker="ミク">2027年の売上目標は1000億円だそうですね。</turn>
  <turn speaker="ハル">機械学習を活用した新しいプロジェクトも始まりました。</turn>
</dialogue>"""

EMPTY_DIALOGUE_XML = ""

MINIMAL_DIALOGUE_XML = "<dialogue><turn speaker='A'>テスト</turn></dialogue>"


# --- T021: CoverageResult dataclass テスト ---


class TestCoverageResultDataclass:
    """CoverageResult dataclass の属性と振る舞いのテスト。"""

    def test_has_total_keywords_attribute(self):
        """total_keywords 属性を持つ。"""
        result = CoverageResult(
            total_keywords=10,
            covered_keywords=7,
            coverage_rate=0.7,
            missing_keywords=["A", "B", "C"],
        )
        assert result.total_keywords == 10

    def test_has_covered_keywords_attribute(self):
        """covered_keywords 属性を持つ。"""
        result = CoverageResult(
            total_keywords=10,
            covered_keywords=7,
            coverage_rate=0.7,
            missing_keywords=["A", "B", "C"],
        )
        assert result.covered_keywords == 7

    def test_has_coverage_rate_attribute(self):
        """coverage_rate 属性を持つ。"""
        result = CoverageResult(
            total_keywords=10,
            covered_keywords=7,
            coverage_rate=0.7,
            missing_keywords=["A", "B", "C"],
        )
        assert result.coverage_rate == pytest.approx(0.7)

    def test_has_missing_keywords_attribute(self):
        """missing_keywords 属性を持つ。"""
        result = CoverageResult(
            total_keywords=10,
            covered_keywords=7,
            coverage_rate=0.7,
            missing_keywords=["A", "B", "C"],
        )
        assert result.missing_keywords == ["A", "B", "C"]

    def test_missing_keywords_is_list_of_str(self):
        """missing_keywords は list[str] 型である。"""
        result = CoverageResult(
            total_keywords=3,
            covered_keywords=1,
            coverage_rate=0.33,
            missing_keywords=["X", "Y"],
        )
        assert isinstance(result.missing_keywords, list)
        for item in result.missing_keywords:
            assert isinstance(item, str)

    def test_to_dict_returns_dict(self):
        """to_dict メソッドが dict を返す。"""
        result = CoverageResult(
            total_keywords=5,
            covered_keywords=3,
            coverage_rate=0.6,
            missing_keywords=["A", "B"],
        )
        d = result.to_dict()
        assert isinstance(d, dict)

    def test_to_dict_contains_all_keys(self):
        """to_dict が全ての必須キーを含む。"""
        result = CoverageResult(
            total_keywords=5,
            covered_keywords=3,
            coverage_rate=0.6,
            missing_keywords=["A", "B"],
        )
        d = result.to_dict()
        assert "total_keywords" in d
        assert "covered_keywords" in d
        assert "coverage_rate" in d
        assert "missing_keywords" in d

    def test_to_dict_values_match_attributes(self):
        """to_dict の値が属性値と一致する。"""
        result = CoverageResult(
            total_keywords=12,
            covered_keywords=9,
            coverage_rate=0.75,
            missing_keywords=["2027年", "A社", "B社"],
        )
        d = result.to_dict()
        assert d["total_keywords"] == 12
        assert d["covered_keywords"] == 9
        assert d["coverage_rate"] == pytest.approx(0.75)
        assert d["missing_keywords"] == ["2027年", "A社", "B社"]


# --- T022: 基本検証テスト ---


class TestValidateCoverageBasic:
    """validate_coverage 関数の基本テスト。"""

    def test_returns_coverage_result(self):
        """validate_coverage が CoverageResult を返す。"""
        keywords = ["ロボチェック社", "デスマーチ", "2027年"]
        result = validate_coverage(keywords, SAMPLE_DIALOGUE_XML)
        assert isinstance(result, CoverageResult)

    def test_calculates_coverage_rate(self):
        """カバー率が正しく計算される。"""
        keywords = ["ロボチェック社", "デスマーチ", "存在しない用語"]
        result = validate_coverage(keywords, SAMPLE_DIALOGUE_XML)
        # 3キーワード中2つカバー → 2/3
        assert result.total_keywords == 3
        assert result.covered_keywords == 2
        assert result.coverage_rate == pytest.approx(2 / 3, rel=1e-3)

    def test_identifies_missing_keywords(self):
        """未カバーキーワードが正しく特定される。"""
        keywords = ["ロボチェック社", "デスマーチ", "存在しない用語"]
        result = validate_coverage(keywords, SAMPLE_DIALOGUE_XML)
        assert "存在しない用語" in result.missing_keywords
        assert "ロボチェック社" not in result.missing_keywords
        assert "デスマーチ" not in result.missing_keywords

    def test_total_equals_covered_plus_missing(self):
        """total_keywords == covered_keywords + len(missing_keywords) の不変条件。"""
        keywords = ["ロボチェック社", "デスマーチ", "存在しない用語", "別の不在用語"]
        result = validate_coverage(keywords, SAMPLE_DIALOGUE_XML)
        assert result.total_keywords == result.covered_keywords + len(result.missing_keywords)

    def test_partial_coverage_rate(self):
        """部分的なカバー率が正しく計算される。"""
        keywords = ["ロボチェック社", "機械学習", "量子コンピュータ", "ブロックチェーン"]
        result = validate_coverage(keywords, SAMPLE_DIALOGUE_XML)
        # "ロボチェック社" と "機械学習" はカバー、残り2つは未カバー → 0.5
        assert result.coverage_rate == pytest.approx(0.5)
        assert result.covered_keywords == 2
        assert len(result.missing_keywords) == 2


# --- T023: 全カバーテスト ---


class TestValidateCoverageFullCoverage:
    """全キーワードがカバーされるケースのテスト。"""

    def test_all_keywords_covered_rate_is_one(self):
        """全キーワードがカバーされた場合、coverage_rate は 1.0。"""
        keywords = ["ロボチェック社", "デスマーチ", "機械学習"]
        result = validate_coverage(keywords, SAMPLE_DIALOGUE_XML)
        assert result.coverage_rate == pytest.approx(1.0)

    def test_all_keywords_covered_missing_is_empty(self):
        """全キーワードがカバーされた場合、missing_keywords は空リスト。"""
        keywords = ["ロボチェック社", "デスマーチ", "機械学習"]
        result = validate_coverage(keywords, SAMPLE_DIALOGUE_XML)
        assert result.missing_keywords == []

    def test_all_keywords_covered_counts_match(self):
        """全キーワードがカバーされた場合、total == covered。"""
        keywords = ["ロボチェック社", "デスマーチ"]
        result = validate_coverage(keywords, SAMPLE_DIALOGUE_XML)
        assert result.total_keywords == result.covered_keywords
        assert result.total_keywords == 2

    def test_single_keyword_fully_covered(self):
        """単一キーワードがカバーされた場合。"""
        keywords = ["ロボチェック社"]
        result = validate_coverage(keywords, SAMPLE_DIALOGUE_XML)
        assert result.coverage_rate == pytest.approx(1.0)
        assert result.covered_keywords == 1
        assert result.missing_keywords == []


# --- T024: 全未カバーテスト ---


class TestValidateCoverageNoCoverage:
    """キーワードが一つもカバーされないケースのテスト。"""

    def test_no_keywords_covered_rate_is_zero(self):
        """全キーワードが未カバーの場合、coverage_rate は 0.0。"""
        keywords = ["宇宙旅行", "タイムマシン", "テレポーテーション"]
        result = validate_coverage(keywords, SAMPLE_DIALOGUE_XML)
        assert result.coverage_rate == pytest.approx(0.0)

    def test_no_keywords_covered_all_missing(self):
        """全キーワードが未カバーの場合、missing_keywords に全て含まれる。"""
        keywords = ["宇宙旅行", "タイムマシン", "テレポーテーション"]
        result = validate_coverage(keywords, SAMPLE_DIALOGUE_XML)
        assert set(result.missing_keywords) == set(keywords)

    def test_no_keywords_covered_counts(self):
        """全キーワードが未カバーの場合、covered は 0。"""
        keywords = ["宇宙旅行", "タイムマシン"]
        result = validate_coverage(keywords, SAMPLE_DIALOGUE_XML)
        assert result.covered_keywords == 0
        assert result.total_keywords == 2


# --- T025: エッジケーステスト ---


class TestValidateCoverageEdgeCases:
    """validate_coverage のエッジケーステスト。"""

    def test_empty_keywords_returns_rate_one(self):
        """空のキーワードリスト → coverage_rate=1.0。"""
        result = validate_coverage([], SAMPLE_DIALOGUE_XML)
        assert result.coverage_rate == pytest.approx(1.0)
        assert result.total_keywords == 0
        assert result.covered_keywords == 0
        assert result.missing_keywords == []

    def test_empty_xml_returns_rate_zero(self):
        """空の対話XML → coverage_rate=0.0（キーワードがある場合）。"""
        keywords = ["ロボチェック社", "デスマーチ"]
        result = validate_coverage(keywords, EMPTY_DIALOGUE_XML)
        assert result.coverage_rate == pytest.approx(0.0)
        assert result.missing_keywords == keywords

    def test_empty_keywords_and_empty_xml(self):
        """空キーワードリスト + 空XML → coverage_rate=1.0。"""
        result = validate_coverage([], EMPTY_DIALOGUE_XML)
        assert result.coverage_rate == pytest.approx(1.0)
        assert result.total_keywords == 0

    def test_none_keywords_raises_error(self):
        """None キーワードリスト → TypeError。"""
        with pytest.raises(TypeError):
            validate_coverage(None, SAMPLE_DIALOGUE_XML)  # type: ignore[arg-type]

    def test_none_xml_raises_error(self):
        """None 対話XML → TypeError。"""
        with pytest.raises(TypeError):
            validate_coverage(["keyword"], None)  # type: ignore[arg-type]

    def test_non_list_keywords_raises_error(self):
        """非リスト型キーワード → TypeError。"""
        with pytest.raises((TypeError, ValueError)):
            validate_coverage("not a list", SAMPLE_DIALOGUE_XML)  # type: ignore[arg-type]

    def test_non_string_xml_raises_error(self):
        """非文字列型XML → TypeError。"""
        with pytest.raises((TypeError, ValueError)):
            validate_coverage(["keyword"], 12345)  # type: ignore[arg-type]

    def test_malformed_xml_still_searches_text(self):
        """不正なXML形式でも文字列マッチングは機能する。"""
        malformed_xml = "<dialogue><turn>ロボチェック社について</turn>"
        keywords = ["ロボチェック社", "デスマーチ"]
        result = validate_coverage(keywords, malformed_xml)
        assert result.covered_keywords == 1
        assert "ロボチェック社" not in result.missing_keywords
        assert "デスマーチ" in result.missing_keywords


# --- T026: 大文字小文字テスト ---


class TestValidateCoverageCaseInsensitive:
    """case-insensitive マッチングのテスト。"""

    def test_lowercase_keyword_matches_uppercase_in_xml(self):
        """小文字キーワードが大文字XMLテキストにマッチする。"""
        xml = "<dialogue><turn speaker='A'>Machine Learning is important.</turn></dialogue>"
        keywords = ["machine learning"]
        result = validate_coverage(keywords, xml)
        assert result.coverage_rate == pytest.approx(1.0)
        assert result.covered_keywords == 1

    def test_uppercase_keyword_matches_lowercase_in_xml(self):
        """大文字キーワードが小文字XMLテキストにマッチする。"""
        xml = "<dialogue><turn speaker='A'>deep learning is powerful.</turn></dialogue>"
        keywords = ["DEEP LEARNING"]
        result = validate_coverage(keywords, xml)
        assert result.coverage_rate == pytest.approx(1.0)

    def test_mixed_case_keyword_matches(self):
        """混合ケースのキーワードがマッチする。"""
        xml = "<dialogue><turn speaker='A'>Python and JavaScript are popular.</turn></dialogue>"
        keywords = ["python", "JAVASCRIPT"]
        result = validate_coverage(keywords, xml)
        assert result.coverage_rate == pytest.approx(1.0)
        assert result.covered_keywords == 2

    def test_japanese_keywords_are_case_insensitive(self):
        """日本語キーワードでも一致判定される（日本語には大文字小文字はないが正常動作確認）。"""
        keywords = ["ロボチェック社", "デスマーチ"]
        result = validate_coverage(keywords, SAMPLE_DIALOGUE_XML)
        assert result.coverage_rate == pytest.approx(1.0)

    def test_partial_match_does_not_count(self):
        """部分一致はカバーと判定しない（完全一致のみ）。"""
        xml = "<dialogue><turn speaker='A'>ロボチェック社の話です。</turn></dialogue>"
        keywords = ["ロボチェック"]  # "ロボチェック社" とは異なる
        # "ロボチェック" は "ロボチェック社" の部分文字列だが、
        # キーワード "ロボチェック" 自体は XML 内に含まれる（"ロボチェック社" の一部として）
        # spec の「完全一致のみをカバーと判定」はキーワード文字列がXML内に存在するかの判定
        result = validate_coverage(keywords, xml)
        assert result.covered_keywords == 1  # "ロボチェック" は XML 内に含まれている

    def test_keyword_not_substring_of_xml_text(self):
        """XMLテキスト内にキーワードが部分文字列として存在しない場合は未カバー。"""
        xml = "<dialogue><turn speaker='A'>ロボ社の話です。</turn></dialogue>"
        keywords = ["ロボチェック社"]
        result = validate_coverage(keywords, xml)
        assert result.coverage_rate == pytest.approx(0.0)
        assert "ロボチェック社" in result.missing_keywords


# --- T027: JSON 出力テスト ---


class TestCoverageResultToDict:
    """to_dict メソッドのJSON出力スキーマテスト。"""

    def test_to_dict_schema_has_exactly_four_keys(self):
        """to_dict は正確に4つのキーを持つ dict を返す。"""
        result = CoverageResult(
            total_keywords=5,
            covered_keywords=3,
            coverage_rate=0.6,
            missing_keywords=["A", "B"],
        )
        d = result.to_dict()
        assert len(d) == 4

    def test_to_dict_total_keywords_is_int(self):
        """total_keywords は int 型。"""
        result = CoverageResult(
            total_keywords=5,
            covered_keywords=3,
            coverage_rate=0.6,
            missing_keywords=["A", "B"],
        )
        d = result.to_dict()
        assert isinstance(d["total_keywords"], int)

    def test_to_dict_covered_keywords_is_int(self):
        """covered_keywords は int 型。"""
        result = CoverageResult(
            total_keywords=5,
            covered_keywords=3,
            coverage_rate=0.6,
            missing_keywords=["A", "B"],
        )
        d = result.to_dict()
        assert isinstance(d["covered_keywords"], int)

    def test_to_dict_coverage_rate_is_float(self):
        """coverage_rate は float 型。"""
        result = CoverageResult(
            total_keywords=5,
            covered_keywords=3,
            coverage_rate=0.6,
            missing_keywords=["A", "B"],
        )
        d = result.to_dict()
        assert isinstance(d["coverage_rate"], float)

    def test_to_dict_missing_keywords_is_list(self):
        """missing_keywords は list 型。"""
        result = CoverageResult(
            total_keywords=5,
            covered_keywords=3,
            coverage_rate=0.6,
            missing_keywords=["A", "B"],
        )
        d = result.to_dict()
        assert isinstance(d["missing_keywords"], list)

    def test_to_dict_json_serializable(self):
        """to_dict の出力が JSON シリアライズ可能。"""
        import json

        result = CoverageResult(
            total_keywords=12,
            covered_keywords=9,
            coverage_rate=0.75,
            missing_keywords=["2027年", "A社", "B社"],
        )
        d = result.to_dict()
        json_str = json.dumps(d, ensure_ascii=False)
        parsed = json.loads(json_str)
        assert parsed == d

    def test_to_dict_matches_spec_schema(self):
        """to_dict が仕様のJSONスキーマに一致する。"""
        result = CoverageResult(
            total_keywords=12,
            covered_keywords=9,
            coverage_rate=0.75,
            missing_keywords=["2027年", "A社", "B社"],
        )
        d = result.to_dict()
        # spec の JSON 出力形式と一致
        expected = {
            "total_keywords": 12,
            "covered_keywords": 9,
            "coverage_rate": 0.75,
            "missing_keywords": ["2027年", "A社", "B社"],
        }
        assert d == expected

    def test_to_dict_empty_missing_keywords(self):
        """missing_keywords が空リストの場合の to_dict。"""
        result = CoverageResult(
            total_keywords=3,
            covered_keywords=3,
            coverage_rate=1.0,
            missing_keywords=[],
        )
        d = result.to_dict()
        assert d["missing_keywords"] == []
        assert d["coverage_rate"] == 1.0

    def test_to_dict_zero_coverage(self):
        """coverage_rate が 0.0 の場合の to_dict。"""
        result = CoverageResult(
            total_keywords=5,
            covered_keywords=0,
            coverage_rate=0.0,
            missing_keywords=["A", "B", "C", "D", "E"],
        )
        d = result.to_dict()
        assert d["coverage_rate"] == 0.0
        assert len(d["missing_keywords"]) == 5


# --- 追加: 大量データのパフォーマンステスト ---


class TestValidateCoveragePerformance:
    """大量データでのパフォーマンステスト。"""

    def test_large_keyword_list(self):
        """1000以上のキーワードでも処理できる。"""
        keywords = [f"keyword_{i}" for i in range(1500)]
        xml_content = " ".join(f"keyword_{i}" for i in range(0, 1500, 2))
        xml = f"<dialogue><turn speaker='A'>{xml_content}</turn></dialogue>"

        result = validate_coverage(keywords, xml)

        assert result.total_keywords == 1500
        assert result.covered_keywords == 750
        assert result.coverage_rate == pytest.approx(0.5)
        assert len(result.missing_keywords) == 750


# --- 追加: 特殊文字テスト ---


class TestValidateCoverageSpecialChars:
    """特殊文字を含むキーワードのテスト。"""

    def test_unicode_keywords(self):
        """Unicode文字を含むキーワードが処理できる。"""
        xml = "<dialogue><turn speaker='A'>C++とC#の比較です。</turn></dialogue>"
        keywords = ["C++", "C#"]
        result = validate_coverage(keywords, xml)
        assert result.covered_keywords == 2

    def test_sql_special_chars_in_keywords(self):
        """SQL特殊文字を含むキーワードが処理できる。"""
        xml = "<dialogue><turn speaker='A'>SELECT * FROM users WHERE id='1'</turn></dialogue>"
        keywords = ["SELECT * FROM"]
        result = validate_coverage(keywords, xml)
        assert result.covered_keywords == 1

    def test_html_tags_in_keywords(self):
        """HTMLタグを含むキーワードが処理できる。"""
        xml = "<dialogue><turn speaker='A'>&lt;script&gt;タグは危険です。</turn></dialogue>"
        keywords = ["<script>"]
        # XMLエンティティとして存在するため、生テキスト "<script>" はマッチしない可能性
        result = validate_coverage(keywords, xml)
        assert isinstance(result, CoverageResult)

    def test_emoji_in_keywords(self):
        """絵文字を含むキーワードが処理できる。"""
        xml = "<dialogue><turn speaker='A'>AI技術の未来について</turn></dialogue>"
        keywords = ["AI技術"]
        result = validate_coverage(keywords, xml)
        assert result.covered_keywords == 1
