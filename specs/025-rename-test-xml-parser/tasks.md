# Tasks: XML関連ファイル名の統一

**入力**: `/specs/025-rename-test-xml-parser/` のデザインドキュメント
**前提条件**: plan.md (必須), spec.md (必須), research.md

**テスト**: このタスクはリファクタリング（ファイルリネーム）のため、TDDワークフローは適用外。既存テストスイートを検証として使用する。

**構成**: タスクはユーザーストーリーごとにグループ化され、独立した実装とテストが可能。

## フォーマット: `[ID] [P?] [Story] Description`

- **[P]**: 依存関係なし（別ファイル、実行順序自由）
- **[Story]**: このタスクが属するユーザーストーリー（US1, US2など）
- 説明には正確なファイルパスを含める

## ユーザーストーリーサマリー

| ID | タイトル | 優先度 | FR | シナリオ |
|----|----------|--------|----|----------|
| US1 | ソースファイル名の統一 | P1 | FR-001,002,009-012 | ソースリネーム + インポート更新 |
| US2 | テストファイル名の統一 | P2 | FR-003-008 | テストリネーム + インポート更新 |

## パス規約

- **プロジェクトタイプ**: single（CLIツール）
- **ソース**: `src/` （リポジトリルート）
- **テスト**: `tests/` （リポジトリルート）

---

## Phase 1: Setup（事前確認）— TDDなし

**目的**: 現在の状態確認と変更準備

- [x] T001 現在のテスト状態を確認: `make test` を実行
- [x] T002 [P] 現在のカバレッジを記録: `make coverage` を実行
- [x] T003 [P] リネーム対象ファイルの存在確認: `src/xml2_parser.py`, `src/xml2_pipeline.py`
- [x] T004 [P] インポート参照を確認: `grep -r "xml2_parser\|xml2_pipeline" src/ tests/`
- [x] T005 出力生成: specs/025-rename-test-xml-parser/tasks/ph1-output.md

---

## Phase 2: User Story 1 - ソースファイル名の統一 (Priority: P1) MVP

**ゴール**: ソースファイルを `xml_` プレフィックスにリネームし、インポートを更新

**独立テスト**: `python -c "from src.xml_parser import parse_book2_xml"` が成功すること

### Input

- [x] T006 前フェーズ出力を読む: specs/025-rename-test-xml-parser/tasks/ph1-output.md

### Implementation

#### ソースファイルのリネーム

- [x] T007 [US1] `git mv src/xml2_parser.py src/xml_parser.py` を実行
- [x] T008 [US1] `git mv src/xml2_pipeline.py src/xml_pipeline.py` を実行

#### ソースファイル内のインポート更新

- [x] T009 [P] [US1] `src/xml_pipeline.py` の `from src.xml2_parser` を `from src.xml_parser` に更新
- [x] T010 [P] [US1] `src/text_cleaner_cli.py` の `from src.xml2_parser` を `from src.xml_parser` に更新
- [x] T011 [P] [US1] `src/chapter_processor.py` の `from src.xml2_parser` を `from src.xml_parser` に更新
- [x] T012 [P] [US1] `src/generate_reading_dict.py` の `from src.xml2_parser` を `from src.xml_parser` に更新
- [x] T013 [P] [US1] `src/dict_manager.py` の `from src.xml2_parser` を `from src.xml_parser` に更新

### Verification

- [x] T014 インポート検証: `python -c "from src.xml_parser import parse_book2_xml"` が成功
- [x] T015 インポート検証: `python -c "from src.xml_pipeline import main"` が成功
- [x] T016 出力生成: specs/025-rename-test-xml-parser/tasks/ph2-output.md

**チェックポイント**: ソースファイルのリネームとインポート更新が完了。テストはまだ失敗する可能性あり（テストファイル内のインポートが未更新のため）。

---

## Phase 3: User Story 2 - テストファイル名の統一 (Priority: P2)

**ゴール**: テストファイルを `xml_` プレフィックスにリネームし、インポートを更新

**独立テスト**: `pytest --collect-only` で全テストが検出されること

### Input

- [ ] T017 セットアップ分析を読む: specs/025-rename-test-xml-parser/tasks/ph1-output.md
- [ ] T018 前フェーズ出力を読む: specs/025-rename-test-xml-parser/tasks/ph2-output.md

### Implementation

#### テストファイルのリネーム

- [ ] T019 [US2] `git mv tests/test_xml2_parser.py tests/test_xml_parser.py` を実行
- [ ] T020 [P] [US2] `git mv tests/test_xml2_pipeline_args.py tests/test_xml_pipeline_args.py` を実行
- [ ] T021 [P] [US2] `git mv tests/test_xml2_pipeline_cleaned_text.py tests/test_xml_pipeline_cleaned_text.py` を実行
- [ ] T022 [P] [US2] `git mv tests/test_xml2_pipeline_integration.py tests/test_xml_pipeline_integration.py` を実行
- [ ] T023 [P] [US2] `git mv tests/test_xml2_pipeline_output.py tests/test_xml_pipeline_output.py` を実行
- [ ] T024 [P] [US2] `git mv tests/test_xml2_pipeline_processing.py tests/test_xml_pipeline_processing.py` を実行

#### テストファイル内のインポート更新（リネーム済みファイル）

