# タスク: 読み辞書生成のXMLファイル対応

**Input**: 設計ドキュメント `/specs/006-xml-dict-support/`
**Prerequisites**: plan.md (必須), spec.md (必須), research.md, data-model.md

**テスト**: ユーザーストーリーフェーズでは TDD が必須。Test Implementation (RED) → Implementation (GREEN) → Verification のワークフローに従う。

**構成**: タスクはユーザーストーリー単位で整理し、各ストーリーを独立して実装・テスト可能にする。

## フォーマット: `[ID] [P?] [Story] 説明`

- **[P]**: 依存なし（異なるファイル、実行順序自由）
- **[Story]**: 対応するユーザーストーリー（US1, US2 など）
- 説明には正確なファイルパスを含める

## ユーザーストーリーサマリー

| ID  | タイトル | 優先度 | FR | シナリオ |
|-----|----------|--------|-----|----------|
| US1 | XMLファイルから読み辞書を生成 | P1 | FR-001,002,003,004,005,006 | XMLパース→チャプターグループ化→用語抽出→辞書生成 |
| US2 | Markdownファイルの既存動作を維持 | P1 | FR-001,007 | 既存MD入力のリグレッション防止+エッジケース |

## パス規約

- **ソースコード**: `src/` （リポジトリルート直下）
- **テスト**: `tests/` （リポジトリルート直下）
- **フィクスチャ**: `tests/fixtures/`
- **仕様**: `specs/006-xml-dict-support/`

---

## Phase 1: セットアップ（既存コード確認・準備） — TDD なし

**目的**: 既存実装の確認と変更準備

- [x] T001 既存の辞書生成コードを確認: `src/generate_reading_dict.py`
- [x] T002 [P] 既存のXMLパーサーを確認: `src/xml2_parser.py`
- [x] T003 [P] 既存の辞書管理モジュールを確認: `src/dict_manager.py`
- [x] T004 [P] 既存の用語抽出関数を確認: `src/llm_reading_generator.py`
- [x] T005 [P] 既存のテストを確認: `tests/test_xml2_parser.py`
- [x] T006 テスト用XMLフィクスチャを作成: `tests/fixtures/dict_test_book.xml`（チャプター2つ、各チャプターに技術用語を含むパラグラフ）
- [x] T007 `make test` で既存テストがすべてパスすることを確認
- [x] T008 セットアップ出力を編集・リネーム: `specs/006-xml-dict-support/tasks/ph1-output-template.md` → `ph1-output.md`

---

## Phase 2: ユーザーストーリー 1 - XMLファイルから読み辞書を生成 (Priority: P1) MVP

**Goal**: `main()` にXML分岐ロジックを追加し、XMLファイルからチャプター単位で用語抽出して辞書生成できるようにする

**独立テスト**: `make gen-dict INPUT=sample/book2.xml` を実行し、`data/{hash}/readings.json` が正しく生成されることを確認する

### Input

- [x] T009 前フェーズの出力を読む: `specs/006-xml-dict-support/tasks/ph1-output.md`

### Test Implementation (RED)

- [x] T010 [P] [US1] XMLファイル入力時に `parse_book2_xml()` が呼ばれることをテスト: `tests/test_generate_reading_dict.py`
- [x] T011 [P] [US1] ContentItemのチャプター単位グループ化と用語抽出をテスト: `tests/test_generate_reading_dict.py`
- [x] T012 [P] [US1] XML入力で辞書ファイルが正しいパス（`data/{hash}/readings.json`）に保存されることをテスト: `tests/test_generate_reading_dict.py`
- [x] T013 [P] [US1] `--merge` オプションがXML入力で動作することをテスト: `tests/test_generate_reading_dict.py`
- [x] T014 `make test` が FAIL することを確認 (RED)
- [x] T015 RED出力を生成: `specs/006-xml-dict-support/red-tests/ph2-test.md`

### Implementation (GREEN)

