# Data Model: XML から TTS へのローダー

**Feature Branch**: `002-xml-ttl-loader`
**Date**: 2026-02-07

## Entities

### XmlPage

XML の `<page>` 要素に対応するデータクラス。

```python
@dataclass
class XmlPage:
    """XML から抽出したページデータ."""

    number: int           # <page number="N"> の N
    source_file: str      # <page sourceFile="..."> の値
    announcement: str     # <pageAnnouncement> のテキスト
    content_text: str     # <content> から抽出したテキスト
    figures: list[Figure] # <figure> 要素のリスト
```

### Figure

画像とその説明を表すデータクラス。

```python
@dataclass
class Figure:
    """図の情報."""

    file_path: str        # <file> のテキスト
    description: str      # <description> のテキスト
    read_aloud: str       # readAloud 属性値（"true", "false", "optional"）
```

### Page（既存）

既存の `src/text_cleaner.py` で定義されている Page クラス。

```python
@dataclass(frozen=True)
class Page:
    """A single page extracted from the book markdown."""

    number: int
    text: str
```

## Relationships

```
XmlPage ──── to_page() ────> Page
    │
    └── figures: list[Figure]
```

## Conversion

### XmlPage → Page

```python
def to_page(xml_page: XmlPage) -> Page:
    """XmlPage を既存の Page に変換."""
    # テキストを結合
    parts = []
    if xml_page.announcement:
        parts.append(xml_page.announcement)
    if xml_page.content_text:
        parts.append(xml_page.content_text)
    for fig in xml_page.figures:
        if fig.read_aloud != "false" and fig.description:
            parts.append(fig.description)

    text = "\n".join(parts)
    return Page(number=xml_page.number, text=text)
```

## XML Structure Mapping

```xml
<book>                              <!-- Root element -->
  <metadata>                        <!-- Ignored -->
    <title>...</title>
  </metadata>
  <page number="1" sourceFile="page_0001.png">
    <pageAnnouncement>1ページ</pageAnnouncement>  <!-- → announcement -->
    <content>
      <paragraph>...</paragraph>    <!-- → content_text -->
      <heading level="1">...</heading>
      <list>
        <item>...</item>
      </list>
    </content>
    <figure readAloud="optional">   <!-- → figures[] -->
      <file readAloud="false">...</file>
      <description>...</description>
    </figure>
    <pageMetadata readAloud="false">...</pageMetadata>  <!-- Skipped -->
  </page>
</book>
```

## Validation Rules

| フィールド | ルール |
|-----------|--------|
| `XmlPage.number` | 必須、正の整数 |
| `XmlPage.source_file` | オプション（空文字列可） |
| `XmlPage.announcement` | オプション（空文字列可） |
| `XmlPage.content_text` | オプション（空文字列可） |
| `Figure.read_aloud` | "true", "false", "optional" のいずれか |

## State Transitions

なし（データは読み取り専用）

## Scale Assumptions

| 項目 | 想定値 |
|------|--------|
| XML ファイルサイズ | 最大 10MB |
| ページ数 | 最大 1000 ページ |
| ページあたり文字数 | 最大 10,000 文字 |
