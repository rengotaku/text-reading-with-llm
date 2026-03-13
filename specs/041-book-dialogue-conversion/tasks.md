# Tasks: 書籍内容の対話形式変換

**入力**: `/specs/041-book-dialogue-conversion/` のデザインドキュメント
**前提**: plan.md, spec.md, research.md, data-model.md, contracts/

**テスト**: User Story フェーズでは TDD 必須。Test Implementation (RED) → Implementation (GREEN) → Verification のワークフロー。

## フォーマット: `[ID] [P?] [Story] 説明`

- **[P]**: 依存関係なし（異なるファイル、実行順序自由）
- **[Story]**: タスクが属するユーザーストーリー（US1, US2, US3）
- ファイルパスを説明に含める

## User Story サマリー

| ID | タイトル | 優先度 | FR | シナリオ |
|----|----------|--------|-----|----------|
| US1 | 書籍セクションを対話形式に変換 | P1 | FR-001〜005,007 | セクション→対話テキスト |
| US2 | 長文セクションの分割処理 | P2 | FR-006 | 4,000文字超→分割変換 |
| US3 | 対話形式音声の生成 | P3 | FR-008〜010 | 対話テキスト→複数話者音声 |

## パス規約

- **ソースコード**: `src/` (リポジトリルート)
- **テスト**: `tests/` (リポジトリルート)
- **スペック**: `specs/041-book-dialogue-conversion/`

---

## Phase 1: Setup (共有インフラ) — NO TDD

**目的**: プロジェクト初期化、既存コード確認、変更準備

- [X] T001 既存のXMLパーサー実装を確認: src/xml_parser.py
- [X] T002 [P] 既存のVOICEVOXクライアント実装を確認: src/voicevox_client.py
- [X] T003 [P] 既存のLLM辞書生成実装を確認: src/llm_reading_generator.py
- [X] T004 [P] 既存のテキストクリーナー実装を確認: src/text_cleaner.py
- [X] T005 [P] 既存のテスト構造を確認: tests/
- [X] T006 data-model.md に基づきデータクラス設計を確認: specs/041-book-dialogue-conversion/data-model.md
- [X] T007 contracts/cli-spec.md に基づきCLI設計を確認: specs/041-book-dialogue-conversion/contracts/cli-spec.md
- [X] T008 `make test` で既存テストがすべてパスすることを確認
- [X] T009 Edit: specs/041-book-dialogue-conversion/tasks/ph1-output.md

---

## Phase 2: User Story 1 - 書籍セクションを対話形式に変換 (Priority: P1) MVP

**ゴール**: セクション内容をLLMで対話形式に変換し、博士と助手の会話テキストを生成する

**独立テスト**: 単一セクションを入力し、対話形式XMLが出力されることを確認

### Input

- [x] T010 前フェーズ出力を読む: specs/041-book-dialogue-conversion/tasks/ph1-output.md

### Test Implementation (RED)

- [x] T011 [P] [US1] DialogueBlock, Utterance データクラスのテストを実装: tests/test_dialogue_converter.py
- [x] T012 [P] [US1] セクション抽出関数のテストを実装: tests/test_dialogue_converter.py
- [x] T013 [P] [US1] LLM構造分析（intro/dialogue/conclusion分類）のテストを実装: tests/test_dialogue_converter.py
- [x] T014 [P] [US1] LLM対話生成（A/B発話）のテストを実装: tests/test_dialogue_converter.py
- [x] T015 [P] [US1] 対話XMLシリアライズのテストを実装: tests/test_dialogue_converter.py
- [x] T016 [P] [US1] エッジケース（短文、空セクション）のテストを実装: tests/test_dialogue_converter.py
- [x] T017 `make test` で FAIL (RED) を確認
- [x] T018 REDテスト出力を生成: specs/041-book-dialogue-conversion/red-tests/ph2-test.md

### Implementation (GREEN)

- [x] T019 REDテストを読む: specs/041-book-dialogue-conversion/red-tests/ph2-test.md
- [x] T020 [P] [US1] DialogueBlock, Utterance, ConversionResult データクラスを実装: src/dialogue_converter.py
- [x] T021 [P] [US1] セクション抽出関数 extract_sections() を実装: src/dialogue_converter.py
- [x] T022 [US1] LLM構造分析関数 analyze_structure() を実装: src/dialogue_converter.py
- [x] T023 [US1] LLM対話生成関数 generate_dialogue() を実装: src/dialogue_converter.py
- [x] T024 [US1] 対話XMLシリアライズ関数 to_dialogue_xml() を実装: src/dialogue_converter.py
- [x] T025 [US1] convert_section() 統合関数を実装: src/dialogue_converter.py
- [x] T026 `make test` で PASS (GREEN) を確認

