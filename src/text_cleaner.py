"""Clean markdown text for TTS reading."""

import logging
import re
from dataclasses import dataclass

from src.dict_manager import load_dict_from_content
from src.llm_reading_generator import apply_llm_readings
from src.mecab_reader import convert_to_kana
from src.number_normalizer import normalize_numbers
from src.punctuation_normalizer import normalize_punctuation
from src.reading_dict import apply_reading_rules

logger = logging.getLogger(__name__)

# Placeholder for HEADING_MARKER during text cleaning
# Using a unique string that won't appear in normal text
_HEADING_PLACEHOLDER = "__HEADING_MARKER_PLACEHOLDER__"

# LLM-generated dictionary (set per-book via init_for_content)
_LLM_READINGS: dict[str, str] = {}

# Enable/disable kanji → kana conversion via MeCab
ENABLE_KANJI_CONVERSION = True

# URL patterns for cleaning (US1)
MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\([^)]+\)")
# Match bare URLs but stop before Japanese characters, parentheses, and brackets
BARE_URL_PATTERN = re.compile(r"https?://[^\s\u3000-\u9fff\uff00-\uffef）」』】\]]+")
URL_TEXT_PATTERN = re.compile(r"^https?://")

# Reference patterns for TTS normalization (US2/US3)
REFERENCE_PATTERNS = [
    (re.compile(r"図(\d+)[.．](\d+)"), r"ず\1の\2"),  # 図X.Y
    (re.compile(r"図(\d+)"), r"ず\1"),  # 図X
    (re.compile(r"表(\d+)[.．](\d+)"), r"ひょう\1の\2"),  # 表X.Y
    (re.compile(r"表(\d+)"), r"ひょう\1"),  # 表X
    (re.compile(r"注(\d+)[.．](\d+)"), r"ちゅう\1の\2"),  # 注X.Y
    (re.compile(r"注(\d+)"), r"ちゅう\1"),  # 注X
]

# Number prefix pattern (US2)
# No.X pattern (case insensitive)
NUMBER_PREFIX_PATTERN = re.compile(r"No\.(\d+)", re.IGNORECASE)

# Chapter pattern (US2)
# Chapter X pattern (case insensitive)
CHAPTER_PATTERN = re.compile(r"Chapter\s+(\d+)", re.IGNORECASE)

# ISBN patterns (US4)
# ISBN-13: 978/979 + 10 digits with optional hyphens
# ISBN-10: 10 digits/chars with optional hyphens (last char can be X)
ISBN_PATTERN = re.compile(
    r"[Ii][Ss][Bb][Nn]\s*"  # ISBN prefix (case insensitive)
    r"(?:"
    r"97[89][-\s]?\d[-\s]?\d{1,5}[-\s]?\d{1,7}[-\s]?\d"  # ISBN-13 with hyphens
    r"|97[89]\d{10}"  # ISBN-13 without hyphens
    r"|\d[-\s]?\d{1,5}[-\s]?\d{1,7}[-\s]?[\dXx]"  # ISBN-10 with hyphens
    r"|\d{9}[\dXx]"  # ISBN-10 without hyphens
    r")"
)

# Parenthetical patterns for English term removal (US5)
# Matches brackets containing only ASCII letters, numbers, spaces, hyphens, periods, commas
# But preserves brackets containing Japanese characters or empty content
PAREN_ENGLISH_FULL = re.compile(r"（[A-Za-z][A-Za-z0-9\s\-.,]*）")
PAREN_ENGLISH_HALF = re.compile(r"\([A-Za-z][A-Za-z0-9\s\-.,]*\)")

# Markdown cleanup patterns (compiled for performance)
HTML_COMMENT_PATTERN = re.compile(r"<!--.*?-->", flags=re.DOTALL)
FIGURE_DESC_PATTERN = re.compile(r"^図は、.*$", flags=re.MULTILINE)
PAGE_NUMBER_PATTERN = re.compile(r"^.*?\d+\s*/\s*\d+\s*$", flags=re.MULTILINE)
HEADING_PATTERN = re.compile(r"^#{1,6}\s+", flags=re.MULTILINE)
BOLD_ITALIC_PATTERN = re.compile(r"\*{1,3}(.*?)\*{1,3}")
HORIZONTAL_RULE_PATTERN = re.compile(r"^---+\s*$", flags=re.MULTILINE)
LIST_MARKER_PATTERN = re.compile(r"^[\-\*]\s+")
LIST_BLOCK_PATTERN = re.compile(r"(^[\-\*]\s+.+$\n?)+", flags=re.MULTILINE)
INLINE_CODE_PATTERN = re.compile(r"`([^`]*)`")
CODE_BLOCK_PATTERN = re.compile(r"```.*?```", flags=re.DOTALL)
TRAILING_WHITESPACE_PATTERN = re.compile(r"[ \t]+$", flags=re.MULTILINE)
DOUBLE_SPACE_PATTERN = re.compile(r"  $", flags=re.MULTILINE)
MULTIPLE_NEWLINES_PATTERN = re.compile(r"\n{3,}")


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


