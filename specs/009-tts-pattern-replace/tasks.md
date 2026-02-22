# タスク: TTS前処理パターン置換

**Input**: `/specs/009-tts-pattern-replace/` の設計ドキュメント
**Prerequisites**: plan.md (完了), spec.md (完了), research.md (完了), quickstart.md (完了)

**Tests**: TDD は User Story フェーズで必須。各フェーズは Test Implementation (RED) → Implementation (GREEN) → Verification のワークフローに従う。

**Organization**: タスクは User Story ごとにグループ化し、各ストーリーの独立した実装・テストを可能にする。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 依存関係なし（異なるファイル、実行順序自由）
- **[Story]**: タスクが属する User Story（例: US1, US2, US3）
- 説明には正確なファイルパスを含める

## User Story Summary

| ID | Title | Priority | FR | Scenario |
|----|-------|----------|----|----------|
| US1 | URL含有テキストの自然な読み上げ | P1 | FR-001,002,003 | 裸URL→「ウェブサイト」、Markdownリンク保持 |
| US2 | 番号表記の自然な読み上げ | P2 | FR-004,005 | No.X→「ナンバーX」、Chapter X→「だいXしょう」 |
| US3 | ISBN・書籍メタ情報の適切な処理 | P3 | FR-006,007,008 | ISBN削除、括弧・ラベル削除、空白正規化 |

## Path Conventions

- **Source**: `src/text_cleaner.py`
- **Tests**: `tests/test_*.py`
- **Feature Dir**: `specs/009-tts-pattern-replace/`

---

## Phase 1: Setup (既存コード確認) — NO TDD

**Purpose**: 既存実装の確認と変更準備

- [X] T001 Read current implementation in src/text_cleaner.py
- [X] T002 [P] Read existing URL tests in tests/test_url_cleaning.py
- [X] T003 [P] Read existing ISBN tests in tests/test_isbn_cleaning.py
- [X] T004 [P] Read number normalizer in src/number_normalizer.py
- [X] T005 Run `make test` to verify current test status
- [X] T006 Generate setup output: specs/009-tts-pattern-replace/tasks/ph1-output.md

---

## Phase 2: User Story 1 - URL含有テキストの自然な読み上げ (Priority: P1) MVP

**Goal**: 裸のURLを「ウェブサイト」に置換し、Markdownリンクのリンクテキストを保持する

**Independent Test**: URLを含むテキストをTTS処理し、「ダブリュー」「ドット」などのURL構成要素が含まれないことを確認

### Input

- [ ] T007 Read previous phase output: specs/009-tts-pattern-replace/tasks/ph1-output.md

### Test Implementation (RED)

- [ ] T008 [P] [US1] Update test for bare URL replacement in tests/test_url_cleaning.py (期待値: "" → "ウェブサイト")
- [ ] T009 [P] [US1] Add test for URL-as-link-text replacement in tests/test_url_cleaning.py (期待値: "" → "ウェブサイト")
- [ ] T010 [P] [US1] Add test for multiple consecutive URLs in tests/test_url_cleaning.py
- [ ] T011 [P] [US1] Add test for URL with trailing punctuation in tests/test_url_cleaning.py
- [ ] T012 Verify `make test` FAIL (RED) - 変更したテストが失敗することを確認
- [ ] T013 Generate RED output: specs/009-tts-pattern-replace/red-tests/ph2-test.md

### Implementation (GREEN)

- [ ] T014 Read RED tests: specs/009-tts-pattern-replace/red-tests/ph2-test.md
- [ ] T015 [US1] Modify `_clean_urls()` in src/text_cleaner.py: BARE_URL_PATTERN.sub("ウェブサイト", text)
- [ ] T016 [US1] Modify `_clean_urls()` in src/text_cleaner.py: URL-as-link-text → "ウェブサイト"
- [ ] T017 Verify `make test` PASS (GREEN)

### Verification

- [ ] T018 Verify `make test` passes all tests (回帰なし)
- [ ] T019 Generate phase output: specs/009-tts-pattern-replace/tasks/ph2-output.md

**Checkpoint**: US1 が独立して機能し、テスト可能であること

---

## Phase 3: User Story 2 - 番号表記の自然な読み上げ (Priority: P2)

**Goal**: `No.X` を「ナンバーX」に、`Chapter X` を「だいXしょう」に変換する

**Independent Test**: `No.X` 形式を含むテキストをTTS処理し、「ナンバー」+数字読みとして出力されることを確認

### Input

