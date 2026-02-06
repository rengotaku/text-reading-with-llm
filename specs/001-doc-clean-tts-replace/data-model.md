# Data Model: doc-clean-tts-replace

**Date**: 2026-02-06
**Branch**: `001-doc-clean-tts-replace`

## 概要

本機能はテキスト変換パイプラインの拡張であり、新規エンティティの永続化は不要。
変換ルールは正規表現パターンとして定数定義される。

## 変換ルール定義

### 1. URL変換ルール

| ルール名 | パターン | 変換結果 | 優先度 |
|---------|---------|---------|--------|
| markdown_link | `\[([^\]]+)\]\([^)]+\)` | `\1` (リンクテキスト) | 1 |
| markdown_link_url_text | `\[https?://[^\]]+\]\([^)]+\)` | (削除) | 0 (最優先) |
| bare_url | `https?://[^\s<>\[\]]+` | (削除) | 2 |

**処理順序**: markdown_link_url_text → markdown_link → bare_url

### 2. 参照変換ルール

| ルール名 | パターン | 変換結果 |
|---------|---------|---------|
| figure_ref | `図(\d+)[\.．](\d+)` | 数字を読み仮名に変換 |
| table_ref | `表(\d+)[\.．](\d+)` | 数字を読み仮名に変換 |
| note_ref | `注(\d+)[\.．](\d+)` | 数字を読み仮名に変換 |

**数字→読み仮名マッピング**:
```python
DIGIT_READINGS = {
    "0": "ゼロ", "1": "いち", "2": "に", "3": "さん", "4": "よん",
    "5": "ご", "6": "ろく", "7": "なな", "8": "はち", "9": "きゅう"
}
```

### 3. ISBN変換ルール

| ルール名 | パターン | 変換結果 |
|---------|---------|---------|
| isbn | `ISBN[\s\-]?[\d\-]{10,17}` | (削除) |

### 4. 括弧付き英語表記ルール

| ルール名 | パターン | 変換結果 |
|---------|---------|---------|
| paren_english | `([ぁ-んァ-ヶ一-龯]+)（([A-Za-z\s\-]+)）` | `\1` |
| paren_english_half | `([ぁ-んァ-ヶ一-龯]+)\(([A-Za-z\s\-]+)\)` | `\1` |

**除外条件**: 括弧内が日本語文字を含む場合は変換しない

### 5. 読点除外パターン

| パターン | 説明 |
|---------|------|
| `ではありません` | 否定丁寧形 |
| `ではない` | 否定形 |
| `ではなく` | 否定接続 |
| `にはならない` | 否定可能 |
| `とはいえない` | 否定推量 |
| `にはなりません` | 否定丁寧可能 |
| `とはいえません` | 否定丁寧推量 |

### 6. コロン変換ルール

| ルール名 | パターン | 変換結果 | 除外条件 |
|---------|---------|---------|---------|
| colon_full | `([^:\/])：([^\/])` | `\1は、\2` | URL内、数字パターン |
| colon_half | `([^:\/\d]):([^\/\d])` | `\1は、\2` | URL内、数字パターン |

**除外パターン**:
- `://` (URL scheme)
- `\d:\d` (時刻、比率)

### 7. 鉤括弧変換ルール

| ルール名 | パターン | 変換結果 |
|---------|---------|---------|
| bracket_open | `「` | `、` |
| bracket_close | `」` | `、` |

**冪等性**: 連続する読点 `、、` は単一の `、` に正規化

## 状態遷移

本機能は状態を持たないテキスト変換のため、状態遷移は不要。

## バリデーションルール

| フィールド | ルール |
|-----------|--------|
| 入力テキスト | UTF-8文字列、空文字可 |
| 出力テキスト | UTF-8文字列、入力と同じ行数を維持 |

## 関係図

```
text_cleaner.py
├── _clean_urls()                    # NEW
│   ├── URL_LINK_URL_TEXT_PATTERN
│   ├── URL_LINK_PATTERN
│   └── URL_BARE_PATTERN
├── _clean_isbn()                    # NEW
│   └── ISBN_PATTERN
├── _clean_parenthetical_english()   # NEW
│   ├── PAREN_ENGLISH_FULL_PATTERN
│   └── PAREN_ENGLISH_HALF_PATTERN
├── _normalize_references()          # NEW
│   ├── FIGURE_REF_PATTERN
│   ├── TABLE_REF_PATTERN
│   └── NOTE_REF_PATTERN
└── normalize_punctuation()          # MODIFIED (in punctuation_normalizer.py)
    ├── _normalize_colons()          # NEW
    │   ├── COLON_FULL_PATTERN
    │   └── COLON_HALF_PATTERN
    ├── _normalize_brackets()        # NEW
    │   ├── BRACKET_OPEN_PATTERN
    │   └── BRACKET_CLOSE_PATTERN
    └── _normalize_line()            # MODIFIED
        └── EXCLUSION_PATTERNS       # NEW (negative lookahead)
