# Phase 2 Output: User Story 1 - XML パーサー実装

**Date**: 2026-02-07
**Status**: ✅ Complete

## 作業概要

- Phase 2 - User Story 1 (XML to TTS Pipeline) の実装完了
- FAIL テスト 33 件を PASS させた
- XML パーサーの基本機能を実装

## 修正ファイル一覧

### 新規作成

- `src/xml_parser.py` - XML パーサーモジュール
  - `Figure` dataclass: 図の情報 (file_path, description, read_aloud)
  - `XmlPage` dataclass: XML から抽出したページデータ (number, source_file, announcement, content_text, figures)
  - `parse_book_xml(xml_path)`: XML ファイルをパースして XmlPage リストを返す
  - `to_page(xml_page)`: XmlPage を既存の Page オブジェクトに変換
  - `_extract_content_text(content_elem)`: content 要素からテキストを抽出

## 実装の詳細

### parse_book_xml() の動作

1. XML ファイルを xml.etree.ElementTree でパース
2. 各 `<page>` 要素から以下を抽出:
   - `number` 属性 → int 型に変換
   - `sourceFile` 属性
   - `<pageAnnouncement>` テキスト
   - `<content>` 内のテキスト (DOM 順)
   - `<figure>` 要素のリスト
3. XmlPage オブジェクトのリストを返す

### _extract_content_text() の動作

content 要素内の子要素を DOM 順に処理:
- `<paragraph>`: テキストを抽出
- `<heading>`: テキストを抽出
- `<list>`: 各 `<item>` のテキストを抽出

抽出したテキストを改行で結合して返す。

### to_page() の動作

XmlPage を Page に変換:
1. `announcement` を先頭に配置
2. `content_text` を追加
3. `figures` の description を追加 (readAloud != "false" の場合)
4. すべてを改行で結合して Page オブジェクトを作成

## テスト結果

```
190 passed in 0.10s
```

全 190 テストが PASS:
- 既存テスト: 157 件 (リグレッションなし)
- 新規テスト: 33 件 (US1 XML パーサー)

### 新規テスト内訳

| カテゴリ | テスト数 | 内容 |
|---------|---------|------|
| TestParseBookXmlReturnsPages | 3 | parse_book_xml の基本動作 |
| TestXmlPageHasNumberAndText | 5 | XmlPage dataclass のフィールド |
| TestExtractParagraphText | 3 | paragraph テキスト抽出 |
| TestExtractHeadingText | 3 | heading テキスト抽出 |
| TestExtractListItems | 2 | list/item テキスト抽出 |
| TestExtractPageAnnouncement | 3 | ページアナウンス抽出 |
| TestToPageConversion | 5 | XmlPage → Page 変換 |
| TestFigureDataclass | 4 | Figure dataclass のフィールド |
| TestToPageWithFigureDescription | 1 | figure description の to_page 統合 |
| TestParseBookXmlWithPath | 2 | Path 型対応 |
| TestEdgeCases | 3 | エッジケース |

## 注意点

### Phase 3 (US2) で実装する機能

現時点では **readAloud 属性のフィルタリングは未実装**。Phase 3 で以下を実装:
- `readAloud="false"` 要素のスキップ
- content 要素内の paragraph, heading での readAloud チェック
- figure の readAloud チェックは既に to_page() で実装済み

### データフロー

```
XML file → parse_book_xml() → list[XmlPage] → to_page() → list[Page] → TTS pipeline
```

### 技術選択

- **xml.etree.ElementTree**: Python 標準ライブラリの XML パーサー
  - 軽量で高速
  - XML コメントは自動的に無視される
  - DOM 順でのテキスト抽出が容易

## 次 Phase への引き継ぎ

### Phase 3 で必要な作業

1. **readAloud 属性フィルタリングの実装**:
   - `_should_read_aloud(elem)` ヘルパー関数を追加
   - `_extract_content_text()` を更新して readAloud="false" をスキップ
   - `pageMetadata` 要素のスキップ

2. **テストの追加**:
   - readAloud="false" 要素のスキップテスト
   - pageMetadata のスキップテスト
   - XML コメントの無視テスト (既に動作中)

### 既存コードとの互換性

- `Page` dataclass は frozen=True なのでイミュータブル
- `process_pages()` は `list[Page]` を期待するため、変換済みリストを渡す
- 既存の TTS パイプラインは変更不要

## 実装のミス・課題

なし - 全テスト PASS、リグレッションなし
