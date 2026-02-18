# Phase 1 Output: Setup

**Date**: 2026-02-18
**Status**: 完了

## 実行タスク

- [x] T001 Read current implementation in src/xml2_parser.py, src/xml2_pipeline.py
- [x] T002 [P] Read existing tests in tests/test_xml2_parser.py, tests/test_xml2_pipeline.py
- [x] T003 [P] Read text_cleaner in src/text_cleaner.py (clean_page_text function)
- [x] T004 Verify `make test` passes (no regression from existing tests)
- [x] T005 Edit and rename: specs/005-chapter-split-cleaning/tasks/ph1-output-template.md → ph1-output.md

## 既存コード分析

### src/xml2_parser.py

**構造**:
- `ContentItem` (dataclass): 読み上げ対象のコンテンツ単位
  - `item_type: str` - "paragraph", "heading", "list_item"
  - `text: str` - テキスト内容（マーカー含む）
  - `heading_info: HeadingInfo | None` - 見出し情報
- `HeadingInfo` (dataclass): 見出し詳細
  - `level: int` - 見出しレベル（1=章, 2+=節）
  - `number: str` - 見出し番号
  - `title: str` - 見出しテキスト
  - `read_aloud: bool` - 読み上げ対象か
- `CHAPTER_MARKER = "\uE001"` - 章マーカー（Unicode private use area）
- `SECTION_MARKER = "\uE002"` - 節マーカー
- `format_heading_text(level, number, title)` - 見出し整形（第N章/第N節）
- `parse_book2_xml(xml_path)` - book2.xml パース、ContentItem リスト返却

**更新が必要な箇所**:
1. `ContentItem` dataclass: `chapter_number: int | None = None` フィールドを追加（US2対応）
2. `parse_book2_xml()`: chapter 要素を追跡し、各 ContentItem に chapter_number を割り当て

**現在の chapter 処理**:
- `<chapter>` 要素は level=1 heading として処理される（L116-130）
- chapter 内の子要素を再帰的に処理
- **chapter_number の追跡はまだ実装されていない**

### src/xml2_pipeline.py

**構造**:
- `parse_args()` - CLI引数パース
- `load_sound(sound_path, target_sr)` - 効果音ロード・リサンプリング・正規化
- `process_content(content_items, synthesizer, ...)` - コンテンツ処理・音声生成
- `main()` - エントリーポイント

**更新が必要な箇所**:
1. `process_content()`:
   - `clean_page_text()` 呼び出し追加（US1対応、L199付近のマーカー除去後）
   - chapter 分割出力ロジック追加（US2対応）
2. `main()`:
   - cleaned_text.txt 出力時に clean_page_text() 適用（US3対応、L269-278）

**現在のマーカー処理フロー** (L185-196):
```python
for item in content_items:
    text = item.text
    # マーカー除去
    if text.startswith(CHAPTER_MARKER):
        audio_segments.append(chapter_sound)
        text = text[len(CHAPTER_MARKER):]
    elif text.startswith(SECTION_MARKER):
        audio_segments.append(section_sound)
        text = text[len(SECTION_MARKER):]
    # ここで clean_page_text() を追加する（US1）
    # TTS 生成
```

**現在の出力構造** (L222-224):
```python
combined = np.concatenate(audio_segments)
output_path = output_dir / "book.wav"  # 1ファイルのみ
```

### src/text_cleaner.py

**構造**:
- `clean_page_text(text, heading_marker)` - テキストクリーニング（L187-269）
  - URL除去 (`_clean_urls`)
  - ISBN除去 (`_clean_isbn`)
  - 括弧内英語除去 (`_clean_parenthetical_english`)
  - 参照正規化 (`_normalize_references`)
  - Markdown処理
  - 句読点正規化 (`normalize_punctuation`)
  - 数値正規化 (`normalize_numbers`) - 123 → ひゃくにじゅうさん
  - 静的辞書適用 (`apply_reading_rules`)
  - LLM辞書適用 (`apply_llm_readings`)
  - 漢字→カナ変換 (`convert_to_kana`)

**変更不要**: 既存実装は完全であり、xml_pipeline で動作実績がある。そのまま xml2_pipeline で再利用。

## 既存テスト分析

- `tests/test_xml2_parser.py` (756行): parse_book2_xml, ContentItem, HeadingInfo の包括的テスト
  - Phase 2/3 RED Tests (format_heading_text, markers) が既に含まれている
  - **不足**: chapter_number 関連テスト（US2で追加）