### Verification

- [x] T027 `make test` ですべてのテストがパスすることを確認
- [x] T028 `make coverage` でカバレッジ70%以上を確認
- [x] T029 Edit: specs/041-book-dialogue-conversion/tasks/ph2-output.md

**チェックポイント**: 単一セクションの対話変換が動作し、独立してテスト可能

---

## Phase 3: User Story 2 - 長文セクションの分割処理 (Priority: P2)

**ゴール**: 4,000文字を超えるセクションを見出し単位で分割し、それぞれを対話形式に変換

**独立テスト**: 5,000文字以上のセクションを入力し、分割された複数の対話ブロックが出力されることを確認

### Input

- [x] T030 セットアップ分析を読む: specs/041-book-dialogue-conversion/tasks/ph1-output.md
- [x] T031 前フェーズ出力を読む: specs/041-book-dialogue-conversion/tasks/ph2-output.md

### Test Implementation (RED)

- [x] T032 [P] [US2] 文字数判定関数のテストを実装: tests/test_dialogue_converter.py
- [x] T033 [P] [US2] 見出し単位分割関数のテストを実装: tests/test_dialogue_converter.py
- [x] T034 [P] [US2] 分割後の連続性（コンテキスト維持）テストを実装: tests/test_dialogue_converter.py
- [x] T035 [P] [US2] 境界ケース（3,500〜4,500文字）のテストを実装: tests/test_dialogue_converter.py
- [x] T036 `make test` で FAIL (RED) を確認
- [x] T037 REDテスト出力を生成: specs/041-book-dialogue-conversion/red-tests/ph3-test.md

### Implementation (GREEN)

- [x] T038 REDテストを読む: specs/041-book-dialogue-conversion/red-tests/ph3-test.md
- [x] T039 [P] [US2] 文字数判定関数 should_split() を実装: src/dialogue_converter.py
- [x] T040 [P] [US2] 見出し単位分割関数 split_by_heading() を実装: src/dialogue_converter.py
- [x] T041 [US2] 分割コンテキスト維持ロジックを実装: src/dialogue_converter.py
- [x] T042 [US2] convert_section() に分割ロジックを統合: src/dialogue_converter.py
- [x] T043 `make test` で PASS (GREEN) を確認

### Verification

- [x] T044 `make test` ですべてのテストがパスすることを確認（US1回帰含む）
- [x] T045 `make coverage` でカバレッジ70%以上を確認
- [x] T046 Edit: specs/041-book-dialogue-conversion/tasks/ph3-output.md

**チェックポイント**: 長文セクションも分割処理で対話形式に変換可能

---

## Phase 4: User Story 3 - 対話形式音声の生成 (Priority: P3)

**ゴール**: 対話形式XMLから3話者（ナレーター、博士、助手）による音声ファイルを生成

**独立テスト**: 対話形式XMLを入力し、3種類の声で読み上げられた音声ファイルが生成されることを確認

### Input

- [x] T047 セットアップ分析を読む: specs/041-book-dialogue-conversion/tasks/ph1-output.md
- [x] T048 前フェーズ出力を読む: specs/041-book-dialogue-conversion/tasks/ph3-output.md

### Test Implementation (RED)

- [x] T049 [P] [US3] Speaker データクラスのテストを実装: tests/test_dialogue_pipeline.py
- [x] T050 [P] [US3] 対話XMLパース関数のテストを実装: tests/test_dialogue_pipeline.py
- [x] T051 [P] [US3] 話者別スタイルID取得のテストを実装: tests/test_dialogue_pipeline.py
- [x] T052 [P] [US3] 発話単位音声生成のテストを実装: tests/test_dialogue_pipeline.py
- [x] T053 [P] [US3] セクション音声結合のテストを実装: tests/test_dialogue_pipeline.py
- [x] T054 [P] [US3] CLI引数パースのテストを実装: tests/test_dialogue_pipeline.py
- [x] T055 `make test` で FAIL (RED) を確認
- [x] T056 REDテスト出力を生成: specs/041-book-dialogue-conversion/red-tests/ph4-test.md