def _clean_urls(text: str) -> str:
    """Replace URLs with 'ウェブサイト' for TTS.

    - Markdown links: Keep link text, remove URL
    - URL as link text: Replace with 'ウェブサイト'
    - Bare URLs: Replace with 'ウェブサイト'
    """

    # Step 1: Handle Markdown links
    def replace_markdown_link(match):
        link_text = match.group(1)
        # If link text is a URL, replace with 'ウェブサイト'
        if URL_TEXT_PATTERN.match(link_text):
            return "ウェブサイト"
        return link_text

    text = MARKDOWN_LINK_PATTERN.sub(replace_markdown_link, text)

    # Step 2: Replace bare URLs with 'ウェブサイト'
    text = BARE_URL_PATTERN.sub("ウェブサイト", text)

    return text


def _normalize_references(text: str) -> str:
    """Normalize figure/table/note references for TTS.

    Converts:
    - 図X.Y → ずXのY
    - 表X.Y → ひょうXのY
    - 注X.Y → ちゅうXのY
    """
    for pattern, replacement in REFERENCE_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def _clean_number_prefix(text: str) -> str:
    """Replace No.X pattern with ナンバーX for TTS.

    Converts:
    - No.21 → ナンバー21
    - no.5 → ナンバー5 (case insensitive)
    - NO.100 → ナンバー100
    """
    return NUMBER_PREFIX_PATTERN.sub(r"ナンバー\1", text)


def _clean_chapter(text: str) -> str:
    """Replace Chapter X pattern with 第X章 for TTS.

    Converts:
    - Chapter 5 → 第5章
    - chapter 12 → 第12章 (case insensitive)
    - CHAPTER 1 → 第1章

    Note: 第X章 will be further converted to だいXしょう by normalize_numbers()
    """
    return CHAPTER_PATTERN.sub(r"第\1章", text)


def _clean_isbn(text: str) -> str:
    """Remove ISBN numbers from text for TTS.

    Removes all ISBN patterns (ISBN-10 and ISBN-13, with or without hyphens).
    """
    return ISBN_PATTERN.sub("", text)


def _clean_parenthetical_english(text: str) -> str:
    """Remove parenthetical English terms for TTS.

    Removes:
    - 全角括弧内の英語のみ: トイル（Toil）→ トイル
    - 半角括弧内の英語のみ: トイル(Toil) → トイル

    Preserves:
    - 日本語を含む括弧: SRE（サイト信頼性）→ 保持
    - 空括弧: （）→ 保持
    - 数字のみ括弧: （1.0）→ 保持

    Args:
        text: Input text containing parenthetical terms

    Returns:
        Text with English-only parenthetical terms removed
    """
    text = PAREN_ENGLISH_FULL.sub("", text)
    text = PAREN_ENGLISH_HALF.sub("", text)
    return text


def clean_page_text(text: str, heading_marker: str | None = None) -> str:
    """Clean a single page's text for TTS consumption.

    Args:
        text: Text to clean
        heading_marker: Optional marker to preserve through cleaning (e.g., HEADING_MARKER)
    """
    # Preserve heading marker through text cleaning (MeCab strips Unicode private use area)
    if heading_marker and heading_marker in text:
        text = text.replace(heading_marker, _HEADING_PLACEHOLDER)

    # NEW: Text cleaning for TTS (before markdown cleanup)
    # Process in specific order to avoid interference
    text = _clean_urls(text)  # US1: Remove URLs
    text = _clean_isbn(text)  # US4: Remove ISBN
    text = _clean_number_prefix(text)  # US2: No.X → ナンバーX
    text = _clean_chapter(text)  # US2: Chapter X → 第X章
    text = _clean_parenthetical_english(text)  # US5: Remove (English)
    text = _normalize_references(text)  # US2/3: 図X.Y → ずXのY

    # Remove HTML comments (figure markers)
    text = HTML_COMMENT_PATTERN.sub("", text)

    # Remove figure description paragraphs (lines starting with 図は、)
    text = FIGURE_DESC_PATTERN.sub("", text)

    # Remove page number markers like "1 / 1", "はじめに 1 / 3"
    text = PAGE_NUMBER_PATTERN.sub("", text)

    # Remove markdown heading markers but keep text
    text = HEADING_PATTERN.sub("", text)

    # Remove bold/italic markers
    text = BOLD_ITALIC_PATTERN.sub(r"\1", text)

    # Remove horizontal rules
    text = HORIZONTAL_RULE_PATTERN.sub("", text)

    # Convert consecutive list items into single line with periods
    def convert_list_block(match: re.Match) -> str:
        lines = match.group(0).strip().split("\n")
        items = []
        for line in lines:
            content = LIST_MARKER_PATTERN.sub("", line)
            if content and content[-1] not in "。！？、":
                content += "。"
            items.append(content)
        return "".join(items)

    text = LIST_BLOCK_PATTERN.sub(convert_list_block, text)

    # Remove inline code backticks
    text = INLINE_CODE_PATTERN.sub(r"\1", text)

    # Remove code blocks
    text = CODE_BLOCK_PATTERN.sub("", text)

    # Remove trailing whitespace from lines
    text = TRAILING_WHITESPACE_PATTERN.sub("", text)

    # Remove markdown line breaks (trailing double space)
    text = DOUBLE_SPACE_PATTERN.sub("", text)

    # Collapse multiple blank lines into one
    text = MULTIPLE_NEWLINES_PATTERN.sub("\n\n", text)

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

    # Restore heading marker if it was preserved
    if heading_marker and _HEADING_PLACEHOLDER in text:
        text = text.replace(_HEADING_PLACEHOLDER, heading_marker)

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
