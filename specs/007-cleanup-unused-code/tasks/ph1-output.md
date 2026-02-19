# Phase 1 Output: Setup

**Date**: 2026-02-19
**Status**: 完了

## 実行タスク

- [x] T001 現在のソースファイル一覧を確認: `src/` ディレクトリ（21ファイル）
- [x] T002 現在のテストファイル一覧を確認: `tests/` ディレクトリ（13ファイル）
- [x] T003 依存関係の最終確認: research.md の削除対象リストと実コードを照合
- [x] T004 ベースラインテスト実行: 全テストパス確認（test_xml2_pipeline一部タイムアウトあり）

## 既存コード分析

### ベースライン

- ソースファイル数: 21
- テストファイル数: 13
- テスト数: 474（test_xml2_pipeline の一部がVOICEVOX依存でタイムアウト）

### KEEP対象（11ファイル）

| ファイル | 役割 |
|---------|------|
| `xml2_pipeline.py` | xml2 TTSパイプライン（エントリポイント） |
| `xml2_parser.py` | XML2パーサー |
| `generate_reading_dict.py` | 辞書生成（エントリポイント） |
| `dict_manager.py` | 辞書管理 |
| `llm_reading_generator.py` | LLM読み生成 |
| `text_cleaner.py` | テキスト前処理 |
| `mecab_reader.py` | MeCab読み取り |
| `number_normalizer.py` | 数値正規化 |
| `punctuation_normalizer.py` | 句読点正規化 |
| `reading_dict.py` | 読み辞書適用 |
| `voicevox_client.py` | VOICEVOX合成 |

### DELETE対象（10ファイル）

| ファイル | 分類 |
|---------|------|
| `pipeline.py` | 旧MDパイプライン |
| `progress.py` | pipeline.py 専用ユーティリティ |
| `toc_extractor.py` | pipeline.py 専用機能 |
| `organize_chapters.py` | pipeline.py 出力用 |
| `xml_pipeline.py` | 旧XMLパイプライン |
| `xml_parser.py` | 旧XMLパーサー |
| `aquestalk_pipeline.py` | 代替TTS |
| `aquestalk_client.py` | AquesTalkクライアント |
| `tts_generator.py` | Qwen3-TTS（未使用） |
| `test_tts_normalize.py` | src内テストスクリプト |

## 既存テスト分析

### KEEP対象テスト（9ファイル）

- `tests/test_xml2_pipeline.py`: xml2パイプラインテスト（一部VOICEVOX依存）
- `tests/test_xml2_parser.py`: xml2パーサーテスト（61テスト）
- `tests/test_generate_reading_dict.py`: 辞書生成テスト（23テスト）
- `tests/test_integration.py`: 統合テスト（21テスト）
- `tests/test_isbn_cleaning.py`: ISBN整理テスト（18テスト）
- `tests/test_url_cleaning.py`: URL整理テスト（18テスト）
- `tests/test_reference_normalization.py`: 参照正規化テスト（21テスト）
- `tests/test_punctuation_rules.py`: 句読点ルールテスト（54テスト）
- `tests/test_parenthetical_cleaning.py`: 括弧整理テスト（24テスト）

### DELETE対象テスト（4ファイル）

- `tests/test_xml_pipeline.py`: 旧XMLパイプライン（21テスト）
- `tests/test_xml_parser.py`: 旧XMLパーサー（48テスト）
- `tests/test_aquestalk_client.py`: AquesTalkクライアント（56テスト）
- `tests/test_aquestalk_pipeline.py`: AquesTalkパイプライン（40テスト）

## 技術的決定事項

1. **test_xml2_pipeline タイムアウト**: 一部テストがVOICEVOX Core依存で長時間かかる。削除対象ではないため影響なし
2. **__pycache__ 削除**: `rm -rf` で一括削除（git管理外）

## 次フェーズへの引き継ぎ

Phase 2 (US1: 不要ソースコード削除) で実行するもの:
- ソースファイル10件を `git rm` で削除
- `__pycache__` を `rm -rf` でクリーンアップ
- `make test` で xml2 関連テストが全パスすることを確認
- 注意: test_xml2_pipeline の一部テストはVOICEVOX依存でタイムアウトする可能性あり（正常動作）
