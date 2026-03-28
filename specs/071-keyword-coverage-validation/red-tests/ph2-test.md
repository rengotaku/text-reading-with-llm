# Phase 2 RED Tests: キーワード抽出

**Date**: 2026-03-28
**Status**: RED (FAIL verified)
**User Story**: US1 - キーワード抽出

## Summary

| Item | Value |
|------|-------|
| テスト作成数 | 25 |
| 失敗数 | 25 (収集エラーにより全テスト失敗) |
| テストファイル | tests/test_keyword_extractor.py |

## テストクラス構成

| クラス/グループ | テスト数 | 対象タスク |
|----------------|---------|-----------|
| TestExtractKeywordsPrompt | 7 | T007: プロンプトファイル検証 |
| TestExtractKeywords | 6 | T008: 基本抽出テスト |
| TestExtractKeywordsEdgeCases | 8 | T009: エッジケーステスト |
| TestExtractKeywordsOutputFormat | 8 | T010: 出力形式テスト |

## 失敗テスト一覧

| テストファイル | テストメソッド | 期待する動作 |
|--------------|--------------|-------------|
| tests/test_keyword_extractor.py | TestExtractKeywordsPrompt::test_extract_keywords_prompt_file_exists | extract_keywords.txt が存在する |
| tests/test_keyword_extractor.py | TestExtractKeywordsPrompt::test_extract_keywords_prompt_has_system_section | [SYSTEM] セクションがある |
| tests/test_keyword_extractor.py | TestExtractKeywordsPrompt::test_extract_keywords_prompt_has_user_section | [USER] セクションがある |
| tests/test_keyword_extractor.py | TestExtractKeywordsPrompt::test_extract_keywords_prompt_has_section_text_placeholder | {section_text} プレースホルダーがある |
| tests/test_keyword_extractor.py | TestExtractKeywordsPrompt::test_extract_keywords_prompt_loads_with_placeholder | load_prompt で読み込める |
| tests/test_keyword_extractor.py | TestExtractKeywordsPrompt::test_extract_keywords_prompt_mentions_keyword_extraction | キーワード抽出の役割定義がある |
| tests/test_keyword_extractor.py | TestExtractKeywordsPrompt::test_extract_keywords_prompt_specifies_comma_output | カンマ区切り出力指示がある |
| tests/test_keyword_extractor.py | TestExtractKeywords::test_extracts_keywords_from_text_with_proper_nouns | 固有名詞がキーワードとして抽出される |
| tests/test_keyword_extractor.py | TestExtractKeywords::test_extracts_keywords_from_text_with_technical_terms | 専門用語がキーワードとして抽出される |
| tests/test_keyword_extractor.py | TestExtractKeywords::test_extracts_keywords_from_text_with_numbers | 数値がキーワードとして抽出される |
| tests/test_keyword_extractor.py | TestExtractKeywords::test_passes_section_text_to_llm_prompt | テキストがLLMプロンプトに渡される |
| tests/test_keyword_extractor.py | TestExtractKeywords::test_uses_default_model | デフォルトモデルが使用される |
| tests/test_keyword_extractor.py | TestExtractKeywords::test_custom_model_is_used | カスタムモデルが指定できる |
| tests/test_keyword_extractor.py | TestExtractKeywordsEdgeCases::test_empty_text_returns_empty_list | 空テキストで空リスト |
| tests/test_keyword_extractor.py | TestExtractKeywordsEdgeCases::test_whitespace_only_text_returns_empty_list | 空白のみで空リスト |
| tests/test_keyword_extractor.py | TestExtractKeywordsEdgeCases::test_none_text_raises_error_or_returns_empty | None入力でエラー |
| tests/test_keyword_extractor.py | TestExtractKeywordsEdgeCases::test_llm_returns_empty_response | 空LLMレスポンスで空リスト |
| tests/test_keyword_extractor.py | TestExtractKeywordsEdgeCases::test_llm_returns_whitespace_only_response | 空白のみLLMレスポンスで空リスト |
| tests/test_keyword_extractor.py | TestExtractKeywordsEdgeCases::test_special_characters_in_text | 特殊文字を含むテキスト処理 |
| tests/test_keyword_extractor.py | TestExtractKeywordsEdgeCases::test_unicode_emoji_in_text | Unicode文字を含むテキスト処理 |
| tests/test_keyword_extractor.py | TestExtractKeywordsEdgeCases::test_very_long_text | 長大テキスト処理 |
| tests/test_keyword_extractor.py | TestExtractKeywordsOutputFormat::test_comma_separated_response_is_parsed | カンマ区切りパース |
| tests/test_keyword_extractor.py | TestExtractKeywordsOutputFormat::test_keywords_are_trimmed | 前後空白のtrim |
| tests/test_keyword_extractor.py | TestExtractKeywordsOutputFormat::test_duplicate_keywords_are_removed | 重複除去 |
| tests/test_keyword_extractor.py | TestExtractKeywordsOutputFormat::test_empty_items_in_response_are_filtered | 空要素フィルタ |

## 失敗理由

### 主要エラー: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'src.keyword_extractor'
```

以下のファイルが未作成のため、全テストが収集エラーで失敗:

1. **`src/keyword_extractor.py`** - キーワード抽出モジュール（未作成）
2. **`src/prompts/extract_keywords.txt`** - キーワード抽出プロンプト（未作成）

## GREEN化に必要な実装

### 1. `src/prompts/extract_keywords.txt`

- `[SYSTEM]` セクション: キーワード抽出の専門家としての役割定義（「キーワード」を含むこと）
- `[USER]` セクション: `{section_text}` プレースホルダーを含む
- カンマ区切り出力形式の指示を含む

### 2. `src/keyword_extractor.py`

- `extract_keywords(section_text, model, ollama_chat_func)` 関数:
  - 空テキスト/空白のみ: LLM呼び出しなしで空リスト返却
  - None入力: TypeError/ValueError を送出
  - `load_prompt("extract_keywords", section_text=section_text)` でプロンプト取得
  - `ollama_chat_func` でLLM呼び出し
  - レスポンスをカンマで分割、trim、空要素除去、重複除去
  - 出現順序を保持した `list[str]` を返却

## make test 出力（抜粋）

```
ERROR collecting tests/test_keyword_extractor.py
tests/test_keyword_extractor.py:9: in <module>
    from src.keyword_extractor import extract_keywords
E   ModuleNotFoundError: No module named 'src.keyword_extractor'
1 error in 0.08s
```

## 既存テストへの影響

既存テスト 885件は全てパス。新規テストのみが失敗。
