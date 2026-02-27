# Tasks: mypy 型チェック導入

**Input**: `/specs/014-mypy-type-checking/` の設計ドキュメント
**Prerequisites**: plan.md, spec.md, research.md

**特記事項**: この機能はツール設定・インフラ変更のため、従来の TDD（テストコード作成）ではなく、ツール実行による検証を行う。各フェーズの「テスト」は実際のコマンド実行と出力確認で代替する。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 依存関係なし（異なるファイル、実行順序自由）
- **[Story]**: 該当するユーザーストーリー（US1, US2, US3, US4）

## User Story Summary

| ID | Title | Priority | FR | 検証方法 |
|----|-------|----------|----|----------|
| US1 | 型チェック設定の構成 | P1 | FR-001〜004,006 | `mypy src/` 実行成功 |
| US2 | CI での型チェック | P1 | FR-005 | CI ワークフロー構文検証 |
| US3 | ローカルでの型チェック実行 | P1 | FR-007 | `make lint` 実行成功 |
| US4 | 既存コードの段階的型付け | P2 | FR-004 | 型なしコードでエラーなし |

## Path Conventions

- **設定ファイル**: `pyproject.toml`, `Makefile`
- **CI ワークフロー**: `.github/workflows/ci.yml`
- **型チェック対象**: `src/`

---

## Phase 1: Setup (現状分析) — NO TDD

**Purpose**: 現在のプロジェクト状態を確認し、変更準備を行う

- [x] T001 現在の pyproject.toml を読み込み、既存設定を確認する: pyproject.toml
- [x] T002 [P] 現在の Makefile を読み込み、lint ターゲットを確認する: Makefile
- [x] T003 [P] 現在の CI ワークフローを読み込み、lint ジョブを確認する: .github/workflows/ci.yml
- [x] T004 [P] src/ 配下の Python ファイル一覧を取得し、型チェック対象を確認する
- [x] T005 `mypy --version` が実行可能か確認（未インストールなら後続で追加）
- [x] T006 Edit: specs/014-mypy-type-checking/tasks/ph1-output.md

---

## Phase 2: US1 - 型チェック設定の構成 (Priority: P1) MVP

**Goal**: pyproject.toml に mypy 設定を追加し、型チェックが実行可能な状態にする

**Independent Test**: `mypy src/` コマンドを実行し、エラー 0 で完了することを確認

### Input

- [x] T007 Read: specs/014-mypy-type-checking/tasks/ph1-output.md

### 検証準備 (RED 相当)

- [x] T008 [US1] 現時点で `mypy src/` を実行し、設定なしの状態を記録する
- [x] T009 Generate RED output: specs/014-mypy-type-checking/red-tests/ph2-test.md

### Implementation (GREEN)

- [x] T010 Read RED tests: specs/014-mypy-type-checking/red-tests/ph2-test.md
- [x] T011 [US1] pyproject.toml の [project.optional-dependencies] dev に "mypy" を追加する: pyproject.toml
- [x] T012 [US1] pyproject.toml に [tool.mypy] セクションを追加する: pyproject.toml

```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = false
ignore_missing_imports = true
files = ["src"]
```

- [x] T013 [US1] mypy をインストールする: `pip install -e ".[dev]"`
- [x] T014 [US1] `mypy src/` を実行し、エラー 0 で完了することを確認する (GREEN)

### Verification

- [x] T015 [US1] `warn_return_any` が機能することを確認（Any を返す関数があれば警告出力）
- [ ] T016 Edit: specs/014-mypy-type-checking/tasks/ph2-output.md

**Checkpoint**: `mypy src/` が設定に基づいて実行可能

---

## Phase 3: US2 + US3 - CI & ローカル統合 (Priority: P1)

**Goal**: CI ワークフローと Makefile に mypy を統合する

**Independent Test**: `make lint` 成功、CI ワークフロー構文検証成功

### Input

- [x] T017 Read: specs/014-mypy-type-checking/tasks/ph1-output.md
- [x] T018 Read: specs/014-mypy-type-checking/tasks/ph2-output.md

### 検証準備 (RED 相当)

- [x] T019 [US3] 現時点で `make lint` を実行し、mypy が含まれていないことを確認する
- [x] T020 Generate RED output: specs/014-mypy-type-checking/red-tests/ph3-test.md

### Implementation (GREEN)

- [x] T021 Read RED tests: specs/014-mypy-type-checking/red-tests/ph3-test.md
- [x] T022 [P] [US3] Makefile の lint ターゲットに mypy コマンドを追加する: Makefile

```makefile
lint: ## Run ruff linter, format check, and mypy
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .
	$(VENV)/bin/mypy src/
```

- [x] T023 [P] [US2] .github/workflows/ci.yml に mypy ステップを追加する: .github/workflows/ci.yml

```yaml
      - name: Run mypy
        run: mypy src/
```

- [x] T024 [US3] `make lint` を実行し、mypy が実行されることを確認する (GREEN)
- [x] T025 [US2] CI ワークフロー構文を検証する: `python -m py_compile` または `yamllint`（オプション）

### Verification

