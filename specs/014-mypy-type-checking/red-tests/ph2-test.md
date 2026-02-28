# Phase 2 RED Test Output: US1 型チェック設定の構成

**Date**: 2026-02-28
**Status**: RED (設定前の状態)

## 目的

pyproject.toml に mypy 設定を追加する前の状態を記録する。

## 現在の状態

### mypy インストール状況

```bash
$ mypy --version
command not found: mypy
```

```bash
$ python -m pip list | grep mypy
(出力なし)
```

**結果**: mypy は未インストール

### pyproject.toml の dev 依存

```toml
[project.optional-dependencies]
dev = [
    "ruff",
    "pre-commit",
    "pytest",
    "pytest-cov",
    "pytest-timeout",
    "pytest-forked",
]
```

**結果**: "mypy" は含まれていない

### [tool.mypy] セクション

**結果**: pyproject.toml に `[tool.mypy]` セクションは存在しない

## 期待される GREEN 状態

1. pyproject.toml の `[project.optional-dependencies].dev` に "mypy" が追加される
2. pyproject.toml に `[tool.mypy]` セクションが追加される
3. `pip install -e ".[dev]"` 実行後、mypy がインストールされる
4. `mypy src/` コマンドが実行可能になる
5. `mypy src/` がエラー 0 で完了する

## Implementation Hints

### 1. dev 依存に mypy 追加

```toml
[project.optional-dependencies]
dev = [
    "ruff",
    "pre-commit",
    "pytest",
    "pytest-cov",
    "pytest-timeout",
    "pytest-forked",
    "mypy",  # ← 追加
]
```

### 2. [tool.mypy] セクション追加

pyproject.toml の末尾に以下を追加:

```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = false
ignore_missing_imports = true
files = ["src"]
```

設定の意味:
- `python_version = "3.10"`: Python 3.10 構文を使用
- `warn_return_any = true`: Any 型を返す関数に警告
- `warn_unused_ignores = true`: 不要な `# type: ignore` に警告
- `disallow_untyped_defs = false`: 型ヒントなし関数を許可（段階的導入）
- `ignore_missing_imports = true`: 型スタブのないライブラリを無視
- `files = ["src"]`: src/ ディレクトリのみ型チェック

### 3. インストールとテスト

```bash
# venv 有効化
source .venv/bin/activate

# mypy を含む dev 依存をインストール
pip install -e ".[dev]"

# mypy バージョン確認
mypy --version

# src/ を型チェック
mypy src/
```

期待される出力:
```
Success: no issues found in 14 source files
```

## 検証項目

- [ ] mypy がインストールされている
- [ ] `mypy --version` が実行可能
- [ ] `mypy src/` がエラー 0 で完了
- [ ] `warn_return_any` 設定が有効（Any を返す関数があれば警告が出る）

## Notes

- 既存コードには型ヒントがほとんどないため、`disallow_untyped_defs = false` が重要
- サードパーティライブラリ（fugashi, soundfile 等）の型スタブがないため、`ignore_missing_imports = true` が必要
- src/ 配下の 14 ファイルが型チェック対象
