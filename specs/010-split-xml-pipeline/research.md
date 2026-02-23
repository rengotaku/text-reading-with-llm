# リサーチ: XML パイプライン分割

**ブランチ**: `010-split-xml-pipeline`
**日付**: 2026-02-23

## 調査項目

### 1. 現在の xml2_pipeline.py 構造

**調査結果**:
- `main()` 関数（L88-224）が以下を順次実行:
  1. XML パース (`parse_book2_xml`)
  2. ハッシュ計算・出力ディレクトリ作成 (`get_content_hash`)
  3. テキストクリーニング・cleaned_text.txt 保存 (L133-175)
  4. VOICEVOX 初期化・TTS 生成 (L177-224)

**決定**: テキストクリーニング部分（L133-175 相当）を新規 CLI に抽出

**根拠**: 既存コードの構造が明確に分離されており、抽出が容易

### 2. ハッシュベースディレクトリ生成

**調査結果**:
- `src/dict_manager.py` の `get_content_hash()` が使用されている
- コンテンツ全体のテキストを結合 → MD5 ハッシュ → ディレクトリ名
- 同一コンテンツは同一ディレクトリに出力（冪等性）

**決定**: `text_cleaner_cli.py` も同じハッシュ計算ロジックを使用

**根拠**: `clean-text` と `xml-tts` で同一ディレクトリを参照する必要がある

### 3. Makefile パターン

**調査結果**:
- 既存ターゲット: `gen-dict`, `xml-tts`, `test`, `lint`, `format`
- 変数: `INPUT`, `OUTPUT`, `STYLE_ID`, `SPEED`
- Python 実行: `PYTHONPATH=$(CURDIR) $(PYTHON) -m src.module_name`

**決定**: 既存パターンに従い新ターゲットを追加

**根拠**: 一貫性の維持

### 4. テストパターン

**調査結果**:
- `tests/test_xml2_pipeline.py` に包括的なテストが存在
- フィクスチャ: `FIXTURES_DIR`, `SAMPLE_BOOK2_XML`
- モック: `@patch` で VOICEVOX 初期化をスキップ

**決定**: 同様のパターンで `test_text_cleaner_cli.py` を作成

**根拠**: プロジェクトの既存テストスタイルとの一貫性

### 5. --cleaned-text オプション設計

**調査結果**:
- 現在の `parse_args()` は `--input` が required
- cleaned_text.txt を直接読み込む場合、XML パースは不要
- ただし、チャプター情報は XML から取得している

**決定**: `--cleaned-text` 指定時は以下の動作:
1. XML パースは行うがテキストクリーニングはスキップ
2. 指定された cleaned_text.txt を読み込む
3. チャプター情報は XML から取得

**根拠**: チャプター区切りや見出し情報は XML にのみ存在するため

**代替案却下**:
- cleaned_text.txt にチャプター情報を埋め込む → フォーマット変更が必要で後方互換性に影響

## 技術決定サマリー

| 決定項目 | 選択 | 理由 |
|----------|------|------|
| CLI 抽出方法 | 新規ファイル `text_cleaner_cli.py` | 責務の分離、テスト容易性 |
| ハッシュ計算 | `dict_manager.get_content_hash` 再利用 | DRY 原則、同一ディレクトリ参照 |
| --cleaned-text 動作 | XML パース + クリーニングスキップ | チャプター情報の維持 |
| Makefile パターン | 既存に準拠 | 一貫性 |
