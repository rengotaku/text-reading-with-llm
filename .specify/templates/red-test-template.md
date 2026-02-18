---
description: "RED test output format template"
---

# RED Test Output Template

tdd-generator が出力する RED (FAIL) テスト結果のフォーマット。

**Language**: Japanese

---

```markdown
# Phase N RED Tests: [Phase Name]

**Date**: YYYY-MM-DD
**Status**: RED (FAIL確認済み)
**User Story**: US[N] - [Title]

## サマリー

| 項目 | 値 |
|------|-----|
| 作成テスト数 | X |
| FAIL数 | X |
| テストファイル | tests/test_xxx.py, tests/test_yyy.py |

## FAILテスト一覧

| テストファイル | テストメソッド | 期待動作 |
|--------------|--------------|----------|
| tests/test_xxx.py | test_feature_basic | [expected behavior] |
| tests/test_xxx.py | test_feature_edge | [expected behavior] |

## 実装ヒント

- `function_name`: [implementation hint]
- エッジケース: [what to handle]

## make test 出力 (抜粋)

```
FAILED tests/test_xxx.py::test_feature_basic - AssertionError
FAILED tests/test_xxx.py::test_feature_edge - AttributeError
...
X failed, Y passed
```
```
