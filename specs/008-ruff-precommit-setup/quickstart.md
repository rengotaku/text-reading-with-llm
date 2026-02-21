# Quickstart: ruff + pre-commit セットアップ

## 開発環境セットアップ（3ステップ）

```bash
# 1. 開発用依存関係をインストール
pip install -r requirements-dev.txt

# 2. pre-commitフックをインストール
pre-commit install

# 3. 既存ファイルに対して初回チェック実行（任意）
pre-commit run --all-files
```

## 日常の開発フロー

通常通り `git commit` するだけ。pre-commitが自動的にruff check/formatを実行。

```bash
git add src/my_file.py
git commit -m "feat: add new feature"
# → ruff check + ruff format が自動実行
```

## 手動実行

```bash
ruff check .              # リントチェック
ruff check --fix .        # 自動修正付きチェック
ruff format .             # フォーマット適用
ruff format --check .     # フォーマット差分確認
```

## Makefileターゲット

```bash
make setup-dev            # 開発用依存関係インストール + pre-commit install
make lint                 # ruff check + ruff format --check
make format               # ruff format（自動修正）
```
