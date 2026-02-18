# Tasks: チャプター分割とクリーニング

**Input**: Design documents from `/specs/005-chapter-split-cleaning/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: TDD is MANDATORY for User Story phases. Each phase follows テスト実装 (RED) → 実装 (GREEN) → 検証 workflow.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: No dependencies (different files, execution order free)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## User Story Summary

| ID | Title | Priority | FR | Scenario |
|----|-------|----------|----|----------|
| US1 | テキストクリーニングの適用 | P1 | FR-001,006,007,008 | clean_page_text() 適用 |
| US2 | チャプター単位の分割出力 | P2 | FR-002,003,004,009 | chapters/ 出力 |
| US3 | cleaned_text.txt の品質向上 | P3 | FR-005 | クリーニング済みテキスト出力 |

## Path Conventions

- **Project Type**: Single project (`src/`, `tests/` at repository root)
- **修正ファイル**: `src/xml2_parser.py`, `src/xml2_pipeline.py`
- **テストファイル**: `tests/test_xml2_parser.py`, `tests/test_xml2_pipeline.py`

---

## Phase 1: Setup (共有インフラ) — NO TDD

**Purpose**: 既存コード確認、変更準備

- [x] T001 Read current implementation in src/xml2_parser.py, src/xml2_pipeline.py
- [x] T002 [P] Read existing tests in tests/test_xml2_parser.py, tests/test_xml2_pipeline.py
- [x] T003 [P] Read text_cleaner in src/text_cleaner.py (clean_page_text function)
- [x] T004 Verify `make test` passes (no regression from existing tests)
- [x] T005 Edit and rename: specs/005-chapter-split-cleaning/tasks/ph1-output-template.md → ph1-output.md

---

## Phase 2: User Story 1 - テキストクリーニングの適用 (Priority: P1) MVP

**Goal**: xml2_pipeline で処理する全テキストに clean_page_text() を適用し、音声品質を向上

**Independent Test**: URL、括弧英語、ISBN を含む book2.xml を処理し、音声生成前にクリーニングが適用されることを確認

### 入力

- [x] T006 Read previous phase output: specs/005-chapter-split-cleaning/tasks/ph1-output.md

### テスト実装 (RED)

- [x] T007 [P] [US1] Implement test_process_content_applies_clean_page_text in tests/test_xml2_pipeline.py
- [x] T008 [P] [US1] Implement test_process_content_removes_url in tests/test_xml2_pipeline.py
- [x] T009 [P] [US1] Implement test_process_content_removes_parenthetical_english in tests/test_xml2_pipeline.py
- [x] T010 [P] [US1] Implement test_process_content_converts_numbers_to_kana in tests/test_xml2_pipeline.py
- [x] T011 Verify `make test` FAIL (RED)
- [x] T012 Generate RED output: specs/005-chapter-split-cleaning/red-tests/ph2-test.md

### 実装 (GREEN)

- [x] T013 Read RED tests: specs/005-chapter-split-cleaning/red-tests/ph2-test.md
- [x] T014 [US1] Update process_content() to call clean_page_text() in src/xml2_pipeline.py
- [x] T015 Verify `make test` PASS (GREEN)

### 検証

- [x] T016 Verify `make test` passes all tests (no regressions)
- [x] T017 Edit and rename: specs/005-chapter-split-cleaning/tasks/ph2-output-template.md → ph2-output.md

**Checkpoint**: US1 が独立して動作・テスト可能であること

---

## Phase 3: User Story 2 - チャプター単位の分割出力 (Priority: P2)

**Goal**: chapter 要素ごとに個別 WAV ファイルを出力し、全 chapter を結合した book.wav も生成

**Independent Test**: 複数 chapter を含む book2.xml を処理し、chapters/ に chapter 毎の WAV が出力されることを確認

### 入力

- [x] T018 Read setup analysis: specs/005-chapter-split-cleaning/tasks/ph1-output.md
- [x] T019 Read previous phase output: specs/005-chapter-split-cleaning/tasks/ph2-output.md

### テスト実装 (RED)

- [x] T020 [P] [US2] Implement test_content_item_has_chapter_number in tests/test_xml2_parser.py
- [x] T021 [P] [US2] Implement test_parse_book2_xml_assigns_chapter_numbers in tests/test_xml2_parser.py
- [x] T022 [P] [US2] Implement test_sanitize_filename in tests/test_xml2_pipeline.py
- [x] T023 [P] [US2] Implement test_process_chapters_creates_chapter_files in tests/test_xml2_pipeline.py
- [x] T024 [P] [US2] Implement test_process_chapters_creates_book_wav in tests/test_xml2_pipeline.py
- [x] T025 [P] [US2] Implement test_process_content_without_chapters_creates_book_wav in tests/test_xml2_pipeline.py
- [x] T026 Verify `make test` FAIL (RED)
- [x] T027 Generate RED output: specs/005-chapter-split-cleaning/red-tests/ph3-test.md

### 実装 (GREEN)

- [x] T028 Read RED tests: specs/005-chapter-split-cleaning/red-tests/ph3-test.md
- [x] T029 [P] [US2] Add chapter_number field to ContentItem dataclass in src/xml2_parser.py
- [x] T030 [US2] Update parse_book2_xml() to track and assign chapter_number in src/xml2_parser.py
- [x] T031 [P] [US2] Implement sanitize_filename() helper in src/xml2_pipeline.py
- [x] T032 [US2] Implement process_chapters() function in src/xml2_pipeline.py
- [x] T033 [US2] Update main() to call process_chapters() in src/xml2_pipeline.py
- [x] T034 Verify `make test` PASS (GREEN)

### 検証

- [x] T035 Verify `make test` passes all tests (including US1 regressions)
- [x] T036 Edit and rename: specs/005-chapter-split-cleaning/tasks/ph3-output-template.md → ph3-output.md

**Checkpoint**: US1 AND US2 が両方独立して動作すること

---

## Phase 4: User Story 3 - cleaned_text.txt の品質向上 (Priority: P3)

**Goal**: cleaned_text.txt に clean_page_text() 適用済みテキストを出力

**Independent Test**: book2.xml を処理し、cleaned_text.txt が URL 除去・カナ変換済みであることを確認

### 入力

- [x] T037 Read setup analysis: specs/005-chapter-split-cleaning/tasks/ph1-output.md
- [x] T038 Read previous phase output: specs/005-chapter-split-cleaning/tasks/ph3-output.md

### テスト実装 (RED)

- [x] T039 [P] [US3] Implement test_cleaned_text_file_contains_cleaned_content in tests/test_xml2_pipeline.py
- [x] T040 [P] [US3] Implement test_cleaned_text_file_has_chapter_markers in tests/test_xml2_pipeline.py
- [x] T041 Verify `make test` FAIL (RED)
- [x] T042 Generate RED output: specs/005-chapter-split-cleaning/red-tests/ph4-test.md

### 実装 (GREEN)

- [x] T043 Read RED tests: specs/005-chapter-split-cleaning/red-tests/ph4-test.md
- [x] T044 [US3] Update main() to write cleaned text to cleaned_text.txt in src/xml2_pipeline.py
- [x] T045 Verify `make test` PASS (GREEN)

### 検証

- [x] T046 Verify `make test` passes all tests (including US1, US2 regressions)
- [x] T047 Edit and rename: specs/005-chapter-split-cleaning/tasks/ph4-output-template.md → ph4-output.md

**Checkpoint**: 全 US (1, 2, 3) が動作し、E2E テスト可能であること

---

## Phase 5: Polish & Cross-Cutting Concerns — NO TDD

**Purpose**: ドキュメント、型ヒント、クリーンアップ

### 入力

- [x] T048 Read setup analysis: specs/005-chapter-split-cleaning/tasks/ph1-output.md
- [x] T049 Read previous phase output: specs/005-chapter-split-cleaning/tasks/ph4-output.md

### 実装

- [x] T050 [P] Add docstrings to new functions in src/xml2_pipeline.py (sanitize_filename, process_chapters)
- [x] T051 [P] Add type hints to new functions in src/xml2_parser.py and src/xml2_pipeline.py
- [x] T052 Run quickstart.md validation (manual test with sample/book2.xml)

### 検証

- [x] T053 Run `make test` to verify all tests pass after cleanup
- [x] T054 Edit and rename: specs/005-chapter-split-cleaning/tasks/ph5-output-template.md → ph5-output.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - Main agent direct execution
- **User Stories (Phase 2-4)**: TDD flow (tdd-generator → phase-executor)
  - Phase 2 (US1) → Phase 3 (US2) → Phase 4 (US3)
- **Polish (Phase 5)**: Depends on all user stories - phase-executor only

### Within Each User Story Phase (TDD Flow)

1. **入力**: Read setup analysis (ph1) + previous phase output
2. **テスト実装 (RED)**: Write tests FIRST → verify `make test` FAIL → generate RED output
3. **実装 (GREEN)**: Read RED tests → implement → verify `make test` PASS
4. **検証**: Confirm no regressions → generate phase output

### Agent Delegation

- **Phase 1 (Setup)**: Main agent direct execution
- **Phase 2-4 (User Stories)**: tdd-generator (RED) → phase-executor (GREEN + 検証)
- **Phase 5 (Polish)**: phase-executor only

### [P] Marker (No Dependencies)

`[P]` indicates "no dependencies on other tasks, execution order is flexible". Does not guarantee parallel execution.

---

## Phase Output & RED Test Artifacts

### Directory Structure

```
specs/005-chapter-split-cleaning/
├── tasks.md                    # This file
├── tasks/
│   ├── ph1-output.md           # Phase 1 output (Setup results)
│   ├── ph2-output.md           # Phase 2 output (US1 GREEN results)
│   ├── ph3-output.md           # Phase 3 output (US2 GREEN results)
│   ├── ph4-output.md           # Phase 4 output (US3 GREEN results)
│   └── ph5-output.md           # Phase 5 output (Polish results)
└── red-tests/
    ├── ph2-test.md             # Phase 2 RED test results
    ├── ph3-test.md             # Phase 3 RED test results
    └── ph4-test.md             # Phase 4 RED test results
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

