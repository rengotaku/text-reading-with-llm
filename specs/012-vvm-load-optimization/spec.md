# Feature Specification: VOICEVOX モデルロード最適化

**Feature Branch**: `012-vvm-load-optimization`
**Created**: 2026-02-24
**Status**: Draft
**Input**: GitHub Issue #17 - perf: VOICEVOX モデルロードの最適化とバージョン不一致警告の解消

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 必要なモデルのみロード (Priority: P1)

開発者として、`make xml-tts` を実行する際に、指定した `--style-id` に対応する VVM ファイルのみをロードしたい。これにより、起動時間を短縮し、メモリ使用量を削減できる。

**Why this priority**: 現在 26 個すべての VVM ファイルをロードしており、実際に使用するのは 1 つだけ。起動時間とリソース効率に直結する最も重要な改善。

**Independent Test**: `make xml-tts` を実行し、ログ出力で指定した style_id に対応する VVM ファイルのみがロードされることを確認できる。

**Acceptance Scenarios**:

1. **Given** style_id 0 を指定している状態で、**When** `make xml-tts` を実行する、**Then** style_id 0 を含む VVM ファイル 1 つのみがロードされる
2. **Given** 複数の style_id を使用するシナリオで、**When** XML 内に異なる style_id が指定されている、**Then** それらの style_id に対応する VVM ファイルのみがロードされる
3. **Given** 存在しない style_id を指定した状態で、**When** `make xml-tts` を実行する、**Then** 明確なエラーメッセージが表示される

---

### User Story 2 - バージョン警告の解消 (Priority: P2)

開発者として、VVM ファイルと VOICEVOX Core のバージョンを一致させ、警告メッセージを解消したい。これにより、ログ出力がクリーンになり、潜在的な互換性問題を防止できる。

**Why this priority**: 機能的には動作するが、警告メッセージがログを汚染し、実際の問題を見落とすリスクがある。P1 の後に対応すべき品質改善。

**Independent Test**: `make xml-tts` を実行し、バージョン不一致に関する WARNING ログが出力されないことを確認できる。

**Acceptance Scenarios**:

1. **Given** VVM ファイルと VOICEVOX Core のバージョンが一致している状態で、**When** `make xml-tts` を実行する、**Then** バージョン不一致の警告が表示されない
2. **Given** モデルロード完了後、**When** 音声生成を実行する、**Then** 既存の動作と同じ品質の音声が生成される

---

### User Story 3 - 後方互換性の維持 (Priority: P3)

開発者として、最適化後も既存のワークフローがそのまま動作することを確認したい。

**Why this priority**: 機能追加ではなく最適化のため、既存機能の破壊がないことの確認は必須だが、P1/P2 の実装後の検証作業。

**Independent Test**: 既存のテストスイートがすべてパスし、生成される音声ファイルが同一であることを確認できる。

**Acceptance Scenarios**:

1. **Given** 最適化実装後、**When** 既存のテストを実行する、**Then** すべてのテストがパスする
2. **Given** 同じ入力 XML と style_id で、**When** 最適化前後で音声生成を実行する、**Then** 同一の音声出力が得られる

---

### Edge Cases

- style_id が VVM ファイル内に存在しない場合、明確なエラーを返す
- 複数の style_id が同一 VVM ファイルに含まれる場合、重複ロードしない
- VVM ファイルが破損または欠損している場合、適切にエラーハンドリングする

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: システムは、指定された style_id に対応する VVM ファイルのみをロードしなければならない
- **FR-002**: システムは、style_id から対応する VVM ファイルを特定するマッピング機能を提供しなければならない
- **FR-003**: システムは、同一セッション内で複数の style_id が使用される場合、対応する各 VVM ファイルを必要に応じてロードしなければならない
- **FR-004**: システムは、存在しない style_id が指定された場合、ユーザーに明確なエラーメッセージを表示しなければならない
- **FR-005**: システムは、VVM ファイルと VOICEVOX Core のバージョンを一致させ、警告を発生させてはならない
- **FR-006**: システムは、最適化後も既存の音声生成機能を損なってはならない

### Key Entities

- **VVM ファイル**: VOICEVOX の音声モデルファイル。各ファイルは 1 つ以上の style_id を含む
- **style_id**: 音声スタイルの識別子。VVM ファイル内の特定の声質や話し方を指定
- **VOICEVOX Core**: 音声合成エンジン。VVM ファイルをロードして音声を生成

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `make xml-tts` の起動からモデルロード完了までの時間が、従来比で 80% 以上短縮される（26 モデル → 1 モデルロードのため）
- **SC-002**: 音声生成時のメモリ使用量が、従来比で大幅に削減される
- **SC-003**: `make xml-tts` 実行時に、バージョン不一致に関する警告が 0 件である
- **SC-004**: 既存のテストスイートが 100% パスする
- **SC-005**: 同一入力に対する音声出力が、最適化前後で一致する

## Assumptions

- style_id と VVM ファイルのマッピングは、VOICEVOX の公式仕様または既存コードから取得可能
- VOICEVOX Core のバージョンアップまたは VVM ファイルの再取得により、バージョン不一致は解消可能
- 現在の `load_all_models()` の呼び出しは、選択的ロードに置き換え可能

## Dependencies

- `src/xml2_pipeline.py`: `load_all_models()` 呼び出し箇所の変更
- `src/voicevox_client.py`: `load_model()`, `load_all_models()` 実装の確認・修正
- `Makefile`: VOICEVOX_VERSION 定義の確認

## Out of Scope

- 新しい音声スタイルの追加
- GUI やユーザーインターフェースの変更
- VOICEVOX Core 自体のアップグレード（バージョン一致のための VVM 再取得を優先）
