# Phase 3 Output: US3 - xml2_pipeline.py ファイル分割

**Date**: 2026-02-21
**Status**: 完了
**User Story**: US3 - 大規模ファイルの分割

## 実行タスク

- [x] T033 REDテストを読む: specs/008-ruff-precommit-setup/red-tests/ph3-test.md
- [x] T034 [US3] src/process_manager.py を新規作成（get_pid_file_path, kill_existing_process, write_pid_file, cleanup_pid_file を移動）
- [x] T035 [US3] src/chapter_processor.py を新規作成（sanitize_filename, load_sound, process_chapters, process_content を移動）
- [x] T036 [US3] src/xml2_pipeline.py をリファクタリング（parse_args, main を残し、re-exportを追加）
- [x] T037 make test でPASS確認 (GREEN)
- [x] T038 各ファイルの行数確認（全て600行以下）
- [x] T039 ruff check で分割後ファイルがruffチェック合格を確認
- [x] T040 ruff format --check で分割後ファイルのフォーマット確認
- [x] T041 make test で全テストパスを確認（リグレッションなし）

## 変更ファイル一覧

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| src/process_manager.py | 新規 | PID管理関数4個を抽出（91行） |
| src/chapter_processor.py | 新規 | 音声処理関数4個を抽出（325行） |
| src/xml2_pipeline.py | 修正 | メインエントリーポイントのみ残し、re-export追加（218行） |
| tests/test_xml2_pipeline.py | 修正 | パッチパスを更新（src.xml2_pipeline.* → src.chapter_processor.*） |

## 分割結果

### ファイル行数

```
  218 src/xml2_pipeline.py      (元: 613行 → 395行削減)
   91 src/process_manager.py     (新規)
  325 src/chapter_processor.py   (新規)
  634 total                      (元: 613行 → 21行増加は re-export とコメントによる)
```

全ファイルが600行以下の制約を満たしています。

### 分割詳細

**src/process_manager.py** (91行):
- `get_pid_file_path`: PIDファイルパス取得
- `kill_existing_process`: 既存プロセス終了
- `write_pid_file`: PIDファイル書き込み
- `cleanup_pid_file`: PIDファイル削除
- 必要なimport: os, signal, logging, pathlib

**src/chapter_processor.py** (325行):
- `sanitize_filename`: ファイル名サニタイズ
- `load_sound`: 音声ファイルロード（モノラル変換・リサンプリング）
- `process_chapters`: チャプター別WAV生成
- `process_content`: コンテンツ処理（TTS呼び出し）
- 必要なimport: re, logging, pathlib, numpy, soundfile, src.text_cleaner, src.voicevox_client, src.xml2_parser

**src/xml2_pipeline.py** (218行):
- `parse_args`: CLI引数パース
- `main`: メインエントリーポイント
- re-export: 分割した2モジュールから全関数を re-export（後方互換性維持）

### re-export パターン

```python
# Re-exports from split modules (for backward compatibility)
from src.chapter_processor import (  # noqa: F401
    load_sound,
    process_chapters,
    process_content,
    sanitize_filename,
)
from src.process_manager import (  # noqa: F401
    cleanup_pid_file,
    get_pid_file_path,
    kill_existing_process,
    write_pid_file,
)
```

noqa: F401 コメントで ruff の未使用import警告を抑制（re-export目的のため）

## テスト結果

### file split tests (新規)

```
============================= 27 passed in 0.07s ==============================
```

全27テストがPASS:
- process_manager.py のimport互換性テスト: 6件
- chapter_processor.py のimport互換性テスト: 6件
- xml2_pipeline.py のre-export動作テスト: 12件
- 各ファイルの行数上限テスト: 3件

### xml2_pipeline tests (既存)

全69テストがPASS（パッチパス更新後）

**カバレッジ**: 既存カバレッジ維持（目標: 80%）

### ruff check/format

```
# ruff check
All checks passed!

# ruff format --check
3 files already formatted
```

## 発見した問題/課題

1. **テストのパッチパス更新が必要**: chapter_processor.py に移動した関数を使用するテストは、パッチパスを `src.xml2_pipeline.*` から `src.chapter_processor.*` に更新する必要があった
   - 対応: tests/test_xml2_pipeline.py のパッチパス76箇所を sed で一括更新
   - 影響: clean_page_text, generate_audio, save_audio, concatenate_audio_files のパッチ
   - 解決: 全テストがPASSすることを確認

2. **ruff の未使用import警告**: re-export目的のimportがF401 (unused import) として検出された
   - 対応: noqa: F401 コメントを追加して re-export であることを明示
   - 理由: これらのimportは xml2_pipeline.py では直接使用されないが、他モジュールからの互換import のために必要

## 次フェーズへの引き継ぎ

Phase 4 (Polish・最終検証) で実装するもの:
- ファイル分割完了、全成功基準達成済み
- ruff check/format がプロジェクト全体でクリーン
- 全テスト（96テスト）がPASS
- 注意点: re-export パターンにより既存コードの import パスは変更不要だが、新規コードでは各モジュールから直接 import することを推奨
