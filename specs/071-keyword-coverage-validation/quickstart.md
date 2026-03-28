# Quickstart: キーワード抽出とカバー率検証

**Date**: 2026-03-28
**Feature**: 071-keyword-coverage-validation

## 概要

本機能は対話生成の品質検証を行う。原文からキーワードを抽出し、生成された対話がそれらをカバーしているか検証する。

## 使用方法

### キーワード抽出

```python
from src.keyword_extractor import extract_keywords

# 原文セクションからキーワードを抽出
section_text = """
ロボチェック社は2027年にアームチェッカーを発売した。
ハルさんはA社、B社、C社と競合分析を行い、
自動検査と自動調整の機能をMVPスコープに含めた。
"""

keywords = extract_keywords(section_text)
# => ["ロボチェック社", "2027年", "アームチェッカー", "ハルさん", "A社", "B社", "C社", "自動検査", "自動調整", "MVP"]
```

### カバー率検証

```python
from src.coverage_validator import validate_coverage

# 対話XMLに対してキーワードのカバー率を検証
dialogue_xml = """
<dialogue>
  <line speaker="A">ロボチェック社のアームチェッカーについて話しましょう。</line>
  <line speaker="B">2027年に発売されたんですよね。MVPには自動検査機能が含まれています。</line>
</dialogue>
"""

result = validate_coverage(keywords, dialogue_xml)
# => CoverageResult(
#      total_keywords=10,
#      covered_keywords=6,
#      coverage_rate=0.6,
#      missing_keywords=["ハルさん", "A社", "B社", "C社", "自動調整"]
#    )
```

### JSON出力

```python
import json

# CoverageResult を JSON に変換
print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
```

出力:
```json
{
  "total_keywords": 10,
  "covered_keywords": 6,
  "coverage_rate": 0.6,
  "missing_keywords": ["ハルさん", "A社", "B社", "C社", "自動調整"]
}
```

## 前提条件

- Python 3.10+
- ollama がインストールされ、適切なモデルが利用可能であること
- `.venv` が有効化されていること

## ファイル構成

```
src/
├── keyword_extractor.py      # キーワード抽出
├── coverage_validator.py     # カバー率検証
└── prompts/
    └── extract_keywords.txt  # キーワード抽出プロンプト
```
