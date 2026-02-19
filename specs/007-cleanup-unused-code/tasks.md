# Tasks: 不要機能の削除リファクタリング

**Input**: Design documents from `/specs/007-cleanup-unused-code/`
**Prerequisites**: plan.md (required), spec.md (required), research.md

**Tests**: 本タスクは削除リファクタリングのため、新規テスト作成は不要。各フェーズで既存テストの通過を検証する。

**Organization**: ユーザーストーリー単位でタスクをグループ化。各ストーリーは独立して実装・検証可能。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 依存関係なし（異なるファイル、実行順序自由）
- **[Story]**: 対応するユーザーストーリー（US1, US2, US3）
- 正確なファイルパスを記述に含む

## User Story Summary

| ID  | Title                      | Priority | FR        | Scenario                                |
|-----|----------------------------|----------|-----------|-----------------------------------------|
| US1 | 不要ソースコード削除       | P1       | FR-1,2,3,4 | ソース10件削除→既存テスト全パス         |
| US2 | 不要テストコード削除       | P2       | FR-5,7    | テスト4件削除→残テスト全パス            |
| US3 | Makefile・設定ファイル整理 | P3       | FR-6      | ターゲット削除/修正→make help全有効     |

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Feature dir**: `specs/007-cleanup-unused-code/`

---

## Phase 1: Setup（現状分析・ベースライン確認）— NO TDD

**Purpose**: 削除前の現状把握とベースラインテスト実行

- [x] T001 現在のソースファイル一覧を確認: `src/` ディレクトリ
- [x] T002 [P] 現在のテストファイル一覧を確認: `tests/` ディレクトリ
- [x] T003 [P] 依存関係の最終確認: research.md の削除対象リストと実コードを照合
- [x] T004 ベースラインテスト実行: `make test` で全テストがパスすることを確認
- [x] T005 Edit and rename: specs/007-cleanup-unused-code/tasks/ph1-output-template.md → ph1-output.md

---

## Phase 2: User Story 1 - 不要ソースコード削除 (Priority: P1) MVP

**Goal**: 不要なソースファイル10件を削除し、xml2パイプラインと辞書生成が正常動作することを確認

**Independent Test**: `make test` で xml2 関連テストが全パスすること

### Input

- [x] T006 Read previous phase output: specs/007-cleanup-unused-code/tasks/ph1-output.md

### Implementation

- [x] T007 [P] [US1] `git rm` で旧MDパイプライン関連を削除: `src/pipeline.py`, `src/progress.py`, `src/toc_extractor.py`, `src/organize_chapters.py`
- [x] T008 [P] [US1] `git rm` で旧XMLパイプライン関連を削除: `src/xml_pipeline.py`, `src/xml_parser.py`
- [x] T009 [P] [US1] `git rm` でAquesTalk関連を削除: `src/aquestalk_pipeline.py`, `src/aquestalk_client.py`
- [x] T010 [P] [US1] `git rm` でその他不要ファイルを削除: `src/tts_generator.py`, `src/test_tts_normalize.py`
- [x] T011 [US1] `__pycache__` 内の対応 `.pyc` ファイルを削除: `src/__pycache__/`

### Verification

- [x] T012 `make test` を実行し全テストがパスすることを確認（リグレッションなし）
- [x] T013 Edit and rename: specs/007-cleanup-unused-code/tasks/ph2-output-template.md → ph2-output.md

**Checkpoint**: ソースファイル削除完了、xml2パイプライン正常動作

---

## Phase 3: User Story 2 - 不要テストコード削除 (Priority: P2)

**Goal**: 削除済みモジュールに対応するテストファイル4件を削除し、テストスイートを整理

**Independent Test**: `make test` で残テストが全パスし、インポートエラーがないこと

### Input

- [x] T014 Read setup analysis: specs/007-cleanup-unused-code/tasks/ph1-output.md
- [x] T015 Read previous phase output: specs/007-cleanup-unused-code/tasks/ph2-output.md

### Implementation

- [x] T016 [P] [US2] `git rm` で旧XMLパイプラインテストを削除: `tests/test_xml_pipeline.py`, `tests/test_xml_parser.py`
- [x] T017 [P] [US2] `git rm` でAquesTalkテストを削除: `tests/test_aquestalk_client.py`, `tests/test_aquestalk_pipeline.py`
- [x] T018 [US2] `__pycache__` 内の対応テストキャッシュを削除: `tests/__pycache__/`

### Verification

- [x] T019 `make test` を実行し全テストがパスすることを確認
- [x] T020 Edit and rename: specs/007-cleanup-unused-code/tasks/ph3-output-template.md → ph3-output.md

**Checkpoint**: テストファイル削除完了、テストスイート整合性確認済み

---

## Phase 4: User Story 3 - Makefile・設定ファイル整理 (Priority: P3)

**Goal**: 削除済みモジュールに関連する Makefile ターゲットを削除・修正し、ビルドシステムを整理

