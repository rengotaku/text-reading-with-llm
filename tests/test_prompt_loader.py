"""prompt_loader モジュールのテスト。"""

import pytest

from src.prompt_loader import (
    PROMPTS_DIR,
    PromptLoadError,
    get_available_prompts,
    load_prompt,
)


class TestLoadPrompt:
    """load_prompt関数のテスト。"""

    def test_load_analyze_structure_prompt(self):
        """analyze_structure プロンプトが読み込める。"""
        system, user = load_prompt("analyze_structure", paragraphs_text="1. テスト段落")
        assert "構造分析" in system or "分類" in system
        assert "テスト段落" in user

    def test_load_generate_introduction_prompt(self):
        """generate_introduction プロンプトが読み込める。"""
        system, user = load_prompt("generate_introduction", original_text="テストテキスト")
        assert "ナレーター" in system or "導入" in system
        assert "テストテキスト" in user

    def test_load_generate_conclusion_prompt(self):
        """generate_conclusion プロンプトが読み込める。"""
        system, user = load_prompt("generate_conclusion", original_text="テストテキスト")
        assert "ナレーター" in system or "結論" in system
        assert "テストテキスト" in user

    def test_load_generate_dialogue_prompt(self):
        """generate_dialogue プロンプトが読み込める。"""
        system, user = load_prompt(
            "generate_dialogue",
            a_name="教授",
            b_name="助手",
            a_role="解説役",
            b_role="聞き役",
            full_context="テストコンテンツ",
        )
        assert "対話" in system or "会話" in system
        assert "教授" in user
        assert "助手" in user
        assert "テストコンテンツ" in user

    def test_load_nonexistent_prompt_raises_error(self):
        """存在しないプロンプトでエラー。"""
        with pytest.raises(PromptLoadError) as exc_info:
            load_prompt("nonexistent_prompt")
        assert "見つかりません" in str(exc_info.value)

    def test_placeholder_replacement(self):
        """プレースホルダーが正しく置換される。"""
        system, user = load_prompt("generate_introduction", original_text="置換テスト文字列")
        assert "{original_text}" not in user
        assert "置換テスト文字列" in user

    def test_multiple_placeholder_replacement(self):
        """複数のプレースホルダーが正しく置換される。"""
        system, user = load_prompt(
            "generate_dialogue",
            a_name="A名前",
            b_name="B名前",
            a_role="A役割",
            b_role="B役割",
            full_context="コンテキスト",
        )
        assert "{a_name}" not in user
        assert "{b_name}" not in user
        assert "A名前" in user
        assert "B名前" in user

    def test_missing_placeholder_raises_error(self):
        """必要なプレースホルダーが不足している場合エラー。"""
        with pytest.raises(PromptLoadError) as exc_info:
            # generate_dialogue は5つのプレースホルダーが必要だが1つだけ渡す
            load_prompt("generate_dialogue", a_name="教授")
        assert "未置換のプレースホルダー" in str(exc_info.value)


class TestGetAvailablePrompts:
    """get_available_prompts関数のテスト。"""

    def test_returns_list(self):
        """リストを返す。"""
        result = get_available_prompts()
        assert isinstance(result, list)

    def test_contains_expected_prompts(self):
        """期待されるプロンプトが含まれる。"""
        result = get_available_prompts()
        assert "analyze_structure" in result
        assert "generate_introduction" in result
        assert "generate_conclusion" in result
        assert "generate_dialogue" in result

    def test_returns_names_without_extension(self):
        """拡張子なしの名前を返す。"""
        result = get_available_prompts()
        for name in result:
            assert not name.endswith(".txt")


class TestPromptsDirectory:
    """プロンプトディレクトリのテスト。"""

    def test_prompts_dir_exists(self):
        """プロンプトディレクトリが存在する。"""
        assert PROMPTS_DIR.exists()

    def test_prompts_dir_contains_txt_files(self):
        """プロンプトディレクトリに.txtファイルが含まれる。"""
        txt_files = list(PROMPTS_DIR.glob("*.txt"))
        assert len(txt_files) >= 4

    def test_all_prompts_have_system_section(self):
        """全プロンプトに[SYSTEM]セクションがある。"""
        for prompt_file in PROMPTS_DIR.glob("*.txt"):
            content = prompt_file.read_text(encoding="utf-8")
            assert "[SYSTEM]" in content, f"{prompt_file.name}に[SYSTEM]がありません"

    def test_all_prompts_have_user_section(self):
        """全プロンプトに[USER]セクションがある。"""
        for prompt_file in PROMPTS_DIR.glob("*.txt"):
            content = prompt_file.read_text(encoding="utf-8")
            assert "[USER]" in content, f"{prompt_file.name}に[USER]がありません"
