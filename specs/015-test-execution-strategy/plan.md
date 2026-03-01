---
status: completed
created: 2026-03-01
branch: 015-test-execution-strategy
---

# Plan: test_xml2_pipeline.py ハング問題の修正

## 概要

`test_xml2_pipeline.py` がフルスイート実行時にハングする問題を修正する。
個別テストは高速（< 1秒）だが、連続実行でテスト間の状態分離の問題が発生している。

## ゴール

- [x] フルテストスイートが5分以内に完了する（1.02秒で完了）
- [x] pytest-timeout が正常に機能する
- [x] テスト間の状態分離が保証される

## スコープ外

- 変更検出機能（make test-changed）
- 軽量テストマーカー（@pytest.mark.quick）
- CI ワークフローの変更

## 前提条件

- 調査済み: モックは適切に使用されている（660箇所）
- 調査済み: 個別テストは高速
- 調査済み: `test_xml2_pipeline.py` (79テスト/2380行) が原因

## 実装タスク

### Phase 1: 原因特定

- [x] T001 [tests/test_xml2_pipeline.py] グローバル状態・シングルトンの使用箇所を特定
- [x] T002 [src/xml2_pipeline.py] main() 内の状態リークの可能性を調査（PID ファイル、atexit 登録など）
- [x] T003 [tests/] conftest.py の追加が必要か判断

### Phase 2: 修正

- [x] T004 [tests/test_xml2_pipeline.py] テスト間の状態分離を修正（autouse フィクスチャで PID 管理と atexit をモック化）

### Phase 3: 確認

- [x] T005 フルテストスイートが5分以内に完了することを確認（1.02秒で完了）
- [x] T006 個別テストの実行速度が維持されていることを確認（全79テスト、1秒以内）

## リスク

| レベル | 内容 |
|-------|------|
| MEDIUM | 原因がテスト間状態分離以外の可能性（プロセスフォーク、リソース競合） |

## 調査メモ

調査で判明した事実:
- `test_xml2_pipeline.py` 内の後半テスト（TestMainWithCleanedTextSkipsCleaning 等）でハング
- `main()` 関数は PID ファイル管理、atexit 登録を行う（状態リークの可能性）
- モックは適切に設定されているが、`clean_page_text` 等は一部モック化されていない

Phase 1 調査結果:
- **根本原因**: PID ファイルと atexit 登録の累積
  - `main()` は `tmp/pids/` に PID ファイルを作成し、atexit で cleanup_pid_file を登録
  - テストが main() を複数回呼ぶと atexit ハンドラが累積
  - `kill_existing_process()` の `time.sleep(0.5)` が累積してハング
- **修正方針**:
  - PID ファイルと atexit 登録をモック化
  - または、各テストでクリーンアップを保証
