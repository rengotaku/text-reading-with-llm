"""Rule-based punctuation normalizer for TTS.

Uses MeCab morphological analysis to insert commas at appropriate positions.
"""

import re
from dataclasses import dataclass

import fugashi


@dataclass
class PunctuationRule:
    """A rule for inserting punctuation."""
    name: str
    pattern: str  # Regex pattern for surface forms
    insert_after: str = "、"


# 連体修飾句パターン（〜に関する、〜における、等の後に読点）
RENTAI_PATTERNS = [
    "に関する",
    "における",
    "による",
    "のための",
    "についての",
    "に対する",
    "からの",
    "への",
    "としての",
]

# Lazy initialization
_tagger: fugashi.Tagger | None = None


def _get_tagger() -> fugashi.Tagger:
    global _tagger
    if _tagger is None:
        _tagger = fugashi.Tagger()
    return _tagger


def normalize_punctuation(text: str) -> str:
    """Add punctuation for natural TTS reading.

    Args:
        text: Input text (with kanji)

    Returns:
        Text with additional punctuation for TTS
    """
    # Process line by line to preserve structure
    lines = text.split("\n")
    result_lines = []

    for line in lines:
        if not line.strip():
            result_lines.append(line)
            continue
        result_lines.append(_normalize_line(line))

    return "\n".join(result_lines)


def _normalize_line(line: str, min_prefix_len: int = 8) -> str:
    """Normalize a single line.

    Args:
        line: Input line
        min_prefix_len: Minimum characters before pattern to trigger comma insertion
    """
    # Rule 1: Insert comma after 連体修飾句 patterns
    # Only if preceded by long enough phrase (since last punctuation)
    for pattern in RENTAI_PATTERNS:
        # Match: (long prefix)(pattern)(non-punctuation char)
        # Prefix must be at least min_prefix_len chars without punctuation
        line = re.sub(
            rf"([^、。！？]{{{min_prefix_len},}})({re.escape(pattern)})([^、。！？\s])",
            r"\1\2、\3",
            line
        )

    return line


def _insert_after_long_phrases(line: str) -> str:
    """Insert commas after long noun phrases.

    Analyzes morphology to find long sequences of nouns/modifiers
    and inserts commas at phrase boundaries.
    """
    tagger = _get_tagger()
    words = list(tagger(line))

    if len(words) < 5:
        return line

    result = []
    noun_phrase_len = 0

    for i, word in enumerate(words):
        surface = word.surface
        pos = word.feature.pos1 if hasattr(word.feature, 'pos1') else ""

        # Count consecutive noun-like elements
        if pos in ("名詞", "接頭辞", "形容詞", "連体詞"):
            noun_phrase_len += len(surface)
        else:
            # Reset counter on non-noun
            if noun_phrase_len > 15 and pos == "助詞":
                # Long noun phrase followed by particle - consider adding comma
                # But only if next element starts a new clause
                if i + 1 < len(words):
                    next_pos = words[i + 1].feature.pos1 if hasattr(words[i + 1].feature, 'pos1') else ""
                    if next_pos in ("名詞", "動詞", "形容詞"):
                        # Check if comma already exists
                        if not surface.endswith("、"):
                            surface = surface + "、"
            noun_phrase_len = 0

        result.append(surface)

    return "".join(result)


def show_analysis(text: str) -> None:
    """Debug: Show morphological analysis of text."""
    tagger = _get_tagger()
    for word in tagger(text):
        pos1 = word.feature.pos1 if hasattr(word.feature, 'pos1') else "?"
        pos2 = word.feature.pos2 if hasattr(word.feature, 'pos2') else "?"
        print(f"{word.surface}\t{pos1}/{pos2}")


if __name__ == "__main__":
    # Test
    test_cases = [
        "筆者は日本国内初のSREに関するテックカンファレンス「SRE NEXT」を立ち上げた",
        "SREにおける信頼性の定義について解説する",
        "このシステムによる効果は大きい",
    ]

    print("=== Punctuation Normalization Test ===\n")
    for text in test_cases:
        normalized = normalize_punctuation(text)
        print(f"Before: {text}")
        print(f"After:  {normalized}")
        print()
