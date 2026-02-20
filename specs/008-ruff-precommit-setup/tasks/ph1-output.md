# Phase 1 Output: Setup

**Date**: 2026-02-21
**Status**: 完了

## 実行タスク

- [x] T001 現在の src/xml2_pipeline.py の構造と依存関係を分析
- [x] T002 現在の tests/test_xml2_pipeline.py のimportパターンを分析
- [x] T003 pyproject.toml を新規作成（ruff設定）
- [x] T004 requirements-dev.txt を新規作成（ruff, pre-commit）
- [x] T005 .pre-commit-config.yaml を新規作成
- [x] T006 Makefile に setup-dev, lint, format, coverage ターゲットを追加
- [x] T007 pip install -r requirements-dev.txt で開発用依存関係をインストール
- [x] T008 ruff check / ruff format --check で現在の違反状況を確認

## 既存コード分析

### src/xml2_pipeline.py (651行)

**構造**:
- `get_pid_file_path`: PIDファイルパス取得
- `kill_existing_process`: 既存プロセス終了
- `write_pid_file`: PIDファイル書き込み
- `cleanup_pid_file`: PIDファイル削除
- `parse_args`: CLI引数パース
- `sanitize_filename`: ファイル名サニタイズ
- `load_sound`: 音声ファイルロード（モノラル変換・リサンプリング）
- `process_chapters`: チャプター別WAV生成
- `process_content`: コンテンツ処理（TTS呼び出し）
- `main`: メインエントリーポイント

**分割方針（Phase 3で実行）**:
1. `process_manager.py`: PID管理関数4個（get_pid_file_path, kill_existing_process, write_pid_file, cleanup_pid_file）→ ~90行
2. `chapter_processor.py`: 音声処理関数4個（sanitize_filename, load_sound, process_chapters, process_content）→ ~320行
3. `xml2_pipeline.py`（残り）: parse_args, main + re-export → ~240行

### tests/test_xml2_pipeline.py (2075行)

**importパターン**:
- `from src.xml2_pipeline import process_chapters`
- `from src.xml2_pipeline import process_content`
- `from src.xml2_pipeline import sanitize_filename`
- `from src.xml2_pipeline import load_sound`
- `from src.xml2_pipeline import main, parse_args`
- `from src.xml2_parser import ContentItem, HeadingInfo, CHAPTER_MARKER`

**注意**: re-exportパターンにより既存importパスは変更不要

## 既存テスト分析

- `tests/test_xml2_pipeline.py`: parse_args, load_sound, process_content, process_chapters, main, sanitize_filename をカバー
- **新規作成予定**: tests/test_ruff_config.py（Phase 2: ruff/pre-commit設定検証）
- **新規作成予定**: tests/test_file_split.py（Phase 3: ファイル分割・import互換性検証）

## 新規作成ファイル

### pyproject.toml
- ruff設定: line-length=120, target-version=py310, select=E,F,I,W
- isort known-first-party: src

### requirements-dev.txt
- ruff, pre-commit

### .pre-commit-config.yaml
- astral-sh/ruff-pre-commit v0.9.7: ruff --fix, ruff-format

### Makefile更新
- `setup-dev`: dev deps install + pre-commit install
- `lint`: ruff check + ruff format --check
- `format`: ruff check --fix + ruff format
- `coverage`: pytest --cov

## ruff違反状況（ベースライン）

- **lint**: 69エラー（48件auto-fixable）
- **format**: 18ファイルが要フォーマット
- **主なエラー**: F401(未使用import), I001(import順), E501(行長), W291(末尾空白)

## 次フェーズへの引き継ぎ

Phase 2 (US1+US2 - ruff設定・pre-commit・既存コード修正) で実装するもの:
- `ruff check --fix .` で自動修正 → 残りを手動対応
- `ruff format .` で全ファイルフォーマット
- `pre-commit install` でgit hookを登録
- tests/test_ruff_config.py でruff/pre-commit設定の検証テスト
- 注意点: F401の自動修正で使用中importを削除しないよう確認が必要
