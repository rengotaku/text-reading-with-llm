# Phase 4 RED Tests: 対話形式音声の生成

**Date**: 2026-03-14
**Status**: RED (FAIL verified)
**User Story**: US3 - 対話形式音声の生成

## Summary

| Item | Value |
|------|-------|
| テスト作成数 | 65 |
| FAIL数 | 65 |
| テストファイル | tests/test_dialogue_pipeline.py |

## テストクラス別内訳

| クラス | テスト数 | 対象タスク | テスト対象 |
|--------|----------|------------|------------|
| TestSpeaker | 7 | T049 | Speaker データクラス |
| TestParseDialogueXml | 14 | T050 | parse_dialogue_xml() |
| TestGetStyleId | 8 | T051 | get_style_id() |
| TestSynthesizeUtterance | 10 | T052 | synthesize_utterance() |
| TestConcatenateSectionAudio | 8 | T053 | concatenate_section_audio() |
| TestParseArgs | 18 | T054 | parse_args() |

## Failed Tests

| テストファイル | テストメソッド | 期待する動作 |
|-----------|-------------|-------------|
| test_dialogue_pipeline.py | TestSpeaker::test_speaker_narrator_creation | ナレーターSpeaker生成(id=narrator, style_id=13) |
| test_dialogue_pipeline.py | TestSpeaker::test_speaker_a_creation | 博士Speaker生成(id=A, style_id=67) |
| test_dialogue_pipeline.py | TestSpeaker::test_speaker_b_creation | 助手Speaker生成(id=B, style_id=2) |
| test_dialogue_pipeline.py | TestSpeaker::test_speaker_equality | 同値Speakerの等価比較 |
| test_dialogue_pipeline.py | TestSpeaker::test_speaker_inequality | 異値Speakerの不等比較 |
| test_dialogue_pipeline.py | TestSpeaker::test_speaker_fields_are_required | 必須フィールド不足でTypeError |
| test_dialogue_pipeline.py | TestSpeaker::test_speaker_voicevox_style_id_is_int | style_idのint型確認 |
| test_dialogue_pipeline.py | TestParseDialogueXml::test_parse_single_section | 単一セクションXMLパース |
| test_dialogue_pipeline.py | TestParseDialogueXml::test_parse_section_number | セクション番号取得(1.1) |
| test_dialogue_pipeline.py | TestParseDialogueXml::test_parse_section_title | セクションタイトル取得 |
| test_dialogue_pipeline.py | TestParseDialogueXml::test_parse_introduction | introduction要素パース |
| test_dialogue_pipeline.py | TestParseDialogueXml::test_parse_utterances | utterance要素パース(3件) |
| test_dialogue_pipeline.py | TestParseDialogueXml::test_parse_utterance_text | utteranceテキスト取得 |
| test_dialogue_pipeline.py | TestParseDialogueXml::test_parse_conclusion | conclusion要素パース |
| test_dialogue_pipeline.py | TestParseDialogueXml::test_parse_multiple_sections | 複数セクションパース(2件) |
| test_dialogue_pipeline.py | TestParseDialogueXml::test_parse_empty_xml_raises | 空XMLでエラー |
| test_dialogue_pipeline.py | TestParseDialogueXml::test_parse_invalid_xml_raises | 不正XMLでエラー |
| test_dialogue_pipeline.py | TestParseDialogueXml::test_parse_no_dialogue_sections | セクションなし->空リスト |
| test_dialogue_pipeline.py | TestParseDialogueXml::test_parse_xml_with_unicode | Unicode文字処理 |
| test_dialogue_pipeline.py | TestParseDialogueXml::test_parse_section_without_introduction | introduction省略対応 |
| test_dialogue_pipeline.py | TestParseDialogueXml::test_parse_from_file | ファイルパスからパース |
| test_dialogue_pipeline.py | TestGetStyleId::test_narrator_default_style_id | narrator->13 |
| test_dialogue_pipeline.py | TestGetStyleId::test_speaker_a_default_style_id | A->67 |
| test_dialogue_pipeline.py | TestGetStyleId::test_speaker_b_default_style_id | B->2 |
| test_dialogue_pipeline.py | TestGetStyleId::test_custom_style_id_mapping | カスタムマッピング対応 |
| test_dialogue_pipeline.py | TestGetStyleId::test_unknown_speaker_raises | 未知話者でエラー |
| test_dialogue_pipeline.py | TestGetStyleId::test_empty_speaker_raises | 空文字列でエラー |
| test_dialogue_pipeline.py | TestGetStyleId::test_none_speaker_raises | Noneでエラー |
| test_dialogue_pipeline.py | TestGetStyleId::test_case_sensitive | 大文字小文字区別 |
| test_dialogue_pipeline.py | TestSynthesizeUtterance::test_synthesize_returns_audio_data | 音声データ(numpy, int)返却 |
| test_dialogue_pipeline.py | TestSynthesizeUtterance::test_synthesize_uses_correct_style_id_for_a | A->style_id=67で呼出 |
| test_dialogue_pipeline.py | TestSynthesizeUtterance::test_synthesize_uses_correct_style_id_for_b | B->style_id=2で呼出 |
| test_dialogue_pipeline.py | TestSynthesizeUtterance::test_synthesize_narrator | ナレーター合成(style_id=13) |
| test_dialogue_pipeline.py | TestSynthesizeUtterance::test_synthesize_empty_text_raises | 空テキストでエラー |
| test_dialogue_pipeline.py | TestSynthesizeUtterance::test_synthesize_none_text_raises | Noneテキストでエラー |
| test_dialogue_pipeline.py | TestSynthesizeUtterance::test_synthesize_unknown_speaker_raises | 未知話者でエラー |
| test_dialogue_pipeline.py | TestSynthesizeUtterance::test_synthesize_with_special_characters | 特殊文字テキスト処理 |
| test_dialogue_pipeline.py | TestSynthesizeUtterance::test_synthesize_long_text | 1000文字超テキスト処理 |
| test_dialogue_pipeline.py | TestSynthesizeUtterance::test_synthesize_with_custom_speed | 速度パラメータ指定 |
| test_dialogue_pipeline.py | TestConcatenateSectionAudio::test_concatenate_two_segments | 2セグメント結合 |
| test_dialogue_pipeline.py | TestConcatenateSectionAudio::test_concatenate_single_segment | 単一セグメント返却 |
| test_dialogue_pipeline.py | TestConcatenateSectionAudio::test_concatenate_empty_list_raises | 空リストでエラー |
| test_dialogue_pipeline.py | TestConcatenateSectionAudio::test_concatenate_preserves_sample_rate | サンプルレート保持 |
| test_dialogue_pipeline.py | TestConcatenateSectionAudio::test_concatenate_with_silence_duration | 無音間隔指定 |
| test_dialogue_pipeline.py | TestConcatenateSectionAudio::test_concatenate_many_segments | 15セグメント結合 |
| test_dialogue_pipeline.py | TestConcatenateSectionAudio::test_concatenate_returns_numpy_array | numpy配列返却 |
| test_dialogue_pipeline.py | TestConcatenateSectionAudio::test_concatenate_output_to_file | ファイル保存 |
| test_dialogue_pipeline.py | TestParseArgs::test_required_input_argument | --input必須(SystemExit) |
| test_dialogue_pipeline.py | TestParseArgs::test_input_short_flag | -i フラグ |
| test_dialogue_pipeline.py | TestParseArgs::test_input_long_flag | --input フラグ |
| test_dialogue_pipeline.py | TestParseArgs::test_output_default | デフォルト ./output |
| test_dialogue_pipeline.py | TestParseArgs::test_output_custom | カスタム出力パス |
| test_dialogue_pipeline.py | TestParseArgs::test_narrator_style_default | デフォルト 13 |
| test_dialogue_pipeline.py | TestParseArgs::test_narrator_style_custom | カスタム narrator style |
| test_dialogue_pipeline.py | TestParseArgs::test_speaker_a_style_default | デフォルト 67 |
| test_dialogue_pipeline.py | TestParseArgs::test_speaker_a_style_custom | カスタム A style |
| test_dialogue_pipeline.py | TestParseArgs::test_speaker_b_style_default | デフォルト 2 |
| test_dialogue_pipeline.py | TestParseArgs::test_speaker_b_style_custom | カスタム B style |
| test_dialogue_pipeline.py | TestParseArgs::test_speed_default | デフォルト 1.0 |
| test_dialogue_pipeline.py | TestParseArgs::test_speed_custom | カスタム速度 |
| test_dialogue_pipeline.py | TestParseArgs::test_voicevox_dir_default | デフォルト ./voicevox_core |
| test_dialogue_pipeline.py | TestParseArgs::test_voicevox_dir_custom | カスタムパス |
| test_dialogue_pipeline.py | TestParseArgs::test_acceleration_mode_default | デフォルト AUTO |
| test_dialogue_pipeline.py | TestParseArgs::test_acceleration_mode_custom | カスタムモード |
| test_dialogue_pipeline.py | TestParseArgs::test_all_options_combined | 全オプション同時指定 |

