# Phase 1 Output: Setup

**Date**: 2026-03-02
**Status**: Completed

## Executed Tasks

- [x] T001 現在のカバレッジ状態を確認: `pytest --cov=src --cov-report=term-missing`
- [x] T002 [P] pyproject.toml の現在の pytest 設定を確認
- [x] T003 [P] .github/workflows/ci.yml の現在の設定を確認
- [x] T004 [P] README.md の現在の状態を確認
- [x] T005 作成: ph1-output.md（このファイル）

## Existing Code Analysis

### pyproject.toml

**Current State**:
- `[tool.pytest.ini_options]` セクション: **なし**
- pytest-cov: dev 依存に含まれる ✅
- ruff, mypy 設定: あり

**Required Updates**:
1. `[tool.pytest.ini_options]` セクションを追加
2. `testpaths = ["tests"]` を設定
3. `addopts` にカバレッジオプションを追加

### .github/workflows/ci.yml

**Current State**:
- Python version: 3.10
- Cache: `pip` + `cache-dependency-path: pyproject.toml` ✅（最適化済み）
- pytest: `PYTHONPATH=. pytest tests/ --forked --tb=short -q`
- permissions セクション: **なし**
- カバレッジレポート生成: **なし**
- PR コメントアクション: **なし**

**Required Updates**:
1. `permissions` セクションを追加（`contents: write`, `pull-requests: write`）
2. pytest ステップにカバレッジオプション追加（pyproject.toml から継承）
3. `py-cov-action/python-coverage-comment-action` ステップを追加

### README.md

**Current State**:
- プロジェクト説明: あり
- セットアップガイド: あり
- カバレッジバッジ: **なし**

**Required Updates**:
1. カバレッジバッジマークダウンを先頭に追加

## Coverage Analysis

**Current Coverage**: 72% (509 tests passed)

| Module | Coverage | Status |
|--------|----------|--------|
| src/chapter_processor.py | 89% | ✅ |
| src/xml2_parser.py | 96% | ✅ |
| src/text_cleaner_cli.py | 92% | ✅ |
| src/reading_dict.py | 100% | ✅ |
| src/xml2_pipeline.py | 85% | ✅ |
| src/text_cleaner.py | 76% | ⚠️ |
| src/mecab_reader.py | 75% | ⚠️ |
| src/number_normalizer.py | 68% | ⚠️ |
| src/generate_reading_dict.py | 66% | ⚠️ |
| src/punctuation_normalizer.py | 64% | ⚠️ |
| src/voicevox_client.py | 61% | ⚠️ |
| src/llm_reading_generator.py | 55% | ⚠️ |
| src/dict_manager.py | 47% | ❌ |
| src/process_manager.py | 22% | ❌ |

**Note**: 閾値 80% を設定すると現在のテストは失敗する。初期は閾値を 70% に設定し、段階的に引き上げることを推奨。

## Technical Decisions

1. **PYTHONPATH=. の継続使用**: CI で既に使用中、pytest 設定でも `pythonpath = ["."]` を追加して一貫性を保つ
2. **閾値 70% からスタート**: 現在のカバレッジ 72% に対してマージンを持たせ、失敗を回避
3. **キャッシュ設定変更なし**: research.md より既に最適化済み
4. **py-cov-action を採用**: 外部サービス不要、シンプルな設定

## Handoff to Next Phase

### Phase 2 (User Story 1 - テスト設定の標準化):

実装項目:
- `pyproject.toml` に `[tool.pytest.ini_options]` セクション追加
- `addopts` にカバレッジオプション追加
- `--cov-fail-under=70`（初期値）

注意事項:
- PYTHONPATH 設定を `pythonpath = ["."]` で追加
- XML レポート出力を含める（CI でコメントアクションが使用）
