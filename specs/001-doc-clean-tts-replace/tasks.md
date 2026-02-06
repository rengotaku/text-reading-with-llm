# Tasks: ドキュメントクリーン TTS代替置換機能

**Input**: Design documents from `/specs/001-doc-clean-tts-replace/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: TDD is MANDATORY for User Story phases. Each phase follows テスト実装 (RED) → 実装 (GREEN) → 検証 workflow.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: No dependencies (different files, execution order free)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## User Story Summary

| ID | Title | Priority | FR | Independent Test |
|----|-------|----------|----|------------------|
| US1 | URLの除去・簡略化 | P1 | FR-001,002,003 | URLを含むテキストを処理し、リンクテキストのみ残る/削除される |
| US2 | 図表参照の適切な読み上げ | P2 | FR-004,005 | 「図2.1」「表1.2」が読み仮名に変換される |
| US3 | 脚注・注釈番号の処理 | P3 | FR-006 | 「注1.6」が読み仮名に変換される |
| US4 | ISBN・書籍情報の簡略化 | P3 | FR-007 | ISBN番号が削除される |
| US5 | 括弧付き用語の重複読み防止 | P2 | FR-010 | 「トイル（Toil）」→「トイル」 |
| US6 | 不適切な読点挿入の修正 | P2 | FR-011 | 「ではありません」に読点が入らない |
| US7 | コロン記号の自然な読み上げ変換 | P2 | FR-012 | 「目的：」→「目的は、」 |
| US8 | 鉤括弧の読点変換 | P2 | FR-013 | 「」→読点に変換 |

## Path Conventions

- **Source**: `src/` at repository root
- **Tests**: `tests/` at repository root
- **Feature docs**: `specs/001-doc-clean-tts-replace/`

---

## Phase 1: Setup (Shared Infrastructure) — NO TDD

**Purpose**: Project initialization, existing code review, and change preparation

- [ ] T001 Read current implementation in src/text_cleaner.py
- [ ] T002 [P] Read current implementation in src/punctuation_normalizer.py
- [ ] T003 [P] Read existing tests in tests/ directory (if any)
- [ ] T004 Verify pytest environment with `make test`
- [ ] T005 Generate phase output: specs/001-doc-clean-tts-replace/tasks/ph1-output.md

---

## Phase 2: User Story 1 - URLの除去・簡略化 (Priority: P1) MVP

**Goal**: Markdownリンク/裸URLを適切に処理し、TTSで意味のあるテキストのみ残す

**Independent Test**: `_clean_urls()` 関数単体でURL処理が正しく動作することを確認

### 入力

- [ ] T006 Read previous phase output: specs/001-doc-clean-tts-replace/tasks/ph1-output.md

### テスト実装 (RED)

- [ ] T007 [P] [US1] Implement test_clean_urls_markdown_link in tests/test_url_cleaning.py
- [ ] T008 [P] [US1] Implement test_clean_urls_url_as_link_text in tests/test_url_cleaning.py
- [ ] T009 [P] [US1] Implement test_clean_urls_bare_url in tests/test_url_cleaning.py
- [ ] T010 [P] [US1] Implement test_clean_urls_multiple_urls in tests/test_url_cleaning.py
- [ ] T011 [P] [US1] Implement test_clean_urls_idempotent in tests/test_url_cleaning.py
- [ ] T012 Verify `make test` FAIL (RED)
- [ ] T013 Generate RED output: specs/001-doc-clean-tts-replace/red-tests/ph2-test.md

### 実装 (GREEN)

- [ ] T014 Read RED tests: specs/001-doc-clean-tts-replace/red-tests/ph2-test.md
- [ ] T015 [US1] Add URL pattern constants at top of src/text_cleaner.py
- [ ] T016 [US1] Implement _clean_urls() function in src/text_cleaner.py
- [ ] T017 Verify `make test` PASS (GREEN)

### 検証

- [ ] T018 Verify `make test` passes all tests (no regressions)
- [ ] T019 Generate phase output: specs/001-doc-clean-tts-replace/tasks/ph2-output.md

**Checkpoint**: URL処理が単体で動作し、テスト通過を確認

---

## Phase 3: User Story 2/3 - 図表・注釈参照の読み上げ (Priority: P2/P3)

**Goal**: 図表参照(図X.Y, 表X.Y)と脚注参照(注X.Y)を自然な読み仮名に変換

**Independent Test**: `_normalize_references()` 関数単体で参照変換が正しく動作することを確認

### 入力

- [ ] T020 Read previous phase output: specs/001-doc-clean-tts-replace/tasks/ph2-output.md

### テスト実装 (RED)

- [ ] T021 [P] [US2] Implement test_normalize_figure_reference in tests/test_reference_normalization.py
- [ ] T022 [P] [US2] Implement test_normalize_table_reference in tests/test_reference_normalization.py
- [ ] T023 [P] [US3] Implement test_normalize_note_reference in tests/test_reference_normalization.py
- [ ] T024 [P] [US2] Implement test_normalize_references_mixed in tests/test_reference_normalization.py
- [ ] T025 Verify `make test` FAIL (RED)
- [ ] T026 Generate RED output: specs/001-doc-clean-tts-replace/red-tests/ph3-test.md

### 実装 (GREEN)

- [ ] T027 Read RED tests: specs/001-doc-clean-tts-replace/red-tests/ph3-test.md
- [ ] T028 [US2] Add DIGIT_READINGS constant in src/text_cleaner.py
- [ ] T029 [US2] Add reference pattern constants in src/text_cleaner.py
- [ ] T030 [US2] Implement _normalize_references() function in src/text_cleaner.py
- [ ] T031 Verify `make test` PASS (GREEN)

### 検証

- [ ] T032 Verify `make test` passes all tests (including US1 regressions)
- [ ] T033 Generate phase output: specs/001-doc-clean-tts-replace/tasks/ph3-output.md

**Checkpoint**: URL処理 + 参照正規化が両方動作することを確認

---

## Phase 4: User Story 4 - ISBN・書籍情報の簡略化 (Priority: P3)

**Goal**: ISBN番号を検出して削除

**Independent Test**: `_clean_isbn()` 関数単体でISBN削除が正しく動作することを確認

### 入力

- [ ] T034 Read previous phase output: specs/001-doc-clean-tts-replace/tasks/ph3-output.md

### テスト実装 (RED)

- [ ] T035 [P] [US4] Implement test_clean_isbn_with_hyphens in tests/test_isbn_cleaning.py
- [ ] T036 [P] [US4] Implement test_clean_isbn_with_space in tests/test_isbn_cleaning.py
- [ ] T037 [P] [US4] Implement test_clean_isbn_in_sentence in tests/test_isbn_cleaning.py
- [ ] T038 Verify `make test` FAIL (RED)
- [ ] T039 Generate RED output: specs/001-doc-clean-tts-replace/red-tests/ph4-test.md

### 実装 (GREEN)

- [ ] T040 Read RED tests: specs/001-doc-clean-tts-replace/red-tests/ph4-test.md
- [ ] T041 [US4] Add ISBN_PATTERN constant in src/text_cleaner.py
- [ ] T042 [US4] Implement _clean_isbn() function in src/text_cleaner.py
- [ ] T043 Verify `make test` PASS (GREEN)

### 検証

- [ ] T044 Verify `make test` passes all tests (including US1-3 regressions)
- [ ] T045 Generate phase output: specs/001-doc-clean-tts-replace/tasks/ph4-output.md

**Checkpoint**: URL + 参照 + ISBN処理が動作することを確認

---

## Phase 5: User Story 5 - 括弧付き用語の重複読み防止 (Priority: P2)

**Goal**: 「トイル（Toil）」形式から括弧と英語表記を除去

**Independent Test**: `_clean_parenthetical_english()` 関数単体で括弧除去が正しく動作することを確認

### 入力

- [ ] T046 Read previous phase output: specs/001-doc-clean-tts-replace/tasks/ph4-output.md

### テスト実装 (RED)

- [ ] T047 [P] [US5] Implement test_clean_parenthetical_english_full_width in tests/test_parenthetical_cleaning.py
- [ ] T048 [P] [US5] Implement test_clean_parenthetical_english_half_width in tests/test_parenthetical_cleaning.py
- [ ] T049 [P] [US5] Implement test_clean_parenthetical_preserve_japanese in tests/test_parenthetical_cleaning.py
- [ ] T050 [P] [US5] Implement test_clean_parenthetical_alphabet_term in tests/test_parenthetical_cleaning.py
- [ ] T051 Verify `make test` FAIL (RED)
- [ ] T052 Generate RED output: specs/001-doc-clean-tts-replace/red-tests/ph5-test.md

### 実装 (GREEN)

- [ ] T053 Read RED tests: specs/001-doc-clean-tts-replace/red-tests/ph5-test.md
- [ ] T054 [US5] Add parenthetical pattern constants in src/text_cleaner.py
- [ ] T055 [US5] Implement _clean_parenthetical_english() function in src/text_cleaner.py
- [ ] T056 Verify `make test` PASS (GREEN)

### 検証

- [ ] T057 Verify `make test` passes all tests (including US1-4 regressions)
- [ ] T058 Generate phase output: specs/001-doc-clean-tts-replace/tasks/ph5-output.md

**Checkpoint**: text_cleaner.py の新規関数がすべて動作することを確認

---

## Phase 6: User Story 6 - 不適切な読点挿入の修正 (Priority: P2)

**Goal**: 「ではありません」等のパターンで「は」の後に読点を挿入しない

**Independent Test**: `_normalize_line()` 関数で除外パターンが正しく動作することを確認

### 入力

- [ ] T059 Read previous phase output: specs/001-doc-clean-tts-replace/tasks/ph5-output.md

### テスト実装 (RED)

- [ ] T060 [P] [US6] Implement test_normalize_line_deha_arimasen in tests/test_punctuation_rules.py
- [ ] T061 [P] [US6] Implement test_normalize_line_deha_nai in tests/test_punctuation_rules.py
- [ ] T062 [P] [US6] Implement test_normalize_line_mixed_ha_patterns in tests/test_punctuation_rules.py
- [ ] T063 [P] [US6] Implement test_normalize_line_niha_naranai in tests/test_punctuation_rules.py
- [ ] T064 Verify `make test` FAIL (RED)
- [ ] T065 Generate RED output: specs/001-doc-clean-tts-replace/red-tests/ph6-test.md

### 実装 (GREEN)

- [ ] T066 Read RED tests: specs/001-doc-clean-tts-replace/red-tests/ph6-test.md
- [ ] T067 [US6] Add EXCLUSION_SUFFIXES constant in src/punctuation_normalizer.py
- [ ] T068 [US6] Modify _normalize_line() Rule 4 with negative lookahead in src/punctuation_normalizer.py
- [ ] T069 Verify `make test` PASS (GREEN)

### 検証

- [ ] T070 Verify `make test` passes all tests (including US1-5 regressions)
- [ ] T071 Generate phase output: specs/001-doc-clean-tts-replace/tasks/ph6-output.md

**Checkpoint**: 読点除外パターンが正しく動作することを確認

---

## Phase 7: User Story 7 - コロン記号の自然な読み上げ変換 (Priority: P2)

**Goal**: コロン（：/:）を「は、」に変換（時刻・比率は除外）

**Independent Test**: `_normalize_colons()` 関数単体でコロン変換が正しく動作することを確認

### 入力

- [ ] T072 Read previous phase output: specs/001-doc-clean-tts-replace/tasks/ph6-output.md

### テスト実装 (RED)

- [ ] T073 [P] [US7] Implement test_normalize_colons_full_width in tests/test_punctuation_rules.py
- [ ] T074 [P] [US7] Implement test_normalize_colons_half_width in tests/test_punctuation_rules.py
- [ ] T075 [P] [US7] Implement test_normalize_colons_exclude_time in tests/test_punctuation_rules.py
- [ ] T076 [P] [US7] Implement test_normalize_colons_exclude_ratio in tests/test_punctuation_rules.py
- [ ] T077 Verify `make test` FAIL (RED)
- [ ] T078 Generate RED output: specs/001-doc-clean-tts-replace/red-tests/ph7-test.md

### 実装 (GREEN)

- [ ] T079 Read RED tests: specs/001-doc-clean-tts-replace/red-tests/ph7-test.md
- [ ] T080 [US7] Add colon pattern constants in src/punctuation_normalizer.py
- [ ] T081 [US7] Implement _normalize_colons() function in src/punctuation_normalizer.py
- [ ] T082 Verify `make test` PASS (GREEN)

### 検証

- [ ] T083 Verify `make test` passes all tests (including US1-6 regressions)
- [ ] T084 Generate phase output: specs/001-doc-clean-tts-replace/tasks/ph7-output.md

**Checkpoint**: コロン変換が正しく動作することを確認

---

## Phase 8: User Story 8 - 鉤括弧の読点変換 (Priority: P2)

**Goal**: 鉤括弧「」を読点（、）に変換

**Independent Test**: `_normalize_brackets()` 関数単体で鉤括弧変換が正しく動作することを確認

### 入力

- [ ] T085 Read previous phase output: specs/001-doc-clean-tts-replace/tasks/ph7-output.md

### テスト実装 (RED)

- [ ] T086 [P] [US8] Implement test_normalize_brackets_basic in tests/test_punctuation_rules.py
- [ ] T087 [P] [US8] Implement test_normalize_brackets_with_text in tests/test_punctuation_rules.py
- [ ] T088 [P] [US8] Implement test_normalize_brackets_consecutive in tests/test_punctuation_rules.py
- [ ] T089 Verify `make test` FAIL (RED)
- [ ] T090 Generate RED output: specs/001-doc-clean-tts-replace/red-tests/ph8-test.md

### 実装 (GREEN)

- [ ] T091 Read RED tests: specs/001-doc-clean-tts-replace/red-tests/ph8-test.md
- [ ] T092 [US8] Implement _normalize_brackets() function in src/punctuation_normalizer.py
- [ ] T093 Verify `make test` PASS (GREEN)

### 検証

- [ ] T094 Verify `make test` passes all tests (including US1-7 regressions)
- [ ] T095 Generate phase output: specs/001-doc-clean-tts-replace/tasks/ph8-output.md

**Checkpoint**: punctuation_normalizer.py の新規関数がすべて動作することを確認

---

## Phase 9: パイプライン統合 (FR-008, FR-009)

**Goal**: 全ての新規関数を clean_page_text() と normalize_punctuation() に統合

**Independent Test**: 統合テストで全変換が正しい順序で適用されることを確認

### 入力

- [ ] T096 Read previous phase output: specs/001-doc-clean-tts-replace/tasks/ph8-output.md

### テスト実装 (RED)

- [ ] T097 [P] Implement test_clean_page_text_integration in tests/test_integration.py
- [ ] T098 [P] Implement test_clean_page_text_processing_order in tests/test_integration.py
- [ ] T099 [P] Implement test_clean_page_text_idempotent in tests/test_integration.py
- [ ] T100 [P] Implement test_normalize_punctuation_integration in tests/test_integration.py
- [ ] T101 Verify `make test` FAIL (RED)
- [ ] T102 Generate RED output: specs/001-doc-clean-tts-replace/red-tests/ph9-test.md

### 実装 (GREEN)

- [ ] T103 Read RED tests: specs/001-doc-clean-tts-replace/red-tests/ph9-test.md
- [ ] T104 Modify clean_page_text() to call new functions in src/text_cleaner.py
- [ ] T105 Modify normalize_punctuation() to call new functions in src/punctuation_normalizer.py
- [ ] T106 Verify `make test` PASS (GREEN)

### 検証

- [ ] T107 Verify `make test` passes all tests (全機能統合確認)
- [ ] T108 Generate phase output: specs/001-doc-clean-tts-replace/tasks/ph9-output.md

**Checkpoint**: 全機能が統合され、パイプラインが正しく動作することを確認

---

## Phase 10: Polish & Cross-Cutting Concerns — NO TDD

**Purpose**: パフォーマンス検証、コード品質向上、最終確認

### 入力

- [ ] T109 Read previous phase output: specs/001-doc-clean-tts-replace/tasks/ph9-output.md

### 実装

- [ ] T110 [P] Compile regex patterns at module level for performance in src/text_cleaner.py
- [ ] T111 [P] Compile regex patterns at module level for performance in src/punctuation_normalizer.py
- [ ] T112 Run performance benchmark with sample/book.md
- [ ] T113 Verify processing time increase ≤10% (SC-006)
- [ ] T114 Run quickstart.md validation scenarios

### 検証

- [ ] T115 Run `make test` to verify all tests pass after cleanup
- [ ] T116 Generate phase output: specs/001-doc-clean-tts-replace/tasks/ph10-output.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - メインエージェント直接実行
- **User Stories (Phase 2-9)**: TDD フロー (tdd-generator → phase-executor)
  - User stories proceed sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 10)**: Depends on all user stories - phase-executor のみ

### Within Each User Story Phase (TDD Flow)

1. **入力**: Read previous phase output (context from prior work)
2. **テスト実装 (RED)**: Write tests FIRST → verify `make test` FAIL → generate RED output
3. **実装 (GREEN)**: Read RED tests → implement → verify `make test` PASS
4. **検証**: Confirm no regressions → generate phase output

### Agent Delegation

- **Phase 1 (Setup)**: メインエージェント直接実行
- **Phase 2-9 (User Stories)**: tdd-generator (RED) → phase-executor (GREEN + 検証)
- **Phase 10 (Polish)**: phase-executor のみ

### [P] マーク（依存関係なし）

`[P]` は「他タスクとの依存関係がなく、実行順序が自由」であることを示す。並列実行を保証するものではない。

- Setup タスクの [P]: 異なるファイル・ディレクトリの読み込みで相互依存なし
- RED テストの [P]: 異なるテスト関数への書き込みで相互依存なし
- GREEN 実装の [P]: 異なる関数への書き込みで相互依存なし
- User Story 間: 各 Phase は前 Phase の出力に依存するため [P] 不可

---

## Phase Output & RED Test Artifacts

### Directory Structure

```
specs/001-doc-clean-tts-replace/
├── tasks.md                    # This file
├── tasks/
│   ├── ph1-output.md           # Phase 1 output (Setup results)
│   ├── ph2-output.md           # Phase 2 output (US1 GREEN results)
│   ├── ph3-output.md           # Phase 3 output (US2/3 GREEN results)
│   ├── ph4-output.md           # Phase 4 output (US4 GREEN results)
│   ├── ph5-output.md           # Phase 5 output (US5 GREEN results)
│   ├── ph6-output.md           # Phase 6 output (US6 GREEN results)
│   ├── ph7-output.md           # Phase 7 output (US7 GREEN results)
│   ├── ph8-output.md           # Phase 8 output (US8 GREEN results)
│   ├── ph9-output.md           # Phase 9 output (Integration GREEN results)
│   └── ph10-output.md          # Phase 10 output (Polish results)
└── red-tests/
    ├── ph2-test.md             # Phase 2 RED test results
    ├── ph3-test.md             # Phase 3 RED test results
    ├── ph4-test.md             # Phase 4 RED test results
    ├── ph5-test.md             # Phase 5 RED test results
    ├── ph6-test.md             # Phase 6 RED test results
    ├── ph7-test.md             # Phase 7 RED test results
    ├── ph8-test.md             # Phase 8 RED test results
    └── ph9-test.md             # Phase 9 RED test results
