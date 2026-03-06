---
status: completed
created: 2026-03-05
branch: 040-fix-config-input-default
issue: "#40"
---

# fix: config.yaml の input デフォルト値修正

## 概要

`config.yaml` のデフォルト `input` 値が `sample/book.md` (Markdown) になっているが、パイプラインコードは XML 形式を期待している。これを `sample/book2.xml` に修正する。

追加で発見した `STYLE_ID_TO_VVM` マッピングの誤りも修正。

## ゴール

- [x] `config.yaml` の input を `sample/book2.xml` に変更
- [x] 不要なサンプルファイルの削除を検討
- [x] `STYLE_ID_TO_VVM` マッピングを実際のVVMファイル内容に合わせて修正

## スコープ外

- パイプラインコードの変更
- 新しいサンプルファイルの追加

## 前提条件

- `sample/book2.xml` が存在すること（確認済み）
- パイプラインは `xml_parser.py` を使用（確認済み）

---

## 実装タスク

### Phase 1: 修正

- [x] T001 [config.yaml] `input: sample/book.md` を `input: sample/book2.xml` に変更

### Phase 2: 確認

- [x] T002 不要ファイル調査: `sample/book.md` と `sample/book.xml` の使用箇所確認
- [x] T003 `make run` で動作確認

---

## リスク

| レベル | 内容 |
|-------|------|
| LOW   | サンプルファイル削除による影響（他で使用されている可能性） |

---

## 確認事項（Issue より）

- [ ] `sample/book.md` は使用されているか？不要なら削除検討
- [ ] `sample/book.xml` (旧形式) も不要なら削除検討
