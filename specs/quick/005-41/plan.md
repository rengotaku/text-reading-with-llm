---
status: completed
created: 2026-03-07
branch: quick/005-41
---

# OpenJTalk警告回避: テキスト先頭の句読点・長音記号を除去

## 概要

VOICEVOXの内部で使用されるOpenJTalkから、テキストの先頭に句読点や長音記号がある場合に警告が発生する。音声生成自体は正常に動作するが、ログが汚れるため前処理で回避する。

## ゴール

- [x] テキスト先頭の句読点・記号を除去する前処理関数を追加
- [x] synthesize メソッドで前処理を適用
- [x] ユニットテストを追加

## スコープ外

- テキスト中間・末尾の記号処理
- OpenJTalk 本体の修正

## 前提条件

- 既存の `VoicevoxSynthesizer.synthesize` メソッドを修正
- 正規表現パターン: `^[、。，．,.\\s…ー－]+`

---

## 実装タスク

### Phase 1: 前処理関数の追加

- [x] T001 [src/voicevox_client.py] `clean_text_for_voicevox` 関数を追加（先頭の句読点・記号を除去）

### Phase 2: synthesize メソッドへの適用

- [x] T002 [src/voicevox_client.py] `synthesize` メソッド内で `clean_text_for_voicevox` を呼び出し

### Phase 3: テスト

- [x] T003 [tests/test_voicevox_client.py] `clean_text_for_voicevox` のユニットテストを追加

---

## リスク

| レベル | 内容 |
|-------|------|
| LOW   | 正規表現パターンが不足している可能性（追加の記号が必要になる場合がある） |

---

## 完了条件

- [x] 全タスク完了
- [x] テスト通過
- [x] コードレビュー完了
