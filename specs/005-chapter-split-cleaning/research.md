# Research: チャプター分割とクリーニング

**Date**: 2026-02-18
**Branch**: `005-chapter-split-cleaning`

## 調査項目

### 1. 既存 clean_page_text() の処理内容

**Decision**: 既存関数をそのまま再利用する

**調査結果** (`src/text_cleaner.py:186-268`):

```python
def clean_page_text(text: str, heading_marker: str | None = None) -> str:
    # 1. URL除去 (_clean_urls)
    # 2. ISBN除去 (_clean_isbn)
    # 3. 括弧内英語除去 (_clean_parenthetical_english)
    # 4. 参照正規化 (_normalize_references) - 図X.Y → ずXのY
    # 5. HTMLコメント除去
    # 6. 図の説明除去
    # 7. ページ番号除去
    # 8. Markdown処理
    # 9. 句読点正規化 (normalize_punctuation)
    # 10. 数値正規化 (normalize_numbers) - 123 → ひゃくにじゅうさん
    # 11. 静的辞書適用 (apply_reading_rules)
    # 12. LLM辞書適用 (apply_llm_readings)
    # 13. 漢字→カナ変換 (convert_to_kana)
```

**Rationale**: 既存実装は十分に成熟しており、xml_pipeline で動作実績がある。変更は不要。

---

### 2. ContentItem への chapter_number 追加方法

**Decision**: オプショナル属性として追加（デフォルト None）

**調査結果** (`src/xml2_parser.py:35-46`):

現在の ContentItem:
```python
@dataclass
class ContentItem:
    item_type: str
    text: str
    heading_info: HeadingInfo | None = None
```

追加後:
```python
@dataclass
class ContentItem:
    item_type: str
    text: str
    heading_info: HeadingInfo | None = None
    chapter_number: int | None = None  # 追加
```

**Rationale**:
- デフォルト None により既存テストとの後方互換性を維持
- chapter がない XML でも動作可能

---

### 3. ファイル名サニタイズ方法

**Decision**: 日本語タイトルは chapter 番号のみをファイル名に使用

**Alternatives considered**:

| 方法 | メリット | デメリット |
|------|----------|------------|
| ローマ字変換 | タイトルが分かる | 変換ライブラリ依存、長くなる |
| 番号のみ | シンプル、確実 | タイトルが分からない |
| 番号+短縮タイトル | バランス良い | 実装複雑 |

**選択**: `ch{NN}_{short_title}.wav` 形式
- 番号: 2桁ゼロ埋め
- タイトル: 半角英数字とアンダースコアのみ許可、日本語は除去、最大20文字

**実装例**:
```python
def sanitize_filename(title: str, max_length: int = 20) -> str:
    # 半角英数字とアンダースコアのみ残す
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '', title)
    if not sanitized:
        return "untitled"
    return sanitized[:max_length]
```

---

### 4. chapter 分割出力の実装パターン

**Decision**: xml_pipeline の pages 処理パターンを参考にする

**調査結果** (`src/xml_pipeline.py:159-211`):

```python
def process_pages_with_heading_sound(...):
    pages_dir = output_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    for page in pages:
        # ページ毎に処理・出力
        page_path = pages_dir / f"page_{page.number:04d}.wav"
        save_audio(combined, sample_rate, page_path)

    # 全ページ結合
    concatenate_audio_files(wav_files, combined_path)
```

**適用**:
```python
def process_chapters(...):
    chapters_dir = output_dir / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)

    for chapter_num, items in grouped_by_chapter.items():
        chapter_path = chapters_dir / f"ch{chapter_num:02d}_{title}.wav"
        # chapter 毎に処理・出力

    # 全 chapter 結合
    concatenate_audio_files(wav_files, book_path)
```

---

### 5. clean_page_text() 呼び出しタイミング

**Decision**: process_content() 内、TTS 生成直前に適用

**調査結果**:

xml_pipeline では:
```python
# L261
cleaned_text = clean_page_text(page.text, heading_marker=HEADING_MARKER)
```

xml2_pipeline での適用箇所:
```python
def process_content(...):
    for item in content_items:
        text = item.text
        # マーカー除去
        if text.startswith(CHAPTER_MARKER):
            text = text[len(CHAPTER_MARKER):]
        # ここで clean_page_text() を適用
        text = clean_page_text(text)
        # TTS 生成
```

**Rationale**: マーカー除去後、TTS 生成前が最適なタイミング

---

## 未解決事項

なし - 全ての調査項目が解決済み
