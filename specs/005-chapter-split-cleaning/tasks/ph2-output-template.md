---
description: "Phase N (TDD/Standard) output format template"
---

# Phase N Output Template

TDD/Standard Phase の出力フォーマット。実装結果をsubagentに伝達する。

**Language**: Japanese

---

```markdown
# Phase N Output: [Phase Name]

**Date**: YYYY-MM-DD
**Status**: 完了 | エラー
**User Story**: US[N] - [Title]

## 実行タスク

- [x] T0XX [task description]
- [x] T0XX [task description]
...

## 変更ファイル一覧

| ファイル | 変更種別 | 概要 |
|----------|----------|------|
| src/xxx.py | 新規 | [description] |
| src/yyy.py | 修正 | [what changed] |
| tests/test_xxx.py | 新規 | [test coverage] |

## テスト結果

```
make test 出力 (抜粋)
...
X passed, Y failed
```

**カバレッジ**: XX% (目標: 80%)

## 発見した問題/課題

1. **[Issue]**: [description] → [resolution or deferred to Phase N]
2. ...

## 次フェーズへの引き継ぎ

Phase N+1 ([Story Name]) で実装するもの:
- [dependency from this phase]
- [API/interface established]
- 注意点: [caveats]
```
