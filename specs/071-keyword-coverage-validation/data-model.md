# Data Model: キーワード抽出とカバー率検証

**Date**: 2026-03-28
**Feature**: 071-keyword-coverage-validation

## Entities

### KeywordList

キーワード抽出の出力。

```python
# 型定義（実装時）
KeywordList = list[str]
```

**属性**:
- 各要素は抽出されたキーワード文字列
- 重複なし
- 空白は trim 済み

**例**:
```python
["デスマーチ", "ロボチェック社", "ハルさん", "2027年"]
```

---

### CoverageResult

カバー率検証の出力。

```python
from dataclasses import dataclass

@dataclass
class CoverageResult:
    total_keywords: int      # 総キーワード数
    covered_keywords: int    # カバーされたキーワード数
    coverage_rate: float     # カバー率 (0.0 - 1.0)
    missing_keywords: list[str]  # 未カバーのキーワードリスト
```

**制約**:
- `coverage_rate = covered_keywords / total_keywords`（total_keywords > 0 の場合）
- `total_keywords == 0` の場合、`coverage_rate = 1.0`
- `covered_keywords + len(missing_keywords) == total_keywords`

**JSON出力形式**:
```json
{
  "total_keywords": 12,
  "covered_keywords": 9,
  "coverage_rate": 0.75,
  "missing_keywords": ["2027年", "A社", "B社"]
}
```

---

## Input/Output Flows

### キーワード抽出フロー

```
Input: str (原文セクション)
  ↓
  [LLM: extract_keywords.txt プロンプト]
  ↓
Output: list[str] (キーワードリスト)
```

### カバー率検証フロー

```
Input:
  - keywords: list[str] (キーワードリスト)
  - dialogue_xml: str (対話XML)
  ↓
  [文字列マッチング]
  ↓
Output: CoverageResult
```

---

## Edge Cases

| ケース | 入力 | 出力 |
|--------|------|------|
| 空テキスト | `""` | `[]` |
| 空キーワードリスト | `keywords=[]` | `CoverageResult(0, 0, 1.0, [])` |
| 全カバー | 全キーワードが対話に含まれる | `coverage_rate=1.0` |
| 全未カバー | キーワードが一つも含まれない | `coverage_rate=0.0` |
