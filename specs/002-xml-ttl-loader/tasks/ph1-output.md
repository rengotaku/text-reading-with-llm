# Phase 1 Output: Setup

**Date**: 2026-02-07
**Status**: ✅ Complete

## 既存コード分析

### Page クラス (`src/text_cleaner.py:89-94`)

```python
@dataclass(frozen=True)
class Page:
    """A single page extracted from the book markdown."""
    number: int
    text: str
```

- フィールド: `number: int`, `text: str`
- frozen=True（イミュータブル）
- シンプルな構造 → XmlPage からの変換が容易

### process_pages() (`src/pipeline.py:130-213`)

- 入力: `list[Page]`, `VoicevoxSynthesizer`, `output_dir`, `args`
- 処理フロー:
  1. テキストをチャンクに分割 (`split_text_into_chunks`)
  2. 各チャンクを音声合成 (`generate_audio`)
  3. 音声を正規化 (`normalize_audio`)
  4. ページ単位で WAV 保存
  5. 全ページを結合
- 依存: `args.max_chunk_chars`, `args.style_id`, `args.speed`

### VoicevoxSynthesizer (`src/voicevox_client.py:49-193`)

- 主要メソッド:
  - `__init__(config)`: 設定で初期化
  - `initialize()`: Core の初期化
  - `load_model(style_id)`: モデルロード
  - `synthesize(text, style_id, ...)`: 音声合成
  - `tts(text, style_id, ...)`: 簡易 TTS

## XML 構造分析 (`sample/book.xml`)

### 基本構造

```xml
<book>
  <metadata><title>...</title></metadata>
  <page number="N" sourceFile="page_NNNN.png">
    <pageAnnouncement format="simple">Nページ</pageAnnouncement>
    <content>
      <paragraph>...</paragraph>
      <heading level="N">...</heading>
      <list><item>...</item></list>
    </content>
    <figure readAloud="optional|false">
      <file readAloud="false">...</file>
      <description>...</description>
    </figure>
    <pageMetadata readAloud="false">...</pageMetadata>
  </page>
</book>
```

### readAloud 属性

| 値 | 処理 |
|----|------|
| なし | 読み上げる |
| `"true"` | 読み上げる |
| `"optional"` | 読み上げる |
| `"false"` | スキップ |

### テキスト抽出順序

1. `<pageAnnouncement>` → ページ先頭
2. `<content>` 内要素（DOM 順）
3. `<figure>/<description>` → readAloud 属性次第

## 成果物

### テストフィクスチャ

- `tests/fixtures/` ディレクトリ作成済み
- `tests/fixtures/sample_book.xml` 作成済み
  - 3 ページ構成
  - 各種要素（paragraph, heading, list, figure）含む
  - readAloud="false" のテストケース含む

## 次のフェーズへの引継ぎ

### Phase 2 で実装するもの

1. `XmlPage`, `Figure` データクラス
2. `parse_book_xml()` 関数
3. `to_page()` 変換関数
4. `_extract_content_text()` ヘルパー

### 注意点

- `Page` は frozen=True なので、変換時に新規インスタンス作成
- `process_pages()` は `args` の特定フィールドを参照するため、互換性を保つ
- XML コメントは ElementTree で自動的に無視される