- `tests/test_xml2_pipeline.py` (598行): xml2_pipeline の包括的テスト
  - Phase 4 RED Tests (parse_args, load_sound, process_content, main) が既に含まれている
  - **不足**: clean_page_text 適用テスト（US1で追加）
  - **不足**: chapter 分割出力テスト（US2で追加）
  - **不足**: cleaned_text.txt クリーニング適用テスト（US3で追加）

**追加が必要なフィクスチャ**:
- なし（既存の `tests/fixtures/sample_book2.xml` で十分）

## テスト実行結果

```bash
make test
============================= 404 passed in 0.79s ==============================
```

**すべてのテストが PASS** - 既存機能への影響なし、安全に変更可能。

## 技術的決定事項

1. **ContentItem.chapter_number はオプショナル（デフォルト None）**:
   - 既存テストとの後方互換性を維持
   - chapter がない XML でも動作可能
   - chapter 外のコンテンツは chapter_number=None

2. **clean_page_text() 呼び出しタイミング**:
   - process_content() 内、マーカー除去後・TTS生成前（L199付近）
   - マーカー（CHAPTER_MARKER, SECTION_MARKER）は clean_page_text に渡さない
   - 理由: マーカーは効果音挿入にのみ使用、TTS対象外

3. **chapter 分割出力の実装パターン**:
   - xml_pipeline の pages 処理パターンを参考にする
   - `process_chapters()` 関数を新規作成
   - chapters/ ディレクトリに chapter 毎の WAV を出力
   - 全 chapter を結合して book.wav を出力

4. **ファイル名サニタイズ**:
   - 形式: `ch{NN}_{sanitized_title}.wav`
   - 番号: 2桁ゼロ埋め
   - タイトル: 半角英数字とアンダースコアのみ、日本語除去、最大20文字
   - 空の場合: "untitled"

## 次フェーズへの引き継ぎ

### Phase 2 (US1: テキストクリーニングの適用)

**実装するもの**:
- `xml2_pipeline.py::process_content()` 内に `clean_page_text()` 呼び出しを追加

**既存コード流用**:
- `text_cleaner.py::clean_page_text()` - そのまま呼び出し可能
- マーカー除去ロジック（L189-196）- 既に実装済み

**注意点**:
- clean_page_text() はマーカー除去後に呼び出す
- heading_marker パラメータは不要（マーカーは既に除去済み）
- 空文字列チェック（L200-201）は clean_page_text() の後でも維持

### Phase 3 (US2: チャプター単位の分割出力)

**実装するもの**:
- `xml2_parser.py::ContentItem` に `chapter_number` フィールド追加
- `xml2_parser.py::parse_book2_xml()` に chapter 追跡ロジック追加
- `xml2_pipeline.py::sanitize_filename()` 関数を新規作成
- `xml2_pipeline.py::process_chapters()` 関数を新規作成
- `xml2_pipeline.py::main()` で `process_chapters()` 呼び出し

**既存コード流用**:
- `xml_pipeline.py::process_pages_with_heading_sound()` のパターン
- `pipeline.py::concatenate_audio_files()` - WAV 結合

**注意点**:
- ContentItem 変更による既存テスト影響を確認
- chapter_number がない場合（=None）は従来通り book.wav のみ出力
- chapters/ ディレクトリは mkdir(parents=True, exist_ok=True)

### Phase 4 (US3: cleaned_text.txt の品質向上)

**実装するもの**:
- `xml2_pipeline.py::main()` の cleaned_text.txt 出力部分（L269-278）を修正
- item.text に clean_page_text() を適用してから出力

**既存コード流用**:
- `text_cleaner.py::clean_page_text()` - 同じ関数を再利用

**注意点**:
- マーカー（CHAPTER_MARKER, SECTION_MARKER）は表示用に変換（`[章]`, `[節]`）
- マーカー変換は clean_page_text() 適用後に行う
- chapter 区切りマーカーを挿入（`=== Chapter N: Title ===`）

### Phase 5 (Polish: ドキュメント・型ヒント・クリーンアップ)

**実装するもの**:
- docstrings 追加（sanitize_filename, process_chapters）
- 型ヒント追加（新規関数）
- quickstart.md の手動検証

**注意点**:
- 既存コードの docstring スタイルに従う
- 型ヒントは Python 3.10+ 形式（`list[str]`, `dict[str, int]`）