### Implementation (GREEN)

- [x] T057 REDテストを読む: specs/041-book-dialogue-conversion/red-tests/ph4-test.md
- [x] T058 [P] [US3] Speaker データクラスを実装: src/dialogue_pipeline.py
- [x] T059 [P] [US3] 対話XMLパース関数 parse_dialogue_xml() を実装: src/dialogue_pipeline.py
- [x] T060 [P] [US3] 話者別スタイルID取得 get_style_id() を実装: src/dialogue_pipeline.py
- [x] T061 [US3] 発話単位音声生成 synthesize_utterance() を実装: src/dialogue_pipeline.py
- [x] T062 [US3] セクション音声結合 concatenate_section_audio() を実装: src/dialogue_pipeline.py
- [x] T063 [US3] process_dialogue_sections() 統合関数を実装: src/dialogue_pipeline.py
- [x] T064 [US3] CLI引数パース parse_args() を実装: src/dialogue_pipeline.py
- [x] T065 [US3] main() エントリーポイントを実装: src/dialogue_pipeline.py
- [x] T066 `make test` で PASS (GREEN) を確認

### Verification

- [x] T067 `make test` ですべてのテストがパスすることを確認（US1,US2回帰含む）
- [x] T068 `make coverage` でカバレッジ70%以上を確認
- [x] T069 Edit: specs/041-book-dialogue-conversion/tasks/ph4-output.md

**チェックポイント**: 対話形式から3話者音声が生成可能

---

## Phase 5: CLI統合 & Makefile (Priority: P3続)

**ゴール**: dialogue_converter.py のCLI実装とMakefile統合

### Input

- [x] T070 セットアップ分析を読む: specs/041-book-dialogue-conversion/tasks/ph1-output.md
- [x] T071 前フェーズ出力を読む: specs/041-book-dialogue-conversion/tasks/ph4-output.md

### Test Implementation (RED)

- [x] T072 [P] dialogue_converter.py CLI引数パースのテストを実装: tests/test_dialogue_converter.py
- [x] T073 [P] dialogue_converter.py main() 統合テストを実装: tests/test_dialogue_converter.py
- [x] T074 `make test` で FAIL (RED) を確認
- [x] T075 REDテスト出力を生成: specs/041-book-dialogue-conversion/red-tests/ph5-test.md

### Implementation (GREEN)

- [ ] T076 REDテストを読む: specs/041-book-dialogue-conversion/red-tests/ph5-test.md
- [ ] T077 [P] dialogue_converter.py の parse_args() を実装: src/dialogue_converter.py
- [ ] T078 dialogue_converter.py の main() を実装: src/dialogue_converter.py
- [ ] T079 `make test` で PASS (GREEN) を確認

### Verification

- [ ] T080 `make test` ですべてのテストがパスすることを確認
- [ ] T081 Edit: specs/041-book-dialogue-conversion/tasks/ph5-output.md

---

## Phase 6: Polish & クロスカッティング — NO TDD

**目的**: 全User Storyに影響する改善

### Input

- [ ] T082 セットアップ分析を読む: specs/041-book-dialogue-conversion/tasks/ph1-output.md
- [ ] T083 前フェーズ出力を読む: specs/041-book-dialogue-conversion/tasks/ph5-output.md

### Implementation

- [ ] T084 [P] Makefile に dialogue-convert, dialogue-tts, dialogue ターゲットを追加: Makefile
- [ ] T085 [P] pyproject.toml に新規モジュールの除外設定を追加（必要な場合）: pyproject.toml
- [ ] T086 [P] コードの型アノテーション確認と修正: src/dialogue_converter.py, src/dialogue_pipeline.py
- [ ] T087 quickstart.md の検証を実行: specs/041-book-dialogue-conversion/quickstart.md

### Verification

- [ ] T088 `make lint` でリントエラーがないことを確認
- [ ] T089 `make test` ですべてのテストがパスすることを確認
- [ ] T090 `make coverage` でカバレッジ70%以上を確認
- [ ] T091 Edit: specs/041-book-dialogue-conversion/tasks/ph6-output.md

---

## Dependencies & Execution Order

### Phase 依存関係

- **Setup (Phase 1)**: 依存なし - メインエージェント直接実行
- **User Stories (Phase 2〜5)**: TDD フロー (speckit:tdd-generator → speckit:phase-executor)
  - User Story は優先度順に順次実行 (P1 → P2 → P3)
