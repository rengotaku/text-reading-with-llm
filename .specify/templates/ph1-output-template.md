---
description: "Phase 1 (Setup) output format template"
---

# Phase 1 Output Template

Setup Phase の出力フォーマット。既存コードの分析結果をsubagentに伝達する。

**Language**: Japanese

---

```markdown
# Phase 1 Output: Setup

**Date**: YYYY-MM-DD
**Status**: 完了 | エラー

## 実行タスク

- [x] T001 [task description]
- [x] T002 [task description]
...

## 既存コード分析

### [filename.ext]

**構造**:
- `ClassName`: [purpose]
- `function_name`: [purpose]

**更新が必要な箇所**:
1. `function_name`: [current] → [required change]
2. ...

### [another_file.ext]
...

## 既存テスト分析

- `tests/test_xxx.py`: [what it covers]
- **存在しない**: tests/test_yyy.py → 新規作成

**追加が必要なフィクスチャ**:
- `fixture_name`: [purpose]

## 新規作成ファイル

### [new_file.ext] (スケルトン)

- `function_name`: [purpose] (Phase N で実装)
- `ClassName`: [purpose]

## 技術的決定事項

1. **[Decision]**: [rationale]
2. **[Decision]**: [rationale]

## 次フェーズへの引き継ぎ

Phase 2 ([Story Name]) で実装するもの:
- `function_name`: [description]
- 既存コード流用: [what can be reused]
- 注意点: [caveats]
```
