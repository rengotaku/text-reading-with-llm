# Phase 1 Output: Setup

**Date**: 2026-02-28
**Status**: Completed

## Executed Tasks

- [x] T001 現在の pyproject.toml を読み込み、既存設定を確認する
- [x] T002 [P] 現在の Makefile を読み込み、lint ターゲットを確認する
- [x] T003 [P] 現在の CI ワークフローを読み込み、lint ジョブを確認する
- [x] T004 [P] src/ 配下の Python ファイル一覧を取得し、型チェック対象を確認する
- [x] T005 `mypy --version` が実行可能か確認（未インストール）
- [x] T006 Edit: specs/014-mypy-type-checking/tasks/ph1-output.md

## Existing Code Analysis

### pyproject.toml

**Structure**:
- `[project]`: name, version, requires-python (>=3.10), dependencies
- `[project.optional-dependencies]`: dev (ruff, pre-commit, pytest, pytest-cov, pytest-timeout, pytest-forked)
- `[tool.ruff]`: line-length=120, target-version="py310"
- `[tool.ruff.lint]`: select=["E", "F", "I", "W"]
- `[tool.ruff.lint.isort]`: known-first-party=["src"]

**Required Updates**:
1. `[project.optional-dependencies].dev`: 追加 → "mypy"
2. `[tool.mypy]`: 新規セクション追加

### Makefile

**Structure**:
- `lint`: ruff check + ruff format --check のみ

**Required Updates**:
1. `lint` ターゲット: mypy src/ を追加

### .github/workflows/ci.yml

**Structure**:
- Install dependencies: pip install -e ".[dev]"
- Run ruff check
- Run ruff format check
- Run pytest

**Required Updates**:
1. pytest の前に "Run mypy" ステップを追加

### src/ Python Files (14 files)

```
src/chapter_processor.py
src/mecab_reader.py
src/number_normalizer.py
src/process_manager.py
src/punctuation_normalizer.py
src/reading_dict.py
src/xml2_parser.py
src/llm_reading_generator.py
src/text_cleaner.py
src/text_cleaner_cli.py
src/dict_manager.py
src/generate_reading_dict.py
src/voicevox_client.py
src/xml2_pipeline.py
```

## mypy Installation Status

- **mypy**: 未インストール（dev 依存に追加後、pip install -e ".[dev]" で導入）

## Technical Decisions

1. **段階的導入**: `disallow_untyped_defs = false` で既存コードへの影響を最小化
2. **ignore_missing_imports**: サードパーティライブラリ（fugashi, soundfile等）の型スタブ不足に対応
3. **files = ["src"]**: 型チェック対象を src/ に限定（tests/ は除外）

## Handoff to Next Phase

Items to implement in Phase 2 (US1: 型チェック設定の構成):
- pyproject.toml に `[tool.mypy]` セクション追加
- dev 依存に "mypy" 追加
- `pip install -e ".[dev]"` で mypy インストール
- `mypy src/` 実行でエラー 0 確認