```

---

## Implementation Strategy

### MVP First (Phase 1 + Phase 2)

1. Complete Phase 1: Setup (existing code review)
2. Complete Phase 2: User Story 1 - URL処理 (RED → GREEN → 検証)
3. **STOP and VALIDATE**: `make test` で全テスト通過を確認
4. sample/book.md で手動確認: URLが正しく処理されることを確認

### Full Delivery

1. Phase 1 → Phase 2 → Phase 3 → ... → Phase 10
2. Each phase commits: `feat(phase-N): description`

---

## Test Coverage Rules

**境界テストの原則**: データ変換が発生する**すべての境界**でテストを書く

```
[入力] → [URL処理] → [ISBN処理] → [括弧処理] → [参照正規化] → [句読点正規化] → [出力]
   ↓        ↓           ↓           ↓            ↓               ↓            ↓
 テスト   テスト      テスト      テスト       テスト          テスト       テスト
```

**チェックリスト**:
- [ ] URL処理のテスト (tests/test_url_cleaning.py)
- [ ] 参照正規化のテスト (tests/test_reference_normalization.py)
- [ ] ISBN処理のテスト (tests/test_isbn_cleaning.py)
- [ ] 括弧処理のテスト (tests/test_parenthetical_cleaning.py)
- [ ] 句読点ルールのテスト (tests/test_punctuation_rules.py)
- [ ] 統合テスト (tests/test_integration.py)

---

## Notes

- [P] tasks = no dependencies, execution order free
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- TDD: テスト実装 (RED) → FAIL 確認 → 実装 (GREEN) → PASS 確認
- RED output must be generated BEFORE implementation begins
- Commit after each phase completion
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
