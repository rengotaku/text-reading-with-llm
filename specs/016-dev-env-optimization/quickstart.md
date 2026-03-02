# Quickstart: 開発環境の最適化

**Feature**: 016-dev-env-optimization
**Date**: 2026-03-02

## 概要

このガイドでは、pytest カバレッジ設定、CI 最適化、PR カバレッジコメント、カバレッジバッジの設定方法を説明します。

## 前提条件

- Python 3.10+
- pytest, pytest-cov インストール済み（`pip install -e ".[dev]"`）
- GitHub リポジトリ

## 設定手順

### 1. pytest カバレッジ設定

`pyproject.toml` に以下を追加:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=xml:coverage.xml",
    "--cov-fail-under=80",
]
```

### 2. ローカルでの動作確認

```bash
# テスト実行（カバレッジ付き）
pytest

# 出力例:
# ---------- coverage: ... ----------
# Name                 Stmts   Miss  Cover   Missing
# --------------------------------------------------
# src/module.py           50      5    90%   10-14
# --------------------------------------------------
# TOTAL                  100     10    90%
```

### 3. CI ワークフロー更新

`.github/workflows/ci.yml` に以下を追加:

```yaml
permissions:
  contents: write
  pull-requests: write

# ... existing steps ...

- name: Run pytest with coverage
  run: pytest

- name: Coverage comment
  uses: py-cov-action/python-coverage-comment-action@v3
  with:
    GITHUB_TOKEN: ${{ github.token }}
    MINIMUM_GREEN: 80
    MINIMUM_ORANGE: 60
```

### 4. カバレッジバッジ（README）

README.md の先頭に追加:

```markdown
![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/{user}/{gist_id}/raw/coverage.json)
```

## 検証チェックリスト

- [ ] `pytest` でカバレッジレポートが表示される
- [ ] カバレッジ 80% 未満でテストが失敗する
- [ ] CI で coverage.xml が生成される
- [ ] PR にカバレッジコメントが追加される
- [ ] README にバッジが表示される

## トラブルシューティング

### カバレッジが 80% 未満で失敗する

一時的に閾値を下げる:
```toml
addopts = ["--cov-fail-under=60"]  # 徐々に上げる
```

### PR コメントが追加されない

- `permissions` セクションを確認
- `GITHUB_TOKEN` のスコープを確認
- `continue-on-error: true` を追加して CI は成功させる

### キャッシュが効かない

- `cache-dependency-path` が pyproject.toml を指していることを確認
- Actions のキャッシュクリア（Settings > Actions > Caches）
