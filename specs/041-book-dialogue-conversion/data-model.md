# Data Model: 書籍内容の対話形式変換

**Branch**: `041-book-dialogue-conversion`
**Date**: 2026-03-13

## エンティティ定義

### 1. Section（入力）

既存のXML構造から抽出されるセクション。

| Field | Type | Description |
|-------|------|-------------|
| number | str | セクション番号（"1.1", "2.3"など） |
| title | str | セクションタイトル |
| paragraphs | list[str] | 段落テキストのリスト |
| chapter_number | int | 所属するチャプター番号 |

### 2. DialogueBlock（出力）

LLM変換後の対話ブロック。

| Field | Type | Description |
|-------|------|-------------|
| section_number | str | 元のセクション番号 |
| section_title | str | 元のセクションタイトル |
| introduction | str | 導入テキスト（narrator用） |
| dialogue | list[Utterance] | 対話発言リスト |
| conclusion | str | 結論テキスト（narrator用） |

### 3. Utterance（発言）

対話内の個々の発言。

| Field | Type | Description |
|-------|------|-------------|
| speaker | Literal["A", "B"] | 話者ID（A=博士, B=助手） |
| text | str | 発言テキスト |

### 4. Speaker（話者設定）

VOICEVOXの話者設定。

| Field | Type | Description |
|-------|------|-------------|
| id | Literal["narrator", "A", "B"] | 話者ID |
| role | str | 役割説明 |
| voicevox_style_id | int | VOICEVOXスタイルID |
| character_name | str | キャラクター名 |

**デフォルト設定:**

| id | role | voicevox_style_id | character_name |
|----|------|-------------------|----------------|
| narrator | 導入・結論 | 13 | 青山龍星 |
| A | 博士（説明役） | 67 | 麒ヶ島宗麟 |
| B | 助手（質問役） | 2 | 四国めたん |

### 5. ConversionResult（変換結果）

変換処理の結果。

| Field | Type | Description |
|-------|------|-------------|
| success | bool | 変換成功フラグ |
| dialogue_block | DialogueBlock | None | 変換結果（成功時） |
| error_message | str | None | エラーメッセージ（失敗時） |
| processing_time_sec | float | 処理時間（秒） |
| input_char_count | int | 入力文字数 |
| was_split | bool | 分割処理されたか |

## XML スキーマ

### 入力XML（既存book2.xml）

```xml
<book>
  <chapter number="1">
    <heading level="1">チャプタータイトル</heading>
    <section number="1.1">
      <heading level="2">セクションタイトル</heading>
      <paragraph>段落1のテキスト...</paragraph>
      <paragraph>段落2のテキスト...</paragraph>
    </section>
  </chapter>
</book>
```

### 中間XML（対話形式）

```xml
<dialogue-book>
  <chapter number="1">
    <heading level="1">チャプタータイトル</heading>
    <dialogue-section number="1.1" title="セクションタイトル">
      <introduction speaker="narrator">
        この節では、○○について説明します。
      </introduction>
      <dialogue>
        <utterance speaker="A">
          まず、基本的な概念から説明しましょう。
        </utterance>
        <utterance speaker="B">
          はい、お願いします。○○とは何ですか？
        </utterance>
        <utterance speaker="A">
          ○○とは、△△のことです。
        </utterance>
      </dialogue>
      <conclusion speaker="narrator">
        以上が○○の基本的な説明でした。
      </conclusion>
    </dialogue-section>
  </chapter>
</dialogue-book>
```

## 状態遷移

### セクション変換フロー

```
[Raw Section]
    ↓ extract_paragraphs()
[Paragraphs List]
    ↓ check_length()
    ├── <= 3,500 chars → [Single Block]
    └── > 4,000 chars → split_by_heading() → [Multiple Blocks]
    ↓
[Block(s)]
    ↓ llm_structure_analysis()
[Classified Paragraphs] (intro/dialogue/conclusion)
    ↓ llm_dialogue_generation()
[DialogueBlock]
    ↓ to_xml()
[Dialogue XML]
```

### バリデーションルール

1. **Section**
   - paragraphsは1つ以上必要
   - numberは"X.Y"形式（X, Yは整数）

2. **DialogueBlock**
   - dialogueは1つ以上のUtteranceを含む
   - introductionとconclusionはオプショナル

3. **Utterance**
   - speakerは"A"または"B"のみ
   - textは空でない

4. **Speaker**
   - voicevox_style_idは有効なVOICEVOXスタイル
