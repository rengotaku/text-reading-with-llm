"""プロンプトファイルの読み込みユーティリティ。

プロンプトファイルを読み込み、プレースホルダーを置換して
システムメッセージとユーザーメッセージを返す。

プロンプトファイル形式:
  [SYSTEM]
  システムメッセージ
  [USER]
  ユーザーメッセージ（{placeholder}形式で置換可能）
"""

import re
from pathlib import Path

# プロンプトディレクトリのパス
PROMPTS_DIR: Path = Path(__file__).parent / "prompts"


class PromptLoadError(Exception):
    """プロンプト読み込みエラー。"""


def load_prompt(name: str, **kwargs: str) -> tuple[str, str]:
    """プロンプトファイルを読み込み、プレースホルダーを置換する。

    Args:
        name: プロンプト名（拡張子なし）
        **kwargs: プレースホルダー置換用のキーワード引数

    Returns:
        (system_message, user_message) のタプル

    Raises:
        PromptLoadError: ファイルが見つからない、または形式が不正な場合

    Example:
        >>> system, user = load_prompt(
        ...     "generate_dialogue",
        ...     a_name="教授",
        ...     b_name="助手",
        ...     full_context="テキスト内容",
        ... )
    """
    prompt_path = PROMPTS_DIR / f"{name}.txt"

    if not prompt_path.exists():
        raise PromptLoadError(f"プロンプトファイルが見つかりません: {prompt_path}")

    content = prompt_path.read_text(encoding="utf-8")

    # [SYSTEM] と [USER] セクションを分割（順序も検証）
    if "[SYSTEM]" not in content or "[USER]" not in content:
        raise PromptLoadError(f"プロンプトファイルの形式が不正です（[SYSTEM]と[USER]が必要）: {prompt_path}")

    if content.index("[SYSTEM]") > content.index("[USER]"):
        raise PromptLoadError(f"[SYSTEM]は[USER]より前に配置してください: {prompt_path}")

    parts = content.split("[USER]")
    if len(parts) != 2:
        raise PromptLoadError(f"[USER]セクションが複数あります: {prompt_path}")

    system_part = parts[0].replace("[SYSTEM]", "").strip()
    user_part = parts[1].strip()

    # プレースホルダーを置換
    for key, value in kwargs.items():
        placeholder = "{" + key + "}"
        system_part = system_part.replace(placeholder, value)
        user_part = user_part.replace(placeholder, value)

    # 未置換のプレースホルダーをチェック
    unreplaced = re.findall(r"\{[a-z_]+\}", system_part + user_part)
    if unreplaced:
        raise PromptLoadError(f"未置換のプレースホルダーがあります: {unreplaced} in {prompt_path}")

    return system_part, user_part


def get_available_prompts() -> list[str]:
    """利用可能なプロンプト名のリストを返す。

    Returns:
        プロンプト名のリスト（拡張子なし）
    """
    if not PROMPTS_DIR.exists():
        return []

    return [p.stem for p in PROMPTS_DIR.glob("*.txt")]
