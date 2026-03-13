# Phase 1 Output: Setup

**Date**: 2026-03-13
**Status**: Completed

## Executed Tasks

- [x] T001 既存のXMLパーサー実装を確認: src/xml_parser.py
- [x] T002 既存のVOICEVOXクライアント実装を確認: src/voicevox_client.py
- [x] T003 既存のLLM辞書生成実装を確認: src/llm_reading_generator.py
- [x] T004 既存のテキストクリーナー実装を確認: src/text_cleaner.py
- [x] T005 既存のテスト構造を確認: tests/
- [x] T006 data-model.md に基づきデータクラス設計を確認
- [x] T007 contracts/cli-spec.md に基づきCLI設計を確認
- [x] T008 `make test` で既存テストがすべてパスすることを確認 (589 passed)
- [x] T009 このファイルを生成

## Existing Code Analysis

### src/xml_parser.py

**Structure**:
- `HeadingInfo`: 見出し情報 (level, number, title, read_aloud)
- `ContentItem`: コンテンツ項目 (item_type, text, heading_info, chapter_number)
- `format_heading_text(level, number, title)`: 見出しフォーマット
- `parse_book2_xml(xml_path)`: XMLパース、ContentItemリスト返却
- `CHAPTER_MARKER`, `SECTION_MARKER`: Unicode私用領域マーカー

**Required Updates**:
- 変更なし。dialogue_converter.pyから利用可能

### src/voicevox_client.py

**Structure**:
- `VoicevoxConfig`: 設定 (style_id, speed_scale等)
- `VoicevoxSynthesizer`: 音声合成クラス
  - `initialize()`: Core初期化
  - `load_model_for_style_id(style_id)`: 特定style_idのVVMロード
  - `synthesize(text, style_id)`: 音声合成
- `STYLE_ID_TO_VVM`: style_id → VVMファイル名マッピング
- `generate_audio()`: 音声波形生成
- `concatenate_audio_files()`: WAV結合
- `save_audio()`: WAV保存

**Key Style IDs**:
- 13: 青山龍星 (narrator用、既存パイプラインと同じ)
- 67: 麒ヶ島宗麟 (博士A用)
- 2: 四国めたん (助手B用)

**Required Updates**:
- 変更なし。dialogue_pipeline.pyから利用可能

### src/llm_reading_generator.py

**Structure**:
- `extract_technical_terms(text)`: 技術用語抽出
- `generate_readings_with_llm(terms, model, ollama_chat_func)`: LLM読み生成
- `apply_llm_readings(text, readings)`: 読み適用

**LLM呼び出しパターン**:
```python
response = ollama_chat_func(model=model, messages=messages)
response_text = response.get("message", {}).get("content", "")
```

**Required Updates**:
- 変更なし。LLM呼び出しパターンを dialogue_converter.py で参照

### src/text_cleaner.py

**Structure**:
- `clean_page_text(text, heading_marker)`: テキストクリーニング
- URL、ISBN、括弧内英語、参照の正規化
- normalize_numbers, normalize_punctuation 適用
- MeCabによるかな変換

**Required Updates**:
- 変更なし。dialogue_converter.pyの出力テキストに適用可能

## Existing Test Analysis

- `tests/test_xml_parser.py`: XMLパース、ContentItem、マーカーテスト
- `tests/test_voicevox_client.py`: style_id検証、clean_text_for_voicevox
- `tests/test_llm_reading_generator.py`: 技術用語抽出
- `tests/test_text_cleaner_cli.py`: CLI引数パース

**Does not exist (Create new)**:
- `tests/test_dialogue_converter.py`: 対話変換テスト
- `tests/test_dialogue_pipeline.py`: 対話パイプラインテスト

**Required Fixtures**:
- `sample_section_xml`: セクションXMLサンプル
- `expected_dialogue_xml`: 期待する対話XML出力
- `mock_ollama_chat`: Ollama呼び出しモック

## Newly Created Files

### src/dialogue_converter.py (Implement in Phase 2)

- `DialogueBlock`: 対話ブロック dataclass
- `Utterance`: 発言 dataclass
- `ConversionResult`: 変換結果 dataclass
- `extract_sections()`: セクション抽出
- `analyze_structure()`: LLM構造分析 (intro/dialogue/conclusion)
- `generate_dialogue()`: LLM対話生成
- `to_dialogue_xml()`: XMLシリアライズ
- `convert_section()`: 統合関数
- `parse_args()`, `main()`: CLI (Phase 5)

### src/dialogue_pipeline.py (Implement in Phase 4)

- `Speaker`: 話者設定 dataclass
- `parse_dialogue_xml()`: 対話XMLパース
- `get_style_id()`: 話者別スタイルID取得
- `synthesize_utterance()`: 発話単位音声生成
- `concatenate_section_audio()`: セクション音声結合
- `process_dialogue_sections()`: 統合関数
- `parse_args()`, `main()`: CLI

## Technical Decisions

1. **既存モジュール変更なし**: xml_parser, voicevox_client, text_cleanerは変更せず、新規モジュールから利用
2. **LLM呼び出しパターン**: llm_reading_generator.pyと同様に `ollama.chat()` を使用
3. **3話者構成**: narrator (13), A/博士 (67), B/助手 (2) - research.mdの決定を維持
4. **対話XML構造**: data-model.mdの定義に従う (dialogue-section, introduction, dialogue/utterance, conclusion)

## Handoff to Next Phase

Phase 2 (US1: 書籍セクションを対話形式に変換) で実装:

- `DialogueBlock`, `Utterance`, `ConversionResult` データクラス
- `extract_sections()`: xml_parserのContentItemからセクション抽出
- `analyze_structure()`: LLMで構造分析 (intro/dialogue/conclusion分類)
- `generate_dialogue()`: LLMで対話生成 (A/B発話)
- `to_dialogue_xml()`: 対話XMLシリアライズ
- `convert_section()`: 統合関数

**Reusable existing code**:
- `ollama.chat()`: LLM呼び出し (llm_reading_generator.pyパターン参照)
- `xml.etree.ElementTree`: XML操作
- `dataclasses.dataclass`: データクラス定義

**Caveats**:
- LLMレスポンスは不定形。JSONパースにはエラーハンドリング必須
- 長文(4,000文字超)の分割はPhase 3で実装
- CLIはPhase 5で実装
