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
# 長い修飾句の後にのみ適用（min_prefix_len で制御）
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

# 副詞句パターン（直後に読点を挿入）
# これらは長さに関係なく常に適用
ADVERB_PATTERNS = [
    "大規模に",
    "小規模に",
    "具体的に",
    "一般的に",
    "基本的に",
]

# 接続パターン（直後に読点を挿入、長いフレーズの後のみ）
CONJUNCTION_PATTERNS = [
    "というのが",
    "というのは",
    "ということが",
    "ということは",
]

# Exclusion suffixes for Rule 4 - don't insert comma after は when followed by these
EXCLUSION_SUFFIXES = [
    # では系
    "ありません",
    "ありませんでした",
    "ありますが",
    "ある",
    "ない",
    "なかった",
    "なくて",
    "ないか",
    # には系
    "ならない",
    "ならなかった",
    "至らない",
    # とは系
    "言えない",
    "限らない",
]

# Colon patterns for conversion (US7)
# Time/ratio pattern to exclude:
# - Pure digit sequences: 10:30:45, 1:2:3
# - Ingredient ratios: 水1:砂糖2 (kanji+digit:kanji+digit...)
TIME_RATIO_PATTERN = re.compile(r'[ァ-ヶ一-龠々]+\d+(?::[ァ-ヶ一-龠々]+\d+)+|\d+(?::\d+)+')
# Colon patterns to convert
COLON_FULL_PATTERN = re.compile(r'：')
COLON_HALF_PATTERN = re.compile(r':')

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
        # Apply colon normalization before line normalization
        line = _normalize_colons(line)
        result_lines.append(_normalize_line(line))

    return "\n".join(result_lines)


def _normalize_colons(text: str) -> str:
    """Convert colons to は、 for TTS.

    Converts:
    - 全角コロン（：）→ は、
    - 半角コロン（:）→ は、

    Excludes:
    - 時刻パターン: 10:30
    - 比率パターン: 1:3

    Args:
        text: Input text containing colons

    Returns:
        Text with colons converted to は、
    """
    # Step 1: Protect time/ratio patterns (digit:digit) with placeholders
    time_ratio_matches = []
    def save_time_ratio(match):
        time_ratio_matches.append(match.group(0))
        return f"<<TIME_RATIO_{len(time_ratio_matches)-1}>>"

    text = TIME_RATIO_PATTERN.sub(save_time_ratio, text)

    # Step 2: Convert remaining colons to は、
    text = COLON_FULL_PATTERN.sub("は、", text)
    text = COLON_HALF_PATTERN.sub("は、", text)

    # Step 3: Also remove spaces after converted colons for cleaner output
    text = re.sub(r'は、\s+', 'は、', text)

    # Step 4: Restore time/ratio patterns
    for i, original in enumerate(time_ratio_matches):
        text = text.replace(f"<<TIME_RATIO_{i}>>", original)

    return text


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

    # Rule 2: Insert comma after adverb patterns (always apply)
    for pattern in ADVERB_PATTERNS:
        line = re.sub(
            rf"({re.escape(pattern)})([^、。！？\s])",
            r"\1、\2",
            line
        )

    # Rule 3: Insert comma after conjunction patterns (with prefix check)
    for pattern in CONJUNCTION_PATTERNS:
        line = re.sub(
            rf"([^、。！？]{{{min_prefix_len},}})({re.escape(pattern)})([^、。！？\s])",
            r"\1\2、\3",
            line
        )

    # Rule 4: Insert comma after は when preceded by long phrase
    # Exclude patterns like ではありません, にはならない, etc.
    # 〜カタは、〜ことは、etc.
    # Use shorter threshold (6) because kanji is more compact than kana
    ha_prefix_len = min(min_prefix_len, 6)
    exclusion_pattern = "|".join(re.escape(s) for s in EXCLUSION_SUFFIXES)
    line = re.sub(
        rf"([^、。！？]{{{ha_prefix_len},}})(は)(?!({exclusion_pattern}))([^、。！？\s])",
        r"\1\2、\4",
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
