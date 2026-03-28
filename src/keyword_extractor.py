"""原文セクションからキーワードを抽出するモジュール。

LLMを使用してテキストから重要なキーワードを抽出する。
"""

import os
from typing import Any, Callable

from src.prompt_loader import load_prompt

# CI環境判定（ollamaのインポート前に判定）
_IS_CI = os.environ.get("CI", "").lower() in ("true", "1", "yes")
_OLLAMA_AVAILABLE = False
ollama: Any = None

if not _IS_CI:
    try:
        import ollama as _ollama  # noqa: E402

        ollama = _ollama
        _OLLAMA_AVAILABLE = True
    except ImportError:
        pass

# デフォルトモデル
DEFAULT_MODEL = "gpt-oss:20b"


def extract_keywords(
    section_text: str,
    model: str = DEFAULT_MODEL,
    ollama_chat_func: Callable[..., Any] | None = None,
) -> list[str]:
    """原文セクションからキーワードを抽出する。

    Args:
        section_text: キーワードを抽出する原文テキスト
        model: 使用するLLMモデル名
        ollama_chat_func: LLM呼び出し関数（テスト時にモックを注入可能）

    Returns:
        抽出されたキーワードのリスト（重複なし、空白trimあり）

    Raises:
        TypeError: section_text が None の場合
        ValueError: section_text が str 以外の型の場合
    """
    if section_text is None:
        raise TypeError("section_text は None にできません")

    if not isinstance(section_text, str):
        raise ValueError(f"section_text は str 型である必要があります: {type(section_text)}")

    # 空テキストまたは空白のみのテキストは空リストを返す
    if not section_text.strip():
        return []

    system, user = load_prompt("extract_keywords", section_text=section_text)

    if ollama_chat_func is None:
        ollama_chat_func = ollama.chat

    response = ollama_chat_func(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )

    raw_content: str = response["message"]["content"]

    # 空レスポンスや空白のみのレスポンスは空リストを返す
    if not raw_content.strip():
        return []

    # カンマ区切りでパース、trim、空要素除去、重複除去（出現順序保持）
    keywords = [kw.strip() for kw in raw_content.split(",")]
    keywords = [kw for kw in keywords if kw]

    # 重複除去（出現順序を保持）
    seen: set[str] = set()
    unique_keywords: list[str] = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)

    return unique_keywords
