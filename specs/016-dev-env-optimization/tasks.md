# Tasks: 開発環境の最適化

**Input**: `/specs/016-dev-env-optimization/` のデザインドキュメント
**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Tests**: 本機能は設定ファイル変更のみのため、TDD は適用外。各フェーズで設定の動作確認を行う。

**Organization**: タスクはユーザーストーリーごとにグループ化。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 依存関係なし（異なるファイル、実行順序自由）
- **[Story]**: タスクが属するユーザーストーリー（US1, US2, US3, US4）
- ファイルパスを説明に含める

## ユーザーストーリーサマリー

| ID | タイトル | 優先度 | FR | 概要 |
|----|----------|--------|-----|------|
| US1 | テスト設定の標準化 | P1 | FR-001,002,003 | pytest カバレッジ設定 |
| US2 | CI でのカバレッジ可視化 | P2 | FR-005,006 | PR カバレッジコメント |
| US3 | CI の実行時間最適化 | P2 | FR-004 | キャッシュ確認（既に最適化済み） |
| US4 | カバレッジバッジの表示 | P3 | FR-007 | README バッジ |

## パス規約

- **設定ファイル**: `pyproject.toml`, `.github/workflows/ci.yml`, `README.md`
- **出力先**: `specs/016-dev-env-optimization/tasks/`

---

## Phase 1: Setup（現状分析）— NO TDD

**目的**: 現在の設定状態を確認し、変更計画を立てる

- [x] T001 現在のカバレッジ状態を確認: `pytest --cov=src --cov-report=term-missing` を実行
- [x] T002 [P] pyproject.toml の現在の pytest 設定を確認
- [x] T003 [P] .github/workflows/ci.yml の現在の設定を確認
- [x] T004 [P] README.md の現在の状態を確認
- [x] T005 作成: specs/016-dev-env-optimization/tasks/ph1-output.md（現状分析結果）

---

## Phase 2: User Story 1 - テスト設定の標準化 (Priority: P1) MVP

**Goal**: ローカル環境でカバレッジレポートを自動生成、閾値 80% を設定

**Independent Test**: `pytest` 実行でカバレッジレポートが表示され、閾値チェックが動作することを確認

### Input

- [x] T006 前フェーズ出力を読む: specs/016-dev-env-optimization/tasks/ph1-output.md

### Implementation

- [x] T007 [US1] pyproject.toml に `[tool.pytest.ini_options]` セクションを追加
  - `testpaths = ["tests"]`
  - `addopts` にカバレッジオプション追加
- [x] T008 [US1] カバレッジ閾値を設定: `--cov-fail-under=70`
- [x] T009 [US1] XML レポート出力を追加: `--cov-report=xml:coverage.xml`

### Verification

- [x] T010 `pytest` を実行し、カバレッジレポートが表示されることを確認
- [x] T011 カバレッジ閾値の動作確認（現在のカバレッジ率に基づき調整が必要か判断）
- [x] T012 作成: specs/016-dev-env-optimization/tasks/ph2-output.md

**Checkpoint**: pytest 実行でカバレッジレポートが自動表示される状態

---

## Phase 3: User Story 2 - CI でのカバレッジ可視化 (Priority: P2)

**Goal**: PR にカバレッジレポートをコメントとして自動追加

**Independent Test**: PR を作成し、カバレッジコメントが表示されることを確認

### Input

- [ ] T013 セットアップ分析を読む: specs/016-dev-env-optimization/tasks/ph1-output.md
- [ ] T014 前フェーズ出力を読む: specs/016-dev-env-optimization/tasks/ph2-output.md

### Implementation

- [ ] T015 [US2] .github/workflows/ci.yml に permissions セクションを追加
  - `contents: write`
  - `pull-requests: write`
- [ ] T016 [US2] pytest ステップにカバレッジオプションを追加（pyproject.toml の設定が適用されることを確認）
- [ ] T017 [US2] py-cov-action/python-coverage-comment-action ステップを追加
  - `GITHUB_TOKEN`, `MINIMUM_GREEN`, `MINIMUM_ORANGE` を設定

### Verification

- [ ] T018 CI ワークフロー構文を検証: `gh workflow view ci.yml`
- [ ] T019 作成: specs/016-dev-env-optimization/tasks/ph3-output.md

**Checkpoint**: CI 設定が構文的に正しく、PR コメント機能が設定されている

---

## Phase 4: User Story 3 - CI の実行時間最適化 (Priority: P2)

**Goal**: 依存関係キャッシュが正しく動作していることを確認

**Independent Test**: CI ログで「Cache restored」メッセージを確認

### Input

- [ ] T020 セットアップ分析を読む: specs/016-dev-env-optimization/tasks/ph1-output.md
- [ ] T021 前フェーズ出力を読む: specs/016-dev-env-optimization/tasks/ph3-output.md

### Implementation

