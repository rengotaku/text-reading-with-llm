"""Tests for URL cleaning functionality.

Phase 2 RED Tests - US1: URLの除去・簡略化
Tests for _clean_urls function that processes Markdown links and bare URLs.
"""

from src.text_cleaner import _clean_urls


class TestCleanUrlsMarkdownLink:
    """Test Markdown link processing: [text](url) -> text"""

    def test_clean_urls_markdown_link_basic(self):
        """Markdownリンクからリンクテキストのみを残す"""
        input_text = "詳細は[こちら](https://example.com)を参照"
        expected = "詳細はこちらを参照"

        result = _clean_urls(input_text)

        assert result == expected, (
            f"Markdownリンクのリンクテキストのみが残るべき: got '{result}', expected '{expected}'"
        )

    def test_clean_urls_markdown_link_with_path(self):
        """パス付きURLでもリンクテキストのみを残す"""
        input_text = "参考資料は[SRE NEXT](https://sre-next.dev/2024/schedule)です"
        expected = "参考資料はSRE NEXTです"

        result = _clean_urls(input_text)

        assert result == expected


class TestCleanUrlsUrlAsLinkText:
    """Test when URL itself is the link text: [url](url) -> ウェブサイト"""

    def test_clean_urls_url_as_link_text_replaced_with_website(self):
        """URLがリンクテキストの場合は「ウェブサイト」に置換"""
        input_text = "[https://example.com](https://example.com)をクリック"
        expected = "ウェブサイトをクリック"

        result = _clean_urls(input_text)

        assert result == expected, (
            f"URLがリンクテキストの場合は「ウェブサイト」に置換されるべき: got '{result}', expected '{expected}'"
        )

    def test_clean_urls_url_as_link_text_with_path(self):
        """パス付きURLがリンクテキストの場合も「ウェブサイト」に置換"""
        input_text = "詳細は[https://example.com/docs](https://example.com/docs)を参照"
        expected = "詳細はウェブサイトを参照"

        result = _clean_urls(input_text)

        assert result == expected


class TestCleanUrlsBareUrl:
    """Test bare URL replacement: https://... -> ウェブサイト"""

    def test_clean_urls_bare_url_replaced_with_website(self):
        """裸のURLは「ウェブサイト」に置換"""
        input_text = "アクセス先はhttps://example.com/path?query=1です"
        expected = "アクセス先はウェブサイトです"

        result = _clean_urls(input_text)

        assert result == expected, f"裸のURLは「ウェブサイト」に置換されるべき: got '{result}', expected '{expected}'"

    def test_clean_urls_bare_url_http(self):
        """HTTPプロトコルのURLも「ウェブサイト」に置換"""
        input_text = "古いサイトはhttp://legacy.example.comにあります"
        expected = "古いサイトはウェブサイトにあります"

        result = _clean_urls(input_text)

        assert result == expected

    def test_clean_urls_bare_url_with_fragment(self):
        """フラグメント付きURLも「ウェブサイト」に置換"""
        input_text = "セクションはhttps://docs.example.com/guide#section-1を参照"
        expected = "セクションはウェブサイトを参照"

        result = _clean_urls(input_text)

        assert result == expected


class TestCleanUrlsMultipleUrls:
    """Test multiple URLs in single text"""

    def test_clean_urls_multiple_markdown_links(self):
        """複数のMarkdownリンクを処理"""
        input_text = "[リンク1](https://a.com)と[リンク2](https://b.com)がある"
        expected = "リンク1とリンク2がある"

        result = _clean_urls(input_text)

        assert result == expected, f"複数のMarkdownリンクを正しく処理すべき: got '{result}', expected '{expected}'"

    def test_clean_urls_mixed_markdown_and_bare(self):
        """Markdownリンクと裸URLの混在"""
        input_text = "[公式サイト](https://official.com)とhttps://example.comを参照"
        expected = "公式サイトとウェブサイトを参照"

        result = _clean_urls(input_text)

        assert result == expected

    def test_clean_urls_multiple_bare_urls(self):
        """複数の裸URLがそれぞれ「ウェブサイト」に置換"""
        input_text = "サイトAはhttps://a.com、サイトBはhttps://b.comです"
        expected = "サイトAはウェブサイト、サイトBはウェブサイトです"

        result = _clean_urls(input_text)

        assert result == expected

    def test_clean_urls_multiple_consecutive_bare_urls(self):
        """連続する複数の裸URLがそれぞれ個別に置換される"""
        input_text = "参考: https://example.com https://another.com を参照"
        expected = "参考: ウェブサイト ウェブサイト を参照"

        result = _clean_urls(input_text)

        assert result == expected


