# Phase 3 RED Test: CI & ローカル統合 (統合前)

**Date**: 2026-02-28
**Status**: RED (mypy が CI と Makefile に統合されていない)
**User Story**: US2 + US3 - CI での型チェック & ローカルでの型チェック実行

## Current State (Before Implementation)

### Makefile lint ターゲット

**Current command**:
```makefile
lint: ## Run ruff linter and format check
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .
```

**Execution result**:
```bash
$ make lint
.venv/bin/ruff check .
All checks passed!
.venv/bin/ruff format --check .
31 files already formatted
```

**Issue**: mypy コマンドが含まれていない

### CI Workflow (.github/workflows/ci.yml)

**Current steps**:
```yaml
- name: Install dependencies
  run: pip install -e ".[dev]"

- name: Run ruff check
  run: ruff check .

- name: Run ruff format check
  run: ruff format --check .

- name: Run pytest
  run: PYTHONPATH=. pytest tests/ --forked --tb=short -q
  timeout-minutes: 10
```

**Issue**: mypy ステップが存在しない（ruff format check と pytest の間に追加すべき）

## Expected Changes (GREEN Goal)

### Makefile

Add mypy to lint target:
```makefile
lint: ## Run ruff linter, format check, and mypy
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .
	$(VENV)/bin/mypy src/
```

### CI Workflow

Add mypy step between ruff format check and pytest:
```yaml
- name: Run ruff format check
  run: ruff format --check .

- name: Run mypy
  run: mypy src/

- name: Run pytest
  run: PYTHONPATH=. pytest tests/ --forked --tb=short -q
  timeout-minutes: 10
```

## Validation Criteria (GREEN State)

1. **Makefile**: `make lint` が ruff check + ruff format + mypy src/ を実行する
2. **CI Workflow**: YAML 構文が正しく、mypy ステップが追加されている
3. **Execution**: `make lint` がエラー 0 で完了する（mypy が Phase 2 で設定済みのため）

## Notes

- mypy は Phase 2 で pyproject.toml に設定済み
- `mypy src/` コマンドはエラー 0 で実行可能（Phase 2 検証済み）
- この Phase では統合のみを実施（設定変更なし）
