# Phase 3 Output: カバー率検証と JSON 出力 (US2+US3)

**Date**: 2026-03-29
**Status**: Completed
**User Story**: US2 - カバー率検証 / US3 - 検証結果の出力

## 実行タスク

- [x] T030 Read: specs/071-keyword-coverage-validation/red-tests/ph3-test.md
- [x] T031 [US2] CoverageResult dataclass を実装: src/coverage_validator.py
- [x] T032 [US2] validate_coverage 関数を実装: src/coverage_validator.py
- [x] T033 Verify: `make test` PASS (GREEN)
- [x] T034 Verify: `make test` で全テストパス（US1 含むリグレッションなし）
- [x] T035 Verify: `make coverage` ≥70%（要件達成）
- [x] T036 Edit: specs/071-keyword-coverage-validation/tasks/ph3-output.md

## 変更ファイル

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| src/coverage_validator.py | 新規 | CoverageResult dataclass（to_dict メソッド付き）、validate_coverage 関数（ハイブリッドマッチング実装） |

## テスト結果

```
============================= 962 passed in 13.71s ==============================
```

- Phase 3 新規テスト: 48件（全クラス合計）
  - TestCoverageResultDataclass: 8件
  - TestValidateCoverageBasic: 5件
  - TestValidateCoverageFullCoverage: 4件
  - TestValidateCoverageNoCoverage: 3件
  - TestValidateCoverageEdgeCases: 8件
  - TestValidateCoverageCaseInsensitive: 6件
  - TestCoverageResultToDict: 9件
  - TestValidateCoveragePerformance: 1件
  - TestValidateCoverageSpecialChars: 4件
- 既存テスト: 914件（US1 含むリグレッションなし）

**Coverage**: 71.96%（`make coverage` 要件 70% 達成）
**src/coverage_validator.py 単体カバレッジ**: 100%

## 実装詳細

### src/coverage_validator.py

#### CoverageResult dataclass

- `total_keywords: int`: 総キーワード数
- `covered_keywords: int`: カバーされたキーワード数
- `coverage_rate: float`: カバー率（0.0〜1.0）
- `missing_keywords: list[str]`: 未カバーキーワードリスト
- `to_dict()`: 4つのキーを持つ dict を返す（JSON シリアライズ可能）

#### validate_coverage 関数

引数バリデーション:
- `keywords=None` → `TypeError`
- `dialogue_xml=None` → `TypeError`
- `keywords` が list 型でない → `TypeError`
- `dialogue_xml` が str 型でない → `TypeError`

エッジケース:
- `keywords=[]` → `CoverageResult(0, 0, 1.0, [])`（coverage_rate=1.0）
- `dialogue_xml=""` → 全キーワードが未カバー（coverage_rate=0.0）

マッチング戦略（ハイブリッドマッチング）:
- ASCII英数字+アンダースコアのみのキーワード: 正規表現 `\b` 単語境界マッチングを使用
  - 誤マッチ防止: `keyword_1` が `keyword_10` にマッチしないよう制御
- それ以外（日本語・特殊文字・スペース含む）: 部分文字列マッチング（`in`）を使用
  - 日本語対応: `ロボチェック` が `ロボチェック社` 内にマッチ
  - 全て case-insensitive（`lower()` 変換後に比較）

#### 設計上の判断

`in` による単純な部分文字列マッチングのみでは、パフォーマンステスト（`test_large_keyword_list`）が期待する結果（750件）を返せなかった。原因は `keyword_1` が `keyword_10` などの偶数番号キーワード文字列内に誤マッチするためである。

ハイブリッドマッチング戦略を採用することで、以下の両方を同時に満たした:
1. ASCII単語のマッチング精度（単語境界による完全単語マッチング）
2. 日本語・特殊文字を含むキーワードの部分文字列マッチング（`in`）

## 発見した問題

1. **パフォーマンステストと partial_match テストの見かけ上の矛盾**: 単純な `in` マッチングではパフォーマンステストが失敗（825 vs 期待750）。ハイブリッドマッチング（ASCII英数字には `\b`、それ以外には `in`）で解決。実装後に全48テストが PASS。

## 次フェーズへの引き継ぎ

Phase 4（Polish & Cross-Cutting Concerns）で実施するもの:

- `make lint` でコード品質チェック
- `make mypy` で型チェック
- quickstart.md の使用例を実際に実行して検証

利用可能なインターフェース:
- `extract_keywords(section_text, model, ollama_chat_func)` → `list[str]`（Phase 2 実装済み）
- `validate_coverage(keywords, dialogue_xml)` → `CoverageResult`（Phase 3 実装済み）
- `CoverageResult.to_dict()` → `dict`（JSON 出力対応）

注意事項:
- `coverage_validator.py` は LLM 不使用（文字列マッチングのみ）
- `CoverageResult.coverage_rate` は `total_keywords == 0` の場合 `1.0` を返す
