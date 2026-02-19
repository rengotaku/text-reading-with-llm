# Quickstart: 不要機能の削除リファクタリング

## 前提条件

- Git ブランチ `007-cleanup-unused-code` にチェックアウト済み
- `.venv` が有効化されている
- 既存テストが全てパスする状態

## 実行手順

### 1. 現状確認

```bash
# ブランチ確認
git branch --show-current  # → 007-cleanup-unused-code

# 既存テスト実行（ベースライン）
make test
```

### 2. ソースファイル削除（Phase 1）

```bash
# 不要ソースファイル削除
git rm src/pipeline.py src/progress.py src/toc_extractor.py \
       src/organize_chapters.py src/xml_pipeline.py src/xml_parser.py \
       src/aquestalk_pipeline.py src/aquestalk_client.py \
       src/tts_generator.py src/test_tts_normalize.py

# キャッシュ削除
rm -rf src/__pycache__/

# テスト確認
make test
```

### 3. テストファイル削除（Phase 2）

```bash
# 不要テストファイル削除
git rm tests/test_xml_pipeline.py tests/test_xml_parser.py \
       tests/test_aquestalk_client.py tests/test_aquestalk_pipeline.py

# テストキャッシュ削除
rm -rf tests/__pycache__/

# テスト確認
make test
```

### 4. Makefile 整理（Phase 3）

- `run`, `run-simple`, `toc`, `organize` ターゲット削除
- `xml-tts` から PARSER 分岐を削除し xml2 直接実行に変更
- `.PHONY` 更新

```bash
# 最終テスト
make test
make help
```

## 検証

削除後に保持されるべき機能:
- `make xml-tts` — xml2 パイプラインで TTS 生成
- `make gen-dict` — 辞書生成
- `make test` — 全テストパス
- `make setup` — 環境セットアップ
