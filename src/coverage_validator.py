"""カバー率検証モジュール。

キーワードリストと対話XMLを入力として、
文字列マッチング（LLM不使用）でカバー率を計算する。
"""

import re
from dataclasses import dataclass

_ASCII_WORD_PATTERN = re.compile(r"^[a-zA-Z0-9_]+$")


def _keyword_in_text(keyword: str, text: str) -> bool:
    """キーワードがテキスト内に存在するか確認する（case-insensitive）。

    ASCII英数字+アンダースコアのみのキーワードは単語境界マッチングを使用し、
    それ以外（日本語・特殊文字・スペース含む）は部分文字列マッチングを使用する。
    """
    kw_lower = keyword.lower()
    text_lower = text.lower()
    if _ASCII_WORD_PATTERN.match(kw_lower):
        return bool(re.search(r"\b" + re.escape(kw_lower) + r"\b", text_lower))
    return kw_lower in text_lower


@dataclass
class CoverageResult:
    """カバー率検証の出力結果。"""

    total_keywords: int
    covered_keywords: int
    coverage_rate: float
    missing_keywords: list[str]

    def to_dict(self) -> dict:
        """dict 形式に変換する（JSON出力用）。"""
        return {
            "total_keywords": self.total_keywords,
            "covered_keywords": self.covered_keywords,
            "coverage_rate": self.coverage_rate,
            "missing_keywords": self.missing_keywords,
        }


def validate_coverage(keywords: list[str], dialogue_xml: str) -> CoverageResult:
    """キーワードリストと対話XMLを比較してカバー率を計算する。

    Args:
        keywords: キーワードリスト
        dialogue_xml: 対話XML文字列

    Returns:
        CoverageResult: カバー率検証結果

    Raises:
        TypeError: keywords が None または dialogue_xml が None の場合
        TypeError: keywords が list 型でない場合
        TypeError: dialogue_xml が str 型でない場合
    """
    if keywords is None:
        raise TypeError("keywords は None にできません")
    if dialogue_xml is None:
        raise TypeError("dialogue_xml は None にできません")
    if not isinstance(keywords, list):
        raise TypeError(f"keywords は list 型である必要があります: {type(keywords)}")
    if not isinstance(dialogue_xml, str):
        raise TypeError(f"dialogue_xml は str 型である必要があります: {type(dialogue_xml)}")

    total = len(keywords)
    if total == 0:
        return CoverageResult(
            total_keywords=0,
            covered_keywords=0,
            coverage_rate=1.0,
            missing_keywords=[],
        )

    missing = [kw for kw in keywords if not _keyword_in_text(kw, dialogue_xml)]
    covered = total - len(missing)
    coverage_rate = covered / total

    return CoverageResult(
        total_keywords=total,
        covered_keywords=covered,
        coverage_rate=coverage_rate,
        missing_keywords=missing,
    )
