# Feature Specification: ruff導入・pre-commit設定・ファイル分割

**Feature Branch**: `008-ruff-precommit-setup`
**Created**: 2026-02-20
**Status**: Draft
**Input**: GitHub Issue #7 - ruff導入・pre-commit設定・ファイル分割

## User Scenarios & Testing *(mandatory)*

### User Story 1 - コード品質の自動チェック (Priority: P1)

開発者として、コードをコミットする際にリンターとフォーマッターが自動的に実行され、コードスタイルの一貫性が保たれるようにしたい。手動でのチェック忘れを防ぎ、プロジェクト全体でコード品質を維持するため。

**Why this priority**: コード品質の自動化はプロジェクト全体に影響する基盤であり、他のすべての開発作業の品質を底上げする。

**Independent Test**: `git commit` 実行時にruff checkとruff formatが自動実行され、違反がある場合はコミットがブロックされることを確認する。

**Acceptance Scenarios**:

1. **Given** pre-commitがインストール済みの環境で、**When** スタイル違反のあるPythonファイルをコミットしようとした場合、**Then** ruff checkがエラーを報告しコミットがブロックされる
2. **Given** pre-commitがインストール済みの環境で、**When** フォーマット違反のあるPythonファイルをコミットしようとした場合、**Then** ruff formatが自動的にフォーマットを修正する
3. **Given** pre-commitがインストール済みの環境で、**When** すべてのチェックに合格するPythonファイルをコミットした場合、**Then** コミットが正常に完了する

---

### User Story 2 - ruffによるコード品質設定 (Priority: P1)

開発者として、プロジェクト全体で統一されたリンティング・フォーマッティングルールを持ちたい。pyproject.tomlに設定を集約し、どの開発者も同じルールでコードを書けるようにするため。

**Why this priority**: pre-commitフックの基盤となるruff設定がなければ、自動チェックが機能しない。

**Independent Test**: `ruff check .` と `ruff format --check .` をプロジェクトルートで実行し、設定が正しく適用されることを確認する。

**Acceptance Scenarios**:

1. **Given** pyproject.tomlにruff設定が追加された状態で、**When** `ruff check .` を実行した場合、**Then** 指定されたルール（E, F, I, W）に基づいてチェックが実行される
2. **Given** pyproject.tomlにruff設定が追加された状態で、**When** `ruff format --check .` を実行した場合、**Then** 行長120文字・Python 3.10ターゲットでフォーマットチェックが実行される

---

### User Story 3 - 大規模ファイルの分割 (Priority: P2)

開発者として、600行を超えるファイルを適切な単位に分割し、コードの可読性と保守性を向上させたい。

**Why this priority**: コード品質の向上に寄与するが、ruffとpre-commitの設定（P1）が先に完了している必要がある。分割後のコードもruffチェックに合格する必要があるため。

**Independent Test**: 分割後のファイルがすべて600行以下であり、既存のテストがすべてパスすることを確認する。

**Acceptance Scenarios**:

1. **Given** 651行の `src/xml2_pipeline.py` が存在する状態で、**When** ファイル分割を実行した場合、**Then** 各分割ファイルが600行以下になり、元のすべての機能が維持される
2. **Given** ファイル分割が完了した状態で、**When** 既存のテストスイートを実行した場合、**Then** すべてのテストがパスする
3. **Given** ファイル分割が完了した状態で、**When** `ruff check .` を実行した場合、**Then** 分割後のファイルがすべてruffチェックに合格する

---

### Edge Cases

- ruff checkで既存コードに大量の違反が検出された場合はどうするか？ → 初回は `ruff check --fix` で自動修正可能なものを修正し、残りは手動対応する
- pre-commit hookをスキップしてコミットしたい場合はどうするか？ → `git commit --no-verify` で一時的にスキップ可能（緊急時のみ）
- ファイル分割時にcircular importが発生した場合はどうするか？ → 依存関係を分析し、共通モジュールの抽出やインポート順序の調整で解決する
- `number_normalizer.py` (523行) は現時点で600行以下だが対象とするか？ → Issue記載の通り、現時点では対象外とし、増加傾向がある場合のみ将来対応する

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: プロジェクトの `pyproject.toml` にruffの設定を追加しなければならない（line-length: 120, target-version: py310, select: E, F, I, W）
- **FR-002**: `.pre-commit-config.yaml` を作成し、ruff checkとruff formatのフックを設定しなければならない
- **FR-003**: pre-commit hookが `git commit` 時に自動実行されなければならない
- **FR-004**: ruff checkで違反が検出された場合、コミットをブロックしなければならない
- **FR-005**: ruff formatでフォーマット違反が検出された場合、自動修正を適用しなければならない
- **FR-006**: `src/xml2_pipeline.py` を600行以下の複数ファイルに分割しなければならない
- **FR-007**: ファイル分割後、既存の外部インターフェース（importパス、公開関数・クラス）の後方互換性を維持しなければならない
- **FR-008**: ファイル分割後、既存のすべてのテストがパスしなければならない
- **FR-009**: 分割後のすべてのファイルがruffチェックに合格しなければならない

## Assumptions

- ruffは開発用依存関係として追加する
- pre-commitも開発用依存関係として追加する
- 既存のCI/CDパイプラインへの統合は本スコープ外とする
- `number_normalizer.py` は523行で600行以下のため、本スコープでは分割対象外とする
- ファイル分割の具体的な分割単位は、コードの論理的なまとまり（クラス、機能グループ）に基づいて実装時に決定する

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `ruff check .` がプロジェクト全体で警告・エラー0件で完了する
- **SC-002**: `ruff format --check .` がプロジェクト全体で差分0件で完了する
- **SC-003**: `git commit` 実行時にpre-commitフックが自動的にruff check/formatを実行する
- **SC-004**: `src/xml2_pipeline.py` から分割されたすべてのファイルが600行以下である
- **SC-005**: 既存のテストスイートが100%パスする（分割前と同じテスト結果）
- **SC-006**: 開発者がpre-commitをセットアップするために必要な手順が3ステップ以内である
