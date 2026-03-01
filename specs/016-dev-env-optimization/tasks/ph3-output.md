# Phase 3 Output: User Story 2 - CI でのカバレッジ可視化

**Date**: 2026-03-02
**Status**: Completed
**User Story**: US2 - CI でのカバレッジ可視化

## Executed Tasks

- [x] T013 セットアップ分析を読む: specs/016-dev-env-optimization/tasks/ph1-output.md
- [x] T014 前フェーズ出力を読む: specs/016-dev-env-optimization/tasks/ph2-output.md
- [x] T015 [US2] .github/workflows/ci.yml に permissions セクションを追加
- [x] T016 [US2] pytest ステップにカバレッジオプションを追加（pyproject.toml の設定が適用されることを確認）
- [x] T017 [US2] py-cov-action/python-coverage-comment-action ステップを追加
- [x] T018 CI ワークフロー構文を検証: `gh workflow view ci.yml`
- [x] T019 作成: specs/016-dev-env-optimization/tasks/ph3-output.md

## Changed Files

| File | Change Type | Summary |
|------|-------------|---------|
| .github/workflows/ci.yml | Modified | permissions セクションを追加、coverage comment アクションを追加 |
| specs/016-dev-env-optimization/tasks.md | Modified | Phase 3 タスクを完了としてマーク |

## Implementation Details

### .github/workflows/ci.yml 変更内容

**1. permissions セクションの追加**

PR コメント機能に必要な権限を追加:

```yaml
permissions:
  contents: write
  pull-requests: write
```

- `contents: write`: カバレッジデータ保存用（オプション）
- `pull-requests: write`: PR コメント投稿用（必須）

**2. Coverage comment アクションの追加**

pytest ステップの後に追加:

```yaml
- name: Coverage comment
  uses: py-cov-action/python-coverage-comment-action@v3
  with:
    GITHUB_TOKEN: ${{ github.token }}
    MINIMUM_GREEN: 80
    MINIMUM_ORANGE: 60
```

**設定説明**:
- `GITHUB_TOKEN`: GitHub Actions の自動トークンを使用
- `MINIMUM_GREEN: 80`: カバレッジ 80% 以上で緑色表示
- `MINIMUM_ORANGE: 60`: カバレッジ 60-79% でオレンジ色表示

**3. pytest ステップの確認**

現在の pytest ステップ:

```yaml
- name: Run pytest
  run: PYTHONPATH=. pytest tests/ --forked --tb=short -q
  timeout-minutes: 10
```

pyproject.toml の addopts 設定により、以下が自動的に適用される:
- `--cov=src`: カバレッジ計測
- `--cov-report=term-missing`: ターミナル出力
- `--cov-report=xml:coverage.xml`: XML レポート生成（py-cov-action が使用）
- `--cov-fail-under=70`: 閾値 70%

既存の `--forked --tb=short -q` オプションは維持。

## Workflow Validation

### gh CLI による検証

```bash
$ gh workflow view ci.yml
CI - ci.yml
ID: 238714714

Total runs 15
Recent runs
completed	success	Merge pull request #33 from rengotaku/015-test-execution-strategy	CI	main	push	36s	22540777095
...
```

ワークフロー構文が正常に解析され、エラーなし ✅

## Technical Decisions

1. **py-cov-action/python-coverage-comment-action v3 を採用**
   - 理由: Python 専用、シンプルな設定、外部サービス不要
   - 代替案（Codecov）より軽量で個人プロジェクトに適している

2. **MINIMUM_GREEN=80 に設定**
   - 現在のカバレッジ: 72%
   - pyproject.toml の閾値: 70%
   - PR コメントでは 80% を目標として表示（緑色の基準）
   - 実際のテスト失敗閾値（70%）とは独立

3. **pytest ステップは変更不要**
   - pyproject.toml の addopts により自動的にカバレッジが計測される
   - coverage.xml は pytest 実行時に自動生成される
   - py-cov-action がこのファイルを読み取る

## Discovered Issues

なし。全タスクが計画通りに完了。

## Handoff to Next Phase

### Phase 4 (User Story 3 - CI の実行時間最適化):

前提条件（Phase 3 で完了）:
- ✅ permissions セクションが設定されている
- ✅ coverage.xml が pytest 実行時に自動生成される
- ✅ PR コメント機能が設定されている

実装項目:
- CI キャッシュ設定の確認（research.md より既に最適化済み）
- キャッシュキーの明示化を検討（変更不要の可能性高い）

注意事項:
- Phase 1 の分析により、現在のキャッシュ設定は既に最適化済み
- actions/setup-python@v5 の `cache: 'pip'` + `cache-dependency-path: pyproject.toml` が設定済み
- 追加変更は不要と思われるが、最終確認を実施すること