- [ ] T022 [US3] .github/workflows/ci.yml のキャッシュ設定を確認（research.md より既に最適化済み）
- [ ] T023 [US3] 必要に応じてキャッシュキーの明示化を検討（変更不要の可能性高い）

### Verification

- [ ] T024 CI 設定のキャッシュ部分を最終確認
- [ ] T025 作成: specs/016-dev-env-optimization/tasks/ph4-output.md

**Checkpoint**: キャッシュ設定が最適な状態

---

## Phase 5: User Story 4 - カバレッジバッジの表示 (Priority: P3)

**Goal**: README にカバレッジバッジを表示

**Independent Test**: README にバッジマークダウンが追加され、CI 実行後にバッジが更新される

### Input

- [ ] T026 セットアップ分析を読む: specs/016-dev-env-optimization/tasks/ph1-output.md
- [ ] T027 前フェーズ出力を読む: specs/016-dev-env-optimization/tasks/ph4-output.md

### Implementation

- [ ] T028 [US4] py-cov-action がバッジデータを生成するよう設定確認（Phase 3 で設定済みの可能性）
- [ ] T029 [US4] README.md にカバレッジバッジマークダウンを追加
  - shields.io エンドポイント形式

### Verification

- [ ] T030 README.md のバッジマークダウンが正しい形式であることを確認
- [ ] T031 作成: specs/016-dev-env-optimization/tasks/ph5-output.md

**Checkpoint**: README にバッジが追加されている

---

## Phase 6: Polish & 最終検証 — NO TDD

**Purpose**: 全体の整合性確認と最終調整

### Input

- [ ] T032 セットアップ分析を読む: specs/016-dev-env-optimization/tasks/ph1-output.md
- [ ] T033 前フェーズ出力を読む: specs/016-dev-env-optimization/tasks/ph5-output.md

### Implementation

- [ ] T034 [P] 全設定ファイルの整合性確認
- [ ] T035 [P] quickstart.md の内容と実際の設定が一致しているか確認
- [ ] T036 [P] coverage.xml が .gitignore に含まれているか確認（必要に応じて追加）

### Verification

- [ ] T037 `make test` を実行して全テストがパスすることを確認
- [ ] T038 作成: specs/016-dev-env-optimization/tasks/ph6-output.md

---

## Dependencies & Execution Order

### フェーズ依存関係

- **Phase 1 (Setup)**: 依存なし - メインエージェント直接実行
- **Phase 2 (US1)**: Phase 1 完了後 - speckit:phase-executor
- **Phase 3 (US2)**: Phase 2 完了後 - speckit:phase-executor
- **Phase 4 (US3)**: Phase 3 完了後 - speckit:phase-executor
- **Phase 5 (US4)**: Phase 4 完了後 - speckit:phase-executor
- **Phase 6 (Polish)**: 全 US 完了後 - speckit:phase-executor

### エージェント委譲

- **Phase 1**: メインエージェント直接実行
- **Phase 2-6**: speckit:phase-executor（TDD 不要のため tdd-generator はスキップ）

### [P] マーカー（依存関係なし）

`[P]` は「他のタスクへの依存なし、実行順序自由」を示す。

- Setup タスク [P]: 異なるファイルの読み取り
- Implementation タスク [P]: 異なる設定ファイルの編集

---

## Phase Output Artifacts

### ディレクトリ構造

```
specs/016-dev-env-optimization/
├── tasks.md                    # このファイル
├── tasks/
│   ├── ph1-output.md           # Phase 1 出力（現状分析）
│   ├── ph2-output.md           # Phase 2 出力（US1 完了）
│   ├── ph3-output.md           # Phase 3 出力（US2 完了）
│   ├── ph4-output.md           # Phase 4 出力（US3 完了）
│   ├── ph5-output.md           # Phase 5 出力（US4 完了）
│   └── ph6-output.md           # Phase 6 出力（最終）
└── red-tests/                  # （本機能では使用しない）
```

### Phase Output Format

| Output Type | Template File |
|-------------|---------------|
| `ph1-output.md` | `.specify/templates/ph1-output-template.md` |
| `phN-output.md` | `.specify/templates/phN-output-template.md` |

---

## Implementation Strategy

### MVP First (Phase 1 + Phase 2)

1. Phase 1 完了: 現状分析
2. Phase 2 完了: pytest カバレッジ設定
3. **STOP and VALIDATE**: `pytest` でカバレッジレポート表示を確認
4. 手動検証: カバレッジ率と閾値の動作確認

### Full Delivery

1. Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
2. 各フェーズ完了時にコミット: `feat(016): phase-N description`

---

## Notes

- 本機能は設定ファイル変更のみのため、TDD ワークフローは適用外
- US3（キャッシュ最適化）は research.md より既に最適化済み、確認のみ
- coverage.xml は CI で生成されるため、.gitignore に追加推奨
- PR コメント機能は PR 作成後に初めて検証可能
- バッジは CI 実行後に初めて表示される
