# Quickstart: pyproject.toml 整備 + CI テスト追加

## 概要

このフィーチャー完了後の開発環境セットアップ手順。

## セットアップ手順

### 1. リポジトリクローン

```bash
git clone https://github.com/rengotaku/text-reading-with-llm.git
cd text-reading-with-llm
```

### 2. 仮想環境作成

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 依存関係インストール

```bash
# 本番 + 開発依存を一括インストール
pip install -e ".[dev]"

# VOICEVOX Core（別途必要）
make setup-voicevox
```

### 4. 動作確認

```bash
# テスト実行
make test

# lint 実行
make lint
```

## 変更点サマリー

| 変更前 | 変更後 |
|--------|--------|
| `pip install -r requirements.txt` | `pip install -e ".[dev]"` |
| `pip install -r requirements-dev.txt` | 上記に統合 |
| requirements.txt | 削除 |
| requirements-dev.txt | 削除 |

## CI/CD

PR 作成時に自動実行:
1. ruff check（lint）
2. ruff format --check（format 確認）
3. pytest tests/（テスト）

## トラブルシューティング

### pip install 失敗

```bash
# pip を最新に更新
pip install --upgrade pip

# 再試行
pip install -e ".[dev]"
```

### VOICEVOX 関連エラー

```bash
# VVM ファイル再ダウンロード
make reset-vvm
```
