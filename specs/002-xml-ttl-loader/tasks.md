# Tasks: XML から TTS へのローダー

**Input**: Design documents from `/specs/002-xml-ttl-loader/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: TDD is MANDATORY for User Story phases. Each phase follows Test Implementation (RED) → Implementation (GREEN) → Verification workflow.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: No dependencies (different files, execution order free)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## User Story Summary

| ID | Title | Priority | FR | Scenario |
|----|-------|----------|----|----------|
| US1 | XML ファイルを TTS パイプラインに読み込む | P1 | FR-001,002,003,005,006,007 | XML からテキスト抽出 → TTS 音声生成 |
| US2 | 読み上げ不要な要素をスキップする | P2 | FR-004,008 | readAloud="false" 要素のスキップ |

## Path Conventions

- **Project Type**: Single CLI application
- **Source**: `src/`
- **Tests**: `tests/`
- **Feature Dir**: `specs/002-xml-ttl-loader/`

---

## Phase 1: Setup (Shared Infrastructure) — NO TDD

**Purpose**: 既存コードの理解と新規ファイルのスケルトン作成

- [X] T001 Read existing Page class in src/text_cleaner.py
- [X] T002 [P] Read existing process_pages() in src/pipeline.py
- [X] T003 [P] Read existing VoicevoxSynthesizer in src/voicevox_client.py
- [X] T004 [P] Read sample XML structure in sample/book.xml (first 200 lines)
- [X] T005 Create test fixture directory: tests/fixtures/
- [X] T006 [P] Create minimal test XML: tests/fixtures/sample_book.xml
- [X] T007 Generate phase output: specs/002-xml-ttl-loader/tasks/ph1-output.md

---

## Phase 2: User Story 1 - XML ファイルを TTS パイプラインに読み込む (Priority: P1) MVP

**Goal**: XML から基本的なテキスト抽出ができ、Page オブジェクトに変換できる

**Independent Test**: `sample/book.xml` を読み込み、各ページのテキストが抽出されることを確認

### Input

- [x] T008 Read previous phase output: specs/002-xml-ttl-loader/tasks/ph1-output.md

### テスト実装 (RED)

- [x] T009 [P] [US1] Create test file: tests/test_xml_parser.py with test class skeleton
- [x] T010 [P] [US1] Implement test_parse_book_xml_returns_pages in tests/test_xml_parser.py
- [x] T011 [P] [US1] Implement test_xmlpage_has_number_and_text in tests/test_xml_parser.py
- [x] T012 [P] [US1] Implement test_extract_paragraph_text in tests/test_xml_parser.py
- [x] T013 [P] [US1] Implement test_extract_heading_text in tests/test_xml_parser.py
- [x] T014 [P] [US1] Implement test_extract_list_items in tests/test_xml_parser.py
- [x] T015 [P] [US1] Implement test_extract_page_announcement in tests/test_xml_parser.py
- [x] T016 [P] [US1] Implement test_to_page_conversion in tests/test_xml_parser.py
- [x] T017 Verify `make test` FAIL (RED) - 新規テストが失敗することを確認
- [x] T018 Generate RED output: specs/002-xml-ttl-loader/red-tests/ph2-test.md

### 実装 (GREEN)

- [x] T019 Read RED tests: specs/002-xml-ttl-loader/red-tests/ph2-test.md
- [x] T020 [P] [US1] Create src/xml_parser.py with module docstring and imports
- [x] T021 [P] [US1] Implement Figure dataclass in src/xml_parser.py
- [x] T022 [P] [US1] Implement XmlPage dataclass in src/xml_parser.py
- [x] T023 [US1] Implement parse_book_xml() function in src/xml_parser.py
- [x] T024 [US1] Implement _extract_content_text() helper in src/xml_parser.py
- [x] T025 [US1] Implement to_page() conversion function in src/xml_parser.py
- [x] T026 Verify `make test` PASS (GREEN) - 全テストが通ることを確認

### 検証

- [x] T027 Verify `make test` passes all tests (no regressions)
- [x] T028 Generate phase output: specs/002-xml-ttl-loader/tasks/ph2-output.md

**Checkpoint**: US1 完了 - XML パーサーが基本的なテキスト抽出と Page 変換ができる状態

---

## Phase 3: User Story 2 - 読み上げ不要な要素をスキップする (Priority: P2)

**Goal**: `readAloud="false"` 属性を持つ要素をスキップし、不要な情報を読み上げない

**Independent Test**: `readAloud="false"` を含む XML を処理し、その内容が抽出テキストに含まれないことを確認

### Input

- [x] T029 Read setup analysis: specs/002-xml-ttl-loader/tasks/ph1-output.md
- [x] T030 Read previous phase output: specs/002-xml-ttl-loader/tasks/ph2-output.md

### テスト実装 (RED)

- [x] T031 [P] [US2] Implement test_skip_read_aloud_false_element in tests/test_xml_parser.py
- [x] T032 [P] [US2] Implement test_skip_page_metadata in tests/test_xml_parser.py
- [x] T033 [P] [US2] Implement test_extract_figure_description_when_optional in tests/test_xml_parser.py
- [x] T034 [P] [US2] Implement test_skip_figure_file_path in tests/test_xml_parser.py
- [x] T035 [P] [US2] Implement test_ignore_xml_comments in tests/test_xml_parser.py
- [x] T036 Verify `make test` FAIL (RED) - 新規テストが失敗することを確認
- [x] T037 Generate RED output: specs/002-xml-ttl-loader/red-tests/ph3-test.md

### 実装 (GREEN)

- [x] T038 Read RED tests: specs/002-xml-ttl-loader/red-tests/ph3-test.md
- [x] T039 [US2] Implement _should_read_aloud() helper in src/xml_parser.py
- [x] T040 [US2] Update parse_book_xml() to check readAloud attribute in src/xml_parser.py
- [x] T041 [US2] Update _extract_content_text() to skip readAloud="false" in src/xml_parser.py
- [x] T042 [US2] Implement figure description extraction with readAloud check in src/xml_parser.py
- [x] T043 Verify `make test` PASS (GREEN) - 全テストが通ることを確認

### 検証

- [x] T044 Verify `make test` passes all tests (including US1 regressions)
- [x] T045 Generate phase output: specs/002-xml-ttl-loader/tasks/ph3-output.md

**Checkpoint**: US2 完了 - readAloud 属性に基づく要素フィルタリングが機能する状態

---

## Phase 4: パイプライン統合

**Goal**: 既存の TTS 処理と統合し、XML から音声ファイルを生成

**Independent Test**: `python src/xml_pipeline.py -i sample/book.xml` で音声ファイルが生成される

### Input

- [x] T046 Read setup analysis: specs/002-xml-ttl-loader/tasks/ph1-output.md
- [x] T047 Read previous phase output: specs/002-xml-ttl-loader/tasks/ph3-output.md

### テスト実装 (RED)

- [x] T048 [P] Create test file: tests/test_xml_pipeline.py with test class skeleton
- [x] T049 [P] Implement test_parse_args_required_input in tests/test_xml_pipeline.py
- [x] T050 [P] Implement test_parse_args_defaults in tests/test_xml_pipeline.py
- [x] T051 [P] Implement test_file_not_found_error in tests/test_xml_pipeline.py
- [x] T052 [P] Implement test_invalid_xml_error in tests/test_xml_pipeline.py
- [x] T053 Verify `make test` FAIL (RED) - 新規テストが失敗することを確認
- [x] T054 Generate RED output: specs/002-xml-ttl-loader/red-tests/ph4-test.md

### 実装 (GREEN)

- [ ] T055 Read RED tests: specs/002-xml-ttl-loader/red-tests/ph4-test.md
- [ ] T056 Create src/xml_pipeline.py with module docstring and imports
- [ ] T057 Implement parse_args() function in src/xml_pipeline.py
- [ ] T058 Implement main() function skeleton in src/xml_pipeline.py
- [ ] T059 Integrate xml_parser.parse_book_xml() in main()
- [ ] T060 Integrate text_cleaner.clean_page_text() in main()
- [ ] T061 Integrate pipeline.process_pages() in main()
- [ ] T062 Implement error handling for file not found and invalid XML
- [ ] T063 Verify `make test` PASS (GREEN) - 全テストが通ることを確認

### 検証

- [ ] T064 Verify `make test` passes all tests (including US1, US2 regressions)
- [ ] T065 Manual test: Run xml_pipeline.py with sample/book.xml (first 3 pages)
- [ ] T066 Generate phase output: specs/002-xml-ttl-loader/tasks/ph4-output.md

**Checkpoint**: パイプライン統合完了 - XML から音声ファイルが生成できる状態

---

## Phase 5: Polish & Cross-Cutting Concerns — NO TDD

**Purpose**: ドキュメント整備と最終確認

### Input

- [ ] T067 Read setup analysis: specs/002-xml-ttl-loader/tasks/ph1-output.md
- [ ] T068 Read previous phase output: specs/002-xml-ttl-loader/tasks/ph4-output.md

### 実装

- [ ] T069 [P] Validate quickstart.md examples work correctly
- [ ] T070 [P] Add docstrings to all public functions in src/xml_parser.py
- [ ] T071 [P] Add docstrings to all public functions in src/xml_pipeline.py
- [ ] T072 Update Makefile if needed (add xml-tts target)

### 検証

- [ ] T073 Run `make test` to verify all tests pass after cleanup
- [ ] T074 Run `make lint` if available
- [ ] T075 Generate phase output: specs/002-xml-ttl-loader/tasks/ph5-output.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - Main agent direct execution
- **Phase 2 (US1)**: Depends on Phase 1 - TDD flow (tdd-generator → phase-executor)
- **Phase 3 (US2)**: Depends on Phase 2 - TDD flow (tdd-generator → phase-executor)
- **Phase 4 (Pipeline)**: Depends on Phase 3 - TDD flow (tdd-generator → phase-executor)
- **Phase 5 (Polish)**: Depends on Phase 4 - phase-executor only

### Within Each User Story Phase (TDD Flow)

1. **Input**: Read setup analysis (ph1) + previous phase output
2. **Test Implementation (RED)**: Write tests FIRST → verify `make test` FAIL → generate RED output
3. **Implementation (GREEN)**: Read RED tests → implement → verify `make test` PASS
4. **Verification**: Confirm no regressions → generate phase output

### Agent Delegation

| Phase | Agent | Notes |
|-------|-------|-------|
| Phase 1 (Setup) | Main agent | NO TDD |
| Phase 2 (US1) | tdd-generator → phase-executor | TDD flow |
| Phase 3 (US2) | tdd-generator → phase-executor | TDD flow |
| Phase 4 (Pipeline) | tdd-generator → phase-executor | TDD flow |
| Phase 5 (Polish) | phase-executor | NO TDD |

---

## Phase Output & RED Test Artifacts

### Directory Structure

```
specs/002-xml-ttl-loader/
├── tasks.md                    # This file
├── tasks/
│   ├── ph1-output.md           # Phase 1 output (Setup results)
│   ├── ph2-output.md           # Phase 2 output (US1 GREEN results)
│   ├── ph3-output.md           # Phase 3 output (US2 GREEN results)
│   ├── ph4-output.md           # Phase 4 output (Pipeline results)
│   └── ph5-output.md           # Phase 5 output (Polish results)
└── red-tests/
    ├── ph2-test.md             # Phase 2 RED test results
    ├── ph3-test.md             # Phase 3 RED test results
    └── ph4-test.md             # Phase 4 RED test results
