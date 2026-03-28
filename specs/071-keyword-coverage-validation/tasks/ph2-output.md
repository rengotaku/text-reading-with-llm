# Phase 2 Output: キーワード抽出 (US1)

**Date**: 2026-03-28
**Status**: Completed
**User Story**: US1 - キーワード抽出

## 実行タスク

- [x] T013 Read: specs/071-keyword-coverage-validation/red-tests/ph2-test.md
- [x] T014 [P] [US1] プロンプトファイルを作成: src/prompts/extract_keywords.txt
- [x] T015 [US1] キーワード抽出モジュールを実装: src/keyword_extractor.py（extract_keywords 関数、prompt_loader 使用、ollama 呼び出し）
- [x] T016 Verify: `make test` PASS (GREEN)
- [x] T017 Verify: `make test` で全テストパス（リグレッションなし）
- [x] T018 Edit: specs/071-keyword-coverage-validation/tasks/ph2-output.md

## 変更ファイル

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| src/prompts/extract_keywords.txt | 新規 | キーワード抽出プロンプト（[SYSTEM]/[USER] 形式、{section_text} プレースホルダー、カンマ区切り出力指示） |
| src/keyword_extractor.py | 新規 | extract_keywords 関数（load_prompt 使用、ollama 呼び出し、カンマ分割・trim・重複除去） |

## テスト結果

```
============================= 914 passed in 3.81s ==============================
```

- Phase 2 新規テスト: 25件（TestExtractKeywordsPrompt: 7件、TestExtractKeywords: 6件、TestExtractKeywordsEdgeCases: 8件、TestExtractKeywordsOutputFormat: 8件 ※ファイルには計30テストあるが RED 時は 25件が FAIL 対象）
- 既存テスト: 889件（リグレッションなし）

## 実装詳細

### src/prompts/extract_keywords.txt

- `[SYSTEM]` セクション: キーワード抽出の専門家としての役割定義（「キーワード」を含む）
- `[USER]` セクション: `{section_text}` プレースホルダーで原文を挿入
- カンマ区切り出力形式の指示を明記

### src/keyword_extractor.py

`extract_keywords(section_text, model, ollama_chat_func)` 関数:
- `None` 入力: `TypeError` を送出
- 非 str 入力: `ValueError` を送出
- 空テキスト/空白のみ: LLM 呼び出しなしで `[]` を返す
- `load_prompt("extract_keywords", section_text=section_text)` でプロンプト取得
- `ollama_chat_func` でLLM呼び出し（CI環境でのモック注入対応）
- レスポンスをカンマで分割、trim、空要素除去、重複除去（出現順序保持）
- `list[str]` を返す

CI 環境対応:
- `dialogue_converter.py` と同様のパターンで `_IS_CI` 判定
- `ollama_chat_func` パラメータによりテスト時にモック注入可能

## 発見した問題

特になし。既存 `dialogue_converter.py` パターンをそのまま適用できた。

## 次フェーズへの引き継ぎ

Phase 3（US2 カバー率検証 + US3 JSON 出力）で実装するもの:

- `src/coverage_validator.py`:
  - `CoverageResult` dataclass（total_keywords, covered_keywords, coverage_rate, missing_keywords, to_dict）
  - `validate_coverage(keywords, dialogue_xml)` 関数（文字列マッチング、case-insensitive）
- `tests/test_coverage_validator.py`: 上記のテスト

利用可能なインターフェース:
- `extract_keywords(section_text, model, ollama_chat_func)` → `list[str]`
- `KeywordList = list[str]`（data-model.md 参照）

注意事項:
- カバー率検証は LLM 不使用（文字列マッチングのみ）
- `CoverageResult.coverage_rate`: `total_keywords == 0` の場合は `1.0`