- [x] T026 `make lint` が ruff + mypy を実行することを確認する
- [x] T027 Edit: specs/014-mypy-type-checking/tasks/ph3-output.md

**Checkpoint**: ローカルと CI の両方で mypy が統合完了

---

## Phase 4: US4 - 段階的型付け検証 (Priority: P2)

**Goal**: 既存コードが型エラーなく通過することを確認し、段階的導入の基盤を整える

**Independent Test**: 型ヒントなしの既存コードで mypy エラーが出ないことを確認

### Input

- [ ] T028 Read: specs/014-mypy-type-checking/tasks/ph1-output.md
- [ ] T029 Read: specs/014-mypy-type-checking/tasks/ph3-output.md

### 検証準備 (RED 相当)

- [ ] T030 [US4] 型ヒントのない関数を特定し、リストアップする
- [ ] T031 Generate RED output: specs/014-mypy-type-checking/red-tests/ph4-test.md

### Implementation (GREEN)

- [ ] T032 Read RED tests: specs/014-mypy-type-checking/red-tests/ph4-test.md
- [ ] T033 [US4] `mypy src/` を実行し、型ヒントなしコードでもエラーが出ないことを確認する
- [ ] T034 [US4] エラーが出る場合は `disallow_untyped_defs = false` が有効か確認する

### Verification

- [ ] T035 既存コードすべてで `mypy src/` がエラー 0 で完了することを確認する
- [ ] T036 Edit: specs/014-mypy-type-checking/tasks/ph4-output.md

**Checkpoint**: 段階的導入の設定が正しく機能している

---

## Phase 5: Polish & 最終検証 — NO TDD

**Purpose**: 全体の動作確認とドキュメント整備

### Input

- [ ] T037 Read: specs/014-mypy-type-checking/tasks/ph1-output.md
- [ ] T038 Read: specs/014-mypy-type-checking/tasks/ph4-output.md

### Implementation

- [ ] T039 [P] 全体の lint 実行確認: `make lint`
- [ ] T040 [P] quickstart.md の内容が最新の設定と一致することを確認する
- [ ] T041 [P] 不要な type: ignore コメントがないことを確認する

### Verification

- [ ] T042 `make test` を実行し、全テストが通過することを確認する
- [ ] T043 `make lint` を実行し、エラー 0 で完了することを確認する
- [ ] T044 Edit: specs/014-mypy-type-checking/tasks/ph5-output.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: 依存なし - メインエージェント直接実行
- **Phase 2 (US1)**: Phase 1 完了後 - TDD フロー
- **Phase 3 (US2+US3)**: Phase 2 完了後 - TDD フロー（US1 の設定が必要）
- **Phase 4 (US4)**: Phase 3 完了後 - TDD フロー
- **Phase 5 (Polish)**: Phase 4 完了後 - speckit:phase-executor のみ

### Agent Delegation

| Phase | Agent | 備考 |
|-------|-------|------|
| Phase 1 | メインエージェント | 現状分析、TDD なし |
| Phase 2 | speckit:tdd-generator → speckit:phase-executor | US1: pyproject.toml 設定 |
| Phase 3 | speckit:tdd-generator → speckit:phase-executor | US2+US3: CI & Makefile |
| Phase 4 | speckit:tdd-generator → speckit:phase-executor | US4: 段階的型付け検証 |
| Phase 5 | speckit:phase-executor | 最終検証、TDD なし |

### [P] Marker (No Dependencies)

- T002, T003, T004: 異なるファイルの読み込み
- T022, T023: Makefile と ci.yml の独立した編集
- T039, T040, T041: 独立した検証タスク

---

## Phase Output & RED Test Artifacts

### Directory Structure

```
specs/014-mypy-type-checking/
├── tasks.md                    # このファイル
├── tasks/
│   ├── ph1-output.md           # Phase 1: Setup 結果
│   ├── ph2-output.md           # Phase 2: US1 GREEN 結果
│   ├── ph3-output.md           # Phase 3: US2+US3 GREEN 結果
│   ├── ph4-output.md           # Phase 4: US4 GREEN 結果
│   └── ph5-output.md           # Phase 5: Polish 結果
└── red-tests/
    ├── ph2-test.md             # Phase 2: RED 状態（設定前）
    ├── ph3-test.md             # Phase 3: RED 状態（統合前）
    └── ph4-test.md             # Phase 4: RED 状態（検証前）
```

---

## Implementation Strategy

### MVP First (Phase 1 + Phase 2)

1. Phase 1: Setup（現状確認）
2. Phase 2: US1（pyproject.toml に mypy 設定追加）
3. **STOP and VALIDATE**: `mypy src/` が成功することを確認
4. この時点で最小限の型チェック機能が利用可能

### Full Delivery

1. Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5
2. 各 Phase 完了後にコミット: `chore(mypy): phase-N description`

---

## Notes

- この機能は設定変更のみのため、アプリケーションテストコードの追加は不要
- 「テスト」はツール実行（`mypy src/`, `make lint`）による検証で代替
- 既存の ruff 設定と共存する形で mypy を追加
- CI での失敗時は、`ignore_missing_imports` 設定を確認
