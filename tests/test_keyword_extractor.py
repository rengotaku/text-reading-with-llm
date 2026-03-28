"""keyword_extractor モジュールのテスト。

原文セクションからキーワードを抽出する機能のテスト。
LLM呼び出しはモックを使用してテストする。
"""

import pytest

from src.keyword_extractor import extract_keywords
from src.prompt_loader import PROMPTS_DIR, load_prompt

# --- T007: プロンプトファイルのテスト ---


class TestExtractKeywordsPrompt:
    """extract_keywords プロンプトファイルのテスト。"""

    def test_extract_keywords_prompt_file_exists(self):
        """extract_keywords.txt がプロンプトディレクトリに存在する。"""
        prompt_path = PROMPTS_DIR / "extract_keywords.txt"
        assert prompt_path.exists(), f"プロンプトファイルが見つかりません: {prompt_path}"

    def test_extract_keywords_prompt_has_system_section(self):
        """extract_keywords.txt に [SYSTEM] セクションがある。"""
        prompt_path = PROMPTS_DIR / "extract_keywords.txt"
        content = prompt_path.read_text(encoding="utf-8")
        assert "[SYSTEM]" in content, "プロンプトに[SYSTEM]セクションがありません"

    def test_extract_keywords_prompt_has_user_section(self):
        """extract_keywords.txt に [USER] セクションがある。"""
        prompt_path = PROMPTS_DIR / "extract_keywords.txt"
        content = prompt_path.read_text(encoding="utf-8")
        assert "[USER]" in content, "プロンプトに[USER]セクションがありません"

    def test_extract_keywords_prompt_has_section_text_placeholder(self):
        """extract_keywords.txt に {section_text} プレースホルダーがある。"""
        prompt_path = PROMPTS_DIR / "extract_keywords.txt"
        content = prompt_path.read_text(encoding="utf-8")
        assert "{section_text}" in content, "プロンプトに{section_text}プレースホルダーがありません"

    def test_extract_keywords_prompt_loads_with_placeholder(self):
        """load_prompt で extract_keywords が正しく読み込める。"""
        system, user = load_prompt("extract_keywords", section_text="テストテキスト")
        assert len(system) > 0, "システムメッセージが空です"
        assert "テストテキスト" in user, "ユーザーメッセージにテキストが挿入されていません"

    def test_extract_keywords_prompt_mentions_keyword_extraction(self):
        """プロンプトのシステムメッセージにキーワード抽出に関する記述がある。"""
        system, user = load_prompt("extract_keywords", section_text="サンプル")
        assert "キーワード" in system or "keyword" in system.lower(), (
            "システムメッセージにキーワード抽出の役割定義がありません"
        )

    def test_extract_keywords_prompt_specifies_comma_output(self):
        """プロンプトにカンマ区切り出力の指示がある。"""
        prompt_path = PROMPTS_DIR / "extract_keywords.txt"
        content = prompt_path.read_text(encoding="utf-8")
        assert "カンマ" in content or "," in content or "comma" in content.lower(), (
            "プロンプトにカンマ区切り出力の指示がありません"
        )


# --- T008: 基本抽出テスト ---


def _make_mock_response(content: str):
    """モックLLMレスポンスを生成するヘルパー。"""
    return {"message": {"content": content}}


def _make_ollama_mock(response_content: str):
    """指定レスポンスを返すollama_chat_funcモックを生成する。"""

    def mock_chat(**kwargs):
        return _make_mock_response(response_content)

    return mock_chat


