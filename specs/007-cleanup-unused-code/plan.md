# Implementation Plan: 不要機能の削除リファクタリング

**Branch**: `007-cleanup-unused-code` | **Date**: 2026-02-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-cleanup-unused-code/spec.md`

## Summary

現在使用している xml2 パイプライン（`xml2_pipeline.py`）と辞書生成（`generate_reading_dict.py`）のみを残し、旧MDパイプライン・旧XMLパイプライン・AquesTalkパイプライン等の不要モジュール（10ソースファイル + 4テストファイル）を削除する。Makefile の不要ターゲットも整理する。

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: xml.etree.ElementTree, voicevox_core, MeCab, soundfile, numpy
**Storage**: Files（`data/{hash}/readings.json`）
**Testing**: pytest
**Target Platform**: Linux（ローカル開発環境）
**Project Type**: Single project
**Performance Goals**: N/A（リファクタリング、機能変更なし）
**Constraints**: 既存機能の動作を変更しないこと
**Scale/Scope**: ソースファイル10件削除、テスト4件削除、Makefile修正

## Constitution Check

*GATE: Constitution file not found — no gates to check. Proceeding.*

## Project Structure

### Documentation (this feature)

```text
specs/007-cleanup-unused-code/
├── plan.md              # This file
├── research.md          # 依存関係分析結果
├── quickstart.md        # 削除手順ガイド
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (削除後の状態)

```text
src/
├── xml2_pipeline.py          # エントリポイント: xml-tts xml2
├── xml2_parser.py            # XML2パーサー
├── generate_reading_dict.py  # エントリポイント: gen-dict
├── dict_manager.py           # 辞書管理
├── llm_reading_generator.py  # LLM読み生成
├── text_cleaner.py           # テキスト前処理
├── mecab_reader.py           # MeCab読み取り
├── number_normalizer.py      # 数値正規化
├── punctuation_normalizer.py # 句読点正規化
├── reading_dict.py           # 読み辞書適用
└── voicevox_client.py        # VOICEVOX合成

tests/
├── test_xml2_pipeline.py
├── test_xml2_parser.py
├── test_generate_reading_dict.py
├── test_isbn_cleaning.py
├── test_url_cleaning.py
├── test_reference_normalization.py
├── test_punctuation_rules.py
├── test_parenthetical_cleaning.py
├── test_integration.py
└── fixtures/
```

**Structure Decision**: 既存のフラット構造を維持。不要ファイルのみ削除し、ディレクトリ構成は変更しない。

### 削除対象ファイル

**ソースファイル（10件）**:

| ファイル | 分類 | 依存元 |
|---------|------|--------|
| `src/pipeline.py` | 旧MDパイプライン | なし（エントリポイント） |
| `src/progress.py` | ユーティリティ | pipeline.py のみ |
| `src/toc_extractor.py` | 旧機能 | pipeline.py のみ |
| `src/organize_chapters.py` | 旧機能 | pipeline.py 出力用 |
| `src/xml_pipeline.py` | 旧XMLパイプライン | なし（エントリポイント） |
| `src/xml_parser.py` | 旧XMLパーサー | xml_pipeline, aquestalk_pipeline |
| `src/aquestalk_pipeline.py` | 代替TTS | なし（エントリポイント） |
| `src/aquestalk_client.py` | 代替TTS | aquestalk_pipeline のみ |
| `src/tts_generator.py` | Qwen3-TTS | なし（未使用） |
| `src/test_tts_normalize.py` | テストスクリプト | なし（src内テスト） |

**テストファイル（4件）**:

| ファイル | 対象モジュール |
|---------|--------------|
| `tests/test_xml_pipeline.py` | xml_pipeline.py |
| `tests/test_xml_parser.py` | xml_parser.py |
| `tests/test_aquestalk_client.py` | aquestalk_client.py |
| `tests/test_aquestalk_pipeline.py` | aquestalk_pipeline.py |

**Makefile ターゲット削除/修正**:
- 削除: `run`, `run-simple`, `toc`, `organize`
- 修正: `xml-tts`（PARSER分岐削除、xml2直接実行に変更）
- 修正: `.PHONY`（削除ターゲット除去）

## User Story Phases

### Phase 1 (P1): 不要ソースコード削除

- ソースファイル10件を `git rm` で削除
- `__pycache__` 内の対応 `.pyc` ファイルを削除
- 既存テスト（xml2関連）が全てパスすることを確認

### Phase 2 (P2): 不要テストコード削除

- テストファイル4件を `git rm` で削除
- `make test` で残テストが全パスすることを確認

### Phase 3 (P3): Makefile・設定ファイル整理

- 不要ターゲット削除、`xml-tts` 修正
- `make help` で全ターゲット確認
- 最終テスト実行

## Complexity Tracking

> 違反なし — シンプルなファイル削除リファクタリング