- [ ] T020 Read setup analysis: specs/009-tts-pattern-replace/tasks/ph1-output.md
- [ ] T021 Read previous phase output: specs/009-tts-pattern-replace/tasks/ph2-output.md

### Test Implementation (RED)

- [ ] T022 [P] [US2] Create test file tests/test_number_prefix.py with basic No.X tests
- [ ] T023 [P] [US2] Add case-insensitive test (no., NO., No.) in tests/test_number_prefix.py
- [ ] T024 [P] [US2] Add test for No. without number (置換しない) in tests/test_number_prefix.py
- [ ] T025 [P] [US2] Create test file tests/test_chapter_conversion.py with basic Chapter X tests
- [ ] T026 [P] [US2] Add case-insensitive test (chapter, CHAPTER) in tests/test_chapter_conversion.py
- [ ] T027 Verify `make test` FAIL (RED) - 新規テストが失敗することを確認
- [ ] T028 Generate RED output: specs/009-tts-pattern-replace/red-tests/ph3-test.md

### Implementation (GREEN)

- [ ] T029 Read RED tests: specs/009-tts-pattern-replace/red-tests/ph3-test.md
- [ ] T030 [P] [US2] Add NUMBER_PREFIX_PATTERN constant in src/text_cleaner.py
- [ ] T031 [P] [US2] Add CHAPTER_PATTERN constant in src/text_cleaner.py
- [ ] T032 [US2] Add `_clean_number_prefix()` function in src/text_cleaner.py
- [ ] T033 [US2] Add `_clean_chapter()` function in src/text_cleaner.py
- [ ] T034 [US2] Integrate new functions into `clean_page_text()` in src/text_cleaner.py
- [ ] T035 Verify `make test` PASS (GREEN)

### Verification

- [ ] T036 Verify `make test` passes all tests (US1 回帰含む)
- [ ] T037 Generate phase output: specs/009-tts-pattern-replace/tasks/ph3-output.md

**Checkpoint**: US1 および US2 が独立して機能すること

---

## Phase 4: User Story 3 - ISBN・書籍メタ情報の適切な処理 (Priority: P3)

**Goal**: ISBN削除後の括弧・ラベル削除と空白正規化を実装する

**Independent Test**: `（ISBN: 978-...）` 形式を含むテキストをTTS処理し、括弧ごと削除されることを確認

### Input

- [ ] T038 Read setup analysis: specs/009-tts-pattern-replace/tasks/ph1-output.md
- [ ] T039 Read previous phase output: specs/009-tts-pattern-replace/tasks/ph3-output.md

### Test Implementation (RED)

- [ ] T040 [P] [US3] Add test for parenthetical ISBN removal in tests/test_isbn_cleaning.py: 「この本（ISBN: 978-...）は」→「この本は」
- [ ] T041 [P] [US3] Add test for ISBN with label removal in tests/test_isbn_cleaning.py: 「ISBN: 978-...」→「」
- [ ] T042 [P] [US3] Add test for space normalization after ISBN removal in tests/test_isbn_cleaning.py
- [ ] T043 Verify `make test` FAIL (RED) - 新規テストが失敗することを確認
- [ ] T044 Generate RED output: specs/009-tts-pattern-replace/red-tests/ph4-test.md

### Implementation (GREEN)

- [ ] T045 Read RED tests: specs/009-tts-pattern-replace/red-tests/ph4-test.md
- [ ] T046 [P] [US3] Add ISBN_WITH_CONTEXT_PATTERN constant in src/text_cleaner.py
- [ ] T047 [US3] Enhance `_clean_isbn()` function in src/text_cleaner.py: 括弧・ラベル対応
- [ ] T048 [US3] Add space normalization after ISBN removal in src/text_cleaner.py
- [ ] T049 Verify `make test` PASS (GREEN)

### Verification

- [ ] T050 Verify `make test` passes all tests (US1, US2 回帰含む)
- [ ] T051 Generate phase output: specs/009-tts-pattern-replace/tasks/ph4-output.md

**Checkpoint**: US1, US2, US3 がすべて独立して機能すること

---

## Phase 5: Polish & Cross-Cutting Concerns — NO TDD

**Purpose**: 統合テストと最終検証

### Input

- [ ] T052 Read setup analysis: specs/009-tts-pattern-replace/tasks/ph1-output.md
- [ ] T053 Read previous phase output: specs/009-tts-pattern-replace/tasks/ph4-output.md

### Implementation

