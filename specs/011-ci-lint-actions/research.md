# Research: CI Lint Actions

**Date**: 2026-02-24
**Feature**: 011-ci-lint-actions

## Research Tasks

### 1. GitHub Actions Python Workflow Best Practices

**Decision**: `actions/setup-python` + `actions/cache` を使用

**Rationale**:
- `actions/setup-python@v5` が現在の推奨バージョン
- pip キャッシュは `actions/cache` または `setup-python` の built-in cache で可能
- `setup-python` の `cache: 'pip'` オプションが最もシンプル

**Alternatives Considered**:
- `actions/cache` 単独: より細かい制御が可能だが、設定が複雑
- キャッシュなし: 実行時間が長くなる（requirements-dev.txt は小さいが、毎回のインストールは非効率）

### 2. Ruff Integration in CI

**Decision**: `make lint` コマンドをそのまま使用

**Rationale**:
- ローカルと CI の結果一致が要件 (SC-003)
- Makefile に既に定義済み (`ruff check . && ruff format --check .`)
- 追加の設定なしで pyproject.toml の設定を使用

**Alternatives Considered**:
- `ruff` 直接実行: Makefile との二重管理になる
- `pre-commit run --all-files`: 追加依存が必要、オーバーヘッドあり
- GitHub Actions Marketplace の ruff action: `make lint` との結果一致を保証しにくい

### 3. Workflow Trigger Configuration

**Decision**: `pull_request` + `push` (main ブランチ)

**Rationale**:
- PR 作成・更新時: `pull_request` イベント
- main への直接 push: `push` イベント (branches: [main])
- PR 更新時も自動的にトリガーされる (GitHub の標準動作)

**Alternatives Considered**:
- `pull_request` のみ: main への直接 push をカバーできない
- `push` のみ: すべてのブランチで実行されてしまう

### 4. Dependency Installation Strategy

**Decision**: `requirements-dev.txt` のみインストール

**Rationale**:
- lint には `ruff` のみ必要
- `requirements.txt` には VOICEVOX など重い依存がある
- 最小限のインストールで実行時間短縮

**Implementation**:
```yaml
- run: pip install -r requirements-dev.txt
```

### 5. Python Version Selection

**Decision**: Python 3.10 固定

**Rationale**:
- pyproject.toml の `target-version = "py310"` と一致
- ローカル環境との一貫性

## Resolved Clarifications

なし。すべての技術的決定が明確。

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| actions/checkout | v4 | リポジトリチェックアウト |
| actions/setup-python | v5 | Python 環境セットアップ + キャッシュ |
| ruff | (latest via pip) | lint 実行 |
