"""Tests for llm_reading_generator.py term extraction filtering.

Phase 1 RED Tests - Issue #10: フィルタ関数追加

Target functions:
- src/llm_reading_generator.py::_should_exclude() (未実装)
- src/llm_reading_generator.py::extract_technical_terms()

Test coverage:
- T001: _should_exclude() フィルタ関数のユニットテスト
- T002: extract_technical_terms() のフィルタ適用テスト
"""

from src.llm_reading_generator import extract_technical_terms

# =============================================================================
# T001: _should_exclude() フィルタ関数のユニットテスト
# =============================================================================


class TestShouldExcludeFilter:
    """_should_exclude() のフィルタロジックをテスト"""

    def test_url_with_www_prefix_is_excluded(self):
        """URL (www.* prefix) が除外される"""
        from src.llm_reading_generator import _should_exclude

        assert _should_exclude("www.example.com") is True
        assert _should_exclude("www.google.com") is True

    def test_url_with_http_prefix_is_excluded(self):
        """URL (http* prefix) が除外される"""
        from src.llm_reading_generator import _should_exclude

        assert _should_exclude("https://example.com") is True
        assert _should_exclude("http://foo.bar") is True

    def test_isbn_is_excluded(self):
        """ISBN が除外される"""
        from src.llm_reading_generator import _should_exclude

        assert _should_exclude("ISBN978-4-7981-8771-6") is True
        assert _should_exclude("ISBN-13") is True

    def test_chapter_number_is_excluded(self):
        """章番号 (No.N 形式) が除外される"""
        from src.llm_reading_generator import _should_exclude

        assert _should_exclude("No.21") is True
        assert _should_exclude("No.21-1") is True
        assert _should_exclude("No.1") is True

    def test_stopwords_are_excluded(self):
        """英語ストップワードが除外される"""
        from src.llm_reading_generator import _should_exclude

        # 一般ストップワード
        assert _should_exclude("and") is True
        assert _should_exclude("of") is True
        assert _should_exclude("in") is True
        assert _should_exclude("the") is True

        # URL関連ワード
        assert _should_exclude("https") is True
        assert _should_exclude("http") is True

    def test_short_lowercase_terms_are_excluded(self):
        """2文字以下の小文字のみ用語が除外される"""
        from src.llm_reading_generator import _should_exclude

        assert _should_exclude("eb") is True
        assert _should_exclude("cm") is True
        assert _should_exclude("a") is True
        assert _should_exclude("so") is True

    def test_valid_technical_terms_are_not_excluded(self):
        """有効な技術用語は除外されない"""
        from src.llm_reading_generator import _should_exclude

        assert _should_exclude("API") is False
        assert _should_exclude("Docker") is False
        assert _should_exclude("REST") is False
        assert _should_exclude("JavaScript") is False
        assert _should_exclude("HTTP/2") is False
        assert _should_exclude("OAuth2.0") is False

    def test_mixed_case_stopwords_are_excluded(self):
        """大文字・小文字混在のストップワードも除外される"""
        from src.llm_reading_generator import _should_exclude

        assert _should_exclude("AND") is True
        assert _should_exclude("The") is True
        assert _should_exclude("Of") is True

    def test_three_letter_lowercase_terms_are_not_excluded(self):
        """3文字以上の小文字用語は除外されない（技術用語の可能性）"""
        from src.llm_reading_generator import _should_exclude

        # ストップワードでなければ除外されない
        assert _should_exclude("api") is False
        assert _should_exclude("sql") is False
        assert _should_exclude("npm") is False


# =============================================================================
# T002: extract_technical_terms() のフィルタ適用テスト
# =============================================================================


class TestExtractTechnicalTermsWithFilter:
    """extract_technical_terms() がフィルタを正しく適用することをテスト"""

    def test_extract_terms_excludes_urls(self):
        """URL が除外されて技術用語のみ抽出される"""
        text = "Use API and REST at www.example.com and https://github.com"
        result = extract_technical_terms(text)

        # 技術用語は含まれる
        assert "API" in result
        assert "REST" in result

        # URL は除外される
        assert "www.example.com" not in result
        assert "https://github.com" not in result
        assert "github.com" not in result

    def test_extract_terms_excludes_isbn(self):
        """ISBN が除外される"""
        text = "Read ISBN978-4-7981-8771-6 about Docker and Kubernetes"
        result = extract_technical_terms(text)

        # 技術用語は含まれる
        assert "Docker" in result
        assert "Kubernetes" in result

        # ISBN は除外される
        assert "ISBN978-4-7981-8771-6" not in result

    def test_extract_terms_excludes_chapter_numbers(self):
        """章番号が除外される"""
        text = "Chapter No.21 covers API design and No.22 covers REST"
        result = extract_technical_terms(text)

        # 技術用語は含まれる
        assert "API" in result
        assert "REST" in result

        # 章番号は除外される
        assert "No.21" not in result
        assert "No.22" not in result

    def test_extract_terms_excludes_stopwords(self):
        """英語ストップワードが除外される"""
        text = "Use API and REST in the cloud with Docker"
        result = extract_technical_terms(text)

        # 技術用語は含まれる
        assert "API" in result
        assert "REST" in result
        assert "Docker" in result

        # ストップワードは除外される
        assert "and" not in result
        assert "in" not in result
        assert "the" not in result
        assert "with" not in result

    def test_extract_terms_excludes_short_lowercase(self):
        """2文字以下の小文字用語が除外される"""
        text = "The eb cm API is used for db operations"
        result = extract_technical_terms(text)

        # 技術用語は含まれる
        assert "API" in result

        # 2文字以下の小文字は除外される
        assert "eb" not in result
        assert "cm" not in result
        assert "db" not in result

    def test_extract_terms_complex_mixed_content(self):
        """複雑な混在コンテンツから正しくフィルタリングされる"""
        text = """
        Visit www.example.com to learn about API and REST.
        Read ISBN978-4-123-45678-9 for more info.
        Chapter No.21 covers Docker, Kubernetes, and microservices.
        Use https protocol in production.
        """
        result = extract_technical_terms(text)

        # 有効な技術用語のみ含まれる
        valid_terms = {"API", "REST", "Docker", "Kubernetes"}
        assert valid_terms.issubset(set(result))

        # ノイズは除外される
        noise = {
            "www.example.com",
            "ISBN978-4-123-45678-9",
            "No.21",
            "and",
            "in",
            "for",
            "https",
        }
        assert noise.isdisjoint(set(result))

    def test_extract_terms_preserves_order_after_filtering(self):
        """フィルタ適用後も出現順序が保持される"""
        text = "First API then REST and finally Docker"
        result = extract_technical_terms(text)

        # 順序を確認（ストップワード除外後）
        expected_order = ["API", "REST", "Docker"]
        # 結果の中で expected_order の順序が保たれていることを確認
        filtered_result = [term for term in result if term in expected_order]
        assert filtered_result == expected_order

    def test_extract_terms_empty_after_filtering(self):
        """全てフィルタされた場合は空リストが返る"""
        text = "and the of in at www.example.com"
        result = extract_technical_terms(text)

        assert result == []

    def test_extract_terms_case_sensitivity_in_technical_terms(self):
        """技術用語の大文字小文字は保持される"""
        text = "Use JavaScript and TypeScript with Node.js"
        result = extract_technical_terms(text)

        # 元の大文字小文字が保持される
        assert "JavaScript" in result
        assert "TypeScript" in result
        assert "Node.js" in result

        # ストップワードは除外
        assert "and" not in result
        assert "with" not in result
