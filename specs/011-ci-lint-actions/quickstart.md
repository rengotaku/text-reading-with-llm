# Quickstart: CI Lint Actions

## 概要

GitHub Actions で ruff lint チェックを自動実行する CI を追加します。

## 作成するファイル

```
.github/workflows/lint.yml
```

## ワークフロー構成

```yaml
name: Lint

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
          cache: 'pip'
          cache-dependency-path: requirements-dev.txt

      - name: Install dependencies
        run: pip install -r requirements-dev.txt

      - name: Run lint
        run: make lint
```

## 検証手順

1. **ローカルテスト**
   ```bash
   make lint  # 現在の状態を確認
   ```

2. **PR 作成**
   - フィーチャーブランチから PR を作成
   - Actions タブで lint ジョブを確認
   - 成功/失敗ステータスが PR に表示されることを確認

3. **意図的な失敗テスト**
   - lint エラーのあるコードを push
   - CI が失敗することを確認

## 成功基準の検証

| 基準 | 検証方法 |
|------|----------|
| SC-001: 5分以内完了 | Actions の実行時間を確認 |
| SC-002: エラー時に失敗 | lint エラーのあるコードで PR 作成 |
| SC-003: ローカル一致 | `make lint` の出力と Actions ログを比較 |
