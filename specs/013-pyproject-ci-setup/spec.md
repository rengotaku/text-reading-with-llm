# Feature Specification: pyproject.toml 整備 + CI テスト追加

**Feature Branch**: `013-pyproject-ci-setup`
**Created**: 2026-02-25
**Status**: Draft
**Input**: Issue#23 - プロジェクト設定の基盤整備

## User Scenarios & Testing *(mandatory)*

### User Story 1 - プロジェクトセットアップの簡素化 (Priority: P1)

開発者として、新しい環境でプロジェクトをセットアップする際に、単一のコマンドで全ての依存関係をインストールしたい。これにより、セットアップ時間を短縮し、手順ミスを防ぐことができる。

**Why this priority**: プロジェクトの基盤となる設定であり、他の全ての開発作業に影響する。正しく動作しないと開発が進められない。

**Independent Test**: `pip install -e ".[dev]"` を実行し、全ての依存関係がインストールされ、テストとlintが実行可能になることを確認。

**Acceptance Scenarios**:

1. **Given** クリーンな Python 3.10+ 環境、**When** `pip install -e ".[dev]"` を実行、**Then** 全ての本番依存と開発依存がインストールされる
2. **Given** インストール済み環境、**When** `make test` を実行、**Then** pytest が正常に動作する
3. **Given** インストール済み環境、**When** `make lint` を実行、**Then** ruff が正常に動作する

---

### User Story 2 - CI でのテスト自動実行 (Priority: P1)

開発者として、Pull Request を作成した際に、テストとカバレッジが自動的に実行されることを確認したい。これにより、品質を担保した状態でマージできる。

**Why this priority**: CI テストがないと、壊れたコードがマージされるリスクがある。プロジェクトの品質基盤として必須。

**Independent Test**: PR を作成し、GitHub Actions でテストが実行され、結果が PR に表示されることを確認。

**Acceptance Scenarios**:

1. **Given** main ブランチへの PR、**When** PR が作成される、**Then** lint チェックが自動実行される
2. **Given** main ブランチへの PR、**When** PR が作成される、**Then** pytest が自動実行される
3. **Given** テスト実行完了、**When** テストが失敗、**Then** PR にテスト失敗が表示される
4. **Given** テスト実行完了、**When** 全テスト成功、**Then** PR に成功ステータスが表示される

---

### User Story 3 - 依存関係の一元管理 (Priority: P2)

開発者として、依存関係が pyproject.toml に一元化されていることで、バージョン管理と依存関係の把握が容易になる。

**Why this priority**: 依存関係が分散していると管理コストが上がり、不整合が発生しやすい。P1 の基盤整備が完了してから対応可能。

**Independent Test**: pyproject.toml のみで全依存関係が定義され、requirements.txt が不要になることを確認。

**Acceptance Scenarios**:

1. **Given** pyproject.toml に依存関係定義済み、**When** requirements.txt を削除、**Then** プロジェクトは正常に動作する
2. **Given** 開発者が依存関係を確認したい、**When** pyproject.toml を参照、**Then** 全ての依存関係が一覧できる

---

### Edge Cases

- pyproject.toml の構文エラーがある場合、pip install は明確なエラーメッセージを表示する
- Python バージョンが 3.10 未満の場合、インストール時にエラーとなる
- VOICEVOX wheel は外部 URL からのインストールが必要なため、別途手順が必要

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: pyproject.toml に `[project]` セクションを追加し、プロジェクト名 `text-reading-with-llm` とバージョン `0.1.0` を定義する
- **FR-002**: pyproject.toml の `dependencies` に本番依存（soundfile, pyyaml, numpy, requests, fugashi, unidic-lite）を定義する
- **FR-003**: pyproject.toml の `[project.optional-dependencies]` に開発依存（ruff, pre-commit, pytest, pytest-cov）を定義する
- **FR-004**: Makefile の setup ターゲットを `pip install -e ".[dev]"` を使用するよう更新する
- **FR-005**: GitHub Actions workflow に pytest 実行ステップを追加する
- **FR-006**: requirements.txt と requirements-dev.txt を削除する
- **FR-007**: `src/UNKNOWN.egg-info/` ディレクトリを削除する
- **FR-008**: Python バージョン要件 `>=3.10` を pyproject.toml に明記する

### Key Entities

- **pyproject.toml**: プロジェクトのメタデータ、依存関係、ツール設定を一元管理するファイル
- **GitHub Actions workflow**: CI/CD パイプラインの定義ファイル（.github/workflows/lint.yml）

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 新規環境で `pip install -e ".[dev]"` 実行後、`make test` と `make lint` が正常に動作する
- **SC-002**: PR 作成時に GitHub Actions でテストが自動実行され、結果が PR に表示される
- **SC-003**: 依存関係の定義ファイルが pyproject.toml 1ファイルに統合される（requirements*.txt が不要になる）
- **SC-004**: `src/UNKNOWN.egg-info/` が削除され、正しいプロジェクト名の egg-info が生成される

## Assumptions

- VOICEVOX Core wheel は外部 URL からのインストールが必要なため、Makefile の setup-voicevox ターゲットで別途処理する
- 既存の 509 件のテストは全てパスしている状態を維持する
- pre-commit の設定（.pre-commit-config.yaml）は変更しない
