# Data Model: 新XMLフォーマット対応

**Branch**: `004-new-xml-format` | **Date**: 2026-02-17

## Entities

### HeadingInfo

```python
@dataclass
class HeadingInfo:
    """見出し情報

    Attributes:
        level: 見出しレベル（1=chapter, 2+=section）
        number: 見出し番号（"1", "1.2", "3.10" など）
        title: 見出しテキスト
        read_aloud: 読み上げ対象か
    """
    level: int
    number: str
    title: str
    read_aloud: bool = True
```

### ContentItem

```python
@dataclass
class ContentItem:
    """コンテンツ単位

    Attributes:
        item_type: コンテンツ種別
            - "paragraph": 段落
            - "heading": 見出し
            - "list_item": リスト項目
        text: テキスト内容（マーカー含む）
        heading_info: 見出し情報（heading の場合のみ）
    """
    item_type: str
    text: str
    heading_info: HeadingInfo | None = None
```

## Constants

```python
# src/xml2_parser.py
CHAPTER_MARKER = "\uE001"  # Unicode Private Use Area
SECTION_MARKER = "\uE002"  # Unicode Private Use Area
```

## Processing Flow

```
book2.xml
    │
    ▼
parse_book2_xml()
    │
    ├── Skip: <toc>, <front-matter>, <metadata>
    │
    ├── Process: <heading level="N">
    │   └── HeadingInfo → format_heading_text() → MARKER + text
    │
    ├── Process: <paragraph>
    │   └── ContentItem(item_type="paragraph", text=...)
    │
    └── Process: <list>/<item>
        └── ContentItem(item_type="list_item", text=...)
    │
    ▼
list[ContentItem]
    │
    ▼
text_cleaner (markers preserved)
    │
    ▼
xml2_pipeline
    ├── Split by CHAPTER_MARKER / SECTION_MARKER
    ├── Insert chapter_sound / section_sound
    └── Generate audio via voicevox_client
```

## Validation Rules

### HeadingInfo

| Field | Rule |
|-------|------|
| level | >= 1 |
| number | 非空文字列 |
| title | 非空文字列（空白トリム後） |
| read_aloud | デフォルト True |

### ContentItem

| Field | Rule |
|-------|------|
| item_type | "paragraph" \| "heading" \| "list_item" |
| text | 非空（空白トリム後） |
| heading_info | item_type="heading" の場合のみ設定 |

## Skip Rules

以下の要素は読み上げ対象から除外：

| 要素 | 条件 |
|------|------|
| `<toc>` | 常に除外 |
| `<front-matter>` | 常に除外 |
| `<metadata>` | 常に除外 |
| 任意要素 | `readAloud="false"` |
| 空テキスト | text.strip() == "" |
