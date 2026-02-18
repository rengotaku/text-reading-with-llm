# Phase 2 RED Tests

## サマリー

- Phase: Phase 2 - User Story 1: 新XMLフォーマットの基本パース
- FAIL テスト数: 40 (全テストが import エラーで FAIL)
- テストファイル: tests/test_xml2_parser.py

## FAIL テスト一覧

| テストファイル | テストクラス | テストメソッド | 期待動作 |
|---------------|-------------|---------------|---------|
| tests/test_xml2_parser.py | TestParseBook2XmlReturnsList | test_parse_book2_xml_returns_list | parse_book2_xml が list を返す |
| tests/test_xml2_parser.py | TestParseBook2XmlReturnsList | test_parse_book2_xml_returns_content_item_instances | 各要素が ContentItem インスタンス |
| tests/test_xml2_parser.py | TestParseBook2XmlReturnsList | test_parse_book2_xml_with_pathlib_path | pathlib.Path を受け付ける |
| tests/test_xml2_parser.py | TestParseBook2XmlReturnsList | test_parse_book2_xml_with_string_path | 文字列パスを受け付ける |
| tests/test_xml2_parser.py | TestParseBook2XmlSkipsToc | test_toc_content_not_in_result | toc セクションの内容を除外 |
| tests/test_xml2_parser.py | TestParseBook2XmlSkipsToc | test_toc_section_completely_skipped | toc セクション全体をスキップ |
| tests/test_xml2_parser.py | TestParseBook2XmlSkipsFrontMatter | test_front_matter_paragraph_not_in_result | front-matter 内の paragraph を除外 |
| tests/test_xml2_parser.py | TestParseBook2XmlSkipsFrontMatter | test_front_matter_heading_not_in_result | front-matter 内の heading を除外 |
| tests/test_xml2_parser.py | TestParseBook2XmlExtractsParagraphs | test_extract_paragraph_text | paragraph テキストを抽出 |
| tests/test_xml2_parser.py | TestParseBook2XmlExtractsParagraphs | test_paragraph_text_content | paragraph 内容が正しい |
| tests/test_xml2_parser.py | TestParseBook2XmlExtractsParagraphs | test_paragraph_item_type | item_type が "paragraph" |
| tests/test_xml2_parser.py | TestParseBook2XmlExtractsParagraphs | test_paragraph_has_no_heading_info | heading_info が None |
| tests/test_xml2_parser.py | TestParseBook2XmlExtractsParagraphs | test_multiple_paragraphs_extracted | 複数 paragraph を抽出 |
| tests/test_xml2_parser.py | TestParseBook2XmlRespectsReadAloudFalse | test_skip_paragraph_with_read_aloud_false | readAloud=false をスキップ |
| tests/test_xml2_parser.py | TestParseBook2XmlRespectsReadAloudFalse | test_include_paragraph_with_read_aloud_true | readAloud=true を抽出 |
| tests/test_xml2_parser.py | TestParseBook2XmlRespectsReadAloudFalse | test_default_read_aloud_is_true | 属性なしはデフォルト抽出 |
| tests/test_xml2_parser.py | TestParseBook2XmlExtractsListItems | test_extract_list_items | list item を抽出 |
| tests/test_xml2_parser.py | TestParseBook2XmlExtractsListItems | test_list_item_text_content | list item 内容が正しい |
| tests/test_xml2_parser.py | TestParseBook2XmlExtractsListItems | test_list_item_count | list item 数が 3 |
| tests/test_xml2_parser.py | TestParseBook2XmlExtractsListItems | test_list_item_type | item_type が "list_item" |
| tests/test_xml2_parser.py | TestParseBook2XmlExtractsListItems | test_list_items_preserve_order | list item 順序保持 |
| tests/test_xml2_parser.py | TestContentItemDataclass | test_content_item_has_item_type | item_type フィールドあり |
| tests/test_xml2_parser.py | TestContentItemDataclass | test_content_item_has_text | text フィールドあり |
| tests/test_xml2_parser.py | TestContentItemDataclass | test_content_item_has_heading_info | heading_info フィールドあり |
| tests/test_xml2_parser.py | TestHeadingInfoDataclass | test_heading_info_has_level | level フィールドあり |
| tests/test_xml2_parser.py | TestHeadingInfoDataclass | test_heading_info_has_number | number フィールドあり |
| tests/test_xml2_parser.py | TestHeadingInfoDataclass | test_heading_info_has_title | title フィールドあり |
| tests/test_xml2_parser.py | TestHeadingInfoDataclass | test_heading_info_has_read_aloud | read_aloud フィールドあり |
| tests/test_xml2_parser.py | TestMarkerConstants | test_chapter_marker_defined | CHAPTER_MARKER = "\\uE001" |
| tests/test_xml2_parser.py | TestMarkerConstants | test_section_marker_defined | SECTION_MARKER = "\\uE002" |
| tests/test_xml2_parser.py | TestEdgeCases | test_empty_paragraph_skipped | 空 paragraph をスキップ |
| tests/test_xml2_parser.py | TestEdgeCases | test_text_is_not_empty | 空テキストなし |
| tests/test_xml2_parser.py | TestEdgeCases | test_document_order_preserved | ドキュメント順序保持 |

