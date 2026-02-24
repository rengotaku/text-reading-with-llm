# Implementation Plan: CI Lint Actions

**Branch**: `011-ci-lint-actions` | **Date**: 2026-02-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-ci-lint-actions/spec.md`

## Summary

GitHub Actions を使用して PR 作成・更新時および main ブランチへの push 時に ruff lint チェックを自動実行する CI ワークフローを追加する。既存の `make lint` コマンドを活用し、pip キャッシュで実行時間を短縮する。

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: ruff (requirements-dev.txt)
**Storage**: N/A (CI 設定のみ)
**Testing**: GitHub Actions による実行検証
**Target Platform**: GitHub Actions (ubuntu-latest)
**Project Type**: single (既存プロジェクトへの CI 追加)
**Performance Goals**: 5分以内に lint チェック完了
**Constraints**: 既存の `make lint` コマンドと結果が一致すること
**Scale/Scope**: 単一リポジトリの lint CI

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution ファイルが存在しないため、以下の基本原則で検証:

| Gate | Status | Notes |
|------|--------|-------|
| 最小限の変更 | ✅ Pass | 新規 YAML ファイル 1 つのみ |
| 既存機能との互換性 | ✅ Pass | 既存の `make lint` を再利用 |
| プロジェクト構造維持 | ✅ Pass | `.github/workflows/` は標準ディレクトリ |

## Project Structure

### Documentation (this feature)

```text
specs/011-ci-lint-actions/
├── spec.md              # 機能仕様
├── plan.md              # この計画ファイル
├── research.md          # Phase 0: GitHub Actions ベストプラクティス
├── quickstart.md        # Phase 1: クイックスタートガイド
└── tasks.md             # Phase 2: タスクリスト (/speckit.tasks で生成)
```

### Source Code (repository root)

```text
.github/
└── workflows/
    └── lint.yml         # 新規作成: lint ワークフロー
```

**Structure Decision**: 標準的な GitHub Actions ディレクトリ構造を使用。`.github/workflows/lint.yml` として単一のワークフローファイルを作成。

## Technical Decisions

### Workflow Configuration

| 項目 | 決定 | 根拠 |
|------|------|------|
| Runner | `ubuntu-latest` | Python プロジェクトの標準的な選択 |
| Python Version | `3.10` | pyproject.toml の target-version と一致 |
| Cache | `actions/cache` + pip | 依存インストール時間短縮 |
| Lint Command | `make lint` | 既存コマンド再利用で結果一致を保証 |

### Trigger Events

```yaml
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
```

## Complexity Tracking

違反なし。単一ファイルの追加のみ。
