# タスク: XML パイプライン分割

**入力**: 設計ドキュメント `/specs/010-split-xml-pipeline/`
**前提条件**: plan.md (必須), spec.md (必須), research.md

**テスト**: ユーザーストーリーフェーズでは TDD 必須。各フェーズは Test Implementation (RED) → Implementation (GREEN) → Verification ワークフローに従う。

## フォーマット: `[ID] [P?] [Story] 説明`

- **[P]**: 依存関係なし（異なるファイル、実行順序自由）
- **[Story]**: タスクが属するユーザーストーリー（例: US1, US2, US3）
- 説明には正確なファイルパスを含める

## ユーザーストーリーサマリー

| ID | タイトル | 優先度 | FR | シナリオ |
|----|----------|--------|-----|----------|
| US1 | テキストクリーニング単独実行 | P1 | FR-001 | `make clean-text` で cleaned_text.txt 生成 |
| US2 | 既存テキストから TTS 生成 | P2 | FR-002, FR-005 | `make xml-tts --cleaned-text` で音声生成 |
| US3 | 全ステップ一括実行 | P3 | FR-003 | `make run` で全ステップ順次実行 |

## パス規則

- **ソースコード**: `src/` at repository root
- **テスト**: `tests/` at repository root
- **Makefile**: repository root

---

## Phase 1: Setup (共有インフラ) — NO TDD

**目的**: プロジェクト初期化、既存コード調査、変更準備

- [x] T001 現在の実装を読む: src/xml2_pipeline.py の main() 関数（L88-224）
- [x] T002 [P] 現在の実装を読む: src/text_cleaner.py の clean_page_text() 関数
- [x] T003 [P] 現在の実装を読む: src/dict_manager.py の get_content_hash() 関数
- [x] T004 [P] 既存テストを読む: tests/test_xml2_pipeline.py
- [x] T005 [P] 既存 Makefile を読む: Makefile の gen-dict, xml-tts ターゲット
- [x] T006 編集・リネーム: specs/010-split-xml-pipeline/tasks/ph1-output-template.md → ph1-output.md

---

## Phase 2: User Story 1 - テキストクリーニング単独実行 (優先度: P1) MVP

**ゴール**: `make clean-text INPUT=sample.xml` で XML から cleaned_text.txt のみ生成。TTS 処理は実行しない。

**独立テスト**: `make clean-text INPUT=tests/fixtures/sample_book2.xml` を実行し、出力ディレクトリに cleaned_text.txt が生成されることを確認。

### Input

- [ ] T007 前フェーズ出力を読む: specs/010-split-xml-pipeline/tasks/ph1-output.md

### Test Implementation (RED)

- [ ] T008 [P] [US1] CLI 引数パーステストを実装: tests/test_text_cleaner_cli.py に test_parse_args_* クラス
- [ ] T009 [P] [US1] XML → cleaned_text.txt 生成テストを実装: tests/test_text_cleaner_cli.py に test_main_* テスト
- [ ] T010 [P] [US1] エラーハンドリングテストを実装: tests/test_text_cleaner_cli.py に test_file_not_found, test_invalid_xml テスト
- [ ] T011 [P] [US1] 出力ディレクトリ自動作成テストを実装: tests/test_text_cleaner_cli.py に test_output_directory_creation テスト
- [ ] T012 `make test` FAIL (RED) を確認
- [ ] T013 RED 出力を生成: specs/010-split-xml-pipeline/red-tests/ph2-test.md

### Implementation (GREEN)

- [ ] T014 RED テストを読む: specs/010-split-xml-pipeline/red-tests/ph2-test.md
- [ ] T015 [P] [US1] parse_args() 関数を実装: src/text_cleaner_cli.py に argparse で --input, --output オプション
- [ ] T016 [P] [US1] main() 関数を実装: src/text_cleaner_cli.py に XML パース → テキストクリーニング → cleaned_text.txt 保存
- [ ] T017 [US1] Makefile に clean-text ターゲットを追加: Makefile
- [ ] T018 `make test` PASS (GREEN) を確認

### Verification

- [ ] T019 `make test` で全テスト通過を確認（リグレッションなし）
- [ ] T020 `make clean-text INPUT=tests/fixtures/sample_book2.xml` で動作確認
- [ ] T021 編集・リネーム: specs/010-split-xml-pipeline/tasks/ph2-output-template.md → ph2-output.md

**チェックポイント**: User Story 1 が完全に機能し、独立してテスト可能であること

---

