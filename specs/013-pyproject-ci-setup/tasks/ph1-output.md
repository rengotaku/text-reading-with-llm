# Phase 1 Output: Setup

**Date**: 2026-02-25
**Status**: Completed

## Executed Tasks

- [x] T001 現在の pyproject.toml を確認: pyproject.toml
- [x] T002 [P] 現在の requirements.txt を確認: requirements.txt
- [x] T003 [P] 現在の requirements-dev.txt を確認: requirements-dev.txt
- [x] T004 [P] 現在の Makefile を確認: Makefile
- [x] T005 [P] 現在の CI ワークフローを確認: .github/workflows/lint.yml
- [x] T006 [P] 既存テストが全てパスすることを確認: `make test`
- [x] T007 Edit: specs/013-pyproject-ci-setup/tasks/ph1-output.md

## Existing Code Analysis

### pyproject.toml

**現状**:
- `[tool.ruff]` セクションのみ存在
- `[project]` セクションなし → UNKNOWN.egg-info 生成の原因

**Required Updates**:
1. `[project]` セクション追加: name, version, requires-python, dependencies
2. `[project.optional-dependencies]` 追加: dev 依存

### requirements.txt

**現状**:
```
soundfile
pyyaml
numpy
requests
fugashi
unidic-lite
```

**Required Updates**:
1. pyproject.toml に移行後、削除

### requirements-dev.txt

**現状**:
```
ruff
pre-commit
```

**Required Updates**:
1. pytest, pytest-cov を追加（pyproject.toml の optional-dependencies へ）
2. pyproject.toml に移行後、削除

### Makefile

**現状**:
- `setup`: requirements.txt ベース
- `setup-dev`: requirements-dev.txt ベース
- `setup-voicevox`: 外部 wheel インストール（維持）

**Required Updates**:
1. `$(VENV)/bin/activate` ターゲット: `pip install -e ".[dev]"` に変更
2. `setup-dev` ターゲット: 削除または統合

### .github/workflows/lint.yml

**現状**:
- lint のみ（ruff check, ruff format --check）
- pytest なし
- cache-dependency-path: requirements-dev.txt

**Required Updates**:
1. 依存関係インストール: `pip install -e ".[dev]"`
2. pytest ステップ追加
3. cache-dependency-path: pyproject.toml に変更

## Existing Test Analysis

- `tests/test_*.py`: 509 件のテストが存在、全てパス
- テスト構造は変更不要

## Technical Decisions

1. **VOICEVOX wheel は pyproject.toml 対象外**: PyPI にないため、Makefile で別途インストール継続
2. **setup-dev ターゲットは削除**: setup で全依存をインストール、pre-commit install は別途実行

## Handoff to Next Phase

Phase 2 (US1: プロジェクトセットアップの簡素化) で実装:
- pyproject.toml に `[project]` セクション追加
- Makefile の setup ターゲット更新
- 検証: `pip install -e ".[dev]"` → `make test` 成功
