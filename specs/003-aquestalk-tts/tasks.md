# Tasks: AquesTalk TTS 対応

**Input**: Design documents from `/specs/003-aquestalk-tts/`
**Prerequisites**: spec.md (required), research.md (technical decisions)

**Tests**: TDD is MANDATORY for User Story phases. Each phase follows Test Implementation (RED) → Implementation (GREEN) → Verification workflow.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: No dependencies (different files, execution order free)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## User Story Summary

| ID | Title | Priority | FR | Scenario |
|----|-------|----------|----|----------|
| US1 | XML から AquesTalk 音声生成 | P1 | FR-001,002,003,005,006,008,009,010 | 基本音声生成 |
| US2 | 見出し効果音の挿入 | P2 | FR-004,011 | 効果音 + 速度調整 |
| US3 | 音声パラメータの調整 | P3 | FR-007,012,013 | speed, voice, pitch |

## Path Conventions

- **Source**: `src/` at repository root
- **Tests**: `tests/` at repository root
- **Reference**: `src/xml_pipeline.py` (VOICEVOX 版) をパターンとして参照

---

## Phase 1: Setup (Shared Infrastructure) — NO TDD

**Purpose**: 既存コードの分析、AquesTalk10 ラッパーの設計準備

- [X] T001 Read existing VOICEVOX pipeline in src/xml_pipeline.py
- [X] T002 [P] Read existing text cleaner in src/text_cleaner.py
- [X] T003 [P] Read existing xml parser in src/xml_parser.py
- [X] T004 [P] Read existing pipeline utilities in src/pipeline.py
- [X] T005 [P] Read existing voicevox client pattern in src/voicevox_client.py
- [X] T006 [P] Read existing tests in tests/test_xml_pipeline.py
- [X] T007 Generate phase output: specs/003-aquestalk-tts/tasks/ph1-output.md

---

## Phase 2: User Story 1 - XML から AquesTalk 音声生成 (Priority: P1) MVP

**Goal**: 既存 XML ブックファイルから AquesTalk10 で音声ファイルを生成する基本機能

**Independent Test**: `python -m src.aquestalk_pipeline -i sample/book.xml` を実行し、音声ファイルが生成されることで単独テスト可能

### Input

- [X] T008 Read previous phase output: specs/003-aquestalk-tts/tasks/ph1-output.md

### Test Implementation (RED)

- [X] T009 [P] [US1] Create test file structure tests/test_aquestalk_client.py
- [X] T010 [P] [US1] Implement test_synthesize_basic in tests/test_aquestalk_client.py
- [X] T011 [P] [US1] Implement test_synthesize_with_num_tag in tests/test_aquestalk_client.py
- [X] T012 [P] [US1] Implement test_add_punctuation_to_text in tests/test_aquestalk_client.py
- [X] T013 [P] [US1] Create test file structure tests/test_aquestalk_pipeline.py
- [X] T014 [P] [US1] Implement test_parse_args in tests/test_aquestalk_pipeline.py
- [X] T015 [P] [US1] Implement test_main_generates_audio in tests/test_aquestalk_pipeline.py
- [X] T016 [P] [US1] Implement test_page_range_filtering in tests/test_aquestalk_pipeline.py
- [X] T017 [P] [US1] Implement test_file_not_found_error in tests/test_aquestalk_pipeline.py
- [X] T018 Verify `make test` FAIL (RED)
- [X] T019 Generate RED output: specs/003-aquestalk-tts/red-tests/ph2-test.md

### Implementation (GREEN)

- [X] T020 Read RED tests: specs/003-aquestalk-tts/red-tests/ph2-test.md
- [X] T021 [US1] Create AquesTalkConfig dataclass in src/aquestalk_client.py
- [X] T022 [US1] Create AquesTalkSynthesizer class with initialize() in src/aquestalk_client.py
- [X] T023 [US1] Implement synthesize() method in src/aquestalk_client.py
- [X] T024 [US1] Implement add_punctuation() for heading/paragraph end in src/aquestalk_client.py
- [X] T025 [US1] Implement convert_numbers_to_num_tags() in src/aquestalk_client.py
- [X] T026 [US1] Create parse_args() in src/aquestalk_pipeline.py
- [X] T027 [US1] Create main() with XML parsing + text cleaning in src/aquestalk_pipeline.py
- [X] T028 [US1] Implement page processing loop in src/aquestalk_pipeline.py
- [X] T029 [US1] Implement book.wav concatenation in src/aquestalk_pipeline.py
- [X] T030 Verify `make test` PASS (GREEN)

### Verification

- [X] T031 Verify `make test` passes all tests (no regressions)
- [X] T032 Generate phase output: specs/003-aquestalk-tts/tasks/ph2-output.md

