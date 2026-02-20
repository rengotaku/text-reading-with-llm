"""Tests for ruff and pre-commit configuration verification.

Phase 2 RED Tests - US1+US2: ruff設定・pre-commit設定の検証
pyproject.toml と .pre-commit-config.yaml の設定内容が期待通りであることを確認する。
"""

from pathlib import Path

import pytest

# プロジェクトルートパス
PROJECT_ROOT = Path(__file__).parent.parent


class TestPyprojectTomlRuffSettings:
    """pyproject.toml の ruff 設定値が正しいことを検証する。"""

    @pytest.fixture()
    def pyproject_content(self):
        """pyproject.toml の内容を読み込む。"""
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        assert pyproject_path.exists(), "pyproject.toml がプロジェクトルートに存在しない"
        return pyproject_path.read_text(encoding="utf-8")

    def test_ruff_line_length_is_120(self, pyproject_content):
        """ruff の line-length が 120 に設定されていることを確認する。"""
        assert "line-length = 120" in pyproject_content, (
            "pyproject.toml に line-length = 120 が設定されていない"
        )

    def test_ruff_target_version_is_py310(self, pyproject_content):
        """ruff の target-version が py310 に設定されていることを確認する。"""
        assert 'target-version = "py310"' in pyproject_content, (
            'pyproject.toml に target-version = "py310" が設定されていない'
        )

    def test_ruff_lint_select_contains_required_rules(self, pyproject_content):
        """ruff の lint select に E, F, I, W が含まれていることを確認する。"""
        assert "[tool.ruff.lint]" in pyproject_content, (
            "pyproject.toml に [tool.ruff.lint] セクションがない"
        )
        # select に必要なルールが全て含まれていることを確認
        for rule in ["E", "F", "I", "W"]:
            assert f'"{rule}"' in pyproject_content, (
                f"pyproject.toml の ruff lint select に {rule} が含まれていない"
            )

    def test_ruff_isort_known_first_party(self, pyproject_content):
        """ruff の isort known-first-party に src が設定されていることを確認する。"""
        assert "[tool.ruff.lint.isort]" in pyproject_content, (
            "pyproject.toml に [tool.ruff.lint.isort] セクションがない"
        )
        assert '"src"' in pyproject_content, (
            'pyproject.toml の isort known-first-party に "src" が含まれていない'
        )


class TestPreCommitConfigYaml:
    """pre-commit-config.yaml の設定が正しいことを検証する。"""

    @pytest.fixture()
    def precommit_content(self):
        """.pre-commit-config.yaml の内容を読み込む。"""
        config_path = PROJECT_ROOT / ".pre-commit-config.yaml"
        assert config_path.exists(), ".pre-commit-config.yaml がプロジェクトルートに存在しない"
        return config_path.read_text(encoding="utf-8")

    def test_precommit_config_exists(self):
        """.pre-commit-config.yaml がプロジェクトルートに存在することを確認する。"""
        config_path = PROJECT_ROOT / ".pre-commit-config.yaml"
        assert config_path.exists(), ".pre-commit-config.yaml が存在しない"

    def test_precommit_uses_ruff_pre_commit_repo(self, precommit_content):
        """ruff-pre-commit リポジトリが設定されていることを確認する。"""
        assert "astral-sh/ruff-pre-commit" in precommit_content, (
            ".pre-commit-config.yaml に astral-sh/ruff-pre-commit リポジトリが設定されていない"
        )

    def test_precommit_has_ruff_hook_with_fix(self, precommit_content):
        """ruff フック（--fix オプション付き）が設定されていることを確認する。"""
        assert "id: ruff" in precommit_content, (
            ".pre-commit-config.yaml に ruff フックが設定されていない"
        )
        assert "--fix" in precommit_content, (
            ".pre-commit-config.yaml の ruff フックに --fix オプションが設定されていない"
        )

    def test_precommit_has_ruff_format_hook(self, precommit_content):
        """ruff-format フックが設定されていることを確認する。"""
        assert "id: ruff-format" in precommit_content, (
            ".pre-commit-config.yaml に ruff-format フックが設定されていない"
        )

    def test_precommit_has_version_pinned(self, precommit_content):
        """ruff-pre-commit のバージョンが固定されていることを確認する。"""
        assert "rev:" in precommit_content, (
            ".pre-commit-config.yaml でバージョンが固定されていない（rev が未設定）"
        )


class TestMakefileTargets:
    """Makefile に必要なターゲットが存在することを検証する。"""

    @pytest.fixture()
    def makefile_content(self):
        """Makefile の内容を読み込む。"""
        makefile_path = PROJECT_ROOT / "Makefile"
        assert makefile_path.exists(), "Makefile がプロジェクトルートに存在しない"
        return makefile_path.read_text(encoding="utf-8")

    def test_makefile_has_lint_target(self, makefile_content):
        """Makefile に lint ターゲットが存在することを確認する。"""
        assert "lint:" in makefile_content, (
            "Makefile に lint ターゲットが定義されていない"
        )

    def test_makefile_has_format_target(self, makefile_content):
        """Makefile に format ターゲットが存在することを確認する。"""
        assert "format:" in makefile_content, (
            "Makefile に format ターゲットが定義されていない"
        )

    def test_makefile_has_setup_dev_target(self, makefile_content):
        """Makefile に setup-dev ターゲットが存在することを確認する。"""
        assert "setup-dev:" in makefile_content, (
            "Makefile に setup-dev ターゲットが定義されていない"
        )

    def test_makefile_lint_uses_ruff(self, makefile_content):
        """Makefile の lint ターゲットが ruff を使用していることを確認する。"""
        assert "ruff check" in makefile_content, (
            "Makefile の lint ターゲットが ruff check を使用していない"
        )
        assert "ruff format --check" in makefile_content, (
            "Makefile の lint ターゲットが ruff format --check を使用していない"
        )