- **Polish (Phase 6)**: 全 User Story 完了後 - speckit:phase-executor のみ

### 各 User Story フェーズ内 (TDD フロー)

1. **Input**: セットアップ分析 (ph1) + 前フェーズ出力を読む
2. **Test Implementation (RED)**: テストを先に書く → `make test` FAIL 確認 → RED 出力生成
3. **Implementation (GREEN)**: RED テストを読む → 実装 → `make test` PASS 確認
4. **Verification**: 回帰なし確認 → フェーズ出力生成

### Agent 委譲

- **Phase 1 (Setup)**: メインエージェント直接実行
- **Phase 2〜5 (User Stories)**: speckit:tdd-generator (RED) → speckit:phase-executor (GREEN + Verification)
- **Phase 6 (Polish)**: speckit:phase-executor のみ

### [P] マーカー (依存なし)

`[P]` は「他タスクへの依存なし、実行順序自由」を示す。並列実行を保証するものではない。

- Setup タスク [P]: 異なるファイル/ディレクトリの作成で相互依存なし
- RED テスト [P]: 異なるテストファイルへの書き込みで相互依存なし
- GREEN 実装 [P]: 異なるソースファイルへの書き込みで相互依存なし
- User Story 間: 各 Phase は前 Phase 出力に依存するため [P] 適用外

---

## Phase Output & RED Test Artifacts

### ディレクトリ構造

```
specs/041-book-dialogue-conversion/
├── tasks.md                    # このファイル
├── tasks/
│   ├── ph1-output.md           # Phase 1 出力 (Setup 結果)
│   ├── ph2-output.md           # Phase 2 出力 (US1 GREEN 結果)
│   ├── ph3-output.md           # Phase 3 出力 (US2 GREEN 結果)
│   ├── ph4-output.md           # Phase 4 出力 (US3 GREEN 結果)
│   ├── ph5-output.md           # Phase 5 出力 (CLI統合 結果)
│   └── ph6-output.md           # Phase 6 出力 (Polish 結果)
└── red-tests/
    ├── ph2-test.md             # Phase 2 RED テスト結果 (FAIL 確認)
    ├── ph3-test.md             # Phase 3 RED テスト結果
    ├── ph4-test.md             # Phase 4 RED テスト結果
    └── ph5-test.md             # Phase 5 RED テスト結果
```

### Phase Output フォーマット

| Output タイプ | テンプレートファイル |
|--------------|---------------------|
| `ph1-output.md` | `.specify/templates/ph1-output-template.md` |
| `phN-output.md` | `.specify/templates/phN-output-template.md` |
| `phN-test.md` | `.specify/templates/red-test-template.md` |

---

## Implementation Strategy

### MVP First (Phase 1 + Phase 2)

1. Phase 1 完了: Setup (既存コード確認)
2. Phase 2 完了: User Story 1 (RED → GREEN → Verification)
3. **停止して検証**: `make test` ですべてのテストがパスすることを確認
4. 手動テスト: 単一セクションの対話変換を確認

### Full Delivery

1. Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
2. 各フェーズでコミット: `feat(phase-N): 説明`

---

## Test Coverage Rules

**境界テスト原則**: データ変換が発生するすべての境界でテストを書く

```
[入力XML] → [パース] → [LLM変換] → [対話生成] → [XMLシリアライズ] → [ファイル出力]
     ↓         ↓          ↓            ↓              ↓                ↓
   Test      Test       Test         Test           Test             Test
```

**チェックリスト**:
- [ ] 入力パーステスト (xml_parser との連携)
- [ ] LLM変換ロジックテスト (構造分析、対話生成)
- [ ] **出力生成テスト** (対話XMLシリアライズ)
- [ ] End-to-End テスト (入力XML → 対話XML → 音声ファイル)

---

## Notes

- [P] タスク = 依存なし、実行順序自由
- [Story] ラベルはタスクを特定のユーザーストーリーにマッピング
- 各ユーザーストーリーは独立して完了・テスト可能
- TDD: Test Implementation (RED) → FAIL 確認 → Implementation (GREEN) → PASS 確認
- RED 出力は実装開始前に生成必須
- 各フェーズ完了後にコミット
- チェックポイントで停止してストーリーを独立検証可能
- 避けるべき: 曖昧なタスク、同一ファイル競合、ストーリー間の独立性を破る依存