class TestCleanUrlsIdempotent:
    """Test idempotency: processing already-cleaned text should not change it"""

    def test_clean_urls_idempotent_no_urls(self):
        """URLのないテキストは変化しない"""
        input_text = "これはURLを含まないテキストです"
        expected = "これはURLを含まないテキストです"

        result = _clean_urls(input_text)

        assert result == expected, f"URLのないテキストは変化すべきでない: got '{result}', expected '{expected}'"

    def test_clean_urls_idempotent_already_processed(self):
        """処理済みテキストを再処理しても変化しない"""
        original = "[リンク](https://example.com)を参照"
        first_pass = _clean_urls(original)
        second_pass = _clean_urls(first_pass)

        assert first_pass == second_pass, (
            f"冪等性が保証されるべき: first pass: '{first_pass}', second pass: '{second_pass}'"
        )

    def test_clean_urls_idempotent_plain_text(self):
        """プレーンテキストの冪等性"""
        input_text = "リンクとウェブサイトを参照"  # Already processed result

        result = _clean_urls(input_text)

        assert result == input_text


class TestCleanUrlsTrailingPunctuation:
    """Test URL with trailing punctuation: punctuation should be preserved"""

    def test_clean_urls_bare_url_followed_by_period(self):
        """URL直後の句点は保持される"""
        input_text = "詳細はhttps://example.comを参照。次の項目へ"
        expected = "詳細はウェブサイトを参照。次の項目へ"

        result = _clean_urls(input_text)

        assert result == expected, f"URL後の句点は保持されるべき: got '{result}', expected '{expected}'"

    def test_clean_urls_bare_url_followed_by_comma(self):
        """URL直後の読点は保持される"""
        input_text = "https://example.com、これは参考サイトです"
        expected = "ウェブサイト、これは参考サイトです"

        result = _clean_urls(input_text)

        assert result == expected

    def test_clean_urls_bare_url_at_end_of_sentence(self):
        """文末のURLが「ウェブサイト」に置換される"""
        input_text = "公式サイトはhttps://example.com"
        expected = "公式サイトはウェブサイト"

        result = _clean_urls(input_text)

        assert result == expected


class TestCleanUrlsEdgeCases:
    """Edge cases and special scenarios"""

    def test_clean_urls_empty_string(self):
        """空文字列の処理"""
        result = _clean_urls("")
        assert result == ""

    def test_clean_urls_whitespace_only(self):
        """空白のみのテキスト"""
        result = _clean_urls("   ")
        assert result == "   "

    def test_clean_urls_long_link_text(self):
        """長いリンクテキストの処理"""
        input_text = "[これは非常に長いリンクテキストで五十文字を超えることがありますがそれでも正しく処理されるべきです](https://example.com)"
        expected = "これは非常に長いリンクテキストで五十文字を超えることがありますがそれでも正しく処理されるべきです"

        result = _clean_urls(input_text)

        assert result == expected

    def test_clean_urls_japanese_and_english_mixed_link_text(self):
        """日本語と英語が混在するリンクテキスト"""
        input_text = "[SRE NEXTカンファレンス2024](https://sre-next.dev/2024)に参加"
        expected = "SRE NEXTカンファレンス2024に参加"

        result = _clean_urls(input_text)

        assert result == expected

    def test_clean_urls_url_with_japanese_characters(self):
        """URLに日本語が含まれる場合"""
        input_text = "詳細は[ガイド](https://example.com/日本語/ページ)を参照"
        expected = "詳細はガイドを参照"

        result = _clean_urls(input_text)

        assert result == expected
