"""src.llm_config.load_llm_profile() のユニットテスト。"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.llm_config import load_llm_profile


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    """標準的な llm セクション付きの config.yaml を返す。"""
    content = """
llm:
  defaults:
    temperature: 0.3
    num_predict: 4096
  profiles:
    reading_dict:
      temperature: 0.2
    dialogue:
      temperature: 0.5
      repeat_penalty: 1.2
    introduction:
      temperature: 0.4
"""
    path = tmp_path / "config.yaml"
    path.write_text(content, encoding="utf-8")
    return path


def test_returns_merged_defaults_and_profile(config_file: Path) -> None:
    """defaults に profile を上書きマージした dict を返す。"""
    result = load_llm_profile("dialogue", config_path=config_file)
    assert result == {
        "temperature": 0.5,  # profile override
        "num_predict": 4096,  # from defaults
        "repeat_penalty": 1.2,  # profile only
    }


def test_profile_overrides_single_key(config_file: Path) -> None:
    """profile が temperature だけ持つ場合も正しくマージ。"""
    result = load_llm_profile("reading_dict", config_path=config_file)
    assert result == {"temperature": 0.2, "num_predict": 4096}


def test_unknown_profile_returns_defaults_only(config_file: Path) -> None:
    """未定義 profile 名は defaults のみ返す。"""
    result = load_llm_profile("nonexistent", config_path=config_file)
    assert result == {"temperature": 0.3, "num_predict": 4096}


def test_missing_config_file_returns_empty(tmp_path: Path) -> None:
    """config ファイルが存在しない場合は空 dict を返す。"""
    missing = tmp_path / "no_such.yaml"
    assert load_llm_profile("dialogue", config_path=missing) == {}


def test_config_without_llm_section_returns_empty(tmp_path: Path) -> None:
    """llm セクションが無い場合は空 dict を返す。"""
    path = tmp_path / "config.yaml"
    path.write_text("speakers:\n  SPEAKER_A:\n    name: 教授\n", encoding="utf-8")
    assert load_llm_profile("dialogue", config_path=path) == {}


def test_config_without_defaults(tmp_path: Path) -> None:
    """defaults 無しで profile のみ定義されている場合も動作する。"""
    path = tmp_path / "config.yaml"
    path.write_text(
        "llm:\n  profiles:\n    dialogue:\n      temperature: 0.7\n",
        encoding="utf-8",
    )
    result = load_llm_profile("dialogue", config_path=path)
    assert result == {"temperature": 0.7}


def test_config_without_profiles(tmp_path: Path) -> None:
    """profiles 無しで defaults のみの場合、defaults を返す。"""
    path = tmp_path / "config.yaml"
    path.write_text(
        "llm:\n  defaults:\n    temperature: 0.3\n",
        encoding="utf-8",
    )
    result = load_llm_profile("dialogue", config_path=path)
    assert result == {"temperature": 0.3}


def test_empty_config_file_returns_empty(tmp_path: Path) -> None:
    """空ファイルの場合は空 dict を返す。"""
    path = tmp_path / "config.yaml"
    path.write_text("", encoding="utf-8")
    assert load_llm_profile("dialogue", config_path=path) == {}


def test_malformed_yaml_returns_empty(tmp_path: Path) -> None:
    """YAML パースエラー時は空 dict を返す（warning ログ出力）。"""
    path = tmp_path / "config.yaml"
    path.write_text("llm:\n  defaults:\n    temperature: [invalid\n", encoding="utf-8")
    assert load_llm_profile("dialogue", config_path=path) == {}
