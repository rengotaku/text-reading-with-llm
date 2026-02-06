"""Clean markdown text for TTS reading."""

import logging
import re
from dataclasses import dataclass
from pathlib import Path

from src.dict_manager import load_dict_from_content
from src.llm_reading_generator import apply_llm_readings
from src.mecab_reader import convert_to_kana
from src.number_normalizer import normalize_numbers
from src.punctuation_normalizer import normalize_punctuation
from src.reading_dict import apply_reading_rules

logger = logging.getLogger(__name__)

# LLM-generated dictionary (set per-book via init_for_content)
_LLM_READINGS: dict[str, str] = {}

# Enable/disable kanji → kana conversion via MeCab
ENABLE_KANJI_CONVERSION = True


def init_for_content(markdown_content: str) -> None:
    """Initialize the text cleaner for a specific book content.

    Loads the hash-based LLM dictionary for this content.

    Args:
        markdown_content: The full markdown content of the book
    """
    global _LLM_READINGS
    _LLM_READINGS = load_dict_from_content(markdown_content)
    if _LLM_READINGS:
        logger.info("Loaded LLM dictionary: %d entries", len(_LLM_READINGS))
    else:
        logger.info("No LLM dictionary found for this content")


@dataclass(frozen=True)
class Page:
    """A single page extracted from the book markdown."""

    number: int
    text: str


def split_into_pages(markdown: str) -> list[Page]:
    """Split book.md into pages based on page markers."""
    pattern = r"^--- Page (\d+) \(page_\d+\.png\) ---$"
    parts = re.split(pattern, markdown, flags=re.MULTILINE)

    pages = []
    # parts[0] is text before first marker (usually empty)
    # parts[1], parts[2] = page_number, page_content
    # parts[3], parts[4] = page_number, page_content ...
    for i in range(1, len(parts), 2):
        page_num = int(parts[i])
        raw_text = parts[i + 1] if i + 1 < len(parts) else ""
        cleaned = clean_page_text(raw_text)
        if cleaned.strip():
            pages.append(Page(number=page_num, text=cleaned))
    return pages


def clean_page_text(text: str) -> str:
    """Clean a single page's text for TTS consumption."""
    # Remove HTML comments (figure markers)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    # Remove figure description paragraphs (lines starting with 図は、)
    text = re.sub(r"^図は、.*$", "", text, flags=re.MULTILINE)

    # Remove page number markers like "1 / 1", "はじめに 1 / 3"
    text = re.sub(r"^.*?\d+\s*/\s*\d+\s*$", "", text, flags=re.MULTILINE)

    # Remove markdown heading markers but keep text
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

    # Remove bold/italic markers
    text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)

    # Remove horizontal rules
    text = re.sub(r"^---+\s*$", "", text, flags=re.MULTILINE)

    # Remove list markers (- or *)
    text = re.sub(r"^[\-\*]\s+", "", text, flags=re.MULTILINE)

    # Remove inline code backticks
    text = re.sub(r"`([^`]*)`", r"\1", text)

    # Remove code blocks
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

    # Remove trailing whitespace from lines
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)

    # Remove markdown line breaks (trailing double space)
    text = re.sub(r"  $", "", text, flags=re.MULTILINE)

    # Collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Apply TTS normalization and reading rules
    # 0. Punctuation normalization (add commas for natural reading)
    text = normalize_punctuation(text)
    # 1. Number normalization (123 → ひゃくにじゅうさん)
    text = normalize_numbers(text)
    # 2. Static dictionary (critical terms like SRE, API, AWS)
    text = apply_reading_rules(text)
    # 3. LLM-generated dictionary (additional terms)
    if _LLM_READINGS:
        text = apply_llm_readings(text, _LLM_READINGS)
    # 4. MeCab: Convert remaining kanji to kana
    if ENABLE_KANJI_CONVERSION:
        text = convert_to_kana(text)

    return text.strip()


def split_text_into_chunks(text: str, max_chars: int = 500) -> list[str]:
    """Split text into chunks suitable for TTS generation.

    Splits on sentence boundaries (。！？) to maintain natural reading flow.
    """
    if len(text) <= max_chars:
        return [text] if text.strip() else []

    chunks = []
    remaining = text

    while remaining:
        if len(remaining) <= max_chars:
            if remaining.strip():
                chunks.append(remaining.strip())
            break

        # Find the best split point within max_chars
        split_pos = _find_split_position(remaining, max_chars)
        chunk = remaining[:split_pos].strip()
        if chunk:
            chunks.append(chunk)
        remaining = remaining[split_pos:].strip()

    return chunks


def _find_split_position(text: str, max_chars: int) -> int:
    """Find the best position to split text, preferring sentence boundaries."""
    search_region = text[:max_chars]

    # Try Japanese sentence endings: 。！？
    for delimiter in ["。", "！", "？", "!", "?", "\n\n", "\n", "、", ","]:
        pos = search_region.rfind(delimiter)
        if pos > max_chars // 3:  # Don't split too early
            return pos + len(delimiter)

    # Fallback: split at max_chars
    return max_chars
