# Feature Specification: mypy 型チェック導入

**Feature Branch**: `014-mypy-type-checking`
**Created**: 2026-02-27
**Status**: Draft
**Input**: GitHub Issue #25 - chore: mypy 型チェック導入

## Clarifications

### Session 2026-02-27

- Q: pre-commit フックを利用するか？ → A: 利用しない。CI での型チェックを主要な自動チェック手段とする
- Q: CI 統合アプローチは？ → A: 既存の lint ワークフローに mypy ステップを追加

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 型チェック設定の構成 (Priority: P1)

開発者として、プロジェクトの型チェック設定を pyproject.toml で一元管理したい。これにより、チーム全体で一貫した型チェック基準を適用できる。

**Why this priority**: 設定がなければ型チェック自体が動作しないため、インフラストラクチャとして P1。

**Independent Test**: `mypy src/` コマンドを実行し、設定ファイルの内容に基づいた型チェックが行われることを確認できる。

**Acceptance Scenarios**:

1. **Given** pyproject.toml に mypy 設定が存在する, **When** mypy を実行する, **Then** 設定に基づいた型チェックが実行される
2. **Given** pyproject.toml の設定で `warn_return_any = true` が有効, **When** Any 型を返す関数がある, **Then** 警告が出力される

---

### User Story 2 - CI での型チェック (Priority: P1)

開発者として、プルリクエスト時に CI で型チェックが自動実行されるようにしたい。これにより、コードレビュー前に型エラーを自動検出できる。

**Why this priority**: pre-commit を利用しないため、CI が主要な自動型チェック手段となる。型エラーの混入を防ぐゲートとして必須。

**Independent Test**: GitHub Actions ワークフローを追加し、型エラーのある PR が CI で失敗することを確認できる。

**Acceptance Scenarios**:

1. **Given** GitHub Actions に mypy ジョブが設定されている, **When** 型エラーのあるコードを含む PR を作成する, **Then** CI が失敗しエラー内容が表示される
2. **Given** GitHub Actions に mypy ジョブが設定されている, **When** 型エラーのないコードの PR を作成する, **Then** CI が成功する

---

### User Story 3 - ローカルでの型チェック実行 (Priority: P1)

開発者として、ローカル環境で手動またはMakefileターゲット経由で型チェックを実行したい。PR 作成前にローカルで型エラーを確認できる。

**Why this priority**: CI でのフィードバックを待たずに、開発中に素早く型エラーを検出するため。

**Independent Test**: `make lint` または `mypy src/` を実行し、型エラーが検出されることを確認できる。

**Acceptance Scenarios**:

1. **Given** 開発者がローカル環境で作業している, **When** `mypy src/` を実行する, **Then** 型エラーがあれば検出・表示される
2. **Given** Makefile に lint ターゲットが存在する, **When** `make lint` を実行する, **Then** mypy を含む静的解析が実行される

---

### User Story 4 - 既存コードの段階的型付け (Priority: P2)

開発者として、既存のコードに段階的に型ヒントを追加できるようにしたい。全てのコードに一度に型を付けることは現実的ではないため、新規コードを優先しつつ、既存コードは徐々に改善する。

**Why this priority**: 既存コードの型付けは重要だが、新規コードの型チェック体制が整ってから取り組むべき。

**Independent Test**: 型ヒントのない既存コードが存在していても、厳格モードが無効な状態では mypy がエラーを出さないことを確認できる。

**Acceptance Scenarios**:

1. **Given** `disallow_untyped_defs = false` が設定されている, **When** 型ヒントのない関数を含むモジュールを型チェックする, **Then** エラーなくチェックが完了する
2. **Given** 開発者が既存関数に型ヒントを追加した, **When** 型チェックを実行する, **Then** 追加された型ヒントに基づいて検証が行われる

---

### Edge Cases

- 型チェックで false positive（誤検出）が発生した場合はどうするか？
  → `# type: ignore[<エラーコード>]` コメントで特定の行を除外可能。ただし濫用を防ぐため、理由をコメントに記載することを推奨
- サードパーティライブラリに型スタブがない場合はどうするか？
  → `ignore_missing_imports = true` を設定するか、必要に応じて stubs パッケージをインストール
- 循環インポートが型ヒントで発生した場合はどうするか？
  → `TYPE_CHECKING` ガードと文字列アノテーション（forward reference）を使用

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: pyproject.toml に mypy の設定セクション `[tool.mypy]` を追加しなければならない
- **FR-002**: Python バージョンは 3.10 以上を対象とする設定でなければならない
- **FR-003**: 型エラーの警告として `warn_return_any` と `warn_unused_ignores` を有効化しなければならない
- **FR-004**: 既存コードへの影響を最小限にするため、初期段階では `disallow_untyped_defs = false` としなければならない
- **FR-005**: 既存の GitHub Actions lint ワークフローに mypy ステップを追加し、PR 時に自動実行しなければならない
- **FR-006**: 主要モジュール（`src/` 配下）を型チェック対象としなければならない
- **FR-007**: Makefile に型チェック用ターゲットを追加しなければならない（オプション：既存 lint ターゲットへの統合可）

### Key Entities

- **mypy 設定**: プロジェクト全体の型チェックルールを定義。厳格度、対象 Python バージョン、警告レベルを含む
- **型ヒント**: 関数の引数・戻り値、変数に付与される型情報。コード品質向上のための静的解析の基盤
- **CI ジョブ**: GitHub Actions で実行される mypy チェック。PR のゲートとして機能

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: PR に含まれる型エラーが CI で 100% 検出される
- **SC-002**: 型チェックの実行時間が 30 秒以内に完了する（現在のコードベース規模において）
- **SC-003**: 既存コードベースに対する型チェックが、設定適用後にエラー 0 で通過する（厳格モード無効時）
- **SC-004**: 型関連のランタイムエラー（AttributeError、TypeError など）が導入後 3 ヶ月で 30% 減少する

## Assumptions

- プロジェクトは既に Python 3.10 以上を使用している
- 開発者は基本的な Python 型ヒントの知識を持っている
- CI 環境として GitHub Actions を使用している
- Makefile がプロジェクトに存在する

## Out of Scope

- pre-commit フックの設定（利用しない）
- 既存コードへの型ヒントの完全な追加（段階的に実施）
- 100% の型カバレッジの達成（将来の目標として設定）
- py.typed マーカーの追加（ライブラリとしての配布は想定外）
