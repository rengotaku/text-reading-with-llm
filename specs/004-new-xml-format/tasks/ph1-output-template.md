# Phase 1 Output: Setup

**Date**: YYYY-MM-DD
**Status**: 完了 | エラー

## 実行タスク

- [ ] T001 Read current implementation in src/xml_parser.py, src/xml_pipeline.py
- [ ] T002 Read existing tests in tests/test_xml_parser.py, tests/test_xml_pipeline.py
- [ ] T003 Read sample XML: sample/book2.xml (first 200 lines)
- [ ] T004 Create test fixture: tests/fixtures/sample_book2.xml
- [ ] T005 Verify `make test` passes

## 既存コード分析

### src/xml_parser.py

**構造**:
- `XmlPage`: ページデータクラス
- `Figure`: 図情報データクラス
- `parse_book_xml()`: book.xml パース関数
- `_should_read_aloud()`: readAloud 属性チェック
- `_extract_content_text()`: コンテンツテキスト抽出
- `HEADING_MARKER`: 見出しマーカー定数

**流用可能な箇所**:
1. `_should_read_aloud()`: 同じロジックを xml2_parser.py で再実装
2. `HEADING_MARKER` のアプローチ: CHAPTER_MARKER, SECTION_MARKER で踏襲

### src/xml_pipeline.py

**構造**:
- `parse_args()`: CLI 引数パース
- `load_heading_sound()`: 効果音ロード
- `process_pages_with_heading_sound()`: ページ処理
- `main()`: エントリポイント

**流用可能な箇所**:
1. `load_heading_sound()`: xml2_pipeline.py で再利用

## 既存テスト分析

- `tests/test_xml_parser.py`: book.xml 用テスト（変更不要）
- `tests/test_xml_pipeline.py`: book.xml 用テスト（変更不要）
- **新規作成**: tests/test_xml2_parser.py
- **新規作成**: tests/test_xml2_pipeline.py

**追加が必要なフィクスチャ**:
- `sample_book2.xml`: book2.xml フォーマットのミニマルサンプル

## 新規作成ファイル

### src/xml2_parser.py (スケルトン)

- `HeadingInfo`: 見出し情報データクラス (Phase 2)
- `ContentItem`: コンテンツ単位データクラス (Phase 2)
- `CHAPTER_MARKER`: chapter 効果音マーカー (Phase 2)
- `SECTION_MARKER`: section 効果音マーカー (Phase 2)
- `parse_book2_xml()`: book2.xml パース関数 (Phase 2)
- `format_heading_text()`: 見出し整形関数 (Phase 3)

### src/xml2_pipeline.py (スケルトン)

- `parse_args()`: CLI 引数パース (Phase 4)
- `load_sound()`: 効果音ロード (Phase 4)
- `process_content()`: コンテンツ処理 (Phase 4)
- `main()`: エントリポイント (Phase 4)

## 技術的決定事項

1. **新規ファイル作成**: 既存 xml_parser.py/xml_pipeline.py は変更しない
2. **マーカー設計**: CHAPTER_MARKER (\uE001), SECTION_MARKER (\uE002)
3. **効果音**: assets/sounds/chapter.mp3, assets/sounds/section.mp3

## 次フェーズへの引き継ぎ

Phase 2 (US1 - 基本パース) で実装するもの:
- `parse_book2_xml()`: toc/front-matter スキップ、paragraph/list 抽出
- `HeadingInfo`, `ContentItem` データクラス
- 既存コード流用: `_should_read_aloud()` ロジック
- 注意点: heading 処理は Phase 3 で実装（Phase 2 ではスキップ or 基本テキスト抽出のみ）
