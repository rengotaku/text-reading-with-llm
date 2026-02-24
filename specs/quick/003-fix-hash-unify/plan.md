---
status: completed
created: 2026-02-24
branch: quick/003-fix-hash-unify
issue: 15
---

# fix: gen-dict と xml-tts のハッシュ計算を一元化

## 概要

`make gen-dict INPUT=sample/book2.xml` で生成した辞書が `make xml-tts` 実行時にロードされない問題を修正。
ハッシュ計算を `dict_manager.py` に一元化し、両コマンドで同一ハッシュを使用するようにする。

## ゴール

- [x] `gen-dict` と `xml-tts` で同一ハッシュを使用
- [x] 統合テストで辞書ロードを検証
- [x] 辞書ロード状況がログで明確にわかる

## スコープ外

- MD ファイルのハッシュ方式変更（既存動作維持）
- 既存辞書のマイグレーション

## 前提条件

- `xml2_parser.parse_book2_xml()` は既存のまま使用
- XML → パース後テキストのハッシュに統一（`xml2_pipeline.py` の方式を採用）

---

## 実装タスク

### Phase 1: ハッシュ関数追加

- [x] T001 [src/dict_manager.py] `get_xml_content_hash(xml_path)` 関数を追加
  - `parse_book2_xml()` でパース → テキスト結合 → ハッシュ計算
  - 既存の `get_content_hash()` を内部で使用

### Phase 2: generate_reading_dict.py 修正

- [x] T002 [src/generate_reading_dict.py] XML ファイル時に `get_xml_content_hash()` を使用
  - `get_dict_path()` の代わりに新関数でハッシュ取得
  - `save_dict()` も新ハッシュベースに修正

### Phase 3: テスト追加

- [x] T003 [tests/test_dict_integration.py] 統合テスト作成
  - gen-dict で辞書生成 → xml-tts で辞書ロード確認
  - 同一ハッシュであることを検証

### Phase 4: ログ強化

- [x] T004 [src/dict_manager.py] 辞書ロード時の WARNING メッセージ改善
  - ロード成功/失敗を明示的にログ出力

---

## リスク

| レベル | 内容 |
|-------|------|
| MEDIUM | 既存の XML 辞書が新ハッシュと不一致になる（手動移行必要） |
| LOW | パース処理の追加によるオーバーヘッド |

---

## 完了条件

- [x] 全タスク完了
- [x] `make test` 通過
- [x] `make gen-dict INPUT=sample/book2.xml` で生成した辞書が `make xml-tts` でロードされる
