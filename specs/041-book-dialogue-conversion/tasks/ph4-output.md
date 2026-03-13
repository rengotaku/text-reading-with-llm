# Phase 4 Output: 対話形式音声の生成

**Date**: 2026-03-14
**Status**: Completed
**User Story**: US3 - 対話形式音声の生成

## 実行タスク

- [x] T057 REDテストを読む: specs/041-book-dialogue-conversion/red-tests/ph4-test.md
- [x] T058 [P] Speaker データクラスを実装: src/dialogue_pipeline.py
- [x] T059 [P] 対話XMLパース関数 parse_dialogue_xml() を実装: src/dialogue_pipeline.py
- [x] T060 [P] 話者別スタイルID取得 get_style_id() を実装: src/dialogue_pipeline.py
- [x] T061 発話単位音声生成 synthesize_utterance() を実装: src/dialogue_pipeline.py
- [x] T062 セクション音声結合 concatenate_section_audio() を実装: src/dialogue_pipeline.py
- [x] T063 process_dialogue_sections() 統合関数を実装: src/dialogue_pipeline.py
- [x] T064 CLI引数パース parse_args() を実装: src/dialogue_pipeline.py
- [x] T065 main() エントリーポイントを実装: src/dialogue_pipeline.py
- [x] T066 `make test` で PASS (GREEN) を確認
- [x] T067 `make test` ですべてのテストがパスすることを確認（US1,US2回帰含む）
- [x] T068 `make coverage` でカバレッジ70%以上を確認
- [x] T069 Edit: specs/041-book-dialogue-conversion/tasks/ph4-output.md

## 変更ファイル

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| src/dialogue_pipeline.py | 新規 | 対話形式XMLから3話者音声を生成するパイプライン実装 |
| specs/041-book-dialogue-conversion/tasks.md | 変更 | Phase 4 タスクを完了済みに更新 |

## 実装内容

### src/dialogue_pipeline.py の主要コンポーネント

| 関数/クラス | 説明 |
|-------------|------|
| `Speaker` | 話者データクラス（id, role, voicevox_style_id, character_name） |
| `DEFAULT_STYLE_MAPPING` | デフォルトスタイルIDマッピング（narrator=13, A=67, B=2） |
| `parse_dialogue_xml()` | XML文字列またはファイルパスを解析しセクションリストを返す |
| `get_style_id()` | 話者IDからVOICEVOXスタイルIDを取得 |
| `synthesize_utterance()` | 発話テキストをVOICEVOXで音声合成し(ndarray, int)を返す |
| `concatenate_section_audio()` | 複数音声セグメントを無音間隔付きで結合 |
| `process_dialogue_sections()` | セクションリストから音声ファイルを生成する統合関数 |
| `parse_args()` | CLIコマンドライン引数をargparseで解析 |
| `main()` | エントリーポイント（終了コード 0/1/2/3） |

### CLIオプション（dialogue_pipeline.py）

| オプション | デフォルト | 説明 |
|-----------|-----------|------|
| -i/--input | 必須 | 対話形式XMLファイルパス |
| -o/--output | ./output | 出力ディレクトリ |
| --narrator-style | 13 | ナレーターのスタイルID（青山龍星） |
| --speaker-a-style | 67 | 博士（A）のスタイルID（麒ヶ島宗麟） |
| --speaker-b-style | 2 | 助手（B）のスタイルID（四国めたん） |
| --speed | 1.0 | 読み上げ速度 |
| --voicevox-dir | ./voicevox_core | VOICEVOXディレクトリ |
| --acceleration-mode | AUTO | VOICEVOX加速モード |

## テスト結果

```
============================= test session starts ==============================
collecting ... collected 775 items

tests/test_dialogue_pipeline.py - 65 passed
（全テスト）
============================= 775 passed in 4.58s ==============================
```

**Phase 4 新規テスト**: 65件 PASS (100%)
**全体テスト**: 775件 PASS

**カバレッジ**: 76.66%（目標: 70%）

```
Name                            Stmts   Miss  Cover
---------------------------------------------------
src/dialogue_pipeline.py          150     55    63%
（全体）
---------------------------------------------------
TOTAL                            1791    418    77%
Required test coverage of 70% reached. Total coverage: 76.66%
```

## 発見された課題

1. **dialogue_pipeline.py のカバレッジ**: 63%（全体目標70%は達成）
   - main() 関数のVOICEVOX実際呼び出しパス（行269-316）とprocess_dialogue_sections()の実際合成パス（行389-444）はモックが難しい統合テスト部分のため未カバー
   - Phase 5/6でのE2Eテスト追加で改善可能

## 次フェーズへの引き継ぎ

Phase 5（CLI統合 & Makefile）で実装する内容:

- `dialogue_converter.py` の `parse_args()` と `main()` の実装
- Makefile への `dialogue-convert`, `dialogue-tts`, `dialogue` ターゲット追加
- Phase 4 で確立したインターフェース:
  - `parse_dialogue_xml(xml_str_or_path)` → `list[dict]`
  - `synthesize_utterance(text, speaker_id, synthesizer, speed_scale)` → `(ndarray, int)`
  - `concatenate_section_audio(segments, silence_duration, output_path)` → `(ndarray, int)`
- 注意事項: `dialogue_pipeline.py` の main() は `src.voicevox_client.VoicevoxSynthesizer` に依存。VOICEVOX Core ライブラリが必要な環境でのみ動作可能
