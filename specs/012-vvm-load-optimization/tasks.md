# Tasks: VOICEVOX モデルロード最適化

**Input**: 設計ドキュメント `/specs/012-vvm-load-optimization/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: TDD は User Story フェーズで必須。各フェーズは Test Implementation (RED) → Implementation (GREEN) → Verification のワークフローに従う。

**Language**: 日本語

**Organization**: タスクはユーザーストーリーごとにグループ化し、各ストーリーの独立した実装とテストを可能にする。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 依存関係なし（異なるファイル、実行順序自由）
- **[Story]**: タスクが属するユーザーストーリー（US1, US2, US3）
- 説明には正確なファイルパスを含める

## User Story Summary

| ID | Title | Priority | FR | Scenario |
|----|-------|----------|----|----------|
| US1 | 必要なモデルのみロード | P1 | FR-001, FR-002, FR-003, FR-004 | style_id に対応する VVM のみロード |
| US2 | バージョン警告の解消 | P2 | FR-005 | VVM 再取得でバージョン一致 |
| US3 | 後方互換性の維持 | P3 | FR-006 | 既存テストパス、音声出力一致 |

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- 変更対象ファイル:
  - `src/voicevox_client.py`: マッピング追加、新メソッド追加
  - `src/xml2_pipeline.py`: `load_all_models()` → `load_model_for_style_id()` 置き換え

---

## Phase 1: Setup (既存コード分析) — NO TDD

**Purpose**: 既存実装の分析と変更箇所の特定

- [ ] T001 Read current implementation in src/voicevox_client.py
- [ ] T002 [P] Read current implementation in src/xml2_pipeline.py
- [ ] T003 [P] Read existing tests in tests/test_xml2_pipeline.py
- [ ] T004 [P] Read VOICEVOX Core version in Makefile
- [ ] T005 Identify current load_all_models() call location and usage pattern
- [ ] T006 Generate phase output: specs/012-vvm-load-optimization/tasks/ph1-output.md

---

## Phase 2: User Story 1 - 必要なモデルのみロード (Priority: P1) MVP

**Goal**: `--style-id` で指定された VVM ファイルのみをロードし、起動時間を 80% 以上短縮する

**Independent Test**: `make xml-tts` を実行し、ログ出力で指定した style_id に対応する VVM ファイル 1 つのみがロードされることを確認

### Input

- [ ] T007 Read previous phase output: specs/012-vvm-load-optimization/tasks/ph1-output.md

### Test Implementation (RED)

- [ ] T008 [P] [US1] Implement test_style_id_to_vvm_mapping in tests/test_voicevox_client.py
- [ ] T009 [P] [US1] Implement test_get_vvm_path_for_style_id in tests/test_voicevox_client.py
- [ ] T010 [P] [US1] Implement test_load_model_for_style_id in tests/test_voicevox_client.py
- [ ] T011 [P] [US1] Implement test_invalid_style_id_error in tests/test_voicevox_client.py
- [ ] T012 Verify `make test` FAIL (RED)
- [ ] T013 Generate RED output: specs/012-vvm-load-optimization/red-tests/ph2-test.md

### Implementation (GREEN)

- [ ] T014 Read RED tests: specs/012-vvm-load-optimization/red-tests/ph2-test.md
- [ ] T015 [P] [US1] Add STYLE_ID_TO_VVM dict in src/voicevox_client.py
- [ ] T016 [P] [US1] Implement get_vvm_path_for_style_id() in src/voicevox_client.py
- [ ] T017 [US1] Implement load_model_for_style_id() in src/voicevox_client.py
- [ ] T018 [US1] Replace load_all_models() with load_model_for_style_id() in src/xml2_pipeline.py
- [ ] T019 Verify `make test` PASS (GREEN)

### Verification

- [ ] T020 Verify `make test` passes all tests (no regressions)
- [ ] T021 Verify `make xml-tts` loads only 1 VVM file (check log output)
- [ ] T022 Generate phase output: specs/012-vvm-load-optimization/tasks/ph2-output.md

**Checkpoint**: User Story 1 完了 - 単一モデルロードが機能し、起動時間短縮を達成

---

## Phase 3: User Story 2 - バージョン警告の解消 (Priority: P2)

**Goal**: VVM ファイルを VOICEVOX Core 0.16.3 に合わせて再取得し、バージョン警告を解消する

**Independent Test**: `make xml-tts` 実行時に WARNING ログが 0 件であることを確認

### Input

- [ ] T023 Read setup analysis: specs/012-vvm-load-optimization/tasks/ph1-output.md
- [ ] T024 Read previous phase output: specs/012-vvm-load-optimization/tasks/ph2-output.md

### Test Implementation (RED)

- [ ] T025 [US2] Implement test_no_version_warning in tests/test_voicevox_client.py
- [ ] T026 Verify `make test` FAIL (RED) - 現状の VVM でバージョン警告が出ることを確認
- [ ] T027 Generate RED output: specs/012-vvm-load-optimization/red-tests/ph3-test.md

### Implementation (GREEN)

- [ ] T028 Read RED tests: specs/012-vvm-load-optimization/red-tests/ph3-test.md
- [ ] T029 [US2] Delete existing VVM files: rm -rf voicevox_core/models/vvms/
- [ ] T030 [US2] Re-download VVM files: make setup-voicevox
- [ ] T031 Verify `make test` PASS (GREEN)

### Verification

- [ ] T032 Verify `make xml-tts` shows 0 WARNING logs
- [ ] T033 Verify audio output quality is maintained
- [ ] T034 Generate phase output: specs/012-vvm-load-optimization/tasks/ph3-output.md

**Checkpoint**: User Story 2 完了 - バージョン警告が解消され、ログがクリーンに

---

## Phase 4: User Story 3 + Polish - 後方互換性の維持 (Priority: P3) — NO TDD

**Goal**: 最適化後も既存のワークフローが正常に動作することを検証

**Independent Test**: 既存テストスイートが 100% パス、同一入力に対する音声出力が一致

### Input

- [ ] T035 Read setup analysis: specs/012-vvm-load-optimization/tasks/ph1-output.md
- [ ] T036 Read previous phase output: specs/012-vvm-load-optimization/tasks/ph3-output.md

### Verification

- [ ] T037 [US3] Run `make test` to verify all existing tests pass
- [ ] T038 [US3] Run `make xml-tts` with default style_id and verify output
- [ ] T039 [US3] Compare audio output with pre-optimization baseline (if available)
- [ ] T040 Verify SC-001: モデルロード時間 80% 以上短縮を確認

### Cleanup

- [ ] T041 [P] Remove any dead code related to load_all_models() if not used elsewhere
- [ ] T042 [P] Update docstrings for new methods in src/voicevox_client.py
- [ ] T043 Run quickstart.md validation steps
- [ ] T044 Generate phase output: specs/012-vvm-load-optimization/tasks/ph4-output.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: 依存なし - メインエージェント直接実行
- **Phase 2 (US1)**: TDD フロー (speckit:tdd-generator → speckit:phase-executor)
- **Phase 3 (US2)**: TDD フロー (speckit:tdd-generator → speckit:phase-executor)
- **Phase 4 (US3 + Polish)**: speckit:phase-executor のみ

### Within Each User Story Phase (TDD Flow)

1. **Input**: ph1-output.md（セットアップ分析）+ 前フェーズ出力を読み込み
2. **Test Implementation (RED)**: テストを先に書く → `make test` FAIL 確認 → RED 出力生成
3. **Implementation (GREEN)**: RED テストを読む → 実装 → `make test` PASS 確認
4. **Verification**: リグレッションなし確認 → フェーズ出力生成

### Agent Delegation

- **Phase 1 (Setup)**: メインエージェント直接実行
- **Phase 2-3 (User Stories)**: speckit:tdd-generator (RED) → speckit:phase-executor (GREEN + Verification)
- **Phase 4 (Polish)**: speckit:phase-executor のみ

### [P] Marker (依存関係なし)

`[P]` は「他タスクへの依存なし、実行順序自由」を示す。並列実行を保証するものではない。

- Setup タスク [P]: 異なるファイル/ディレクトリの読み取りで相互依存なし
- RED テスト [P]: 異なるテストファイルへの書き込みで相互依存なし
- GREEN 実装 [P]: 異なるソースファイルへの書き込みで相互依存なし
- User Story 間: 各 Phase は前 Phase 出力に依存するため [P] 適用外

---

## Phase Output & RED Test Artifacts

### Directory Structure

```
specs/012-vvm-load-optimization/
├── tasks.md                    # このファイル
├── tasks/
│   ├── ph1-output.md           # Phase 1 出力 (セットアップ結果)
│   ├── ph2-output.md           # Phase 2 出力 (US1 GREEN 結果)
│   ├── ph3-output.md           # Phase 3 出力 (US2 GREEN 結果)
│   └── ph4-output.md           # Phase 4 出力 (最終検証)
└── red-tests/
    ├── ph2-test.md             # Phase 2 RED テスト結果 (FAIL 確認)
    └── ph3-test.md             # Phase 3 RED テスト結果 (FAIL 確認)
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

