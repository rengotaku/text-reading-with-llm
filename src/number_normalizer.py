"""日本語数字読み変換モジュール.

数字を日本語の読み仮名に変換する。
例: "123" → "ひゃくにじゅうさん"
"""

import re
from typing import Callable

# 基本数字
DIGITS = {
    "0": "ゼロ",
    "1": "いち",
    "2": "に",
    "3": "さん",
    "4": "よん",
    "5": "ご",
    "6": "ろく",
    "7": "なな",
    "8": "はち",
    "9": "きゅう",
}

# 位取り（1の位は空）
PLACES = {
    1: "",
    10: "じゅう",
    100: "ひゃく",
    1000: "せん",
}

# 大きな単位
LARGE_UNITS = {
    10000: "まん",
    100000000: "おく",
    1000000000000: "ちょう",
}

# 特殊読み（位取り×数字の組み合わせ）
SPECIAL_READINGS = {
    # 百の位
    (100, 3): "さんびゃく",
    (100, 6): "ろっぴゃく",
    (100, 8): "はっぴゃく",
    # 千の位
    (1000, 3): "さんぜん",
    (1000, 8): "はっせん",
    # 十の位（1は省略）
    (10, 1): "じゅう",
    # 百の位（1は省略）
    (100, 1): "ひゃく",
    # 千の位（1は省略）
    (1000, 1): "せん",
}

# 助数詞のデフォルト読み
COUNTER_READINGS = {
    "個": "こ",
    "回": "かい",
    "件": "けん",
    "分": "ふん",
    "秒": "びょう",
    "本": "ほん",
    "匹": "ひき",
    "杯": "はい",
    "階": "かい",
    "冊": "さつ",
    "人": "にん",
    "日": "にち",
    "月": "がつ",
    "年": "ねん",
    "時": "じ",
    "歳": "さい",
    "円": "えん",
    "%": "パーセント",
}

# 助数詞とその読み変化（特殊ケース）
COUNTERS = {
    # (助数詞, {数字: 読み})
    "個": {
        1: "いっこ",
        6: "ろっこ",
        8: "はっこ",
        10: "じゅっこ",
    },
    "回": {
        1: "いっかい",
        6: "ろっかい",
        8: "はっかい",
        10: "じゅっかい",
    },
    "件": {
        1: "いっけん",
        6: "ろっけん",
        8: "はっけん",
        10: "じゅっけん",
    },
    "分": {
        1: "いっぷん",
        3: "さんぷん",
        4: "よんぷん",
        6: "ろっぷん",
        8: "はっぷん",
        10: "じゅっぷん",
    },
    "秒": {
        1: "いちびょう",
    },
    "本": {
        1: "いっぽん",
        3: "さんぼん",
        6: "ろっぽん",
        8: "はっぽん",
        10: "じゅっぽん",
    },
    "匹": {
        1: "いっぴき",
        3: "さんびき",
        6: "ろっぴき",
        8: "はっぴき",
        10: "じゅっぴき",
    },
    "杯": {
        1: "いっぱい",
        3: "さんばい",
        6: "ろっぱい",
        8: "はっぱい",
        10: "じゅっぱい",
    },
    "階": {
        1: "いっかい",
        3: "さんがい",
        6: "ろっかい",
        8: "はっかい",
        10: "じゅっかい",
    },
    "冊": {
        1: "いっさつ",
        8: "はっさつ",
        10: "じゅっさつ",
    },
    "人": {
        1: "ひとり",
        2: "ふたり",
        4: "よにん",
        7: "しちにん",
    },
    "日": {  # 日数として
        1: "いちにち",
        2: "ふつか",
        3: "みっか",
        4: "よっか",
        5: "いつか",
        6: "むいか",
        7: "なのか",
        8: "ようか",
        9: "ここのか",
        10: "とおか",
        14: "じゅうよっか",
        20: "はつか",
        24: "にじゅうよっか",
    },
    "月": {  # 月名
        1: "いちがつ",
        2: "にがつ",
        3: "さんがつ",
        4: "しがつ",
        5: "ごがつ",
        6: "ろくがつ",
        7: "しちがつ",
        8: "はちがつ",
        9: "くがつ",
        10: "じゅうがつ",
        11: "じゅういちがつ",
        12: "じゅうにがつ",
    },
    "年": {
        4: "よねん",
    },
    "時": {
        4: "よじ",
        7: "しちじ",
        9: "くじ",
    },
    "歳": {
        1: "いっさい",
        8: "はっさい",
        10: "じゅっさい",
        20: "はたち",
    },
    "円": {
        4: "よえん",
    },
    "%": {
        "suffix": "パーセント",
    },
}