1. Complete Phase 1: Setup (既存コード確認)
2. Complete Phase 2: User Story 1 (RED → GREEN → 検証)
3. **STOP and VALIDATE**: Confirm all tests pass with `make test`
4. Verify with: `make xml-tts INPUT=sample/book2.xml PARSER=xml2` でクリーニング適用確認

### Full Delivery

1. Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5
2. Each phase commits: `feat(phase-N): description`

---

## Test Coverage Rules

**Boundary Test Principle**: Write tests at **every boundary** where data transformation occurs

```
[book2.xml] → [parse_book2_xml] → [ContentItem list] → [clean_page_text] → [process_chapters] → [WAV files]
     ↓              ↓                    ↓                   ↓                    ↓              ↓
   Test           Test                 Test               Test                 Test           Test
```

**Checklist**:
- [ ] XML parsing with chapter_number tests
- [ ] clean_page_text application tests
- [ ] Chapter file generation tests
- [ ] cleaned_text.txt output tests
- [ ] End-to-End tests (input → final output)

---

## Notes

- [P] tasks = no dependencies, execution order free
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- TDD: テスト実装 (RED) → Verify FAIL → 実装 (GREEN) → Verify PASS
- RED output must be generated BEFORE implementation begins
- Commit after each phase completion
- Stop at any checkpoint to validate story independently
