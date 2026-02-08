# Research: XML から TTS へのローダー

**Feature Branch**: `002-xml-ttl-loader`
**Date**: 2026-02-07

## 1. XML パーサー選択

### Decision
Python 標準ライブラリの `xml.etree.ElementTree` を使用する

### Rationale
- 追加依存関係なし（標準ライブラリ）
- `book.xml` のサイズ（約 650KB）は DOM パーサーで十分処理可能
- XPath サポートにより要素選択が容易
- 既存プロジェクトの依存関係を増やさない

### Alternatives Considered
| ライブラリ | 長所 | 短所 | 却下理由 |
|-----------|------|------|----------|
| `lxml` | 高速、XPath 2.0 | 追加依存関係、C 拡張 | 本プロジェクトのサイズでは不要 |
| `xml.dom.minidom` | DOM 標準準拠 | API が冗長 | ElementTree の方が Pythonic |
| `defusedxml` | セキュリティ強化 | 追加依存関係 | 信頼済み XML のみ処理 |

## 2. 既存コンポーネントとの統合

### Decision
`process_pages()` 関数をそのまま再利用し、`Page` データクラスに変換するアダプタを実装する

### Rationale
- `process_pages()` は `list[Page]` を受け取り TTS 処理を行う汎用関数
- `Page` は `number: int` と `text: str` の 2 フィールドのみ持つシンプルな構造
- XML パーサーが `Page` オブジェクトを直接生成すれば、アダプタは不要
- ただし、XML 固有の情報（sourceFile, readAloud 等）を保持するため `XmlPage` を中間表現として使用

### Implementation Approach
```python
@dataclass
class XmlPage:
    number: int
    source_file: str
    text: str  # 抽出済みテキスト

def to_page(xml_page: XmlPage) -> Page:
    """XmlPage を既存の Page に変換"""
    return Page(number=xml_page.number, text=xml_page.text)
```

## 3. readAloud 属性の処理

### Decision
要素走査時に `readAloud` 属性をチェックし、`"false"` の場合はスキップする

### Rationale
- XML の構造上、`readAloud` は任意の要素に付与可能
- 親要素に `readAloud="false"` がある場合、子要素も含めてスキップ
- 属性がない場合、または `readAloud="true"` / `readAloud="optional"` はテキスト抽出対象

### Processing Rules
| 属性値 | 処理 |
|--------|------|
| `readAloud="false"` | スキップ |
| `readAloud="true"` | 抽出 |
| `readAloud="optional"` | 抽出（デフォルト動作） |
| 属性なし | 抽出 |

## 4. テキスト抽出順序

### Decision
XML の DOM 順序に従い、以下の順序でテキストを抽出する

### Extraction Order
1. `<pageAnnouncement>` → ページ先頭に配置
2. `<content>` 内の要素（出現順）:
   - `<heading>` → そのまま抽出
   - `<paragraph>` → そのまま抽出
   - `<list>/<item>` → 各アイテムを抽出
3. `<figure>` 内の `<description>` → `readAloud` 属性に従う

### Text Joining
- 要素間は改行で結合
- 連続する空白・改行は正規化（既存の `clean_page_text()` で処理）

## 5. エラーハンドリング

### Decision
`xml.etree.ElementTree.ParseError` をキャッチし、ユーザーフレンドリーなエラーメッセージを表示

### Error Cases
| エラー | 対応 |
|--------|------|
| ファイル不存在 | "Input file not found: {path}" |
| XML パースエラー | "Invalid XML format: {details}" |
| `<book>` ルートなし | "Missing <book> root element" |
| `<page>` 要素なし | "No <page> elements found" |
| `number` 属性なし | "Page missing 'number' attribute at line {line}" |

## 6. コマンドライン引数

### Decision
既存の `pipeline.py` と同様の引数構造を採用し、入力ファイル指定のみ異なる

### Arguments
| 引数 | 説明 | デフォルト |
|------|------|-----------|
| `--input` / `-i` | 入力 XML ファイル | 必須 |
| `--output` / `-o` | 出力ディレクトリ | `./output` |
| `--start-page` | 開始ページ | 1 |
| `--end-page` | 終了ページ | None（最終まで） |
| `--style-id` | VOICEVOX スタイル ID | 13 |
| `--speed` | 話速 | 1.0 |
| `--voicevox-dir` | VOICEVOX Core ディレクトリ | `./voicevox_core_cuda` |

## 7. テスト戦略

### Decision
ユニットテストと統合テストを分離する

### Test Structure
```
tests/
├── test_xml_parser.py      # XML パーサーのユニットテスト
├── test_xml_integration.py # E2E テスト（XML → WAV）
└── fixtures/
    └── sample_book.xml     # テスト用 XML
```

### Key Test Cases
1. 正常な XML からのテキスト抽出
2. `readAloud="false"` 要素のスキップ
3. 空の `<content>` のハンドリング
4. 不正な XML のエラーハンドリング
5. 既存 `Page` との互換性
