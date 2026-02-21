# Research: ruff導入・pre-commit設定・ファイル分割

**Date**: 2026-02-20
**Feature**: 008-ruff-precommit-setup

## Decision 1: ruff設定

**Decision**: pyproject.tomlにruff設定を追加（Issue #7の要件に準拠）

**Rationale**:
- Issue #7で明示的に指定された設定値を採用
- E: pycodestyle errors, F: pyflakes, I: isort, W: pycodestyle warnings
- line-length 120、target-version py310

**Alternatives**: flake8+isort+black（ruffで統合）、広いルールセット（初期はE/F/I/Wに限定）

## Decision 2: pre-commit設定

**Decision**: ruff公式pre-commitフック（astral-sh/ruff-pre-commit）

**Rationale**: 公式対応、--fixで自動修正、ruff-formatも統合

**Alternatives**: ローカルhook（バージョン管理が煩雑）、husky（Pythonエコシステム不適合）

## Decision 3: ファイル分割戦略

**Decision**: 3ファイル分割 + re-exportパターン

| ファイル | 責務 | 行範囲 |
|---------|------|--------|
| process_manager.py | PID管理 | 49-124 (~90行) |
| chapter_processor.py | 音声チャプター処理 | 202-507 (~320行) |
| xml2_pipeline.py | CLI/メイン | 127-199,510-651 (~240行) |

**Rationale**: 単一責任原則、re-exportで後方互換性100%維持

**Alternatives**: 2分割（550行で上限に近い）、関数単位分割（過度）

## Decision 4: 依存関係管理

**Decision**: requirements-dev.txtに分離、Makefileにsetup-devターゲット追加

## Decision 5: 既存コードのruff違反対応

**Decision**: ruff check --fix + ruff formatで一括修正