## Phase 3: User Story 2 - 既存テキストから TTS 生成 (優先度: P2)

**ゴール**: `make xml-tts --cleaned-text=/path/to/cleaned_text.txt` で既存の cleaned_text.txt から音声生成。テキストクリーニングをスキップして時間節約。

**独立テスト**: 既存の cleaned_text.txt を使用して `make xml-tts` を実行し、音声ファイルが生成されることを確認。

### Input

- [ ] T022 セットアップ分析を読む: specs/010-split-xml-pipeline/tasks/ph1-output.md
- [ ] T023 前フェーズ出力を読む: specs/010-split-xml-pipeline/tasks/ph2-output.md

### Test Implementation (RED)

- [ ] T024 [P] [US2] --cleaned-text オプションパーステストを追加: tests/test_xml2_pipeline.py に test_parse_args_cleaned_text_option テスト
- [ ] T025 [P] [US2] --cleaned-text 指定時のテキストクリーニングスキップテストを追加: tests/test_xml2_pipeline.py に test_main_with_cleaned_text_skips_cleaning テスト
- [ ] T026 [P] [US2] --cleaned-text ファイル不存在時のエラーテストを追加: tests/test_xml2_pipeline.py に test_cleaned_text_file_not_found テスト
- [ ] T027 [P] [US2] 後方互換性テストを追加: tests/test_xml2_pipeline.py に test_backward_compatibility_without_cleaned_text テスト
- [ ] T028 `make test` FAIL (RED) を確認
- [ ] T029 RED 出力を生成: specs/010-split-xml-pipeline/red-tests/ph3-test.md

### Implementation (GREEN)

- [ ] T030 RED テストを読む: specs/010-split-xml-pipeline/red-tests/ph3-test.md
- [ ] T031 [US2] parse_args() に --cleaned-text オプションを追加: src/xml2_pipeline.py
- [ ] T032 [US2] main() を修正して --cleaned-text 指定時はクリーニングスキップ: src/xml2_pipeline.py
- [ ] T033 `make test` PASS (GREEN) を確認

### Verification

- [ ] T034 `make test` で全テスト通過を確認（US1 テスト含む）
- [ ] T035 編集・リネーム: specs/010-split-xml-pipeline/tasks/ph3-output-template.md → ph3-output.md

**チェックポイント**: User Story 1 と 2 の両方が独立して動作すること

---

## Phase 4: User Story 3 - 全ステップ一括実行 (優先度: P3)

**ゴール**: `make run INPUT=sample.xml` で gen-dict → clean-text → xml-tts を順次実行。既存ワークフローとの後方互換性維持。

**独立テスト**: `make run INPUT=tests/fixtures/sample_book2.xml` を実行し、全ステップが順次実行されることを確認。

### Input

- [ ] T036 セットアップ分析を読む: specs/010-split-xml-pipeline/tasks/ph1-output.md
- [ ] T037 前フェーズ出力を読む: specs/010-split-xml-pipeline/tasks/ph3-output.md

### Implementation

- [ ] T038 [US3] Makefile に run ターゲットを追加: gen-dict → clean-text → xml-tts の順次実行
- [ ] T039 [US3] Makefile の .PHONY に run を追加
- [ ] T040 [US3] Makefile の help ターゲットが run を表示することを確認

### Verification

- [ ] T041 `make test` で全テスト通過を確認
- [ ] T042 `make help` で run ターゲットの説明が表示されることを確認
- [ ] T043 編集・リネーム: specs/010-split-xml-pipeline/tasks/ph4-output-template.md → ph4-output.md

**チェックポイント**: 全ユーザーストーリーが完成し、`make run` で一括実行可能

---

## Phase 5: Polish & 横断的関心事項 — NO TDD

**目的**: 複数ユーザーストーリーに影響する改善

### Input

- [ ] T044 セットアップ分析を読む: specs/010-split-xml-pipeline/tasks/ph1-output.md
- [ ] T045 前フェーズ出力を読む: specs/010-split-xml-pipeline/tasks/ph4-output.md

### Implementation

- [ ] T046 [P] コードクリーンアップ: 不要なコメントや重複コード削除
- [ ] T047 [P] ドキュメント更新: README.md に新しい Makefile ターゲットの説明追加
- [ ] T048 成功基準の検証: SC-001 テキストクリーニング 10 秒以内
- [ ] T049 成功基準の検証: SC-004 `make help` で全ターゲットの説明表示

### Verification

