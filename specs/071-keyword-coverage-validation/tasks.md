# Tasks: キーワード抽出とカバー率検証

**Input**: Design documents from `/specs/071-keyword-coverage-validation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: TDD は User Story フェーズで必須。Test Implementation (RED) → Implementation (GREEN) → Verification のフローに従う。

**Organization**: タスクはユーザーストーリーごとにグループ化され、各ストーリーを独立して実装・テストできる。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 依存関係なし（異なるファイル、実行順序自由）
- **[Story]**: タスクが属するユーザーストーリー（例: US1, US2, US3）
- 説明には正確なファイルパスを含める

## User Story Summary

| ID | Title | Priority | FR | Scenario |
|----|-------|----------|----|----------|
| US1 | キーワード抽出 | P1 | FR-1,2,3,4,5 | 原文からキーワードを抽出 |
| US2 | カバー率検証 | P1 | FR-6,7 | 対話XMLのキーワードカバー率を計算 |
| US3 | 検証結果の出力 | P2 | FR-8,9 | JSON形式で結果を出力 |

## Path Conventions

- **プロジェクトタイプ**: single
- **ソースコード**: `src/` （リポジトリルート）
- **テスト**: `tests/` （リポジトリルート）
- **プロンプト**: `src/prompts/`

---

## Phase 1: Setup (既存コード確認) — NO TDD

**Purpose**: 既存の prompt_loader.py パターンと dialogue_converter.py の LLM 使用パターンを確認

- [x] T001 Read: src/prompt_loader.py（プロンプト読み込みパターン確認）
- [x] T002 [P] Read: src/dialogue_converter.py（ollama 使用パターン確認）
- [x] T003 [P] Read: src/prompts/generate_dialogue.txt（プロンプト形式確認）
- [x] T004 [P] Read: tests/test_prompt_loader.py（テストパターン確認）
- [x] T005 Edit: specs/071-keyword-coverage-validation/tasks/ph1-output.md

---

## Phase 2: User Story 1 - キーワード抽出 (Priority: P1) MVP

**Goal**: 原文セクションから重要なキーワードを LLM を使って抽出する

**Independent Test**: 原文テキストを入力として与え、キーワードリストが出力されることを確認

### Input

- [x] T006 Read: specs/071-keyword-coverage-validation/tasks/ph1-output.md

### Test Implementation (RED)

- [x] T007 [P] [US1] プロンプトファイルのテストを実装: tests/test_keyword_extractor.py（extract_keywords.txt が存在し正しい形式であることを確認）
- [x] T008 [P] [US1] 基本抽出テストを実装: tests/test_keyword_extractor.py（固有名詞、専門用語、数値を含むテキストからキーワードが抽出される）
- [x] T009 [P] [US1] エッジケーステストを実装: tests/test_keyword_extractor.py（空テキスト → 空リスト）
- [x] T010 [P] [US1] 出力形式テストを実装: tests/test_keyword_extractor.py（カンマ区切り出力のパース、重複除去、trim）
- [x] T011 Verify: `make test` FAIL (RED)
- [x] T012 Edit: specs/071-keyword-coverage-validation/red-tests/ph2-test.md

### Implementation (GREEN)

- [x] T013 Read: specs/071-keyword-coverage-validation/red-tests/ph2-test.md
- [x] T014 [P] [US1] プロンプトファイルを作成: src/prompts/extract_keywords.txt
- [x] T015 [US1] キーワード抽出モジュールを実装: src/keyword_extractor.py（extract_keywords 関数、prompt_loader 使用、ollama 呼び出し）
- [x] T016 Verify: `make test` PASS (GREEN)

### Verification

- [x] T017 Verify: `make test` で全テストパス（リグレッションなし）
- [x] T018 Edit: specs/071-keyword-coverage-validation/tasks/ph2-output.md

**Checkpoint**: キーワード抽出が独立して動作することを確認

---

## Phase 3: User Story 2 + 3 - カバー率検証と JSON 出力 (Priority: P1/P2)

**Goal**: キーワードリストと対話 XML を入力として、カバー率を計算し JSON 形式で出力する

**Independent Test**: キーワードリストと対話 XML を入力として与え、カバー率と未カバーキーワードが JSON で出力されることを確認

### Input

- [x] T019 Read: specs/071-keyword-coverage-validation/tasks/ph1-output.md
- [x] T020 Read: specs/071-keyword-coverage-validation/tasks/ph2-output.md

### Test Implementation (RED)

- [x] T021 [P] [US2] CoverageResult dataclass テストを実装: tests/test_coverage_validator.py（属性、to_dict メソッド）
- [x] T022 [P] [US2] 基本検証テストを実装: tests/test_coverage_validator.py（キーワードリストと対話 XML → カバー率計算）
- [x] T023 [P] [US2] 全カバーテストを実装: tests/test_coverage_validator.py（全キーワードが含まれる → coverage_rate=1.0）
- [x] T024 [P] [US2] 全未カバーテストを実装: tests/test_coverage_validator.py（キーワードが含まれない → coverage_rate=0.0）
- [x] T025 [P] [US2] エッジケーステストを実装: tests/test_coverage_validator.py（空キーワードリスト → coverage_rate=1.0、空 XML → coverage_rate=0.0）
- [x] T026 [P] [US2] 大文字小文字テストを実装: tests/test_coverage_validator.py（case-insensitive マッチング）
- [x] T027 [P] [US3] JSON 出力テストを実装: tests/test_coverage_validator.py（to_dict が正しいスキーマを返す）
- [x] T028 Verify: `make test` FAIL (RED)
- [x] T029 Edit: specs/071-keyword-coverage-validation/red-tests/ph3-test.md

### Implementation (GREEN)

- [x] T030 Read: specs/071-keyword-coverage-validation/red-tests/ph3-test.md
- [x] T031 [US2] CoverageResult dataclass を実装: src/coverage_validator.py（total_keywords, covered_keywords, coverage_rate, missing_keywords, to_dict）
- [x] T032 [US2] validate_coverage 関数を実装: src/coverage_validator.py（文字列マッチング、case-insensitive）
- [x] T033 Verify: `make test` PASS (GREEN)

### Verification

- [x] T034 Verify: `make test` で全テストパス（US1 含むリグレッションなし）
- [x] T035 Verify: `make coverage` ≥80%
- [x] T036 Edit: specs/071-keyword-coverage-validation/tasks/ph3-output.md

**Checkpoint**: キーワード抽出とカバー率検証が独立して動作することを確認

---

## Phase 4: Polish & Cross-Cutting Concerns — NO TDD

**Purpose**: 統合検証、コード品質、ドキュメント

### Input

- [x] T037 Read: specs/071-keyword-coverage-validation/tasks/ph1-output.md
- [x] T038 Read: specs/071-keyword-coverage-validation/tasks/ph3-output.md

### Implementation

- [x] T039 quickstart.md の使用例を実際に実行して検証
- [x] T040 [P] コード品質チェック: `make lint` でエラーなし
- [x] T041 [P] 型チェック: `make mypy` でエラーなし（または既存の除外設定に従う）

### Verification

- [x] T042 Verify: `make test` で全テストパス
- [x] T043 Edit: specs/071-keyword-coverage-validation/tasks/ph4-output.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: 依存なし - メインエージェント直接実行
- **Phase 2 (US1)**: Phase 1 完了後 - TDD フロー
- **Phase 3 (US2+US3)**: Phase 2 完了後 - TDD フロー
- **Phase 4 (Polish)**: Phase 3 完了後 - speckit:phase-executor のみ

### Agent Delegation

- **Phase 1**: メインエージェント直接実行
- **Phase 2-3**: speckit:tdd-generator (RED) → speckit:phase-executor (GREEN + Verification)
- **Phase 4**: speckit:phase-executor のみ

### [P] Marker

`[P]` は「他のタスクへの依存なし、実行順序自由」を示す。並列実行を保証するものではない。

---

## Phase Output & RED Test Artifacts

### Directory Structure

```
specs/071-keyword-coverage-validation/
├── tasks.md                    # このファイル
├── tasks/
│   ├── ph1-output.md           # Phase 1 出力（Setup 結果）
│   ├── ph2-output.md           # Phase 2 出力（US1 GREEN 結果）
│   ├── ph3-output.md           # Phase 3 出力（US2+US3 GREEN 結果）
│   └── ph4-output.md           # Phase 4 出力（Polish 結果）
└── red-tests/
    ├── ph2-test.md             # Phase 2 RED テスト結果
    └── ph3-test.md             # Phase 3 RED テスト結果
```

---

## Implementation Strategy

### MVP First (Phase 1 + Phase 2)

1. Phase 1 完了: Setup（既存コード確認）
2. Phase 2 完了: US1 キーワード抽出（RED → GREEN → Verification）
3. **STOP and VALIDATE**: `make test` で全テストパス確認
4. 必要に応じて手動テスト

### Full Delivery

1. Phase 1 → Phase 2 → Phase 3 → Phase 4
2. 各フェーズ完了時にコミット: `feat(phase-N): description`

---

## Notes

- US2 と US3 は Phase 3 で統合（CoverageResult.to_dict() が JSON 出力を担う）
- キーワード抽出は LLM 使用、カバー率検証は文字列マッチングのみ（LLM 不使用）
- 既存の prompt_loader.py パターンを再利用
- 各フェーズ完了後にコミット推奨
