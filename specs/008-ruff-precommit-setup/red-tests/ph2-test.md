# Phase 2 RED Tests: US1+US2 - ruff設定・pre-commit設定検証

**Date**: 2026-02-21
**Status**: PASS (設定ファイルがPhase 1で作成済みのため)
**User Story**: US1 - コード品質の自動チェック / US2 - ruffによるコード品質設定

## サマリー

| 項目 | 値 |
|------|-----|
| 作成テスト数 | 13 |
| PASS数 | 13 |
| FAIL数 | 0 (新規テスト) |
| 既存テストFAIL数 | 69 (test_xml2_pipeline.py - Phase 2 GREEN で修正予定) |
| テストファイル | tests/test_ruff_config.py |

## 特記事項: 設定検証テストのRED状態について

Phase 2のテスト対象は**設定ファイルの内容検証**（pyproject.toml, .pre-commit-config.yaml, Makefile）である。
これらの設定ファイルはPhase 1 (Setup) で既に正しい内容で作成済みのため、新規テストは全てPASSする。

これは設定検証テストの性質上、想定される動作である。
Phase 2のGREEN実装の主目的は、ruff違反の修正（`ruff check --fix .` / `ruff format .`）と
pre-commitフックの登録であり、`make test` での既存69件FAILの解消が含まれる。

## テスト一覧

| テストファイル | テストクラス | テストメソッド | 検証内容 |
|--------------|------------|--------------|----------|
| tests/test_ruff_config.py | TestPyprojectTomlRuffSettings | test_ruff_line_length_is_120 | line-length=120 の設定確認 |
| tests/test_ruff_config.py | TestPyprojectTomlRuffSettings | test_ruff_target_version_is_py310 | target-version=py310 の設定確認 |
| tests/test_ruff_config.py | TestPyprojectTomlRuffSettings | test_ruff_lint_select_contains_required_rules | select=E,F,I,W の設定確認 |
| tests/test_ruff_config.py | TestPyprojectTomlRuffSettings | test_ruff_isort_known_first_party | isort known-first-party=src の設定確認 |
| tests/test_ruff_config.py | TestPreCommitConfigYaml | test_precommit_config_exists | .pre-commit-config.yaml の存在確認 |
| tests/test_ruff_config.py | TestPreCommitConfigYaml | test_precommit_uses_ruff_pre_commit_repo | astral-sh/ruff-pre-commit リポジトリ設定確認 |
| tests/test_ruff_config.py | TestPreCommitConfigYaml | test_precommit_has_ruff_hook_with_fix | ruff --fix フック設定確認 |
| tests/test_ruff_config.py | TestPreCommitConfigYaml | test_precommit_has_ruff_format_hook | ruff-format フック設定確認 |
| tests/test_ruff_config.py | TestPreCommitConfigYaml | test_precommit_has_version_pinned | バージョン固定（rev）確認 |
| tests/test_ruff_config.py | TestMakefileTargets | test_makefile_has_lint_target | Makefile lint ターゲット存在確認 |
| tests/test_ruff_config.py | TestMakefileTargets | test_makefile_has_format_target | Makefile format ターゲット存在確認 |
| tests/test_ruff_config.py | TestMakefileTargets | test_makefile_has_setup_dev_target | Makefile setup-dev ターゲット存在確認 |
| tests/test_ruff_config.py | TestMakefileTargets | test_makefile_lint_uses_ruff | lint ターゲットが ruff を使用していることの確認 |

## 実装ヒント

- Phase 2 GREEN の主要タスク:
  1. `ruff check --fix .` で自動修正可能な69件の違反を修正
  2. `ruff format .` で全ファイルのフォーマットを適用
  3. 手動修正が必要なruff違反を個別対応
  4. `pre-commit install` でgit hookを登録
- 注意: F401(未使用import) の自動修正で使用中のimportを削除しないよう確認が必要

## make test 出力 (抜粋)

```
tests/test_ruff_config.py: 13 passed

tests/test_xml2_pipeline.py: 69 failed (既存テスト - ruff format適用前のimportエラー等)

全体: 69 failed, 253 passed in 1.38s
```
