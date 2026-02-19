# Research: 不要機能の削除リファクタリング

**Date**: 2026-02-19
**Branch**: `007-cleanup-unused-code`

## 依存関係分析

### アクティブなエントリポイント

1. `src/xml2_pipeline.py` — `make xml-tts PARSER=xml2`
2. `src/generate_reading_dict.py` — `make gen-dict`

### KEEP: アクティブモジュール（11ファイル）

```
xml2_pipeline.py
  → xml2_parser.py
  → dict_manager.py
  → voicevox_client.py
  → text_cleaner.py
      → llm_reading_generator.py
      → mecab_reader.py
      → number_normalizer.py
      → punctuation_normalizer.py
      → reading_dict.py
      → dict_manager.py

generate_reading_dict.py
  → xml2_parser.py
  → dict_manager.py
  → llm_reading_generator.py
  → text_cleaner.py
```

### DELETE: 不要モジュール（10ファイル）

| モジュール | 分類 | 理由 |
|-----------|------|------|
| `pipeline.py` | 旧MDパイプライン | xml2未使用、独立エントリポイント |
| `progress.py` | ユーティリティ | pipeline.py のみから使用 |
| `toc_extractor.py` | 旧機能 | pipeline.py のみから使用 |
| `organize_chapters.py` | 旧機能 | pipeline.py 出力の整理用 |
| `xml_pipeline.py` | 旧XMLパイプライン | xml2_pipeline に置き換え済み |
| `xml_parser.py` | 旧XMLパーサー | xml2_parser に置き換え済み |
| `aquestalk_pipeline.py` | 代替TTS | 未使用 |
| `aquestalk_client.py` | 代替TTS | aquestalk_pipeline のみから使用 |
| `tts_generator.py` | Qwen3-TTS | 未使用 |
| `test_tts_normalize.py` | テストスクリプト | src/ 内、本番コードではない |

### DELETE: 不要テストファイル（4ファイル）

| テストファイル | 対象モジュール |
|--------------|--------------|
| `test_xml_pipeline.py` | xml_pipeline.py |
| `test_xml_parser.py` | xml_parser.py |
| `test_aquestalk_client.py` | aquestalk_client.py |
| `test_aquestalk_pipeline.py` | aquestalk_pipeline.py |

### Makefile 変更

**削除ターゲット**:
- `run` / `run-simple` — 旧MDパイプライン用
- `toc` — toc_extractor 用
- `organize` — organize_chapters 用
- `xml-tts` の `else` 分岐（旧XML用）

**修正ターゲット**:
- `xml-tts` — PARSER 分岐を削除し xml2 のみに
- `setup` / `setup-voicevox` — 残すがAquesTalk関連があれば削除
- `clean` — 不要な参照があれば修正

### 判断ポイント

- **voicevox_client.py**: KEEP — xml2_pipeline から直接使用
- **mecab_reader.py**: KEEP — text_cleaner から使用
- **progress.py**: DELETE — pipeline.py のみから使用、xml2_pipeline は未使用
- **reading_dict.py**: KEEP — text_cleaner から使用（dict_manager とは別機能）
- **toc_extractor.py**: DELETE — pipeline.py のみから使用、xml2_pipeline は未使用
- **organize_chapters.py**: DELETE — pipeline.py 出力の整理用、xml2 では未使用