## 実装ヒント

- `Speaker`: `@dataclass` で定義。フィールド: id, role, voicevox_style_id, character_name
- `parse_dialogue_xml(xml_str_or_path)`: XML文字列またはファイルパスを受け取り、`list[dict]` を返す。各dictは section_number, section_title, introduction, utterances, conclusion を持つ
- `get_style_id(speaker_id, style_mapping=None)`: デフォルトマッピング narrator=13, A=67, B=2。未知IDはValueError/KeyError
- `synthesize_utterance(text, speaker_id, synthesizer, speed_scale=None)`: VoicevoxSynthesizerのモックを受け取り `(np.ndarray, int)` を返す。空/None テキストはエラー
- `concatenate_section_audio(segments, silence_duration=0.5, output_path=None)`: `list[tuple[np.ndarray, int]]` を受け取り `(np.ndarray, int)` を返す。output_path指定時はWAV保存
- `parse_args(args)`: argparse.ArgumentParser使用。CLI仕様は contracts/cli-spec.md 参照

## エッジケース対応

| カテゴリ | テストケース |
|----------|------------|
| Null/None | None話者ID、Noneテキスト |
| 空値 | 空XML文字列、空テキスト、空セグメントリスト |
| 型エラー | 不正な話者ID型 |
| 境界値 | 単一セグメント、15セグメント |
| エラーパス | 不正XML、未知話者ID |
| 大規模データ | 1000文字超テキスト |
| 特殊文字 | Unicode日本語、括弧・記号・数字 |

## make test 出力（抜粋）

```
FAILED tests/test_dialogue_pipeline.py::TestSpeaker::test_speaker_narrator_creation - ImportError
FAILED tests/test_dialogue_pipeline.py::TestSpeaker::test_speaker_a_creation - ImportError
FAILED tests/test_dialogue_pipeline.py::TestParseDialogueXml::test_parse_single_section - ImportError
FAILED tests/test_dialogue_pipeline.py::TestGetStyleId::test_narrator_default_style_id - ImportError
FAILED tests/test_dialogue_pipeline.py::TestSynthesizeUtterance::test_synthesize_returns_audio_data - ImportError
FAILED tests/test_dialogue_pipeline.py::TestConcatenateSectionAudio::test_concatenate_two_segments - ImportError
FAILED tests/test_dialogue_pipeline.py::TestParseArgs::test_required_input_argument - ImportError
... (全65件)
65 failed, 710 passed in 4.48s
```
