# Data Model: 読み辞書生成のXMLファイル対応

**Branch**: `006-xml-dict-support` | **Date**: 2026-02-18

## 既存エンティティ（変更なし）

### ContentItem (src/xml2_parser.py)

```
ContentItem
  item_type: str          # "paragraph", "heading", "list_item"
  text: str               # テキスト内容
  heading_info: HeadingInfo | None
  chapter_number: int | None   # チャプター番号（グループ化のキー）
```

### readings.json (出力形式)

```json
{
  "技術用語": "よみがな",
  "API": "エーピーアイ",
  ...
}
```

保存先: `data/{content_hash}/readings.json`
ハッシュ: 入力ファイルの全テキストの SHA256 先頭12文字

## 新規概念（コード上のクラスとしては不要）

### ChapterGroup（論理概念）

`ContentItem` を `chapter_number` でグループ化した集合。`main()` 関数内で `itertools.groupby` 等を使ってインラインで処理する。

```
ChapterGroup (in-memory only)
  chapter_number: int | None
  items: list[ContentItem]
  → combined_text: str    # items の text を結合した文字列
```

## データフロー

```
XML入力:
  book2.xml → parse_book2_xml() → list[ContentItem]
            → groupby(chapter_number) → list[ChapterGroup]
            → extract_technical_terms(combined_text) per group
            → set(all_terms)
            → generate_readings_batch(terms)
            → save_dict(readings, input_path)

MD入力（既存・変更なし）:
  book.md → read_text() → split_into_pages() → list[Page]
          → extract_technical_terms(page.text) per page
          → set(all_terms)
          → generate_readings_batch(terms)
          → save_dict(readings, input_path)
```
