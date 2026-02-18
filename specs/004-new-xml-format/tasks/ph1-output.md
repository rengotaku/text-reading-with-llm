# Phase 1 Output: Setup

**Date**: 2026-02-18
**Status**: 完了

## 実行タスク

- [x] T001 Read current implementation in src/xml_parser.py, src/xml_pipeline.py
- [x] T002 [P] Read existing tests in tests/test_xml_parser.py, tests/test_xml_pipeline.py
- [x] T003 [P] Read sample XML: sample/book2.xml (first 200 lines)
- [x] T004 [P] Create test fixture: tests/fixtures/sample_book2.xml (minimal book2.xml format)
- [x] T005 Verify `make test` passes (no regression from existing tests)
- [x] T006 Edit and rename: specs/004-new-xml-format/tasks/ph1-output-template.md → ph1-output.md

## 既存コード分析

### src/xml_parser.py

**構造**:
- `Figure`: 図の情報（file_path, description, read_aloud）
- `XmlPage`: ページデータ（number, source_file, announcement, content_text, figures）
- `parse_book_xml()`: book.xml パース、XmlPage リスト返却
- `_should_read_aloud()`: readAloud 属性チェック
- `_extract_content_text()`: コンテンツテキスト抽出
- `to_page()`: XmlPage → Page 変換
- `HEADING_MARKER`: `\uE000HEADING\uE000` (見出し効果音用マーカー)

**再利用可能なパターン**:
1. `_should_read_aloud()`: readAloud 属性の処理ロジック
2. `HEADING_MARKER` のアプローチ: Unicode Private Use Area 文字使用

**新規実装との違い**:
- 既存: page 単位でコンテンツを処理
- 新規: book 全体を ContentItem リストとして処理
- 既存: HEADING_MARKER 1種類
- 新規: CHAPTER_MARKER + SECTION_MARKER の2種類

### src/xml_pipeline.py

**構造**:
- `parse_args()`: CLI引数パース
- `load_heading_sound()`: 効果音ロード（リサンプリング、ステレオ→モノ変換）
- `process_pages_with_heading_sound()`: ページ処理（HEADING_MARKER で分割、効果音挿入）
- `main()`: エントリポイント

**再利用可能なパターン**:
1. `load_heading_sound()`: 効果音ロード処理（そのまま流用可能）
2. `process_pages_with_heading_sound()` のマーカー分割ロジック
3. VOICEVOX 初期化・設定パターン

**新規実装との違い**:
- 既存: `--heading-sound` 1種類
- 新規: `--chapter-sound` + `--section-sound` の2種類

## 既存テスト分析

- `tests/test_xml_parser.py`: XmlPage, Figure, parse_book_xml, to_page のテスト（62テスト）
- `tests/test_xml_pipeline.py`: parse_args, main のテスト（15テスト）

**存在しない**:
- tests/test_xml2_parser.py → 新規作成（Phase 2）
- tests/test_xml2_pipeline.py → 新規作成（Phase 4）

**作成済みフィクスチャ**:
- `tests/fixtures/sample_book2.xml`: book2.xml 形式の最小テストデータ

## 新規作成ファイル

### src/xml2_parser.py (Phase 2-3 で実装)

- `HeadingInfo`: 見出し情報データクラス（level, number, title, read_aloud）
- `ContentItem`: コンテンツ単位データクラス（item_type, text, heading_info）
- `CHAPTER_MARKER`: `\uE001` (chapter 効果音用)
- `SECTION_MARKER`: `\uE002` (section 効果音用)
- `parse_book2_xml()`: book2.xml パース
- `_should_read_aloud()`: readAloud 属性チェック
- `format_heading_text()`: 見出し整形（第N章/第N.N節）

### src/xml2_pipeline.py (Phase 4 で実装)

- `parse_args()`: CLI引数パース（--chapter-sound, --section-sound）
- `load_sound()`: 効果音ロード（load_heading_sound から流用）
- `process_content()`: コンテンツ処理
- `main()`: エントリポイント

## 技術的決定事項

1. **新規ファイル作成**: 既存コード（xml_parser.py, xml_pipeline.py）は変更しない。後方互換性を維持。
2. **マーカー設計**: CHAPTER_MARKER (`\uE001`) と SECTION_MARKER (`\uE002`) を使用。Unicode Private Use Area で text_cleaner を通過。
3. **効果音ロード**: 既存の load_heading_sound() のロジックを load_sound() として再実装。

## sample/book2.xml 構造

```xml
<book>
    <metadata><title>...</title></metadata>
    <toc begin="N" end="M">
        <entry level="1|2" number="X.Y" title="..." />
    </toc>
    <front-matter>
        <paragraph readAloud="true">...</paragraph>
        <heading level="N" readAloud="true">...</heading>
    </front-matter>
    <!-- Main content -->
    <heading level="1|2|3" readAloud="true|false">...</heading>
    <paragraph readAloud="true|false">...</paragraph>
    <list><item>...</item></list>
</book>
```

**スキップ対象**:
- `<toc>` セクション全体
- `<front-matter>` セクション全体
- `<metadata>` セクション
- `readAloud="false"` の要素

## 次フェーズへの引き継ぎ

Phase 2 (User Story 1 - 新XMLフォーマットの基本パース) で実装するもの:
- `parse_book2_xml()`: book2.xml パース、ContentItem リスト返却
- `ContentItem`, `HeadingInfo`: データクラス定義
- `CHAPTER_MARKER`, `SECTION_MARKER`: マーカー定数
- `_should_read_aloud()`: readAloud 属性チェック

**既存コード流用**:
- `_should_read_aloud()` のロジック（xml_parser.py から）

**注意点**:
- heading 要素は level 属性で chapter/section を判定
- toc, front-matter, metadata はスキップ
- list > item の構造を正しく処理