- [ ] T050 `make test` で全テスト通過を確認
- [ ] T051 `make lint` でリンターエラーなしを確認
- [ ] T052 編集・リネーム: specs/010-split-xml-pipeline/tasks/ph5-output-template.md → ph5-output.md

---

## 依存関係と実行順序

### フェーズ依存関係

- **Setup (Phase 1)**: 依存関係なし - メインエージェント直接実行
- **User Stories (Phase 2-4)**: TDD フロー (tdd-generator → phase-executor)
  - ユーザーストーリーは優先度順に進行 (P1 → P2 → P3)
- **Polish (Phase 5)**: 全ユーザーストーリー完了後 - phase-executor のみ

### 各ユーザーストーリーフェーズ内 (TDD フロー)

1. **Input**: セットアップ分析 (ph1) + 前フェーズ出力読み込み
2. **Test Implementation (RED)**: テストを先に書く → `make test` FAIL 確認 → RED 出力生成
3. **Implementation (GREEN)**: RED テスト読む → 実装 → `make test` PASS 確認
4. **Verification**: リグレッションなしを確認 → フェーズ出力生成

### エージェント委譲

- **Phase 1 (Setup)**: メインエージェント直接実行
- **Phase 2-4 (User Stories)**: tdd-generator (RED) → phase-executor (GREEN + Verification)
- **Phase 5 (Polish)**: phase-executor のみ

### [P] マーカー (依存関係なし)

`[P]` は「他タスクへの依存関係なし、実行順序自由」を示す。並列実行を保証するものではない。

- Setup タスク [P]: 異なるファイル/ディレクトリ作成で相互依存なし
- RED テスト [P]: 異なるテストファイルへの書き込みで相互依存なし
- GREEN 実装 [P]: 異なるソースファイルへの書き込みで相互依存なし
- ユーザーストーリー間: 各フェーズは前フェーズ出力に依存するため [P] 不適用

---

## フェーズ出力 & RED テストアーティファクト

### ディレクトリ構造

```
specs/010-split-xml-pipeline/
├── tasks.md                    # このファイル
├── tasks/
│   ├── ph1-output.md           # Phase 1 出力 (Setup 結果)
│   ├── ph2-output.md           # Phase 2 出力 (US1 GREEN 結果)
│   ├── ph3-output.md           # Phase 3 出力 (US2 GREEN 結果)
│   ├── ph4-output.md           # Phase 4 出力 (US3 結果)
│   └── ph5-output.md           # Phase 5 出力 (Polish 結果)
└── red-tests/
    ├── ph2-test.md             # Phase 2 RED テスト結果 (FAIL 確認)
    └── ph3-test.md             # Phase 3 RED テスト結果 (FAIL 確認)
```

### フェーズ出力フォーマット

| 出力タイプ | テンプレートファイル |
|------------|---------------------|
| `ph1-output.md` | `.specify/templates/ph1-output-template.md` |
| `phN-output.md` | `.specify/templates/phN-output-template.md` |
| `phN-test.md` | `.specify/templates/red-test-template.md` |

---

## 実装戦略

### MVP First (Phase 1 + Phase 2)

1. Phase 1 完了: Setup (既存コード調査)
2. Phase 2 完了: User Story 1 (RED → GREEN → Verification)
3. **停止して検証**: `make test` で全テスト通過を確認
4. 手動テスト: `make clean-text INPUT=sample.xml` で動作確認

### Full Delivery

1. Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5
2. 各フェーズでコミット: `feat(phase-N): description`

---

## テストカバレッジルール

**境界テスト原則**: データ変換が発生する**全ての境界**でテストを書く

```
[入力] → [パース] → [変換] → [出力生成] → [ファイル書込]
   ↓        ↓         ↓          ↓            ↓
 テスト    テスト    テスト     テスト       テスト
```

**チェックリスト**:
- [ ] 入力パーステスト
- [ ] 変換ロジックテスト
- [ ] **出力生成テスト** (見落としがち)
- [ ] End-to-End テスト (入力 → 最終出力)

---

## 備考

- [P] タスク = 依存関係なし、実行順序自由
- [Story] ラベルは特定のユーザーストーリーにタスクをマッピング
- 各ユーザーストーリーは独立して完了・テスト可能であるべき
- TDD: Test Implementation (RED) → Verify FAIL → Implementation (GREEN) → Verify PASS
- RED 出力は実装開始前に生成必須
- 各フェーズ完了後にコミット
- 任意のチェックポイントで停止してストーリーを独立検証可能
- 避けること: 曖昧なタスク、同一ファイル競合、独立性を損なうクロスストーリー依存