```

---

## Implementation Strategy

### MVP First (Phase 1 + Phase 2)

1. Complete Phase 1: Setup (既存コード理解)
2. Complete Phase 2: User Story 1 (RED → GREEN → Verification)
3. **STOP and VALIDATE**: `make test` で全テスト通過を確認
4. Manual test: `python src/xml_parser.py` で基本動作確認

### Full Delivery

1. Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5
2. 各 Phase 完了後にコミット: `feat(phase-N): description`

---

## Test Coverage Rules

**Boundary Test Principle**: Write tests at **every boundary** where data transformation occurs

```
[XML Input] → [Parse] → [XmlPage] → [to_page()] → [Page] → [TTS]
     ↓           ↓          ↓           ↓           ↓
   Test        Test       Test        Test        Test
```

**Checklist**:
- [ ] XML パース正常系テスト
- [ ] readAloud 属性フィルタリングテスト
- [ ] XmlPage → Page 変換テスト
- [ ] エラーハンドリングテスト
- [ ] E2E テスト (XML → Page list)

---

## Notes

- [P] tasks = no dependencies, execution order free
- [Story] label maps task to specific user story for traceability
- TDD: Test Implementation (RED) → Verify FAIL → Implementation (GREEN) → Verify PASS
- RED output must be generated BEFORE implementation begins
- Commit after each phase completion
