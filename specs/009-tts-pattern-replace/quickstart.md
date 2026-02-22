# Quickstart: TTS前処理パターン置換

**Feature**: 009-tts-pattern-replace
**Date**: 2026-02-22

## Overview

TTS読み上げ時の不自然なパターンを自然な日本語表現に置換する機能。

| パターン | 変換前 | 変換後 |
|----------|--------|--------|
| 裸のURL | `www.example.com` | ウェブサイト |
| No.X | `No.21` | ナンバー21 |
| Chapter X | `Chapter 5` | 第5章 |

## Prerequisites

```bash
# venv 有効化
source .venv/bin/activate

# 依存関係確認
pip install -r requirements.txt

# テスト実行確認
make test
```

## Implementation Steps

### Step 1: パターン定数の追加

`src/text_cleaner.py` に以下のパターンを追加:

```python
# No.X パターン（大文字小文字不問）
NUMBER_PREFIX_PATTERN = re.compile(r"No\.(\d+)", re.IGNORECASE)

# Chapter X パターン（大文字小文字不問）
CHAPTER_PATTERN = re.compile(r"Chapter\s+(\d+)", re.IGNORECASE)
```

### Step 2: URL置換関数の修正

`_clean_urls()` を修正し、裸のURLを「ウェブサイト」に置換:

```python
def _clean_urls(text: str) -> str:
    """Remove or replace URLs from text for TTS.

    - Markdown links: Keep link text, remove URL
    - URL as link text: Replace with "ウェブサイト"
    - Bare URLs: Replace with "ウェブサイト"
    """
    def replace_markdown_link(match):
        link_text = match.group(1)
        if URL_TEXT_PATTERN.match(link_text):
            return "ウェブサイト"  # Changed from ""
        return link_text

    text = MARKDOWN_LINK_PATTERN.sub(replace_markdown_link, text)
    text = BARE_URL_PATTERN.sub("ウェブサイト", text)  # Changed from ""
    return text
```

### Step 3: No.X 変換関数の追加

```python
def _clean_number_prefix(text: str) -> str:
    """Convert No.X to ナンバーX for natural TTS reading.

    Examples:
        "No.21" → "ナンバー21"
        "no.5" → "ナンバー5"
    """
    return NUMBER_PREFIX_PATTERN.sub(r"ナンバー\1", text)
```

### Step 4: Chapter X 変換関数の追加

```python
def _clean_chapter(text: str) -> str:
    """Convert Chapter X to 第X章 for natural TTS reading.

    Examples:
        "Chapter 5" → "第5章"
        "chapter 12" → "第12章"
    """
    return CHAPTER_PATTERN.sub(r"第\1章", text)
```

### Step 5: clean_page_text() への統合

`clean_page_text()` 内の処理順序に新関数を追加:

```python
def clean_page_text(text: str, heading_marker: str | None = None) -> str:
    # ... 既存の前処理 ...

    # TTS text cleaning
    text = _clean_urls(text)           # US1: URL置換
    text = _clean_isbn(text)           # US3: ISBN削除
    text = _clean_number_prefix(text)  # US2: No.X → ナンバーX
    text = _clean_chapter(text)        # US2: Chapter X → 第X章
    text = _clean_parenthetical_english(text)
    text = _normalize_references(text)

    # ... 既存の後処理 ...
```

## Testing

### 既存テストの修正

`tests/test_url_cleaning.py`:
- URL削除テスト → URL置換テストに変更
- 期待値を `""` から `"ウェブサイト"` に変更

### 新規テストファイル

`tests/test_number_prefix.py`:
```python
from src.text_cleaner import _clean_number_prefix

class TestCleanNumberPrefix:
    def test_basic_no_pattern(self):
        assert _clean_number_prefix("No.21") == "ナンバー21"

    def test_lowercase(self):
        assert _clean_number_prefix("no.5") == "ナンバー5"

    def test_in_sentence(self):
        input_text = "詳細は No.21 で説明します"
        expected = "詳細は ナンバー21 で説明します"
        assert _clean_number_prefix(input_text) == expected
```

`tests/test_chapter_conversion.py`:
```python
from src.text_cleaner import _clean_chapter

class TestCleanChapter:
    def test_basic_chapter(self):
        assert _clean_chapter("Chapter 5") == "第5章"

    def test_lowercase(self):
        assert _clean_chapter("chapter 12") == "第12章"

    def test_in_sentence(self):
        input_text = "Chapter 5 を参照"
        expected = "第5章 を参照"
        assert _clean_chapter(input_text) == expected
```

## Verification

```bash
# 全テスト実行
make test

# 特定テストのみ
pytest tests/test_url_cleaning.py -v
pytest tests/test_number_prefix.py -v
pytest tests/test_chapter_conversion.py -v

# カバレッジ確認
pytest --cov=src --cov-report=term-missing
```

## Success Criteria Checklist

- [ ] SC-001: TTS出力に「ダブリュー」「ドット」などのURL構成要素が含まれない
- [ ] SC-002: `No.X`形式が「ナンバーX」で読み上げられる
- [ ] SC-003: ISBN形式文字列がTTS出力に含まれない
- [ ] SC-004: 二重空白や不自然な句読点配置が発生しない
- [ ] SC-005: 既存テストがすべて通過する