**Checkpoint**: User Story 1 should be fully functional and testable independently

---

## Phase 3: User Story 2 - 見出し効果音の挿入 (Priority: P2)

**Goal**: 見出し（heading）の前に効果音を挿入し、見出しをゆっくり（speed 80）読む

**Independent Test**: `--heading-sound sample/heading-sound.mp3` オプション付きで実行し、見出し前に効果音が挿入されることで単独テスト可能

### Input

- [X] T033 Read setup analysis: specs/003-aquestalk-tts/tasks/ph1-output.md
- [X] T034 Read previous phase output: specs/003-aquestalk-tts/tasks/ph2-output.md

### Test Implementation (RED)

- [X] T035 [P] [US2] Implement test_load_heading_sound in tests/test_aquestalk_pipeline.py
- [X] T036 [P] [US2] Implement test_heading_sound_insertion in tests/test_aquestalk_pipeline.py
- [X] T037 [P] [US2] Implement test_heading_speed_adjustment in tests/test_aquestalk_client.py
- [X] T038 [P] [US2] Implement test_heading_sound_file_not_found_warning in tests/test_aquestalk_pipeline.py
- [X] T039 Verify `make test` FAIL (RED)
- [X] T040 Generate RED output: specs/003-aquestalk-tts/red-tests/ph3-test.md

### Implementation (GREEN)

- [X] T041 Read RED tests: specs/003-aquestalk-tts/red-tests/ph3-test.md
- [X] T042 [US2] Implement load_heading_sound() with 16kHz resample in src/aquestalk_pipeline.py
- [X] T043 [US2] Implement process_pages_with_heading_sound() in src/aquestalk_pipeline.py
- [X] T044 [US2] Add --heading-sound CLI option in src/aquestalk_pipeline.py
- [X] T045 [US2] Implement heading speed reduction (speed 80) in src/aquestalk_pipeline.py
- [X] T046 Verify `make test` PASS (GREEN)

### Verification

- [X] T047 Verify `make test` passes all tests (including regressions from US1)
- [X] T048 Generate phase output: specs/003-aquestalk-tts/tasks/ph3-output.md

**Checkpoint**: User Stories 1 AND 2 should both work independently

---

## Phase 4: User Story 3 - 音声パラメータの調整 (Priority: P3)

**Goal**: 読み上げ速度、声質、ピッチなどの AquesTalk10 パラメータを CLI から調整可能にする

**Independent Test**: `--speed 150 --voice 100 --pitch 100` オプションで実行し、音声パラメータが反映されることで単独テスト可能

### Input

- [X] T049 Read setup analysis: specs/003-aquestalk-tts/tasks/ph1-output.md
- [X] T050 Read previous phase output: specs/003-aquestalk-tts/tasks/ph3-output.md

### Test Implementation (RED)

- [X] T051 [P] [US3] Implement test_speed_parameter in tests/test_aquestalk_client.py (Phase 3 で既に実装済み)
- [X] T052 [P] [US3] Implement test_voice_parameter in tests/test_aquestalk_client.py
- [X] T053 [P] [US3] Implement test_pitch_parameter in tests/test_aquestalk_client.py
- [X] T054 [P] [US3] Implement test_parameter_validation in tests/test_aquestalk_client.py
- [X] T055 [P] [US3] Implement test_cli_parameter_options in tests/test_aquestalk_pipeline.py (Phase 2 で既に実装済み)
- [X] T056 Verify `make test` FAIL (RED)
- [X] T057 Generate RED output: specs/003-aquestalk-tts/red-tests/ph4-test.md

### Implementation (GREEN)

- [X] T058 Read RED tests: specs/003-aquestalk-tts/red-tests/ph4-test.md
- [X] T059 [US3] Add speed, voice, pitch to AquesTalkConfig in src/aquestalk_client.py
- [X] T060 [US3] Implement parameter validation in src/aquestalk_client.py
- [X] T061 [US3] Add --speed, --voice, --pitch CLI options in src/aquestalk_pipeline.py
- [X] T062 [US3] Pass parameters to synthesizer in src/aquestalk_pipeline.py
- [X] T063 Verify `make test` PASS (GREEN)

### Verification

- [X] T064 Verify `make test` passes all tests (no regressions)
- [X] T065 Generate phase output: specs/003-aquestalk-tts/tasks/ph4-output.md

**Checkpoint**: All User Stories (1, 2, 3) should work independently

---

## Phase 5: Polish & Cross-Cutting Concerns — NO TDD

**Purpose**: コードクリーンアップ、ドキュメント整備、最終検証

### Input

- [X] T066 Read setup analysis: specs/003-aquestalk-tts/tasks/ph1-output.md
- [X] T067 Read previous phase output: specs/003-aquestalk-tts/tasks/ph4-output.md