**Independent Test**: `make help` の全ターゲットが実行可能であること

### Input

- [ ] T021 Read setup analysis: specs/007-cleanup-unused-code/tasks/ph1-output.md
- [ ] T022 Read previous phase output: specs/007-cleanup-unused-code/tasks/ph3-output.md

### Implementation

- [ ] T023 [US3] Makefile から不要ターゲットを削除: `run`, `run-simple`, `toc`, `organize` ターゲット in `Makefile`
- [ ] T024 [US3] `xml-tts` ターゲットを修正: PARSER分岐を削除し xml2 直接実行に変更 in `Makefile`
- [ ] T025 [US3] `.PHONY` から削除済みターゲットを除去 in `Makefile`
- [ ] T026 [US3] 不要な Makefile 変数を削除: `PARSER` 変数等 in `Makefile`

### Verification

- [ ] T027 `make help` を実行し不要ターゲットが表示されないことを確認
- [ ] T028 `make test` を実行し全テストがパスすることを確認
- [ ] T029 Edit and rename: specs/007-cleanup-unused-code/tasks/ph4-output-template.md → ph4-output.md

**Checkpoint**: Makefile 整理完了、全ターゲット有効

---

## Phase 5: Polish & Cross-Cutting Concerns — NO TDD

**Purpose**: 最終検証と成功基準の確認

### Input

- [ ] T030 Read setup analysis: specs/007-cleanup-unused-code/tasks/ph1-output.md
- [ ] T031 Read previous phase output: specs/007-cleanup-unused-code/tasks/ph4-output.md

### Implementation

- [ ] T032 [P] 削除後のソースファイル数を確認し、5ファイル以上減少していることを検証（SC-001）
- [ ] T033 [P] `requirements.txt` から不要な依存パッケージがあれば削除
- [ ] T034 quickstart.md の検証手順を実行

### Verification

- [ ] T035 `make test` を実行し全テストが100%パスすることを最終確認（SC-002）
- [ ] T036 Edit and rename: specs/007-cleanup-unused-code/tasks/ph5-output-template.md → ph5-output.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 依存なし — メインエージェント直接実行
- **US1 (Phase 2)**: Phase 1 完了後 — phase-executor（削除は TDD 不要）
- **US2 (Phase 3)**: Phase 2 完了後 — phase-executor（削除は TDD 不要）
- **US3 (Phase 4)**: Phase 3 完了後 — phase-executor（Makefile 修正）
- **Polish (Phase 5)**: Phase 4 完了後 — phase-executor

### Agent Delegation

- **Phase 1 (Setup)**: メインエージェント直接実行
- **Phase 2-4 (User Stories)**: phase-executor（削除リファクタリングのため TDD 不要、tdd-generator スキップ）
- **Phase 5 (Polish)**: phase-executor

### TDD 適用判断

本タスクは既存コードの削除リファクタリングであり、新規機能追加を伴わない。そのため：
- 新規テスト作成（RED フェーズ）は不要
- 各フェーズで既存テストの通過（GREEN 状態維持）を検証
- tdd-generator は使用せず、全フェーズ phase-executor で実行

### [P] Marker (No Dependencies)

- Setup: T001-T003 は並列実行可能（異なるディレクトリの確認）
- Phase 2: T007-T010 は並列実行可能（異なるファイルの削除）
- Phase 3: T016-T017 は並列実行可能（異なるテストファイルの削除）
- Phase 5: T032-T033 は並列実行可能（異なる検証作業）

---

## Phase Output Artifacts

### Directory Structure

```
specs/007-cleanup-unused-code/
├── tasks.md                    # This file
├── tasks/
│   ├── ph1-output.md           # Phase 1: Setup 結果
│   ├── ph2-output.md           # Phase 2: US1 ソース削除結果
│   ├── ph3-output.md           # Phase 3: US2 テスト削除結果
│   ├── ph4-output.md           # Phase 4: US3 Makefile 整理結果
│   └── ph5-output.md           # Phase 5: Polish 最終検証結果
└── red-tests/                  # 未使用（TDD 不要のため）
```

---

## Implementation Strategy

### MVP First (Phase 1 + Phase 2)

1. Phase 1 完了: 現状分析・ベースラインテスト
2. Phase 2 完了: 不要ソースファイル10件削除
3. **STOP and VALIDATE**: `make test` で全テストパス確認
4. この時点で最大のコードベース削減効果を達成

### Full Delivery

1. Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5
2. 各フェーズでコミット: `refactor(phase-N): description`

---

## Notes

- 全フェーズで `make test` 検証を必須とし、リグレッションを防止
- 削除は Git 管理下で行うため、必要時に復元可能
- `voicevox_client.py`, `mecab_reader.py`, `reading_dict.py` は xml2 パイプラインから使用されているため削除対象外
- `__pycache__` のクリーンアップはソース/テスト削除と同時に実施
