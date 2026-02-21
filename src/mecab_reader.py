"""MeCab-based kanji to kana conversion using fugashi."""

import logging

import fugashi

logger = logging.getLogger(__name__)

# Lazy initialization of tagger
_tagger: fugashi.Tagger | None = None


def _get_tagger() -> fugashi.Tagger:
    """Get or create the MeCab tagger (lazy initialization)."""
    global _tagger
    if _tagger is None:
        _tagger = fugashi.Tagger()
        logger.info("MeCab tagger initialized")
    return _tagger


def _is_kanji(char: str) -> bool:
    """Check if a character is kanji."""
    return "\u4e00" <= char <= "\u9fff" or "\u3400" <= char <= "\u4dbf"


def _contains_kanji(text: str) -> bool:
    """Check if text contains any kanji."""
    return any(_is_kanji(c) for c in text)


def convert_to_kana(text: str) -> str:
    """Convert text with kanji to katakana readings.

    Only kanji portions are converted; hiragana, katakana, and ASCII remain unchanged.
    Newlines are preserved by processing line by line.

    Args:
        text: Input text possibly containing kanji

    Returns:
        Text with kanji replaced by katakana readings
    """
    if not text:
        return text

    # Process line by line to preserve newlines
    lines = text.split("\n")
    converted_lines = []

    for line in lines:
        if not line or not _contains_kanji(line):
            converted_lines.append(line)
            continue

        tagger = _get_tagger()
        result = []

        for word in tagger(line):
            surface = word.surface
            kana = getattr(word.feature, "kana", None)

            if kana and _contains_kanji(surface):
                # Replace kanji with katakana reading
                result.append(kana)
            else:
                # Keep original (hiragana, katakana, ASCII, punctuation, etc.)
                result.append(surface)

        converted_lines.append("".join(result))

    return "\n".join(converted_lines)


def convert_kanji_only(text: str) -> str:
    """Convert only kanji characters, preserving mixed words.

    For words like "信頼性" → "シンライセイ", but keeps particles and
    non-kanji text unchanged.

    This is more conservative than convert_to_kana() and preserves
    more of the original text structure.
    """
    if not text or not _contains_kanji(text):
        return text

    tagger = _get_tagger()
    result = []

    for word in tagger(text):
        surface = word.surface
        kana = getattr(word.feature, "kana", None)

        # Only convert if the surface contains kanji
        if kana and _contains_kanji(surface):
            result.append(kana)
        else:
            result.append(surface)

    return "".join(result)
