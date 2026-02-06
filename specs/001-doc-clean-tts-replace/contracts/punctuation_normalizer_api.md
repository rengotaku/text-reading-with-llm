# Contract: punctuation_normalizer.py API

**Date**: 2026-02-06
**Module**: `src/punctuation_normalizer.py`

## 新規関数インターフェース

### _normalize_colons(text: str) -> str

コロン（：/:）を「は、」に変換する。

**Parameters**:
- `text` (str): 入力テキスト

**Returns**:
- `str`: コロンが変換されたテキスト

**Exclusions**:
- URL内のコロン (`://`)
- 時刻表記 (`10:00`, `23:59`)
- 比率表記 (`1:3`, `16:9`)

**Examples**:
```python
>>> _normalize_colons("効果測定：トイル削減")
"効果測定は、トイル削減"

>>> _normalize_colons("目的:システム改善")
"目的は、システム改善"

>>> _normalize_colons("時刻は10:00です")
"時刻は10:00です"  # 変換しない

>>> _normalize_colons("比率は1:3です")
"比率は1:3です"  # 変換しない
```

---

### _normalize_brackets(text: str) -> str

鉤括弧「」を読点に変換する。

**Parameters**:
- `text` (str): 入力テキスト

**Returns**:
- `str`: 鉤括弧が変換されたテキスト

**Post-processing**:
- 連続する読点 `、、` を単一の `、` に正規化

**Examples**:
```python
>>> _normalize_brackets("「SRE NEXT」を立ち上げ")
"、SRE NEXT、を立ち上げ"

>>> _normalize_brackets("本書は「入門書」です")
"本書は、入門書、です"

>>> _normalize_brackets("「」空の括弧")
"、空の括弧"  # 連続読点は正規化
```

---

## 変更関数インターフェース

### _normalize_line(line: str, min_prefix_len: int = 8) -> str (Modified)

**変更点**: Rule 4 に除外パターンを追加

**除外パターン** (「は」の後に読点を挿入しない):
- `ではありません`
- `ではない`
- `ではなく`
- `にはならない`
- `とはいえない`
- `にはなりません`
- `とはいえません`

**Examples**:
```python
>>> _normalize_line("終わりではありません")
"終わりではありません"  # 「では」の後に読点なし

>>> _normalize_line("これは重要ではありますが")
"これは、重要ではありますが"  # 「これは」OK、「では」は除外
```

**Implementation**:
```python
# Rule 4 の正規表現に負の先読みを追加
EXCLUSION_SUFFIXES = r"(?!ありません|ない|なく|ならない|いえない|なりません|いえません)"
pattern = rf"([^、。！？]{{{ha_prefix_len},}})(は){EXCLUSION_SUFFIXES}([^、。！？\s])"
```

---

### normalize_punctuation(text: str) -> str (Modified)

**変更点**: 新規変換を処理パイプラインに追加

**New Processing Order**:
```python
def normalize_punctuation(text: str) -> str:
    # 1. NEW: コロン変換
    text = _normalize_colons(text)
    # 2. NEW: 鉤括弧変換
    text = _normalize_brackets(text)
    # 3. 既存の行単位処理
    lines = text.split("\n")
    result_lines = []
    for line in lines:
        if not line.strip():
            result_lines.append(line)
            continue
        result_lines.append(_normalize_line(line))
    return "\n".join(result_lines)
```

---

## 新規定数

```python
# 読点挿入除外パターン
EXCLUSION_SUFFIXES = [
    "ありません",
    "ない",
    "なく",
    "ならない",
    "いえない",
    "なりません",
    "いえません",
]
```
