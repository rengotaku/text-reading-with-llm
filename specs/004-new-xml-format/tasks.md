# Tasks: 新XMLフォーマット対応

**Input**: Design documents from `/specs/004-new-xml-format/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: TDD is MANDATORY for User Story phases. Each phase follows テスト実装 (RED) → 実装 (GREEN) → 検証 workflow.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: No dependencies (different files, execution order free)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## User Story Summary

| ID | Title | Priority | FR | Scenario |
|----|-------|----------|----|----------|
| US1 | 新XMLフォーマットの基本パース | P1 | FR-001,003,004,005 | book2.xml パース、toc/front-matter スキップ |
| US2 | 見出し速度調整 | P2 | FR-002,007,008,009 | chapter/section 効果音、見出し形式 |

## Path Conventions

- **Project Type**: Single project (`src/`, `tests/` at repository root)
- **新規ファイル**: `src/xml2_parser.py`, `src/xml2_pipeline.py`
- **テストファイル**: `tests/test_xml2_parser.py`, `tests/test_xml2_pipeline.py`
- **フィクスチャ**: `tests/fixtures/sample_book2.xml`

---

## Phase 1: Setup (共有インフラ) — NO TDD

**Purpose**: プロジェクト初期化、既存コード確認、変更準備

- [X] T001 Read current implementation in src/xml_parser.py, src/xml_pipeline.py
- [X] T002 [P] Read existing tests in tests/test_xml_parser.py, tests/test_xml_pipeline.py
- [X] T003 [P] Read sample XML: sample/book2.xml (first 200 lines)
- [X] T004 [P] Create test fixture: tests/fixtures/sample_book2.xml (minimal book2.xml format)
- [X] T005 Verify `make test` passes (no regression from existing tests)
- [X] T006 Edit and rename: specs/004-new-xml-format/tasks/ph1-output-template.md → ph1-output.md

---

## Phase 2: User Story 1 - 新XMLフォーマットの基本パース (Priority: P1) MVP

**Goal**: book2.xml フォーマットをパースし、toc/front-matter をスキップしてコンテンツを抽出

**Independent Test**: `parse_book2_xml()` で paragraph/list_item が抽出されること

### 入力

- [x] T007 Read previous phase output: specs/004-new-xml-format/tasks/ph1-output.md

### テスト実装 (RED)

- [x] T008 [P] [US1] Implement test_parse_book2_xml_returns_list in tests/test_xml2_parser.py
- [x] T009 [P] [US1] Implement test_parse_book2_xml_skips_toc in tests/test_xml2_parser.py
- [x] T010 [P] [US1] Implement test_parse_book2_xml_skips_front_matter in tests/test_xml2_parser.py
- [x] T011 [P] [US1] Implement test_parse_book2_xml_extracts_paragraphs in tests/test_xml2_parser.py
- [x] T012 [P] [US1] Implement test_parse_book2_xml_respects_read_aloud_false in tests/test_xml2_parser.py
- [x] T013 [P] [US1] Implement test_parse_book2_xml_extracts_list_items in tests/test_xml2_parser.py
- [x] T014 Verify `make test` FAIL (RED)
- [x] T015 Generate RED output: specs/004-new-xml-format/red-tests/ph2-test.md

### 実装 (GREEN)

- [x] T016 Read RED tests: specs/004-new-xml-format/red-tests/ph2-test.md
- [x] T017 [P] [US1] Create dataclasses HeadingInfo, ContentItem in src/xml2_parser.py
- [x] T018 [P] [US1] Create constants CHAPTER_MARKER, SECTION_MARKER in src/xml2_parser.py
- [x] T019 [US1] Implement parse_book2_xml() in src/xml2_parser.py
- [x] T020 [US1] Implement _should_read_aloud() helper in src/xml2_parser.py
- [x] T021 Verify `make test` PASS (GREEN)

### 検証

- [x] T022 Verify `make test` passes all tests (no regressions)
- [x] T023 Edit and rename: specs/004-new-xml-format/tasks/ph2-output-template.md → ph2-output.md

**Checkpoint**: US1 が独立して動作・テスト可能であること

---

## Phase 3: User Story 2 - 見出し速度調整 (Priority: P2)

**Goal**: heading 要素に chapter/section マーカーを付与し、「第N章」「第N.N節」形式で整形

**Independent Test**: `format_heading_text()` が正しい形式を返し、マーカーが付与されること

### 入力

- [x] T024 Read setup analysis: specs/004-new-xml-format/tasks/ph1-output.md
- [x] T025 Read previous phase output: specs/004-new-xml-format/tasks/ph2-output.md

### テスト実装 (RED)

- [x] T026 [P] [US2] Implement test_format_heading_text_chapter in tests/test_xml2_parser.py
- [x] T027 [P] [US2] Implement test_format_heading_text_section in tests/test_xml2_parser.py
- [x] T028 [P] [US2] Implement test_parse_book2_xml_heading_with_chapter_marker in tests/test_xml2_parser.py
- [x] T029 [P] [US2] Implement test_parse_book2_xml_heading_with_section_marker in tests/test_xml2_parser.py
- [x] T030 [P] [US2] Implement test_parse_book2_xml_heading_level3_uses_section_marker in tests/test_xml2_parser.py
- [x] T031 Verify `make test` FAIL (RED)
- [x] T032 Generate RED output: specs/004-new-xml-format/red-tests/ph3-test.md

### 実装 (GREEN)

- [x] T033 Read RED tests: specs/004-new-xml-format/red-tests/ph3-test.md
- [x] T034 [US2] Implement format_heading_text() in src/xml2_parser.py
- [x] T035 [US2] Update parse_book2_xml() to handle heading elements with markers in src/xml2_parser.py
- [x] T036 Verify `make test` PASS (GREEN)

### 検証

- [x] T037 Verify `make test` passes all tests (including US1 regressions)
- [x] T038 Edit and rename: specs/004-new-xml-format/tasks/ph3-output-template.md → ph3-output.md

**Checkpoint**: US1 AND US2 が両方独立して動作すること

---

## Phase 4: User Story 3 - 音声パイプライン統合 (Priority: P2)

**Goal**: xml2_pipeline.py を作成し、効果音付きで音声生成

**Independent Test**: `python -m src.xml2_pipeline --input sample/book2.xml` でエラーなく実行

### 入力

- [ ] T039 Read setup analysis: specs/004-new-xml-format/tasks/ph1-output.md
- [ ] T040 Read previous phase output: specs/004-new-xml-format/tasks/ph3-output.md

### テスト実装 (RED)

- [ ] T041 [P] [US3] Implement test_parse_args_defaults in tests/test_xml2_pipeline.py
- [ ] T042 [P] [US3] Implement test_parse_args_custom_sounds in tests/test_xml2_pipeline.py
- [ ] T043 [P] [US3] Implement test_load_sound_mono_conversion in tests/test_xml2_pipeline.py
- [ ] T044 [P] [US3] Implement test_process_content_with_markers in tests/test_xml2_pipeline.py
- [ ] T045 Verify `make test` FAIL (RED)
- [ ] T046 Generate RED output: specs/004-new-xml-format/red-tests/ph4-test.md

### 実装 (GREEN)

- [ ] T047 Read RED tests: specs/004-new-xml-format/red-tests/ph4-test.md
- [ ] T048 [US3] Implement parse_args() in src/xml2_pipeline.py
- [ ] T049 [US3] Implement load_sound() in src/xml2_pipeline.py (reuse from xml_pipeline.py)
- [ ] T050 [US3] Implement process_content() in src/xml2_pipeline.py
- [ ] T051 [US3] Implement main() in src/xml2_pipeline.py
- [ ] T052 Verify `make test` PASS (GREEN)

### 検証

- [ ] T053 Verify `make test` passes all tests
- [ ] T054 Edit and rename: specs/004-new-xml-format/tasks/ph4-output-template.md → ph4-output.md

**Checkpoint**: CLI でエンドツーエンド実行可能であること

---

## Phase 5: Polish & Cross-Cutting Concerns — NO TDD

**Purpose**: ドキュメント、型ヒント、クリーンアップ

### 入力

- [ ] T055 Read setup analysis: specs/004-new-xml-format/tasks/ph1-output.md
- [ ] T056 Read previous phase output: specs/004-new-xml-format/tasks/ph4-output.md

### 実装

- [ ] T057 [P] Add docstrings to all public functions in src/xml2_parser.py
- [ ] T058 [P] Add docstrings to all public functions in src/xml2_pipeline.py
- [ ] T059 [P] Add type hints to all functions in src/xml2_parser.py
- [ ] T060 [P] Add type hints to all functions in src/xml2_pipeline.py
- [ ] T061 Run quickstart.md validation (manual test with sample/book2.xml)

### 検証

- [ ] T062 Run `make test` to verify all tests pass after cleanup
- [ ] T063 Edit and rename: specs/004-new-xml-format/tasks/ph5-output-template.md → ph5-output.md

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
specs/004-new-xml-format/
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
4. Verify with: `parse_book2_xml()` returns ContentItem list

### Full Delivery

1. Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5
2. Each phase commits: `feat(phase-N): description`

---

## Test Coverage Rules

**Boundary Test Principle**: Write tests at **every boundary** where data transformation occurs

```
[book2.xml] → [parse_book2_xml] → [ContentItem list] → [process_content] → [WAV files]
     ↓              ↓                    ↓                   ↓                ↓
   Test           Test                 Test               Test             Test
```

**Checklist**:
- [ ] XML parsing tests (toc/front-matter skip)
- [ ] readAloud filtering tests
- [ ] Heading format tests (第N章/第N.N節)
- [ ] Marker insertion tests (CHAPTER_MARKER/SECTION_MARKER)
- [ ] CLI argument parsing tests
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
