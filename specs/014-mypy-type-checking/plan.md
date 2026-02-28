# Implementation Plan: mypy 型チェック導入

**Branch**: `014-mypy-type-checking` | **Date**: 2026-02-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/014-mypy-type-checking/spec.md`

## Summary

Python 静的型チェッカー mypy をプロジェクトに導入する。pyproject.toml に設定を追加し、既存の CI lint ワークフローと Makefile lint ターゲットに統合する。段階的導入アプローチにより、既存コードへの影響を最小化しつつ、新規コードの型安全性を確保する。

## Technical Context

**Language/Version**: Python 3.10
**Primary Dependencies**: mypy (新規追加)
**Storage**: N/A
**Testing**: pytest, pytest-cov, pytest-forked
**Target Platform**: Linux (CI: ubuntu-latest)
**Project Type**: Single project (src/ ベース)
**Performance Goals**: 型チェック実行時間 30 秒以内
**Constraints**: 既存コードに型エラーを出さない（段階的導入）
**Scale/Scope**: src/ 配下のモジュール（現在は中規模）

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| 単一プロジェクト構造維持 | ✅ PASS | 新規ファイル追加なし、設定変更のみ |
| 既存ワークフロー統合 | ✅ PASS | 新規 CI ジョブ不要、既存 lint に統合 |
| 最小限の変更 | ✅ PASS | pyproject.toml, ci.yml, Makefile のみ |

## Project Structure

### Documentation (this feature)

```text
specs/014-mypy-type-checking/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── quickstart.md        # Phase 1 output (開発者向けガイド)
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
src/                     # 型チェック対象
├── *.py                 # Python モジュール
└── ...

tests/                   # テストコード（型チェック対象外可）
└── ...

pyproject.toml           # [tool.mypy] 設定追加
Makefile                 # lint ターゲット更新
.github/workflows/
└── ci.yml               # mypy ステップ追加
```

**Structure Decision**: 単一プロジェクト構造を維持。設定ファイルの変更のみで実装完了。

## Phase 0: Research

### 調査項目

1. **mypy 設定ベストプラクティス**: 段階的導入に適した設定オプション
2. **サードパーティライブラリ型スタブ**: 現在の依存関係に対する型スタブ状況
3. **CI 統合パターン**: GitHub Actions での mypy 実行方法

### 調査結果

→ `research.md` に詳細を記載

## Phase 1: Design

### 変更対象ファイル

| ファイル | 変更内容 |
|---------|---------|
| `pyproject.toml` | `[tool.mypy]` セクション追加、dev 依存に mypy 追加 |
| `.github/workflows/ci.yml` | mypy チェックステップ追加（ruff の後） |
| `Makefile` | lint ターゲットに mypy コマンド追加 |

### mypy 設定案

```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = false
ignore_missing_imports = true
files = ["src"]
```

### CI ステップ追加案

```yaml
- name: Run mypy
  run: mypy src/
```

### Makefile lint ターゲット更新案

```makefile
lint: ## Run ruff linter, format check, and mypy
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .
	$(VENV)/bin/mypy src/
```

## Phase 2: Tasks

→ `/speckit.tasks` コマンドで生成

## Complexity Tracking

> 違反なし - Constitution Check すべて PASS