def _digit_at_place(n: int, place: int) -> int:
    """指定した位の数字を取得."""
    return (n // place) % 10


def _read_small_number(n: int) -> str:
    """1-9999の数字を読む."""
    if n == 0:
        return ""

    parts = []

    for place in [1000, 100, 10, 1]:
        digit = _digit_at_place(n, place)
        if digit == 0:
            continue

        # 特殊読みをチェック
        if (place, digit) in SPECIAL_READINGS:
            parts.append(SPECIAL_READINGS[(place, digit)])
        elif place == 1:
            parts.append(DIGITS[str(digit)])
        else:
            parts.append(DIGITS[str(digit)] + PLACES[place])

    return "".join(parts)


def number_to_japanese(n: int) -> str:
    """整数を日本語読みに変換.

    Args:
        n: 変換する整数

    Returns:
        日本語読み

    Examples:
        >>> number_to_japanese(0)
        'ゼロ'
        >>> number_to_japanese(123)
        'ひゃくにじゅうさん'
        >>> number_to_japanese(10000)
        'いちまん'
    """
    if n == 0:
        return "ゼロ"

    if n < 0:
        return "マイナス" + number_to_japanese(-n)

    parts = []

    # 兆の位
    cho = n // 1000000000000
    if cho > 0:
        parts.append(_read_small_number(cho) + "ちょう")
        n %= 1000000000000

    # 億の位
    oku = n // 100000000
    if oku > 0:
        parts.append(_read_small_number(oku) + "おく")
        n %= 100000000

    # 万の位
    man = n // 10000
    if man > 0:
        parts.append(_read_small_number(man) + "まん")
        n %= 10000

    # 千以下
    if n > 0:
        parts.append(_read_small_number(n))

    return "".join(parts)


def decimal_to_japanese(s: str) -> str:
    """小数を日本語読みに変換.

    Args:
        s: 小数文字列 (e.g., "3.14")

    Returns:
        日本語読み (e.g., "さんてんいちよん")
    """
    if "." not in s:
        return number_to_japanese(int(s))

    integer_part, decimal_part = s.split(".", 1)

    # 整数部
    result = number_to_japanese(int(integer_part)) if integer_part else "ゼロ"
    result += "てん"

    # 小数部（1桁ずつ読む）
    for digit in decimal_part:
        result += DIGITS.get(digit, digit)

    return result


def read_with_counter(n: int, counter: str) -> str:
    """助数詞付きの数字を読む.

    Args:
        n: 数字
        counter: 助数詞

    Returns:
        日本語読み
    """
    counter_rules = COUNTERS.get(counter, {})

    # 特別な読み方があればそれを使用
    if n in counter_rules:
        return counter_rules[n]

    # 通常の読み + 助数詞の読み
    base_reading = number_to_japanese(n)

    # パーセントなどの特殊サフィックス
    if "suffix" in counter_rules:
        return base_reading + counter_rules["suffix"]

    # 助数詞のデフォルト読みを使用
    counter_reading = COUNTER_READINGS.get(counter, counter)
    return base_reading + counter_reading


def _normalize_date(match: re.Match) -> str:
    """日付パターンを読みに変換."""
    year = match.group("year")
    month = match.group("month")
    day = match.group("day")

    result = ""

    if year:
        y = int(year)
        # 4で終わる年は「よねん」
        if y % 10 == 4:
            result += number_to_japanese(y // 10 * 10)
            result += "よねん"
        else:
            result += number_to_japanese(y) + "ねん"

    if month:
        m = int(month)
        if m in COUNTERS["月"]:
            result += COUNTERS["月"][m]
        else:
            result += number_to_japanese(m) + "がつ"

    if day:
        d = int(day)
        if d in COUNTERS["日"]:
            result += COUNTERS["日"][d]
        else:
            result += number_to_japanese(d) + "にち"

    return result


def _normalize_time(match: re.Match) -> str:
    """時刻パターンを読みに変換."""
    hour = int(match.group("hour"))
    minute = match.group("minute")

    # 時
    if hour in COUNTERS["時"]:
        result = COUNTERS["時"][hour]
    else:
        result = number_to_japanese(hour) + "じ"

    # 分
    if minute:
        m = int(minute)
        if m in COUNTERS["分"]:
            result += COUNTERS["分"][m]
        elif m == 0:
            pass  # 0分は読まない
        else:
            result += number_to_japanese(m) + "ふん"

    return result


def _normalize_counter(match: re.Match) -> str:
    """助数詞付き数字を読みに変換."""
    number = int(match.group("number"))
    counter = match.group("counter")

    return read_with_counter(number, counter)


def _normalize_percent(match: re.Match) -> str:
    """パーセントを読みに変換."""
    number = match.group("number")

    if "." in number:
        return decimal_to_japanese(number) + "パーセント"
    return number_to_japanese(int(number)) + "パーセント"


def _normalize_plain_number(match: re.Match) -> str:
    """単独の数字を読みに変換."""
    number = match.group(0)

    # 小数
    if "." in number:
        return decimal_to_japanese(number)

    # 整数
    return number_to_japanese(int(number))


# 変換パターン（順序重要）
PATTERNS: list[tuple[re.Pattern, Callable[[re.Match], str]]] = [
    # 日付: 2024年1月1日, 2024/1/1, 2024-1-1
    (
        re.compile(
            r"(?P<year>\d{4})[年/\-](?P<month>\d{1,2})[月/\-](?P<day>\d{1,2})日?"
        ),
        _normalize_date,
    ),
    # 年月: 2024年1月
    (
        re.compile(r"(?P<year>\d{4})年(?P<month>\d{1,2})月(?![\d日])"),
        lambda m: _normalize_date(
            type(
                "Match",
                (),
                {"group": lambda self, x: m.group(x) if x in ("year", "month") else None},
            )()
        ),
    ),
    # 月日: 1月1日
    (
        re.compile(r"(?P<month>\d{1,2})月(?P<day>\d{1,2})日"),
        lambda m: _normalize_date(
            type(
                "Match",
                (),
                {"group": lambda self, x: None if x == "year" else m.group(x)},
            )()
        ),
    ),
    # 年のみ: 2024年
    (
        re.compile(r"(?P<year>\d{4})年"),
        lambda m: _normalize_date(
            type(
                "Match",
                (),
                {
                    "group": lambda self, x: m.group("year")
                    if x == "year"
                    else None
                },
            )()
        ),
    ),
    # 時刻: 10:30, 10時30分
    (
        re.compile(r"(?P<hour>\d{1,2})[:時](?P<minute>\d{2})分?"),
        _normalize_time,
    ),
    # 時のみ: 10時
    (
        re.compile(r"(?P<hour>\d{1,2})時(?!\d)"),
        lambda m: _normalize_time(
            type(
                "Match",
                (),
                {"group": lambda self, x: m.group("hour") if x == "hour" else None},
            )()
        ),
    ),
    # パーセント: 50%, 3.14%
    (
        re.compile(r"(?P<number>\d+(?:\.\d+)?)%"),
        _normalize_percent,
    ),
    # 助数詞付き数字
    (
        re.compile(r"(?P<number>\d+)(?P<counter>[個回件分秒本匹杯階冊人日月歳円])"),
        _normalize_counter,
    ),
    # 第N章/節/回など
    (
        re.compile(r"第(?P<number>\d+)(?P<suffix>[章節回部編条項])"),
        lambda m: "だい"
        + number_to_japanese(int(m.group("number")))
        + m.group("suffix"),
    ),
    # 単独の数字（最後に適用）
    (
        re.compile(r"\d+(?:\.\d+)?"),
        _normalize_plain_number,
    ),
]


def normalize_numbers(text: str) -> str:
    """テキスト中の数字を日本語読みに変換.

    Args:
        text: 入力テキスト

    Returns:
        数字を読みに変換したテキスト

    Examples:
        >>> normalize_numbers("2024年1月1日")
        'にせんにじゅうよねんいちがつついたち'
        >>> normalize_numbers("価格は1000円です")
        '価格はせんえんです'
    """
    for pattern, replacer in PATTERNS:
        text = pattern.sub(replacer, text)
    return text
