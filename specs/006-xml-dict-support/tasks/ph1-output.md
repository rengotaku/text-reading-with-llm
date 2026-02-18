# Phase 1 Output: Setup

**Date**: 2026-02-18
**Status**: 完了

## 実行タスク

- [x] T001 既存の辞書生成コードを確認: `src/generate_reading_dict.py`
- [x] T002 既存のXMLパーサーを確認: `src/xml2_parser.py`
- [x] T003 既存の辞書管理モジュールを確認: `src/dict_manager.py`
- [x] T004 既存の用語抽出関数を確認: `src/llm_reading_generator.py`
- [x] T005 既存のテストを確認: `tests/test_xml2_parser.py`
- [x] T006 テスト用XMLフィクスチャを作成: `tests/fixtures/dict_test_book.xml`
- [x] T007 `make test` で既存テストがすべてパスすることを確認
- [x] T008 セットアップ出力を編集・リネーム

## 既存コード分析

### src/generate_reading_dict.py

**構造**:
- `ollama_chat()`: Ollama API呼び出し
- `generate_readings_batch()`: 用語をバッチでLLMに送信して読みを生成
- `main()`: エントリポイント（argparse → 入力読み込み → 用語抽出 → 読み生成 → 辞書保存）

**更新が必要な箇所**:
1. `main()` L114-178: 現在MDのみ対応。`input_path.suffix` で `.xml`/`.md` 分岐を追加
2. XML分岐: `parse_book2_xml()` → `chapter_number` グループ化 → `extract_technical_terms()` per group
3. 未対応拡張子: `logger.error()` + `sys.exit(1)`

**現在のフロー** (MD only):
```
read_text() → split_into_pages() → extract_technical_terms() per page → generate_readings_batch() → save_dict()
```

**追加するフロー** (XML):
```
parse_book2_xml() → groupby(chapter_number) → extract_technical_terms() per group → generate_readings_batch() → save_dict()
```

### src/xml2_parser.py

**構造**:
- `HeadingInfo`: データクラス（level, number, title, read_aloud）
- `ContentItem`: データクラス（item_type, text, heading_info, chapter_number）
- `parse_book2_xml()`: XMLパース → `list[ContentItem]`（chapter_number付き）
- `format_heading_text()`: 見出しテキストフォーマット
- `_should_read_aloud()`: readAloud属性チェック

**変更不要**: そのまま利用可能

### src/dict_manager.py

**構造**:
- `get_content_hash()`: SHA256ハッシュ計算
- `get_dict_path()`: `data/{hash}/readings.json` パス生成
- `load_dict()` / `save_dict()`: 辞書読み書き

**変更不要**: `save_dict(readings, input_path)` はXMLファイルでもそのまま動作

### src/llm_reading_generator.py

**構造**:
- `extract_technical_terms()`: 正規表現で英字ベース技術用語を抽出
- `generate_readings_with_llm()`: LLMで読みを生成
- `load_dictionary()` / `save_dictionary()`: レガシー辞書I/O

**変更不要**: `extract_technical_terms(text: str)` はプレーンテキスト入力で動作

## 既存テスト分析

- `tests/test_xml2_parser.py`: XMLパーサーのテスト（61テスト、ContentItem, chapter_number含む）
- **存在しない**: `tests/test_generate_reading_dict.py` → 新規作成（Phase 2）

**追加したフィクスチャ**:
- `tests/fixtures/dict_test_book.xml`: 2チャプター、各チャプターに技術用語を含むパラグラフ

## 技術的決定事項

1. **変更対象は `main()` のみ**: `xml2_parser`, `dict_manager`, `llm_reading_generator` は変更不要
2. **`itertools.groupby` でチャプターグループ化**: ContentItemの`chapter_number`をキーにグループ化
3. **拡張子ベース判別**: `input_path.suffix` で `.xml`/`.md` 分岐（research.md R-003準拠）

## 次フェーズへの引き継ぎ

Phase 2 (US1: XMLファイルから読み辞書を生成) で実装するもの:
- `main()` にXML分岐ロジックを追加
- 既存コード流用: `parse_book2_xml()`, `extract_technical_terms()`, `save_dict()`, `load_dict()`, `generate_readings_batch()`
- 注意点: `split_into_pages` はMDフロー固有。XMLフローでは `parse_book2_xml()` + グループ化で代替
- インポート追加: `from xml2_parser import parse_book2_xml` と `from itertools import groupby`
