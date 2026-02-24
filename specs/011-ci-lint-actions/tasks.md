# Tasks: CI Lint Actions

**Input**: Design documents from `/specs/011-ci-lint-actions/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, quickstart.md ✓

**タイプ**: インフラ/CI 設定（TDD 非対象）

**備考**: GitHub Actions ワークフローファイル（YAML）は Python テストの対象外。検証は PR 作成と CI 実行結果の観察で行う。

## User Story Summary

| ID | Title | Priority | FR | シナリオ |
|----|-------|----------|----|----------|
| US1 | PR 作成時の自動 Lint チェック | P1 | FR-001,002,004,005,006,007,008 | PR 作成・更新時に CI 実行 |
| US2 | ローカルと CI の結果一致 | P2 | FR-006 | `make lint` と CI 結果が一致 |
| US3 | main ブランチ保護 | P3 | FR-003 | main への push 時に CI 実行 |

## Path Conventions

```
.github/
└── workflows/
    └── lint.yml    # 新規作成: lint ワークフロー
```

---

## Phase 1: Setup（セットアップ）— NO TDD

**Purpose**: 既存プロジェクト構造の確認と変更準備

- [x] T001 `make lint` を実行して現在の lint 状態を確認
- [x] T002 [P] pyproject.toml の ruff 設定を確認
- [x] T003 [P] requirements-dev.txt の依存関係を確認
- [x] T004 [P] .github/ ディレクトリの存在確認（なければ作成）
- [x] T005 セットアップ分析結果を出力: specs/011-ci-lint-actions/tasks/ph1-output.md

---

## Phase 2: Implementation（US1+US2+US3 統合）— NO TDD

**Goal**: GitHub Actions lint ワークフローを作成し、全ユーザーストーリーを満たす

**Independent Test**: PR を作成し、GitHub Actions が実行されることを確認

### Input

- [x] T006 Read setup analysis: specs/011-ci-lint-actions/tasks/ph1-output.md

### Implementation

- [x] T007 [US1] [US2] [US3] `.github/workflows/lint.yml` を作成（quickstart.md の構成を使用）

**ワークフロー構成**:
```yaml
name: Lint

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
          cache: 'pip'
          cache-dependency-path: requirements-dev.txt

      - name: Install dependencies
        run: pip install -r requirements-dev.txt

      - name: Run lint
        run: make lint
```

### Verification

- [x] T008 `make lint` がローカルで成功することを確認
- [x] T009 YAML 構文検証（yamllint または IDE）
- [x] T010 Phase 出力を生成: specs/011-ci-lint-actions/tasks/ph2-output.md

**Checkpoint**: ワークフローファイル作成完了。PR 作成で CI 動作を検証可能。

---

## Phase 3: Polish（最終検証）— NO TDD

**Purpose**: 成功基準の検証とドキュメント確認

### Input

- [ ] T011 Read setup analysis: specs/011-ci-lint-actions/tasks/ph1-output.md
- [ ] T012 Read previous phase output: specs/011-ci-lint-actions/tasks/ph2-output.md

### Verification Tasks

- [ ] T013 PR を作成し、CI が自動実行されることを確認（SC-001, SC-002 検証）
- [ ] T014 CI の実行時間が 5 分以内であることを確認（SC-001）
- [ ] T015 [P] CI ログと `make lint` の出力を比較し、一致を確認（SC-003）
- [ ] T016 [P] 意図的な lint エラーで CI が失敗することを確認（SC-002）

### Documentation

- [ ] T017 成功基準チェックリストを更新: specs/011-ci-lint-actions/checklists/requirements.md
- [ ] T018 Phase 出力を生成: specs/011-ci-lint-actions/tasks/ph3-output.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: 依存なし - メインエージェント直接実行
- **Phase 2 (Implementation)**: Phase 1 完了後 - メインエージェント直接実行
- **Phase 3 (Polish)**: Phase 2 完了後 + PR 作成・マージ後に検証

### Agent Delegation

- **Phase 1**: メインエージェント直接実行
- **Phase 2**: メインエージェント直接実行（YAML 作成は TDD 非対象）
- **Phase 3**: メインエージェント直接実行（検証は手動 + CI 観察）

### [P] Marker

`[P]` = 依存なし、実行順序自由

- T002, T003, T004: 異なるファイルの読み取り
- T015, T016: 異なる検証タスク

---

## Phase Output Artifacts

### Directory Structure

```
specs/011-ci-lint-actions/
├── tasks.md                    # このファイル
└── tasks/
    ├── ph1-output.md           # Phase 1: セットアップ分析結果
    ├── ph2-output.md           # Phase 2: 実装完了報告
    └── ph3-output.md           # Phase 3: 最終検証結果
```

---

## Implementation Strategy

### MVP (Phase 1 + Phase 2)

1. Phase 1 完了: 既存環境確認
2. Phase 2 完了: lint.yml 作成
3. **検証**: PR 作成 → CI 実行確認

### Full Delivery

1. Phase 1 → Phase 2 → PR 作成・マージ
2. Phase 3: 成功基準の完全検証
3. コミット: `ci: GitHub Actions で ruff lint チェックを追加`

---

## Notes

- この機能は YAML 設定ファイルのため、Python TDD は非対象
- US2（ローカル一致）は `make lint` 使用により自動的に満たされる
- US3（main 保護）は同じトリガー設定で US1 と同時に満たされる
- 検証は PR 作成と CI 実行結果の観察で行う