1. Phase 1 完了: Setup（既存コード分析）
2. Phase 2 完了: User Story 1 (RED → GREEN → Verification)
3. **STOP and VALIDATE**: `make test` で全テストパスを確認
4. `make xml-tts` で単一モデルロードを手動検証

### Full Delivery

1. Phase 1 → Phase 2 → Phase 3 → Phase 4
2. 各フェーズでコミット: `feat(phase-N): description`

---

## Test Coverage Rules

**Boundary Test Principle**: データ変換が発生するすべての境界でテストを書く

```
[style_id 入力] → [マッピング解決] → [VVM パス取得] → [モデルロード]
      ↓               ↓                 ↓               ↓
    Test           Test              Test            Test
```

**Checklist**:
- [ ] style_id 入力のバリデーションテスト
- [ ] マッピング解決テスト（正常・異常）
- [ ] VVM パス取得テスト
- [ ] モデルロードの統合テスト

---

## Notes

- [P] タスク = 依存関係なし、実行順序自由
- [Story] ラベルはタスクを特定のユーザーストーリーにマッピング
- 各ユーザーストーリーは独立して完了・テスト可能
- TDD: Test Implementation (RED) → Verify FAIL → Implementation (GREEN) → Verify PASS
- RED 出力は実装開始前に必ず生成
- 各フェーズ完了後にコミット
- 任意のチェックポイントで停止してストーリーを独立検証可能
- 回避: 曖昧なタスク、同一ファイル競合、ストーリー間の独立性を壊す依存関係