- [x] T016 REDテストを読む: `specs/006-xml-dict-support/red-tests/ph2-test.md`
- [x] T017 [US1] `main()` に拡張子判定の分岐ロジックを実装: `src/generate_reading_dict.py`（`.xml` → XMLフロー、`.md` → 既存フロー、その他 → エラー）
- [x] T018 [US1] XML分岐内にチャプターグループ化 + 用語抽出ロジックを実装: `src/generate_reading_dict.py`（`parse_book2_xml()` → `chapter_number` でグループ化 → `extract_technical_terms()` per group）
- [x] T019 `make test` が PASS することを確認 (GREEN)

### Verification

- [x] T020 `make test` ですべてのテストがパスすることを確認（リグレッションなし）
- [x] T021 フェーズ出力を編集・リネーム: `specs/006-xml-dict-support/tasks/phN-output-template.md` → `ph2-output.md`

**チェックポイント**: US1 が単独で機能し、XMLファイルから辞書が生成できること

---

## Phase 3: ユーザーストーリー 2 - Markdownファイルの既存動作維持 + エッジケース (Priority: P1)

**Goal**: MD入力のリグレッション防止 + 各種エッジケースのテストカバレッジ確保

**独立テスト**: `make gen-dict INPUT=sample/test.md` で従来通り辞書が生成されること + 不正入力に対する適切なエラー

### Input

- [x] T022 セットアップ出力を読む: `specs/006-xml-dict-support/tasks/ph1-output.md`
- [x] T023 前フェーズの出力を読む: `specs/006-xml-dict-support/tasks/ph2-output.md`

### Test Implementation (RED)

- [x] T024 [P] [US2] Markdown入力時に既存フロー（`split_into_pages`）が使われることをテスト: `tests/test_generate_reading_dict.py`
- [x] T025 [P] [US2] 未対応拡張子（`.txt` 等）でエラー終了することをテスト: `tests/test_generate_reading_dict.py`
- [x] T026 [P] [US2] 空XMLファイル（テキストなし）で空辞書が生成されることをテスト: `tests/test_generate_reading_dict.py`
- [x] T027 [P] [US2] 不正なXMLファイルでエラー終了することをテスト: `tests/test_generate_reading_dict.py`
- [x] T028 [P] [US2] チャプター番号なしのContentItemも用語抽出対象になることをテスト: `tests/test_generate_reading_dict.py`
- [x] T029 `make test` が FAIL することを確認 (RED)
- [x] T030 RED出力を生成: `specs/006-xml-dict-support/red-tests/ph3-test.md`

### Implementation (GREEN)

- [ ] T031 REDテストを読む: `specs/006-xml-dict-support/red-tests/ph3-test.md`
- [ ] T032 [US2] 必要に応じてエッジケース処理を追加: `src/generate_reading_dict.py`（不正XML例外キャッチ、空コンテンツ処理等）
- [ ] T033 [P] [US2] 空XMLフィクスチャを作成: `tests/fixtures/dict_test_empty.xml`
- [ ] T034 [P] [US2] 不正XMLフィクスチャを作成: `tests/fixtures/dict_test_invalid.xml`
- [ ] T035 `make test` が PASS することを確認 (GREEN)

### Verification

- [ ] T036 `make test` ですべてのテストがパスすることを確認（US1 + US2 リグレッションなし）
- [ ] T037 フェーズ出力を編集・リネーム: `specs/006-xml-dict-support/tasks/phN-output-template.md` → `ph3-output.md`

**チェックポイント**: US1 と US2 の両方が独立して機能すること

---

## Phase 4: ポリッシュ & 横断的関心事 — TDD なし

**目的**: コード品質の最終確認

### Input

- [ ] T038 セットアップ出力を読む: `specs/006-xml-dict-support/tasks/ph1-output.md`
- [ ] T039 前フェーズの出力を読む: `specs/006-xml-dict-support/tasks/ph3-output.md`

### Implementation

- [ ] T040 [P] 不要なインポートやデッドコードがないか確認・削除: `src/generate_reading_dict.py`
- [ ] T041 quickstart.md の手順で手動検証: `specs/006-xml-dict-support/quickstart.md`

### Verification

- [ ] T042 `make test` で全テストがパスすることを最終確認
- [ ] T043 フェーズ出力を編集・リネーム: `specs/006-xml-dict-support/tasks/phN-output-template.md` → `ph4-output.md`

