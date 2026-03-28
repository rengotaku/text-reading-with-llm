# Phase 3 RED Tests: カバー率検証と JSON 出力

**Date**: 2026-03-28
**Status**: RED (FAIL verified)
**User Story**: US2 - カバー率検証 / US3 - 検証結果の出力

## Summary

| Item | Value |
|------|-------|
| Tests Created | 48 |
| Failed Count | 48（モジュール未存在による収集エラー） |
| Test Files | tests/test_coverage_validator.py |

## Failed Tests

| Test File | テストクラス | テストメソッド数 | 期待される振る舞い |
|-----------|-------------|-----------------|-------------------|
| tests/test_coverage_validator.py | TestCoverageResultDataclass | 8 | CoverageResult dataclass の属性アクセスと to_dict メソッド |
| tests/test_coverage_validator.py | TestValidateCoverageBasic | 5 | キーワードリストと対話XMLからカバー率を計算 |
| tests/test_coverage_validator.py | TestValidateCoverageFullCoverage | 4 | 全キーワードカバー時に coverage_rate=1.0 |
| tests/test_coverage_validator.py | TestValidateCoverageNoCoverage | 3 | 全キーワード未カバー時に coverage_rate=0.0 |
| tests/test_coverage_validator.py | TestValidateCoverageEdgeCases | 8 | 空リスト、None入力、不正XML等のエッジケース |
| tests/test_coverage_validator.py | TestValidateCoverageCaseInsensitive | 6 | 大文字小文字を区別しないマッチング |
| tests/test_coverage_validator.py | TestCoverageResultToDict | 9 | to_dict が正しいJSONスキーマを返す |
| tests/test_coverage_validator.py | TestValidateCoveragePerformance | 1 | 1500キーワードの大量データ処理 |
| tests/test_coverage_validator.py | TestValidateCoverageSpecialChars | 4 | Unicode、SQL特殊文字、HTMLタグ、絵文字の処理 |

## 実装ヒント

- `CoverageResult`: dataclass として実装。`to_dict()` メソッドで4つのキー（total_keywords, covered_keywords, coverage_rate, missing_keywords）を含む dict を返す
- `validate_coverage(keywords: list[str], dialogue_xml: str) -> CoverageResult`:
  - 入力バリデーション: `keywords` は `list` 型、`dialogue_xml` は `str` 型（None で TypeError）
  - 空キーワードリスト: `CoverageResult(0, 0, 1.0, [])` を返す
  - 文字列マッチング: `keyword.lower() in dialogue_xml.lower()` で case-insensitive 判定
  - カバー率計算: `covered_keywords / total_keywords`
- エッジケース:
  - `keywords=[]` -> `coverage_rate=1.0`
  - `dialogue_xml=""` -> `coverage_rate=0.0`（キーワードがある場合）
  - `None` 入力 -> `TypeError`
  - 不正XML -> 文字列マッチングなので正常動作

## make test Output (excerpt)

```
ERROR collecting tests/test_coverage_validator.py
tests/test_coverage_validator.py:9: in <module>
    from src.coverage_validator import CoverageResult, validate_coverage
E   ModuleNotFoundError: No module named 'src.coverage_validator'
1 error in 0.35s
make: *** [Makefile:100: test] Error 2
```
