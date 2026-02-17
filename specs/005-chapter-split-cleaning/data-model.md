# Data Model: チャプター分割とクリーニング

**Date**: 2026-02-18
**Branch**: `005-chapter-split-cleaning`

## Entities

### ContentItem（既存 + 拡張）

読み上げ対象のコンテンツ単位。

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| item_type | str | コンテンツ種別（"paragraph", "heading", "list_item"） | Yes |
| text | str | テキスト内容（マーカー含む場合あり） | Yes |
| heading_info | HeadingInfo \| None | 見出し情報（heading のみ） | No |
| **chapter_number** | int \| None | **所属章番号（新規追加）** | No |

**変更点**: `chapter_number` フィールドを追加（オプショナル、デフォルト None）

**バリデーション**:
- item_type は "paragraph", "heading", "list_item" のいずれか
- chapter_number が設定される場合は 1 以上の整数

---

### HeadingInfo（既存、変更なし）

見出しの詳細情報。

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| level | int | 見出しレベル（1=章, 2=節, 3以上=小節） | Yes |
| number | str | 見出し番号（"1", "1.2" など） | Yes |
| title | str | 見出しタイトル | Yes |
| read_aloud | bool | 読み上げ対象かどうか | Yes |

---

### ChapterInfo（新規）

章の集約情報。出力ファイル生成に使用。

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| number | int | 章番号（1, 2, 3, ...） | Yes |
| title | str | 章タイトル（XML の title 属性から取得） | Yes |
| sanitized_filename | str | サニタイズ済みファイル名（`ch01_title`形式） | Yes |
| items | list[ContentItem] | 章に属するコンテンツ一覧 | Yes |

**バリデーション**:
- number は 1 以上の整数
- sanitized_filename は半角英数字とアンダースコアのみ
- items は空でない（空の章は出力しない）

---

## Relationships

```
book2.xml
    │
    ├── <chapter number="1" title="...">
    │       │
    │       ├── ContentItem (chapter_number=1)
    │       ├── ContentItem (chapter_number=1)
    │       └── ...
    │
    ├── <chapter number="2" title="...">
    │       │
    │       ├── ContentItem (chapter_number=2)
    │       └── ...
    │
    └── ...
```

---

## State Transitions

### ContentItem 処理フロー

```
[Raw XML Text]
      ↓ parse_book2_xml()
[ContentItem with chapter_number]
      ↓ clean_page_text()
[Cleaned Text]
      ↓ generate_audio()
[WAV Data]
      ↓ save_audio()
[WAV File]
```

### Chapter 出力フロー

```
[ContentItem list]
      ↓ group by chapter_number
[ChapterInfo list]
      ↓ for each chapter
[chapters/ch{NN}_{title}.wav]
      ↓ concatenate_audio_files()
[book.wav]
```

---

## Output Structure

```
output/{content_hash}/
├── chapters/
│   ├── ch01_{title}.wav
│   ├── ch02_{title}.wav
│   └── ...
├── book.wav              # 全章結合
└── cleaned_text.txt      # クリーニング済みテキスト
```