---

## 依存関係 & 実行順序

### フェーズ依存関係

- **セットアップ (Phase 1)**: 依存なし — メインエージェント直接実行
- **ユーザーストーリー (Phase 2-3)**: TDDフロー (tdd-generator → phase-executor)
  - Phase 2 (US1) → Phase 3 (US2) の順序で進行
- **ポリッシュ (Phase 4)**: 全ユーザーストーリー完了後 — phase-executor のみ

### 各ユーザーストーリーフェーズ内（TDDフロー）

1. **Input**: セットアップ出力 (ph1) + 前フェーズ出力を読む
2. **Test Implementation (RED)**: テストを先に書く → `make test` FAIL を確認 → RED出力を生成
3. **Implementation (GREEN)**: REDテストを読む → 実装 → `make test` PASS を確認
4. **Verification**: リグレッションなしを確認 → フェーズ出力を生成

### エージェント委譲

- **Phase 1 (セットアップ)**: メインエージェント直接実行
- **Phase 2-3 (ユーザーストーリー)**: tdd-generator (RED) → phase-executor (GREEN + Verification)
- **Phase 4 (ポリッシュ)**: phase-executor のみ

### [P] マーカー（依存なし）

`[P]` は「他タスクへの依存なし、実行順序自由」を示す。並列実行を保証するものではない。

---

## フェーズ出力 & REDテストアーティファクト

### ディレクトリ構造

```
specs/006-xml-dict-support/
├── tasks.md                    # このファイル
├── tasks/
│   ├── ph1-output.md           # Phase 1 出力（セットアップ結果）
│   ├── ph2-output.md           # Phase 2 出力（US1 GREEN結果）
│   ├── ph3-output.md           # Phase 3 出力（US2 GREEN結果）
│   └── ph4-output.md           # Phase 4 出力（ポリッシュ結果）
└── red-tests/
    ├── ph2-test.md             # Phase 2 REDテスト結果（FAIL確認）
    └── ph3-test.md             # Phase 3 REDテスト結果（FAIL確認）
```

### フェーズ出力フォーマット

| 出力タイプ | テンプレートファイル |
|------------|---------------------|
| `ph1-output.md` | `.specify/templates/ph1-output-template.md` |
| `phN-output.md` | `.specify/templates/phN-output-template.md` |
| `phN-test.md` | `.specify/templates/red-test-template.md` |

---

## 実装戦略

### MVP ファースト (Phase 1 + Phase 2)

1. Phase 1 完了: セットアップ（既存コード確認・フィクスチャ作成）
2. Phase 2 完了: US1 (RED → GREEN → Verification)
3. **ストップ & 検証**: `make test` で全テストパスを確認
4. 手動検証: `make gen-dict INPUT=sample/book2.xml`

### フルデリバリー

1. Phase 1 → Phase 2 → Phase 3 → Phase 4
2. 各フェーズ完了時にコミット: `feat(phase-N): 説明`

---

## テストカバレッジルール

**境界テスト原則**: データ変換が発生するすべての境界にテストを書く

```
[XML入力] → [parse_book2_xml] → [チャプターグループ化] → [用語抽出] → [辞書保存]
    ↓            ↓                    ↓                    ↓            ↓
  テスト       テスト               テスト                テスト       テスト
```

**チェックリスト**:
- [ ] 入力パースのテスト（XML → ContentItem）
- [ ] 変換ロジックのテスト（チャプターグループ化）
- [ ] 用語抽出のテスト（extract_technical_terms 適用）
- [ ] 出力生成のテスト（readings.json の内容・パス）
- [ ] E2Eテスト（XML入力 → 最終辞書ファイル）

---

## メモ

- [P] タスク = 依存なし、実行順序自由
- [Story] ラベルはタスクとユーザーストーリーの対応を追跡可能にする
- 各ユーザーストーリーは独立して完了・テスト可能であること
- TDD: Test Implementation (RED) → FAIL確認 → Implementation (GREEN) → PASS確認
- RED出力は実装開始前に生成必須
- 各フェーズ完了時にコミット
- チェックポイントでストーリーを独立して検証可能