### Implementation

- [X] T068 [P] Add docstrings to all public functions in src/aquestalk_client.py
- [X] T069 [P] Add docstrings to all public functions in src/aquestalk_pipeline.py
- [X] T070 [P] Add type hints to all functions in src/aquestalk_client.py
- [X] T071 [P] Add type hints to all functions in src/aquestalk_pipeline.py
- [X] T072 Code cleanup and refactoring
- [X] T073 Run quickstart.md validation (manual test) - skipped, no quickstart.md

### Verification

- [X] T074 Run `make test` to verify all tests pass after cleanup
- [X] T075 Run `make coverage` to verify ≥80% coverage
- [X] T076 Generate phase output: specs/003-aquestalk-tts/tasks/ph5-output.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - Main agent direct execution
- **User Stories (Phase 2-4)**: TDD flow (tdd-generator → phase-executor)
  - User stories proceed sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 5)**: Depends on all user stories - phase-executor only

### Within Each User Story Phase (TDD Flow)

1. **Input**: Read setup analysis (ph1) + previous phase output (context from prior work)
2. **Test Implementation (RED)**: Write tests FIRST → verify `make test` FAIL → generate RED output
3. **Implementation (GREEN)**: Read RED tests → implement → verify `make test` PASS
4. **Verification**: Confirm no regressions → generate phase output

### Agent Delegation

- **Phase 1 (Setup)**: Main agent direct execution
- **Phase 2-4 (User Stories)**: tdd-generator (RED) → phase-executor (GREEN + Verification)
- **Phase 5 (Polish)**: phase-executor only

### [P] Marker (No Dependencies)

`[P]` indicates "no dependencies on other tasks, execution order is flexible". Does not guarantee parallel execution.

- Setup tasks [P]: Different file/directory reading with no interdependencies
- RED tests [P]: Writing to different test files with no interdependencies
- GREEN implementation [P]: Writing to different source files with no interdependencies
- Between User Stories: Each Phase depends on previous Phase output, so [P] not applicable

---

## Phase Output & RED Test Artifacts

### Directory Structure

```
specs/003-aquestalk-tts/
├── tasks.md                    # This file
├── tasks/
│   ├── ph1-output.md           # Phase 1 output (Setup results)
│   ├── ph2-output.md           # Phase 2 output (US1 GREEN results)
│   ├── ph3-output.md           # Phase 3 output (US2 GREEN results)
│   ├── ph4-output.md           # Phase 4 output (US3 GREEN results)
│   └── ph5-output.md           # Final phase output
└── red-tests/
    ├── ph2-test.md             # Phase 2 RED test results (US1 FAIL confirmation)
    ├── ph3-test.md             # Phase 3 RED test results (US2 FAIL confirmation)
    └── ph4-test.md             # Phase 4 RED test results (US3 FAIL confirmation)
```

### Phase Output Content

Each `phN-output.md` should contain:
- Summary of what was done
- Files created/modified
- Test results (`make test` output)
- Any decisions or deviations from the plan

### RED Test Output Content

Each `phN-test.md` should contain:
- Test code written
- `make test` output showing FAIL (RED confirmation)
- Number of failing tests and their names

---

## Implementation Strategy

### MVP First (Phase 1 + Phase 2)

1. Complete Phase 1: Setup (existing code review)
2. Complete Phase 2: User Story 1 (RED → GREEN → Verification)
3. **STOP and VALIDATE**: Confirm all tests pass with `make test`
4. Verify with manual test: `python -m src.aquestalk_pipeline -i sample/book.xml`

### Full Delivery

1. Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5
2. Each phase commits: `feat(phase-N): description`

---

## Test Coverage Rules

**Boundary Test Principle**: Write tests at **every boundary** where data transformation occurs

```
[XML Input] → [xml_parser] → [text_cleaner] → [AquesTalk synthesize] → [WAV Output]
     ↓             ↓              ↓                   ↓                    ↓
   Test          Test           Test                Test                 Test
```

**Checklist**:
- [X] Input parsing tests (XML → Page objects)
- [X] Text transformation tests (cleaner + punctuation + NUM tags)
- [X] Audio synthesis tests (AquesTalk API wrapper)
- [X] Output generation tests (WAV file creation)
- [X] End-to-End tests (XML → book.wav)

---

## Notes

- [P] tasks = no dependencies, execution order free
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- TDD: Test Implementation (RED) → Verify FAIL → Implementation (GREEN) → Verify PASS
- RED output must be generated BEFORE implementation begins
- Commit after each phase completion
- Stop at any checkpoint to validate story independently
- AquesTalk10 sample rate: 16000Hz (effect sounds need resampling)
- Reference: src/xml_pipeline.py (VOICEVOX version) as implementation pattern
