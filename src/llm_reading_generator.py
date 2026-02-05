"""Generate reading dictionary using LLM for technical terms."""

import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# Default dictionary file path
DEFAULT_DICT_PATH = Path(__file__).parent.parent / "data" / "llm_reading_dict.json"


def extract_technical_terms(text: str) -> list[str]:
    """Extract potential technical terms (alphabet-based) from text."""
    # Match sequences of ASCII letters, numbers, and common separators
    pattern = r"[A-Za-z][A-Za-z0-9\-_./]*[A-Za-z0-9]|[A-Z]{2,}"
    matches = re.findall(pattern, text)

    # Deduplicate while preserving order
    seen = set()
    unique_terms = []
    for term in matches:
        normalized = term.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique_terms.append(normalized)

    return unique_terms


def generate_readings_with_llm(
    terms: list[str],
    model: str = "gpt-oss:20b",
    ollama_chat_func=None,
) -> dict[str, str]:
    """Generate readings for terms using LLM.

    Args:
        terms: List of technical terms to convert
        model: Ollama model name
        ollama_chat_func: Function to call Ollama chat API

    Returns:
        Dictionary mapping terms to their katakana readings
    """
    if not terms:
        return {}

    # Build prompt
    terms_list = "\n".join(f"- {term}" for term in terms)
    prompt = f"""以下の技術用語・略語の日本語での読み方をカタカナで答えてください。
一般的に使われる読み方で、TTSで自然に聞こえる読みにしてください。

用語リスト:
{terms_list}

JSON形式で出力してください。例:
{{"SRE": "エスアールイー", "API": "エーピーアイ", "GitHub": "ギットハブ"}}

注意:
- 必ずカタカナで出力
- 略語は一文字ずつ読む（SRE→エスアールイー）
- 固有名詞は一般的な読み方で（Google→グーグル）
- 日本語として不自然な場合はそのまま出力しない

JSON出力:"""

    messages = [
        {"role": "system", "content": "あなたは技術用語の読み方を教える専門家です。正確なカタカナ読みを出力してください。"},
        {"role": "user", "content": prompt},
    ]

    if ollama_chat_func is None:
        raise ValueError("ollama_chat_func must be provided")

    response = ollama_chat_func(model=model, messages=messages)

    # Parse JSON response
    try:
        # Extract JSON from response
        response_text = response.get("message", {}).get("content", "")
        # Try to find JSON in the response
        json_match = re.search(r"\{[^{}]*\}", response_text, re.DOTALL)
        if json_match:
            readings = json.loads(json_match.group())
            return {k: v for k, v in readings.items() if isinstance(v, str)}
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning("Failed to parse LLM response: %s", e)

    return {}


def load_dictionary(path: Path = DEFAULT_DICT_PATH) -> dict[str, str]:
    """Load reading dictionary from file."""
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_dictionary(readings: dict[str, str], path: Path = DEFAULT_DICT_PATH) -> None:
    """Save reading dictionary to file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(readings, f, ensure_ascii=False, indent=2)
    logger.info("Saved %d readings to %s", len(readings), path)


def apply_llm_readings(text: str, readings: dict[str, str]) -> str:
    """Apply LLM-generated readings to text."""
    # Sort by length (longest first) to avoid partial replacements
    sorted_terms = sorted(readings.keys(), key=len, reverse=True)

    for term in sorted_terms:
        reading = readings[term]
        # Use word boundary-like pattern for ASCII terms
        pattern = rf"(?<![A-Za-z]){re.escape(term)}(?![A-Za-z])"
        text = re.sub(pattern, reading, text)

    return text
