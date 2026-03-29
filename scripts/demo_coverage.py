#!/usr/bin/env python3
"""キーワード抽出とカバー率検証のデモスクリプト。

Usage:
    make demo-coverage                    # デフォルトのサンプルで実行
    make demo-coverage SECTION="テキスト"  # カスタムテキストで実行
    make demo-coverage DIALOGUE="<dialogue>...</dialogue>"  # カスタム対話で実行
"""

import argparse
import json
import os
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.coverage_validator import validate_coverage

# デフォルトのサンプルセクション
DEFAULT_SECTION = """
SRE（Site Reliability Engineering）は、Googleが2003年頃に確立した運用手法である。
従来の運用チームとは異なり、SREチームはソフトウェアエンジニアリングのアプローチを採用する。

主要な概念として、SLI（Service Level Indicator）とSLO（Service Level Objective）がある。
SLIはサービスの信頼性を測定する指標であり、SLOはその目標値を定義する。
例えば、可用性99.9%（スリーナイン）を目標とする場合、年間のダウンタイムは約8.7時間以内に抑える必要がある。

エラーバジェットという概念も重要である。これは「許容されるエラーの量」を予算として管理する手法だ。
SLOを99.9%に設定した場合、0.1%のエラーバジェットが与えられる。
"""

# デフォルトのサンプル対話
DEFAULT_DIALOGUE = """
<dialogue>
  <line speaker="A">SREって聞いたことある？Site Reliability Engineeringの略なんだけど。</line>
  <line speaker="B">うーん、Googleが作った運用手法ですよね？2003年頃に確立されたとか。</line>
  <line speaker="A">そうそう。従来の運用チームとは違って、ソフトウェアエンジニアリングのアプローチを使うんだ。</line>
  <line speaker="B">SLIとSLOっていう概念があるって聞きました。</line>
  <line speaker="A">SLIはサービスの信頼性を測る指標で、SLOはその目標値だね。</line>
  <line speaker="B">例えば可用性99.9%とか？スリーナインってやつ。</line>
  <line speaker="A">そう、それだと年間のダウンタイムは8.7時間以内に抑えないといけない。</line>
  <line speaker="B">エラーバジェットという概念もあるんですよね？</line>
  <line speaker="A">許容されるエラーの量を予算として管理する手法だね。新機能リリースに使える。</line>
</dialogue>
"""

# デフォルトのモックキーワード（LLMが抽出する想定）
DEFAULT_KEYWORDS = [
    "SRE",
    "Site Reliability Engineering",
    "Google",
    "2003年",
    "運用チーム",
    "ソフトウェアエンジニアリング",
    "SLI",
    "Service Level Indicator",
    "SLO",
    "Service Level Objective",
    "可用性",
    "99.9%",
    "スリーナイン",
    "ダウンタイム",
    "8.7時間",
    "エラーバジェット",
    "0.1%",
    "新機能",
    "リリース",
]


def extract_keywords_mock(section_text: str) -> list[str]:
    """キーワード抽出のモック（実際はLLMを使用）。

    Note:
        実際の実装では src.keyword_extractor.extract_keywords() を使用するが、
        ollamaが必要なため、デモではモックを使用。
    """
    # 実際のLLM呼び出しの代わりにデフォルトキーワードを返す
    return DEFAULT_KEYWORDS


def main() -> None:
    parser = argparse.ArgumentParser(
        description="キーワード抽出とカバー率検証のデモ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--section",
        default=DEFAULT_SECTION,
        help="検証対象のセクションテキスト",
    )
    parser.add_argument(
        "--dialogue",
        default=DEFAULT_DIALOGUE,
        help="検証対象の対話XML",
    )
    parser.add_argument(
        "--keywords",
        help="カンマ区切りのキーワードリスト（省略時はモック抽出）",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="JSON形式で出力",
    )
    args = parser.parse_args()

    # キーワード抽出
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(",")]
    else:
        keywords = extract_keywords_mock(args.section)

    # カバー率検証
    result = validate_coverage(keywords, args.dialogue)

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print("キーワード抽出とカバー率検証デモ")
        print("=" * 60)
        print()
        print(f"【入力セクション】（{len(args.section)}文字）")
        print(args.section[:200] + "..." if len(args.section) > 200 else args.section)
        print()
        print(f"【抽出キーワード】（{len(keywords)}件）")
        print(", ".join(keywords))
        print()
        print("=" * 60)
        print("【検証結果】")
        print("=" * 60)
        print(f"  総キーワード数: {result.total_keywords}")
        print(f"  カバー数:       {result.covered_keywords}")
        print(f"  カバー率:       {result.coverage_rate:.1%}")
        print()
        if result.missing_keywords:
            print(f"【未カバーキーワード】（{len(result.missing_keywords)}件）")
            for kw in result.missing_keywords:
                print(f"  - {kw}")
        else:
            print("【未カバーキーワード】なし（100%カバー）")
        print()
        print("=" * 60)
        print("【JSON出力】")
        print("=" * 60)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
