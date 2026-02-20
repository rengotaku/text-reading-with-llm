# Tasks: ruff導入・pre-commit設定・ファイル分割

**Input**: 設計ドキュメント `/specs/008-ruff-precommit-setup/`
**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Tests**: TDDはUser Storyフェーズで必須。各フェーズはTest Implementation (RED) → Implementation (GREEN) → Verificationのワークフローに従う。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 依存関係なし（異なるファイル、実行順序自由）
- **[Story]**: タスクが属するUser Story（US1, US2, US3）
- 説明には正確なファイルパスを含む

## User Story Summary

| ID | タイトル | 優先度 | FR | シナリオ |
|----|---------|--------|-----|---------|
| US1 | コード品質の自動チェック | P1 | FR-002,003,004,005 | pre-commit自動実行 |
| US2 | ruffによるコード品質設定 | P1 | FR-001 | ruff check/format実行 |
| US3 | 大規模ファイルの分割 | P2 | FR-006,007,008,009 | xml2_pipeline.py分割 |

## Path Conventions

- **Source**: `src/` (リポジトリルート直下)
- **Tests**: `tests/` (リポジトリルート直下)
- **Feature Dir**: `specs/008-ruff-precommit-setup/`

---

## Phase 1: Setup（共通基盤）— TDDなし

**目的**: ruff・pre-commitのインストール、設定ファイル作成、Makefile更新

- [X] T001 現在の src/xml2_pipeline.py の構造と依存関係を分析
- [X] T002 [P] 現在の tests/test_xml2_pipeline.py のimportパターンを分析
- [X] T003 [P] pyproject.toml を新規作成（ruff設定: line-length=120, target-version=py310, select=E,F,I,W）
- [X] T004 [P] requirements-dev.txt を新規作成（ruff, pre-commit）
- [X] T005 [P] .pre-commit-config.yaml を新規作成（astral-sh/ruff-pre-commit: ruff --fix, ruff-format）
- [X] T006 Makefile に setup-dev, lint, format ターゲットを追加
- [X] T007 `pip install -r requirements-dev.txt` で開発用依存関係をインストール
- [X] T008 `ruff check .` と `ruff format --check .` で現在の違反状況を確認
- [X] T009 specs/008-ruff-precommit-setup/tasks/ph1-output-template.md を編集 → ph1-output.md にリネーム

---

## Phase 2: US1+US2 - ruff設定・pre-commit・既存コード修正 (Priority: P1) MVP

**Goal**: ruff設定とpre-commitフックを導入し、既存コード全体をruffチェック合格状態にする

**Independent Test**: `ruff check .` がエラー0件、`ruff format --check .` が差分0件で完了する

### Input

- [ ] T010 前フェーズ出力を読む: specs/008-ruff-precommit-setup/tasks/ph1-output.md

### Test Implementation (RED)

- [ ] T011 [P] [US2] ruff設定の検証テストを実装: pyproject.tomlの設定値確認テスト tests/test_ruff_config.py
- [ ] T012 [P] [US1] pre-commit設定の検証テストを実装: .pre-commit-config.yaml存在・内容確認テスト tests/test_ruff_config.py
- [ ] T013 `make test` でFAIL確認 (RED)
- [ ] T014 RED出力を生成: specs/008-ruff-precommit-setup/red-tests/ph2-test.md

### Implementation (GREEN)

- [ ] T015 REDテストを読む: specs/008-ruff-precommit-setup/red-tests/ph2-test.md
- [ ] T016 [US2] `ruff check --fix .` で自動修正可能な既存コード違反を一括修正
- [ ] T017 [US2] `ruff format .` で既存コードのフォーマットを一括適用
- [ ] T018 [US2] 手動修正が必要なruff違反を個別対応（残りがあれば）
- [ ] T019 [US1] `pre-commit install` でgit hookを登録
- [ ] T020 `make test` でPASS確認 (GREEN)

### Verification

- [ ] T021 `ruff check .` でエラー0件を確認
- [ ] T022 `ruff format --check .` で差分0件を確認
- [ ] T023 `make test` で全テストパスを確認（リグレッションなし）
- [ ] T024 specs/008-ruff-precommit-setup/tasks/ph2-output-template.md を編集 → ph2-output.md にリネーム

**Checkpoint**: ruff check/formatがプロジェクト全体でクリーン、pre-commitフックが動作可能

---

## Phase 3: US3 - xml2_pipeline.pyファイル分割 (Priority: P2)

**Goal**: src/xml2_pipeline.py (651行) を3ファイルに分割し、各ファイル600行以下にする

**Independent Test**: 分割後の全ファイルが600行以下、既存テストが全パス、re-exportで後方互換性維持

### Input

- [ ] T025 セットアップ分析を読む: specs/008-ruff-precommit-setup/tasks/ph1-output.md
- [ ] T026 前フェーズ出力を読む: specs/008-ruff-precommit-setup/tasks/ph2-output.md

### Test Implementation (RED)