- [ ] T025 [P] [US2] `tests/test_xml_parser.py` の `from src.xml2_parser` を `from src.xml_parser` に更新
- [ ] T026 [P] [US2] `tests/test_xml_pipeline_args.py` の `from src.xml2_pipeline` を `from src.xml_pipeline` に更新
- [ ] T027 [P] [US2] `tests/test_xml_pipeline_cleaned_text.py` の `from src.xml2_pipeline` を `from src.xml_pipeline` に更新
- [ ] T028 [P] [US2] `tests/test_xml_pipeline_integration.py` の `from src.xml2_pipeline` を `from src.xml_pipeline` に更新
- [ ] T029 [P] [US2] `tests/test_xml_pipeline_output.py` のインポートを更新（`xml2_parser` と `xml2_pipeline` 両方）
- [ ] T030 [P] [US2] `tests/test_xml_pipeline_processing.py` のインポートを更新（`xml2_parser` と `xml2_pipeline` 両方）

#### その他テストファイルのインポート更新

- [ ] T031 [P] [US2] `tests/test_dict_integration.py` の `from src.xml2_parser` を `from src.xml_parser` に更新
- [ ] T032 [P] [US2] `tests/test_generate_reading_dict.py` の `from src.xml2_parser` を `from src.xml_parser` に更新
- [ ] T033 [P] [US2] `tests/test_file_split.py` の `from src.xml2_pipeline` を `from src.xml_pipeline` に更新

### Verification

- [ ] T034 テスト検出確認: `pytest --collect-only` が全テストを検出
- [ ] T035 出力生成: specs/025-rename-test-xml-parser/tasks/ph3-output.md

**チェックポイント**: 全ファイルのリネームとインポート更新が完了。

---

## Phase 4: 検証 & 最終確認 — TDDなし

**目的**: 全体検証と残存参照チェック

### Input

- [ ] T036 セットアップ分析を読む: specs/025-rename-test-xml-parser/tasks/ph1-output.md
- [ ] T037 前フェーズ出力を読む: specs/025-rename-test-xml-parser/tasks/ph3-output.md

### Verification

- [ ] T038 `make test` を実行して全テスト通過を確認
- [ ] T039 `make coverage` を実行してカバレッジ維持を確認（ph1-output.mdの値と比較、±1%以内）
- [ ] T040 残存参照チェック: `grep -r "xml2_parser\|xml2_pipeline" src/ tests/` で結果が空
- [ ] T041 [P] 旧ファイル不在確認: `ls src/xml2_*.py tests/test_xml2_*.py` がエラー
- [ ] T042 [P] 新ファイル存在確認: `ls src/xml_parser.py src/xml_pipeline.py` が成功
- [ ] T043 [P] git履歴確認: `git log --follow --oneline -5 src/xml_parser.py` でリネーム履歴が追跡可能
- [ ] T044 出力生成: specs/025-rename-test-xml-parser/tasks/ph4-output.md

---

## 依存関係 & 実行順序

### フェーズ依存関係

- **Phase 1 (Setup)**: 依存なし - メインエージェント直接実行
- **Phase 2 (US1)**: Phase 1 に依存 - speckit:phase-executor
- **Phase 3 (US2)**: Phase 2 に依存 - speckit:phase-executor
- **Phase 4 (検証)**: Phase 3 に依存 - speckit:phase-executor

### エージェント委譲

- **Phase 1 (Setup)**: メインエージェント直接実行
- **Phase 2-4**: speckit:phase-executor（TDDなしリファクタリング）

### [P] マーカー（依存なし）

`[P]` は「他タスクへの依存なし、実行順序自由」を示す。並列実行を保証するものではない。

- Phase 2 の T009-T013: 異なるファイルへの書き込みで相互依存なし
- Phase 3 の T020-T024: 異なるファイルのリネームで相互依存なし
- Phase 3 の T025-T033: 異なるファイルへの書き込みで相互依存なし

---

## フェーズ出力アーティファクト

### ディレクトリ構造

```
specs/025-rename-test-xml-parser/
├── tasks.md                    # このファイル
└── tasks/
    ├── ph1-output.md           # Phase 1 出力（事前確認結果）
    ├── ph2-output.md           # Phase 2 出力（US1 ソースリネーム結果）
    ├── ph3-output.md           # Phase 3 出力（US2 テストリネーム結果）
    └── ph4-output.md           # Phase 4 出力（最終検証結果）
```

### フェーズ出力フォーマット

| 出力タイプ | テンプレートファイル |
|------------|----------------------|
| `ph1-output.md` | `.specify/templates/ph1-output-template.md` |
| `phN-output.md` | `.specify/templates/phN-output-template.md` |

---

## 実装戦略

### MVP First (Phase 1 + Phase 2)

1. Phase 1 完了: Setup（事前確認）
2. Phase 2 完了: User Story 1（ソースファイルリネーム）
3. **停止して検証**: `python -c "from src.xml_parser import parse_book2_xml"` が成功することを確認

### Full Delivery

1. Phase 1 → Phase 2 → Phase 3 → Phase 4
2. 各フェーズ後にコミット: `refactor(phase-N): description`

---

## 注記

- このタスクはリファクタリング（ファイルリネーム）のため、TDDワークフローは適用外
- 既存テストスイートが検証として機能する
- `git mv` を使用してgit履歴の追跡可能性を維持
- 各フェーズ後に `make test` で回帰テストを実行
- キャッシュファイル（`__pycache__/`, `.mypy_cache/`）は自動再生成されるため手動削除不要
