"""LLM プロファイル設定ローダー。

config.yaml の `llm` セクションから用途別（profile）パラメータを読み込み、
defaults + profile のマージ結果を返す。

config.yaml の想定構造:

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
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path("config.yaml")


def load_llm_profile(
    name: str,
    config_path: Path | None = None,
) -> dict[str, Any]:
    """指定された profile 名の LLM options を返す。

    `llm.defaults` に `llm.profiles.<name>` を上書きマージした dict を返す。
    config が存在しない、または `llm` セクションがない場合は空 dict を返す。
    指定された profile 名が存在しない場合は defaults のみを返す。

    Args:
        name: profile 名（例: "reading_dict", "dialogue", "introduction"）
        config_path: 設定ファイルパス（None の場合は `config.yaml`）

    Returns:
        マージ済みの options 辞書（例: {"temperature": 0.5, "num_predict": 4096, "repeat_penalty": 1.2}）
    """
    path = config_path or DEFAULT_CONFIG_PATH
    if not path.exists():
        return {}

    try:
        with open(path, encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    except Exception as e:
        logger.warning("LLM 設定の読み込みに失敗: %s", e)
        return {}

    llm_config = config.get("llm") or {}
    defaults = llm_config.get("defaults") or {}
    profiles = llm_config.get("profiles") or {}
    profile = profiles.get(name) or {}

    merged: dict[str, Any] = {**defaults, **profile}
    return merged
