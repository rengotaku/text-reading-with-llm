# Implementation Plan: 開発環境の最適化

**Branch**: `016-dev-env-optimization` | **Date**: 2026-03-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/016-dev-env-optimization/spec.md`

## Summary

開発体験向上のための追加設定。pytest のカバレッジ設定（閾値 80%）、GitHub Actions の依存関係キャッシュ最適化、PR へのカバレッジレポートコメント、README カバレッジバッジ生成を実装する。

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: pytest, pytest-cov（既存）、GitHub Actions
**Storage**: N/A（設定ファイルのみ）
**Testing**: pytest + pytest-cov
**Target Platform**: Linux（GitHub Actions ubuntu-latest）
**Project Type**: Single project（src/ + tests/）
**Performance Goals**: CI 実行時間 50% 短縮（依存関係キャッシュ利用時）
**Constraints**: 既存 CI ワークフローとの互換性維持
**Scale/Scope**: 単一リポジトリ、個人開発

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution ファイルが存在しないため、標準的なベストプラクティスに従う:
- ✅ 既存のプロジェクト構造を維持
- ✅ 新しい依存関係の追加なし（pytest-cov は既存）
- ✅ 設定変更のみで破壊的変更なし

## Project Structure

### Documentation (this feature)

```text
specs/016-dev-env-optimization/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output (best practices research)
├── quickstart.md        # Phase 1 output (setup guide)
├── checklists/          # Quality checklists
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
# 変更対象ファイル
pyproject.toml           # [tool.pytest.ini_options] 追加
.github/workflows/ci.yml # カバレッジ設定、キャッシュ最適化、PR コメント
README.md                # カバレッジバッジ追加
```

**Structure Decision**: 既存の Single project 構造を維持。設定ファイルの変更のみで、新規ディレクトリやソースコードの追加なし。

## Implementation Phases

### Phase 1: pytest カバレッジ設定（P1）

**目標**: ローカル環境でカバレッジレポートを自動生成、閾値 80% を設定

**変更内容**:
1. `pyproject.toml` に `[tool.pytest.ini_options]` セクション追加
   - `addopts = "--cov=src --cov-report=term-missing --cov-fail-under=80"`
   - テストパス設定: `testpaths = ["tests"]`
2. カバレッジ除外設定（必要に応じて）

**検証方法**:
- `pytest` 実行でカバレッジレポートが表示される
- カバレッジ 80% 未満でテスト失敗

---

### Phase 2: CI キャッシュ最適化（P2）

**目標**: 依存関係のキャッシュを最適化し、CI 実行時間を短縮

**変更内容**:
1. `.github/workflows/ci.yml` の cache 設定確認・最適化
   - 現状: `actions/setup-python@v5` の `cache: 'pip'` を使用中
   - 最適化: キャッシュキーの明示化、復元戦略の改善

**検証方法**:
- 2 回目以降の CI 実行で「Cache restored」メッセージ確認
- 依存関係インストール時間の短縮

---

### Phase 3: PR カバレッジコメント（P2）

**目標**: PR にカバレッジレポートを自動コメント

**変更内容**:
1. CI ワークフローにカバレッジレポート生成ステップ追加
2. `py-cov-action/python-coverage-comment-action` または類似のアクション導入
3. カバレッジ XML レポート生成設定

**検証方法**:
- PR 作成時にカバレッジコメントが自動追加される
- カバレッジ変化（増減）が表示される

---

### Phase 4: カバレッジバッジ（P3）

**目標**: README にカバレッジバッジを表示

**変更内容**:
1. カバレッジバッジ生成アクション追加
   - オプション A: `gist` + `shields.io` 動的バッジ
   - オプション B: `codecov` サービス連携
2. README.md にバッジマークダウン追加

**検証方法**:
- README にバッジが表示される
- CI 実行後にバッジが更新される

## Risk Assessment

| リスク | 影響 | 対策 |
|--------|------|------|
| カバレッジ閾値未達成 | テスト失敗 | 初期は警告のみ or 低めの閾値から開始 |
| キャッシュ破損 | CI 失敗 | キャッシュキーにハッシュを含める |
| PR コメント権限 | コメント失敗 | `continue-on-error: true` で CI は成功させる |
| 外部サービス依存 | バッジ表示不可 | gist ベースの自己ホスト方式を優先 |

## Complexity Tracking

> 本機能は設定変更のみのため、複雑性違反なし

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | - | - |
