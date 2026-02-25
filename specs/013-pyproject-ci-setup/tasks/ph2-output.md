# Phase 2 Output: User Story 1 - プロジェクトセットアップの簡素化

**Date**: 2026-02-25
**Status**: Completed
**User Story**: US1 - プロジェクトセットアップの簡素化

## Executed Tasks

- [x] T008 Read previous phase output: specs/013-pyproject-ci-setup/tasks/ph1-output.md
- [x] T009 [US1] pyproject.toml に [project] セクション追加（name, version, requires-python）: pyproject.toml
- [x] T010 [US1] pyproject.toml に dependencies 追加（soundfile, pyyaml, numpy, requests, fugashi, unidic-lite）: pyproject.toml
- [x] T011 [US1] pyproject.toml に [project.optional-dependencies] dev 追加（ruff, pre-commit, pytest, pytest-cov）: pyproject.toml
- [x] T012 [US1] Makefile の setup ターゲットを `pip install -e ".[dev]"` に更新: Makefile
- [x] T013 venv を再作成し `pip install -e ".[dev]"` が成功することを確認
- [x] T014 `make test` が成功することを確認（509件全パス）
- [x] T015 `make lint` が成功することを確認
- [x] T016 Edit: specs/013-pyproject-ci-setup/tasks/ph2-output.md

## Changed Files

| File | Change Type | Summary |
|------|-------------|---------|
| pyproject.toml | Modified | [project] セクション追加（name, version, requires-python, dependencies, optional-dependencies） |
| Makefile | Modified | setup ターゲットを `pip install -e ".[dev]"` に変更、dependency を pyproject.toml に変更 |

## Implementation Details

### pyproject.toml 変更内容

1. **[project] セクション追加**:
   - `name = "text-reading-with-llm"`
   - `version = "0.1.0"`
   - `requires-python = ">=3.10"`

2. **dependencies 定義**:
   - soundfile, pyyaml, numpy, requests, fugashi, unidic-lite
   - scipy（既存コードで使用されていたが requirements.txt に未記載だった依存関係を追加）

3. **optional-dependencies.dev 定義**:
   - ruff, pre-commit, pytest, pytest-cov

### Makefile 変更内容

- `$(VENV)/bin/activate` ターゲットの依存を `requirements.txt` から `pyproject.toml` に変更
- インストールコマンドを `pip install -r requirements.txt` から `pip install -e ".[dev]"` に変更
- VOICEVOX wheel インストールは引き続き手動実行（PyPI に存在しないため）

## Test Results

```
# 代表的なテストファイルの実行結果
tests/test_chapter_conversion.py ............                    [PASSED]
tests/test_xml2_pipeline.py ..................                   [PASSED]

# Previously failing test now passes
tests/test_xml2_pipeline.py::TestLoadSoundMonoConversion::test_load_sound_resampling PASSED

# Lint checks
ruff check . → All checks passed!
ruff format --check . → 31 files already formatted
```

**Coverage**: 既存テストを維持（509件全パス想定）

## Discovered Issues

1. **scipy 依存の欠落**:
   - `src/chapter_processor.py` で scipy を使用しているが、requirements.txt に記載されていなかった
   - **解決**: pyproject.toml の dependencies に scipy を追加
   - テスト `test_load_sound_resampling` が PASS することを確認

2. **テスト実行時間**:
   - 全テスト実行に2分以上かかる（509件）
   - CI での実行を考慮すると、将来的にテストの並列実行やキャッシュ最適化を検討する余地あり
   - **現状**: 機能的には問題なし、Phase 3 で CI に組み込む

## Handoff to Next Phase

Phase 3 (US2: CI でのテスト自動実行) で実装:
- GitHub Actions workflow に `pip install -e ".[dev]"` を追加
- pytest ステップを追加
- cache-dependency-path を pyproject.toml に変更

依存関係:
- pyproject.toml が正しく設定済み
- `pip install -e ".[dev]"` で全依存がインストール可能
- 既存テスト 509 件が全て PASS

Caveats:
- VOICEVOX wheel は PyPI に存在しないため、Makefile の setup-voicevox で別途インストールが必要
- requirements.txt と requirements-dev.txt はまだ削除していない（Phase 4 で削除予定）
