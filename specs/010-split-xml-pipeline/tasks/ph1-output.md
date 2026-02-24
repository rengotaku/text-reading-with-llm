# Phase 1 Output: Setup

**Date**: 2026-02-23
**Status**: 完了

## 実行タスク

- [x] T001 現在の実装を読む: src/xml2_pipeline.py の main() 関数（L88-224）
- [x] T002 現在の実装を読む: src/text_cleaner.py の clean_page_text() 関数
- [x] T003 現在の実装を読む: src/dict_manager.py の get_content_hash() 関数
- [x] T004 既存テストを読む: tests/test_xml2_pipeline.py
- [x] T005 既存 Makefile を読む: Makefile の gen-dict, xml-tts ターゲット
- [x] T006 編集・リネーム: ph1-output-template.md → ph1-output.md

## 既存コード分析

### src/xml2_pipeline.py

**構造**:
- `parse_args()`: CLI 引数パース（--input, --output, --style-id, --speed 等）
- `main()`: メインエントリポイント（L88-224）
  - XML パース (L115-118)
  - ハッシュ計算・出力ディレクトリ作成 (L127-131)
  - **テキストクリーニング・cleaned_text.txt 保存** (L133-175) ← 抽出対象
  - TTS 生成 (L177-224)

**更新が必要な箇所（Phase 3）**:
1. `parse_args()`: `--cleaned-text` オプション追加
2. `main()`: `--cleaned-text` 指定時はテキストクリーニングをスキップして既存ファイルを使用

**抽出可能なロジック（Phase 2）**:
```python
# L133-175 のテキストクリーニング部分
# 1. combined_text からハッシュ計算
# 2. output_dir 作成
# 3. content_items をループして clean_page_text() 適用
# 4. cleaned_text.txt に保存
```

### src/text_cleaner.py

**構造**:
- `init_for_content()`: コンテンツ用の辞書初期化
- `clean_page_text()`: テキストクリーニング（L283-367）
  - URL/ISBN 削除
  - 括弧英語削除
  - 数字正規化
  - MeCab かな変換

**再利用**: `text_cleaner_cli.py` でそのまま使用可能

### src/dict_manager.py

**構造**:
- `get_content_hash()`: SHA256 ハッシュ → 先頭12文字（L16-27）

**再利用**: `text_cleaner_cli.py` でそのまま使用可能

### Makefile

**既存ターゲット**:
- `gen-dict`: `PYTHONPATH=$(CURDIR) $(PYTHON) src/generate_reading_dict.py "$(INPUT)" --model "$(LLM_MODEL)" --merge`
- `xml-tts`: `PYTHONPATH=$(CURDIR) $(PYTHON) -m src.xml2_pipeline -i "$(INPUT)" -o "$(OUTPUT)" --style-id $(STYLE_ID) --speed $(SPEED)`

**追加が必要**:
1. `clean-text`: 新規ターゲット（Phase 2）
2. `run`: 一括実行ターゲット（Phase 4）

## 既存テスト分析

- `tests/test_xml2_pipeline.py`: parse_args, load_sound, process_content, main のテスト
  - `TestParseArgsDefaults`: CLI 引数デフォルト値
  - `TestParseArgsCustomSounds`: カスタムサウンド設定
  - `TestLoadSoundMonoConversion`: 音声ロード処理
  - `TestProcessContentWithMarkers`: コンテンツ処理
  - `TestMainFunction`: main 関数の基本動作
  - `TestCleanedTextFile*`: cleaned_text.txt 生成

**存在しない**: `tests/test_text_cleaner_cli.py` → 新規作成（Phase 2）

**追加が必要なフィクスチャ**:
- 既存の `tests/fixtures/sample_book2.xml` を再利用可能

## 新規作成ファイル

### src/text_cleaner_cli.py (スケルトン)

- `parse_args()`: CLI 引数パース（--input, --output）（Phase 2 で実装）
- `main()`: XML → cleaned_text.txt 生成（Phase 2 で実装）

**再利用するインポート**:
```python
from src.dict_manager import get_content_hash
from src.text_cleaner import clean_page_text, init_for_content
from src.xml2_parser import CHAPTER_MARKER, SECTION_MARKER, parse_book2_xml
```

### tests/test_text_cleaner_cli.py (スケルトン)

- `TestParseArgs`: CLI 引数パーステスト（Phase 2 で実装）
- `TestMain`: main 関数テスト（Phase 2 で実装）
- `TestErrorHandling`: エラーハンドリングテスト（Phase 2 で実装）

## 技術的決定事項

1. **新規ファイル分離**: `text_cleaner_cli.py` を新規作成し、`xml2_pipeline.py` のテキストクリーニング部分を抽出
2. **ハッシュ計算共有**: `dict_manager.get_content_hash` を両方から呼び出し、同一出力ディレクトリを参照
3. **Makefile パターン踏襲**: 既存の `PYTHONPATH=$(CURDIR) $(PYTHON) -m` パターンを使用

## 次フェーズへの引き継ぎ

Phase 2 (テキストクリーニング単独実行) で実装するもの:
- `src/text_cleaner_cli.py`: XML → cleaned_text.txt 生成 CLI
- `tests/test_text_cleaner_cli.py`: CLI テスト
- `Makefile`: `clean-text` ターゲット

既存コード流用:
- `xml2_pipeline.py main()` の L133-175 のロジックをそのまま抽出
- `CHAPTER_MARKER`, `SECTION_MARKER` の処理ロジック
- `clean_page_text()` の呼び出しパターン

注意点:
- 出力ディレクトリはハッシュベースで生成（`get_content_hash` 使用）
- `init_for_content()` を呼び出して辞書を初期化する必要がある
- 見出しの末尾句点処理（`.rstrip()` + `。` 追加）を忘れずに
