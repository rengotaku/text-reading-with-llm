# Feature Specification: CI Lint Actions

**Feature Branch**: `011-ci-lint-actions`
**Created**: 2026-02-24
**Status**: Draft
**Input**: Issue#19 - ci: GitHub Actions for Lint (ruff) を追加

## 概要

PR 作成・更新時および main ブランチへの push 時に、GitHub Actions を使用して自動的に lint チェック (ruff) を実行する。これにより、コード品質を CI レベルで保証し、レビュー前にコードスタイルの問題を検出できるようにする。

## User Scenarios & Testing

### User Story 1 - PR 作成時の自動 Lint チェック (Priority: P1)

開発者として、PR を作成または更新したときに、自動的に lint チェックが実行され、結果を PR 画面で確認できるようにしたい。これにより、レビュアーがコードスタイルの問題を指摘する前に、自分で修正できる。

**Why this priority**: CI の主要な目的であり、これがないと機能として成立しない。すべての PR で品質チェックが自動実行されることが最も重要。

**Independent Test**: PR を作成し、GitHub Actions が実行されて結果が PR 画面に表示されることを確認する。

**Acceptance Scenarios**:

1. **Given** lint エラーのないコードで PR を作成、**When** GitHub Actions が実行される、**Then** CI が成功ステータスを返し、PR 画面に緑のチェックマークが表示される
2. **Given** lint エラーのあるコードで PR を作成、**When** GitHub Actions が実行される、**Then** CI が失敗ステータスを返し、PR 画面に赤い × マークが表示される
3. **Given** 実行中の CI がある PR、**When** コードを push して更新する、**Then** 新しい CI が実行され、最新のコードに対する結果が表示される

---

### User Story 2 - ローカルと CI の結果一致 (Priority: P2)

開発者として、ローカルで `make lint` を実行した結果と CI の結果が一致することを期待する。これにより、ローカルで問題を修正してから push すれば、CI も通ることが保証される。

**Why this priority**: 開発者体験として重要。ローカルと CI で結果が異なると、無駄な修正サイクルが発生し、生産性が低下する。

**Independent Test**: ローカルで `make lint` を実行し、その結果と CI の出力を比較して一致することを確認する。

**Acceptance Scenarios**:

1. **Given** ローカルで `make lint` が成功するコード、**When** そのコードで PR を作成、**Then** CI も成功する
2. **Given** ローカルで `make lint` が失敗するコード、**When** そのコードで PR を作成、**Then** CI も同じエラーで失敗する
3. **Given** 同じ ruff 設定 (pyproject.toml)、**When** ローカルと CI で lint を実行、**Then** 同一のエラーメッセージが出力される

---

### User Story 3 - main ブランチ保護 (Priority: P3)

プロジェクト管理者として、main ブランチへの直接 push 時にも lint チェックが実行されるようにしたい。これにより、マージ後のコード品質も保証される。

**Why this priority**: PR ベースのワークフローでは通常 P1 でカバーされるが、直接 push のケースへの備えとして必要。

**Independent Test**: main ブランチに直接 push して、GitHub Actions が実行されることを確認する。

**Acceptance Scenarios**:

1. **Given** main ブランチ、**When** コードを直接 push する、**Then** lint チェックが自動実行される

---

### Edge Cases

- **CI 実行中にキャンセル**: ユーザーが手動で CI をキャンセルした場合、中断された状態となり、再実行が可能
- **同時複数 push**: 短時間に複数回 push された場合、最新のコミットに対する CI が実行される
- **依存関係インストール失敗**: pip インストールが失敗した場合、明確なエラーメッセージとともに CI が失敗する
- **ruff 設定エラー**: pyproject.toml の ruff 設定に問題がある場合、設定エラーとして CI が失敗する

## Requirements

### Functional Requirements

- **FR-001**: システムは PR 作成時に自動的に lint チェックを開始しなければならない
- **FR-002**: システムは PR 更新（push）時に自動的に lint チェックを再実行しなければならない
- **FR-003**: システムは main ブランチへの push 時に自動的に lint チェックを実行しなければならない
- **FR-004**: システムは lint エラー検出時に失敗ステータスを返さなければならない
- **FR-005**: システムは lint チェック結果を PR 画面に表示しなければならない
- **FR-006**: システムは既存の `make lint` コマンドを使用して lint チェックを実行しなければならない
- **FR-007**: システムは pip 依存関係のキャッシュを利用して実行時間を短縮しなければならない
- **FR-008**: システムは必要最小限の依存関係のみインストールしなければならない（requirements-dev.txt）

### 前提条件

- ruff の設定は既存の pyproject.toml に定義済み
- pre-commit hook は既にセットアップ済み
- GitHub Actions の利用が許可されたリポジトリである
- Python 3.10+ 環境を使用

## Success Criteria

### Measurable Outcomes

- **SC-001**: PR を作成すると 5 分以内に lint チェックが完了する
- **SC-002**: lint エラーがある場合、100% の確率で CI が失敗ステータスを返す
- **SC-003**: `make lint` でローカル実行した結果と CI の結果が一致する

## Assumptions

- GitHub Actions の無料枠または有料プランで実行時間が確保されている
- リポジトリに `.github/workflows/` ディレクトリへの書き込み権限がある
- requirements-dev.txt に ruff が含まれている
- pyproject.toml の ruff 設定は正常に動作する状態である