- [ ] T027 [P] [US3] process_manager.pyのimport互換性テストを実装 tests/test_file_split.py
- [ ] T028 [P] [US3] chapter_processor.pyのimport互換性テストを実装 tests/test_file_split.py
- [ ] T029 [P] [US3] xml2_pipeline.pyのre-export動作テストを実装 tests/test_file_split.py
- [ ] T030 [P] [US3] 各ファイルの行数上限テストを実装（600行以下確認） tests/test_file_split.py
- [ ] T031 `make test` でFAIL確認 (RED)
- [ ] T032 RED出力を生成: specs/008-ruff-precommit-setup/red-tests/ph3-test.md

### Implementation (GREEN)

- [ ] T033 REDテストを読む: specs/008-ruff-precommit-setup/red-tests/ph3-test.md
- [ ] T034 [US3] src/process_manager.py を新規作成（get_pid_file_path, kill_existing_process, write_pid_file, cleanup_pid_file を移動）
- [ ] T035 [US3] src/chapter_processor.py を新規作成（sanitize_filename, load_sound, process_chapters, process_content を移動）
- [ ] T036 [US3] src/xml2_pipeline.py をリファクタリング（parse_args, main を残し、re-exportを追加）
- [ ] T037 `make test` でPASS確認 (GREEN)

### Verification

- [ ] T038 各ファイルの行数確認: `wc -l src/xml2_pipeline.py src/process_manager.py src/chapter_processor.py`（全て600行以下）
- [ ] T039 `ruff check .` で分割後ファイルがruffチェック合格を確認
- [ ] T040 `ruff format --check .` で分割後ファイルのフォーマット確認
- [ ] T041 `make test` で全テストパスを確認（リグレッションなし）
- [ ] T042 specs/008-ruff-precommit-setup/tasks/ph3-output-template.md を編集 → ph3-output.md にリネーム

**Checkpoint**: 3ファイル全て600行以下、全テストパス、ruffクリーン

---

## Phase 4: Polish・最終検証 — TDDなし

**目的**: 全成功基準の最終確認、クロスカッティング検証

### Input

- [ ] T043 セットアップ分析を読む: specs/008-ruff-precommit-setup/tasks/ph1-output.md
- [ ] T044 前フェーズ出力を読む: specs/008-ruff-precommit-setup/tasks/ph3-output.md

### Implementation

- [ ] T045 [P] 不要になったimportやコメントの削除
- [ ] T046 [P] quickstart.md の手順に従ってセットアップが3ステップ以内で完了することを確認
- [ ] T047 SC-001確認: `ruff check .` エラー0件
- [ ] T048 SC-002確認: `ruff format --check .` 差分0件
- [ ] T049 SC-004確認: 分割ファイル全て600行以下
- [ ] T050 SC-005確認: `make test` で全テスト100%パス

### Verification

- [ ] T051 `make test` で最終全テストパスを確認
- [ ] T052 specs/008-ruff-precommit-setup/tasks/ph4-output-template.md を編集 → ph4-output.md にリネーム

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: 依存なし - メインエージェント直接実行
- **Phase 2 (US1+US2)**: Phase 1完了後 - TDDフロー (tdd-generator → phase-executor)
- **Phase 3 (US3)**: Phase 2完了後 - TDDフロー (tdd-generator → phase-executor)
- **Phase 4 (Polish)**: Phase 3完了後 - phase-executorのみ

### User Story間の依存

- US2 (ruff設定) → US1 (pre-commit) : US2の設定がUS1の前提
- US1+US2 → US3 (ファイル分割) : 分割後コードもruffチェック合格が必要

### Agent Delegation

- **Phase 1 (Setup)**: メインエージェント直接実行
- **Phase 2 (US1+US2)**: tdd-generator (RED) → phase-executor (GREEN + Verification)
- **Phase 3 (US3)**: tdd-generator (RED) → phase-executor (GREEN + Verification)
- **Phase 4 (Polish)**: phase-executorのみ

---

## Phase Output & RED Test Artifacts

### Directory Structure

```
specs/008-ruff-precommit-setup/
├── tasks.md
├── tasks/
│   ├── ph1-output.md
│   ├── ph2-output.md
│   ├── ph3-output.md
│   └── ph4-output.md
└── red-tests/
    ├── ph2-test.md
    └── ph3-test.md
```

---

## Implementation Strategy

### MVP First (Phase 1 + Phase 2)

1. Phase 1完了: ruff/pre-commit設定ファイル作成
2. Phase 2完了: 既存コードのruff違反修正 + pre-commit動作確認
3. **停止・検証**: `ruff check .` と `make test` で確認

### Full Delivery

1. Phase 1 → Phase 2 → Phase 3 → Phase 4
2. 各Phase完了時にコミット

---

## Notes

- US1とUS2は密接に関連するためPhase 2で統合実行
- ファイル分割（US3）のテストは既存テストの再利用 + import互換性テスト
- re-exportパターンにより既存のimportパスを変更不要
- tests/test_ruff_config.py はツール設定の検証用（プロジェクト固有）
- tests/test_file_split.py は分割後の構造検証用