## 実装ヒント

### 必要なファイル

`src/xml2_parser.py` に以下を実装:

```python
from dataclasses import dataclass
from pathlib import Path

# マーカー定数
CHAPTER_MARKER = "\uE001"  # chapter 効果音用
SECTION_MARKER = "\uE002"  # section 効果音用

@dataclass
class HeadingInfo:
    level: int           # 1=chapter, 2+=section
    number: str          # "1", "1.2", "3.10" etc.
    title: str           # 見出しテキスト
    read_aloud: bool = True

@dataclass
class ContentItem:
    item_type: str       # "paragraph", "heading", "list_item"
    text: str            # テキスト内容（マーカー含む）
    heading_info: HeadingInfo | None = None

def parse_book2_xml(xml_path: Path | str) -> list[ContentItem]:
    """Parse book2.xml and extract content items.

    Skips:
    - <toc> section
    - <front-matter> section
    - <metadata> section
    - Elements with readAloud="false"

    Processes:
    - <heading level="N"> elements
    - <paragraph> elements
    - <list>/<item> elements

    Returns:
        List of ContentItem in document order
    """
    pass  # 実装する
```

### 処理フロー

1. XML をパース (`xml.etree.ElementTree`)
2. `<toc>`, `<front-matter>`, `<metadata>` をスキップ
3. 本文要素を順番に処理:
   - `<heading>`: `item_type="heading"`, `heading_info` を設定
   - `<paragraph>`: `item_type="paragraph"`
   - `<list>/<item>`: `item_type="list_item"`
4. `readAloud="false"` の要素をスキップ
5. 空テキストの要素をスキップ
6. `list[ContentItem]` を返却

### テストフィクスチャ

`tests/fixtures/sample_book2.xml` 構造:

```xml
<book>
    <metadata><title>Test Book 2</title></metadata>
    <toc begin="1" end="2">
        <entry level="1" number="1" title="First Chapter" />
        ...
    </toc>
    <front-matter>
        <paragraph readAloud="true">This is front matter text.</paragraph>
        <heading level="2" readAloud="true">Front Matter Heading</heading>
    </front-matter>
    <!-- Main content -->
    <heading level="1" readAloud="true">First Chapter</heading>
    <paragraph readAloud="true">This is the first paragraph...</paragraph>
    <list>
        <item>List item one</item>
        <item>List item two</item>
        <item>List item three</item>
    </list>
    <paragraph readAloud="false">This paragraph should be skipped.</paragraph>
    ...
</book>
```

## FAIL 出力例

```
$ make test
PYTHONPATH=/data/projects/text-reading-with-llm .venv/bin/python -m pytest tests/ -v
============================= test session starts ==============================
platform linux -- Python 3.13.11, pytest-9.0.2, pluggy-1.6.0
collecting ... collected 321 items / 1 error

==================================== ERRORS ====================================
__________________ ERROR collecting tests/test_xml2_parser.py __________________
ImportError while importing test module '/data/projects/text-reading-with-llm/tests/test_xml2_parser.py'.
tests/test_xml2_parser.py:18: in <module>
    from src.xml2_parser import (
E   ModuleNotFoundError: No module named 'src.xml2_parser'
=========================== short test summary info ============================
ERROR tests/test_xml2_parser.py
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.22s ===============================
make: *** [Makefile:63: test] Error 2
```

## 次ステップ

phase-executor が以下を実行:

1. RED tests を読み込み (`specs/004-new-xml-format/red-tests/ph2-test.md`)
2. `src/xml2_parser.py` に実装
3. `make test` で GREEN 確認
4. `specs/004-new-xml-format/tasks/ph2-output.md` を生成
