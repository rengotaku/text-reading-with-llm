# Phase 3 Output: 長文セクションの分割処理

**Date**: 2026-03-14
**Status**: Completed
**User Story**: US2 - 長文セクションの分割処理

## 実行タスク

- [x] T038 REDテストを読む: specs/041-book-dialogue-conversion/red-tests/ph3-test.md
- [x] T039 [P] [US2] 文字数判定関数 should_split() を実装: src/dialogue_converter.py
- [x] T040 [P] [US2] 見出し単位分割関数 split_by_heading() を実装: src/dialogue_converter.py
- [x] T041 [US2] 分割コンテキスト維持ロジックを実装: src/dialogue_converter.py
- [x] T042 [US2] convert_section() に分割ロジックを統合: src/dialogue_converter.py
- [x] T043 `make test` で PASS (GREEN) を確認
- [x] T044 `make test` ですべてのテストがパスすることを確認（US1回帰含む）
- [x] T045 `make coverage` でカバレッジ70%以上を確認
- [x] T046 Edit: specs/041-book-dialogue-conversion/tasks/ph3-output.md

## 変更ファイル

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| src/dialogue_converter.py | 修正 | should_split(), split_by_heading() を追加、convert_section() に分割ロジックを統合 |
| specs/041-book-dialogue-conversion/tasks/ph3-output.md | 新規 | このファイル |
| specs/041-book-dialogue-conversion/tasks.md | 修正 | Phase 3 タスクを完了状態に更新 |

## テスト結果

```
============================= 710 passed in 4.01s ==============================

Coverage:
src/dialogue_converter.py  173   8  95%
TOTAL                     1641 363  78%

Required test coverage of 70% reached. Total coverage: 77.88%
710 passed in 5.58s
```

**カバレッジ**: 78%（目標: 70%以上） — 達成
**dialogue_converter.py カバレッジ**: 95%

## 実装詳細

### 新規関数

- `SPLIT_THRESHOLD = 4000`: 分割閾値定数

- `should_split(section: Section) -> bool`:
  - 全段落の文字数合計を計算
  - 4,000文字**超過**（厳密な大なり比較）でTrueを返す
  - None入力時はFalseを返すガード処理あり

- `split_by_heading(section: Section) -> list[Section]`:
  - 段落内の `## ` で始まる行を分割点として使用
  - 見出し行はサブセクションのタイトルとして使用（段落からは除外）
  - サブセクション番号は `{original_number}-{index}` 形式（例: "1.1-1", "1.1-2"）
  - `chapter_number` を全サブセクションに継承
  - 見出しがない場合は元のセクションをそのまま返す
  - None入力、空段落リストのエッジケース対応済み

### 変更した既存関数

- `convert_section()`:
  - `should_split()` を呼び出して分割要否を事前判定
  - 分割が必要な場合、`split_by_heading()` で最初のサブセクションを変換対象にする
  - `was_split` フラグを `should_split()` の結果に基づいて設定

## 発見した問題

特になし。全47件のREDテストが初回実装でPASSに転じた。

## 次フェーズへの引き継ぎ

Phase 4（US3: 対話形式音声の生成）で実装予定:

- `parse_dialogue_xml()`: 対話XMLをパースして発話リストを取得
- `get_style_id()`: 話者（narrator/A/B）のVOICEVOXスタイルIDを取得
- `synthesize_utterance()`: 個別発話の音声合成
- `concatenate_section_audio()`: セクション内音声を結合
- `process_dialogue_sections()`: 統合関数
- `parse_args()` / `main()`: dialogue_pipeline.py のCLIエントリーポイント

**依存関係**:
- `Section`, `DialogueBlock`, `ConversionResult`, `should_split()`, `split_by_heading()`, `convert_section()` は Phase 3 で実装完了
- `to_dialogue_xml()` の出力スキーマ（`<dialogue-section>`, `<introduction>`, `<dialogue>`, `<conclusion>`, `<utterance>`）は Phase 4 のXMLパーサーが前提とする

**注意事項**:
- `convert_section()` は分割時に最初のサブセクションのみを変換する（全サブセクションを変換する高度な統合は Phase 5 以降で検討）
- `split_by_heading()` の空サブセクション（見出し直後に別の見出しが続くケース）はスキップされる