- [ ] T054 [P] Add integration test for combined patterns in tests/test_integration.py
- [ ] T055 [P] Verify edge cases from spec.md are covered
- [ ] T056 Run quickstart.md validation checklist
- [ ] T057 Code cleanup: remove any debug code, verify docstrings

### Verification

- [ ] T058 Run `make test` to verify all tests pass
- [ ] T059 Run `make coverage` to verify ≥80% coverage
- [ ] T060 Generate phase output: specs/009-tts-pattern-replace/tasks/ph5-output.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: 依存なし - Main agent 直接実行
- **Phase 2 (US1)**: Phase 1 完了後 - TDD flow (tdd-generator → phase-executor)
- **Phase 3 (US2)**: Phase 2 完了後 - TDD flow (tdd-generator → phase-executor)
- **Phase 4 (US3)**: Phase 3 完了後 - TDD flow (tdd-generator → phase-executor)
- **Phase 5 (Polish)**: Phase 4 完了後 - phase-executor のみ

### Within Each User Story Phase (TDD Flow)

1. **Input**: Setup analysis (ph1) + 前フェーズ output を読み込み
2. **Test Implementation (RED)**: テストを先に書く → `make test` FAIL 確認 → RED output 生成
3. **Implementation (GREEN)**: RED tests を読む → 実装 → `make test` PASS 確認
4. **Verification**: 回帰なし確認 → phase output 生成

### Agent Delegation

- **Phase 1 (Setup)**: Main agent 直接実行
- **Phase 2-4 (User Stories)**: tdd-generator (RED) → phase-executor (GREEN + Verification)
- **Phase 5 (Polish)**: phase-executor のみ

### [P] Marker (依存なし)

`[P]` は「他タスクへの依存なし、実行順序自由」を示す。並列実行を保証するものではない。

---

## Phase Output & RED Test Artifacts

### Directory Structure

```
specs/009-tts-pattern-replace/
├── tasks.md                    # このファイル
├── tasks/
│   ├── ph1-output.md           # Phase 1 output (Setup 結果)
│   ├── ph2-output.md           # Phase 2 output (US1 GREEN 結果)
│   ├── ph3-output.md           # Phase 3 output (US2 GREEN 結果)
│   ├── ph4-output.md           # Phase 4 output (US3 GREEN 結果)
│   └── ph5-output.md           # Phase 5 output (Polish 結果)
└── red-tests/
    ├── ph2-test.md             # Phase 2 RED test 結果 (FAIL 確認)
    ├── ph3-test.md             # Phase 3 RED test 結果 (FAIL 確認)
    └── ph4-test.md             # Phase 4 RED test 結果 (FAIL 確認)
```

### Phase Output Format

| Output Type | Template File |
|-------------|---------------|
| `ph1-output.md` | `.specify/templates/ph1-output-template.md` |
| `phN-output.md` | `.specify/templates/phN-output-template.md` |
| `phN-test.md` | `.specify/templates/red-test-template.md` |

---

## Implementation Strategy

### MVP First (Phase 1 + Phase 2)

1. Phase 1 完了: Setup (既存コード確認)
2. Phase 2 完了: User Story 1 (RED → GREEN → Verification)
3. **STOP and VALIDATE**: `make test` で全テスト通過を確認
4. 必要に応じて手動テスト実施

### Full Delivery

1. Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5
2. 各フェーズでコミット: `feat(phase-N): description`

---

## Test Coverage Rules

**Boundary Test Principle**: データ変換が発生するすべての境界でテストを書く

```
[Input] → [Pattern Match] → [Replace/Remove] → [Normalize] → [Output]
   ↓           ↓                ↓                 ↓            ↓
 Test        Test              Test              Test         Test
```

**Checklist**:
- [ ] パターンマッチテスト（URL, No.X, Chapter, ISBN）
- [ ] 置換/削除ロジックテスト
- [ ] 空白正規化テスト
- [ ] End-to-End テスト（clean_page_text 経由）

---

## Notes

- [P] タスク = 依存なし、実行順序自由
- [Story] ラベル = 特定の User Story へのマッピング（トレーサビリティ確保）
- 各 User Story は独立して完了・テスト可能であること
- TDD: Test Implementation (RED) → Verify FAIL → Implementation (GREEN) → Verify PASS
- RED output は実装開始前に生成必須
- 各フェーズ完了後にコミット
- チェックポイントで各ストーリーの独立検証可能
- 避けるべきこと: 曖昧なタスク、同一ファイル競合、ストーリー間の独立性を損なう依存
