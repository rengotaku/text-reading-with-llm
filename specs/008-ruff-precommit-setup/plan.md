# Implementation Plan: ruff導入・pre-commit設定・ファイル分割

**Branch**: `008-ruff-precommit-setup` | **Date**: 2026-02-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-ruff-precommit-setup/spec.md`

## Summary

ruffリンター/フォーマッターの導入、pre-commitフックによる自動品質チェック、および`src/xml2_pipeline.py`（651行）の600行以下への分割を行う。pyproject.tomlにruff設定を集約し、コミット時の自動チェックでコード品質を維持する仕組みを構築する。

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: ruff, pre-commit（開発用依存関係として追加）
**Storage**: N/A
**Testing**: pytest（既存テストスイート: `tests/` ディレクトリ）
**Target Platform**: Linux（ローカル開発環境）
**Project Type**: Single project
**Performance Goals**: N/A（開発ツール設定のため）
**Constraints**: ファイルサイズ上限600行、ruffルール E/F/I/W、line-length 120
**Scale/Scope**: Pythonソースファイル12個、テストファイル9個

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution file未作成のためゲートチェックをスキップ。本フィーチャーは開発ツール設定とリファクタリングのみで、アーキテクチャに複雑性を追加しない。

## Project Structure

### Documentation (this feature)

```text
specs/008-ruff-precommit-setup/
├── plan.md              # This file
├── research.md          # Phase 0: ruff設定・ファイル分割戦略調査
├── quickstart.md        # Phase 1: セットアップ手順
├── checklists/
│   └── requirements.md  # 仕様品質チェックリスト
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
# 新規・変更ファイル
pyproject.toml                    # [新規] ruff設定
.pre-commit-config.yaml           # [新規] pre-commitフック設定

# ファイル分割対象
src/xml2_pipeline.py              # [変更] メインエントリーポイント（main, parse_args）
src/chapter_processor.py          # [新規] 音声処理（process_chapters, process_content, load_sound, sanitize_filename）
src/process_manager.py            # [新規] PID管理（get_pid_file_path, kill_existing_process, write_pid_file, cleanup_pid_file）

# 既存ファイル（ruff適用対象、構造変更なし）
src/
├── dict_manager.py
├── generate_reading_dict.py
├── llm_reading_generator.py
├── mecab_reader.py
├── number_normalizer.py
├── punctuation_normalizer.py
├── reading_dict.py
├── text_cleaner.py
├── voicevox_client.py
└── xml2_parser.py

tests/
├── test_xml2_pipeline.py         # [変更] import先は変更不要（後方互換性維持）
└── ...（その他テストファイル）
```

**Structure Decision**: 既存のフラット構造（`src/` 直下）を維持。xml2_pipeline.pyから論理的なまとまりで2ファイルを抽出し、元ファイルからre-exportして後方互換性を確保。

## File Split Strategy

### xml2_pipeline.py (651行) → 3ファイル分割

| 抽出先 | 関数 | 行範囲 | 推定行数 |
|--------|------|--------|---------|
| `src/process_manager.py` | get_pid_file_path, kill_existing_process, write_pid_file, cleanup_pid_file | 49-124 | ~90行 |
| `src/chapter_processor.py` | sanitize_filename, load_sound, process_chapters, process_content | 202-507 | ~320行 |
| `src/xml2_pipeline.py` (残り) | parse_args, main + re-exports | 127-199, 510-651 | ~240行 |

### 後方互換性

`src/xml2_pipeline.py` に以下のre-exportを追加:
```python
from src.chapter_processor import (
    process_chapters,
    process_content,
    load_sound,
    sanitize_filename,
)
from src.process_manager import (
    get_pid_file_path,
    kill_existing_process,
    write_pid_file,
    cleanup_pid_file,
)
```

これにより `from src.xml2_pipeline import process_chapters` 等の既存importが動作し続ける。

## Complexity Tracking

> 複雑性の追加なし。ファイル分割はre-exportパターンで後方互換性を維持する標準的なリファクタリング。