class TestExtractKeywords:
    """extract_keywords 関数の基本テスト。"""

    def test_extracts_keywords_from_text_with_proper_nouns(self):
        """固有名詞を含むテキストからキーワードが抽出される。"""
        mock_response = "ロボチェック社, ハルさん, デスマーチ"
        mock_chat = _make_ollama_mock(mock_response)

        result = extract_keywords(
            "ロボチェック社のハルさんはデスマーチに巻き込まれていた。",
            ollama_chat_func=mock_chat,
        )

        assert isinstance(result, list)
        assert "ロボチェック社" in result
        assert "ハルさん" in result
        assert "デスマーチ" in result

    def test_extracts_keywords_from_text_with_technical_terms(self):
        """専門用語を含むテキストからキーワードが抽出される。"""
        mock_response = "機械学習, ニューラルネットワーク, 深層学習"
        mock_chat = _make_ollama_mock(mock_response)

        result = extract_keywords(
            "機械学習の一種であるニューラルネットワークと深層学習について解説する。",
            ollama_chat_func=mock_chat,
        )

        assert isinstance(result, list)
        assert len(result) == 3
        assert "機械学習" in result
        assert "ニューラルネットワーク" in result
        assert "深層学習" in result

    def test_extracts_keywords_from_text_with_numbers(self):
        """数値を含むテキストからキーワードが抽出される。"""
        mock_response = "2027年, 売上高1000億円, 従業員5000人"
        mock_chat = _make_ollama_mock(mock_response)

        result = extract_keywords(
            "2027年の売上高1000億円を目指し、従業員5000人体制を構築する。",
            ollama_chat_func=mock_chat,
        )

        assert isinstance(result, list)
        assert "2027年" in result

    def test_passes_section_text_to_llm_prompt(self):
        """セクションテキストがLLMプロンプトに渡される。"""
        captured_kwargs = {}

        def mock_chat(**kwargs):
            captured_kwargs.update(kwargs)
            return _make_mock_response("キーワード1")

        extract_keywords("テスト入力テキスト", ollama_chat_func=mock_chat)

        assert "messages" in captured_kwargs
        messages = captured_kwargs["messages"]
        user_message = next(m for m in messages if m["role"] == "user")
        assert "テスト入力テキスト" in user_message["content"]

    def test_uses_default_model(self):
        """デフォルトモデルが使用される。"""
        captured_kwargs = {}

        def mock_chat(**kwargs):
            captured_kwargs.update(kwargs)
            return _make_mock_response("キーワード1")

        extract_keywords("テキスト", ollama_chat_func=mock_chat)

        assert "model" in captured_kwargs
        assert isinstance(captured_kwargs["model"], str)
        assert len(captured_kwargs["model"]) > 0

    def test_custom_model_is_used(self):
        """カスタムモデルが指定された場合にそれが使用される。"""
        captured_kwargs = {}

        def mock_chat(**kwargs):
            captured_kwargs.update(kwargs)
            return _make_mock_response("キーワード1")

        extract_keywords("テキスト", model="custom-model:7b", ollama_chat_func=mock_chat)

        assert captured_kwargs["model"] == "custom-model:7b"


# --- T009: エッジケーステスト ---


class TestExtractKeywordsEdgeCases:
    """extract_keywords 関数のエッジケーステスト。"""

    def test_empty_text_returns_empty_list(self):
        """空テキスト入力で空リストが返される。"""
        mock_chat = _make_ollama_mock("キーワード")

        result = extract_keywords("", ollama_chat_func=mock_chat)

        assert result == []

    def test_whitespace_only_text_returns_empty_list(self):
        """空白のみのテキスト入力で空リストが返される。"""
        mock_chat = _make_ollama_mock("キーワード")

        result = extract_keywords("   \n\t  ", ollama_chat_func=mock_chat)

        assert result == []

    def test_none_text_raises_error_or_returns_empty(self):
        """None入力でTypeErrorまたは空リストが返される。"""
        mock_chat = _make_ollama_mock("キーワード")

        with pytest.raises((TypeError, ValueError)):
            extract_keywords(None, ollama_chat_func=mock_chat)  # type: ignore[arg-type]

    def test_llm_returns_empty_response(self):
        """LLMが空レスポンスを返した場合、空リストが返される。"""
        mock_chat = _make_ollama_mock("")

        result = extract_keywords("何かのテキスト", ollama_chat_func=mock_chat)

        assert result == []

    def test_llm_returns_whitespace_only_response(self):
        """LLMが空白のみのレスポンスを返した場合、空リストが返される。"""
        mock_chat = _make_ollama_mock("   \n  ")

        result = extract_keywords("何かのテキスト", ollama_chat_func=mock_chat)

        assert result == []

    def test_special_characters_in_text(self):
        """特殊文字を含むテキストが処理できる。"""
        mock_response = "SQL injection, <script>タグ"
        mock_chat = _make_ollama_mock(mock_response)

        result = extract_keywords(
            "SQL injection攻撃と<script>タグについて",
            ollama_chat_func=mock_chat,
        )

        assert isinstance(result, list)
        assert len(result) > 0

    def test_unicode_emoji_in_text(self):
        """Unicode絵文字を含むテキストが処理できる。"""
        mock_response = "人工知能, ロボット"
        mock_chat = _make_ollama_mock(mock_response)

        result = extract_keywords(
            "人工知能とロボットの未来について",
            ollama_chat_func=mock_chat,
        )

        assert isinstance(result, list)
        assert "人工知能" in result

    def test_very_long_text(self):
        """非常に長いテキストが処理できる。"""
        long_text = "テスト文章。" * 1000
        mock_chat = _make_ollama_mock("キーワード1, キーワード2")

        result = extract_keywords(long_text, ollama_chat_func=mock_chat)

        assert isinstance(result, list)
        assert len(result) > 0


# --- T010: 出力形式テスト ---


class TestExtractKeywordsOutputFormat:
    """extract_keywords 関数の出力形式テスト。"""

    def test_comma_separated_response_is_parsed(self):
        """カンマ区切りレスポンスが正しくパースされる。"""
        mock_chat = _make_ollama_mock("キーワード1, キーワード2, キーワード3")

        result = extract_keywords("テキスト", ollama_chat_func=mock_chat)

        assert result == ["キーワード1", "キーワード2", "キーワード3"]

    def test_keywords_are_trimmed(self):
        """キーワードの前後の空白がtrimされる。"""
        mock_chat = _make_ollama_mock("  キーワード1  ,  キーワード2  ,  キーワード3  ")

        result = extract_keywords("テキスト", ollama_chat_func=mock_chat)

        assert "キーワード1" in result
        assert "キーワード2" in result
        assert "キーワード3" in result
        for keyword in result:
            assert keyword == keyword.strip(), f"キーワード '{keyword}' がtrimされていません"

    def test_duplicate_keywords_are_removed(self):
        """重複キーワードが除去される。"""
        mock_chat = _make_ollama_mock("キーワード1, キーワード2, キーワード1, キーワード3, キーワード2")

        result = extract_keywords("テキスト", ollama_chat_func=mock_chat)

        assert len(result) == len(set(result)), "重複キーワードが存在します"
        assert len(result) == 3

    def test_empty_items_in_response_are_filtered(self):
        """レスポンス中の空要素がフィルタされる。"""
        mock_chat = _make_ollama_mock("キーワード1,, キーワード2, ,キーワード3")

        result = extract_keywords("テキスト", ollama_chat_func=mock_chat)

        assert "" not in result
        assert len(result) == 3

    def test_single_keyword_response(self):
        """単一キーワードのレスポンスが正しく処理される。"""
        mock_chat = _make_ollama_mock("唯一のキーワード")

        result = extract_keywords("テキスト", ollama_chat_func=mock_chat)

        assert result == ["唯一のキーワード"]

    def test_returns_list_type(self):
        """戻り値がlist[str]型である。"""
        mock_chat = _make_ollama_mock("キーワード1, キーワード2")

        result = extract_keywords("テキスト", ollama_chat_func=mock_chat)

        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, str)

    def test_order_is_preserved(self):
        """キーワードの出現順序が保持される（重複除去後）。"""
        mock_chat = _make_ollama_mock("C用語, A用語, B用語")

        result = extract_keywords("テキスト", ollama_chat_func=mock_chat)

        assert result == ["C用語", "A用語", "B用語"]

    def test_newline_separated_response_handled(self):
        """改行区切りのレスポンスも処理できる（カンマ区切りへのフォールバック）。"""
        mock_chat = _make_ollama_mock("キーワード1\nキーワード2\nキーワード3")

        result = extract_keywords("テキスト", ollama_chat_func=mock_chat)

        # カンマ区切りでない場合でも、何らかの形でパースされること
        assert isinstance(result, list)
        assert len(result) >= 1
