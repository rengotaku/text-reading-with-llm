#!/usr/bin/env python3
"""LLM対話生成プロンプトの検証スクリプト"""

import argparse
import re
import sys

import ollama

DEFAULT_TEST_DATA = {
    "introduction": (
        "株式会社ロボチェック社は、このたび新しい製品企画「アームチェッカー」の"
        "プロジェクトを立ち上げました。ハルさんが新任プロジェクトリーダーとして、"
        "最初に取り掛かるのが企画提案です。"
    ),
    "dialogue": (
        "必要なのは検査の自動化なんだけど、実際に重要顧客のラインを見たら、"
        "作業者が検査時にアームを調整して不良品も良品にしているのよ。"
        "ええ!自動調整も必要なんですね。それは技術課題だなあ。"
        "重要なのが納期!実はその重要顧客が今度ラインを拡張するらしくてね。"
    ),
    "conclusion": (
        "このように、過度なスペックの開発を請け負わされそうになったとき、"
        "リーダーとしてはしっかり実現性を精査することが重要です。"
    ),
}

CHAR_SETTING = """【キャラクター設定】
- A（教授）: 解説役。専門知識を持ち、丁寧に説明する
- B（助手）: 聞き手。質問し、理解を確認する。丁寧な口調"""

STRUCTURE_GUIDE = """【対話の構成】※必ず守ること
1. 導入（1-2往復）: 今回のトピックを紹介する
2. 本論（主要部分）: 内容を詳しく議論する
3. 結論（1-2往復）: 要点を確認して締める"""

FORMAT_INSTRUCTION = """以下の形式で出力（各行は「A:」または「B:」で始める）:
A: 発話テキスト
B: 発話テキスト"""


def test_single_request(
    data: dict[str, str],
    model: str = "gpt-oss:20b",
    with_structure: bool = True,
) -> str:
    """単一リクエスト方式でテスト"""
    all_text = "\n".join(data.values())

    structure_section = f"\n\n{STRUCTURE_GUIDE}" if with_structure else ""

    prompt = f"""以下のテキストを教授（A）と助手（B）の対話に変換してください。

【テキスト】
{all_text}

{CHAR_SETTING}{structure_section}

{FORMAT_INSTRUCTION}
"""
    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "あなたは技術書をポッドキャスト風の自然な対話に変換する専門家です。",
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response["message"]["content"]


def test_split_request(
    data: dict[str, str],
    model: str = "gpt-oss:20b",
) -> dict[str, str]:
    """3分割リクエスト方式でテスト"""
    part_labels = {
        "introduction": "導入",
        "dialogue": "本論",
        "conclusion": "結論",
    }
    part_instructions = {
        "introduction": "トピックを紹介し、聞き手の興味を引く対話にしてください。",
        "dialogue": "内容を詳しく議論する対話にしてください。",
        "conclusion": "要点を確認し、学びをまとめる対話にしてください。",
    }

    results: dict[str, str] = {}
    for part, text in data.items():
        label = part_labels[part]
        instruction = part_instructions[part]

        prompt = f"""以下のテキストを教授（A）と助手（B）の対話に変換してください。
これは「{label}」パートです。{instruction}

【テキスト】
{text}

{CHAR_SETTING}

{FORMAT_INSTRUCTION}
"""
        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "あなたは技術書をポッドキャスト風の自然な対話に変換する専門家です。",
                },
                {"role": "user", "content": prompt},
            ],
        )
        results[part] = response["message"]["content"]

    return results


def analyze_output(original: str, output: str) -> dict:
    """出力を分析"""
    pattern = re.compile(r"^([AB]):\s*(.+)$", re.MULTILINE)
    matches = pattern.findall(output)

    # 構成チェック（最初と最後の発話者）
    speakers = [m[0] for m in matches]
    has_intro = len(matches) >= 2  # 最低2往復
    has_conclusion = len(matches) >= 2 and "つまり" in output or "ポイント" in output

    return {
        "original_chars": len(original),
        "output_chars": len(output),
        "ratio": round(len(output) / len(original), 1) if original else 0,
        "utterance_count": len(matches),
        "a_count": speakers.count("A"),
        "b_count": speakers.count("B"),
        "has_intro": has_intro,
        "has_conclusion": has_conclusion,
    }


def detect_duplicates(outputs: dict[str, str]) -> list[str]:
    """セクション間の重複キーワードを検出"""
    keywords = [
        "アームチェッカー",
        "ロボチェック",
        "検査",
        "自動化",
        "2026年",
        "実現性",
        "リーダー",
        "ハル",
        "納期",
    ]
    duplicates = []

    for kw in keywords:
        counts = {part: text.count(kw) for part, text in outputs.items()}
        total = sum(counts.values())
        if total > 2:
            parts = [f"{p}:{c}" for p, c in counts.items() if c > 0]
            duplicates.append(f"{kw}: {total}回 ({', '.join(parts)})")

    return duplicates


def print_stats(stats: dict) -> None:
    """統計情報を出力"""
    print(f"文字数: {stats['output_chars']} (原文の{stats['ratio']}倍)")
    print(f"発話数: {stats['utterance_count']} (A:{stats['a_count']}, B:{stats['b_count']})")
    print(f"構成: 導入{'○' if stats['has_intro'] else '×'} / 結論{'○' if stats['has_conclusion'] else '×'}")


def main() -> int:
    parser = argparse.ArgumentParser(description="LLM対話生成プロンプトの検証")
    parser.add_argument("--split", action="store_true", help="3分割方式")
    parser.add_argument("--single", action="store_true", help="単一方式")
    parser.add_argument("--compare", action="store_true", help="両方式を比較")
    parser.add_argument("--no-structure", action="store_true", help="構成指示なし")
    parser.add_argument("--model", default="gpt-oss:20b", help="モデル名")
    args = parser.parse_args()

    data = DEFAULT_TEST_DATA
    original = "\n".join(data.values())

    # デフォルトは比較モード
    if not args.split and not args.single:
        args.compare = True

    if args.compare:
        print("=" * 50)
        print("単一リクエスト（構成指示あり）")
        print("=" * 50)
        single_output = test_single_request(data, args.model, with_structure=True)
        print(single_output)
        print()
        stats = analyze_output(original, single_output)
        print_stats(stats)
        print()

        print("=" * 50)
        print("3分割リクエスト")
        print("=" * 50)
        split_output = test_split_request(data, args.model)
        combined = "\n".join(split_output.values())
        for part, text in split_output.items():
            print(f"--- {part} ---")
            print(text)
            print()
        stats = analyze_output(original, combined)
        print_stats(stats)
        print()

        print("重複キーワード:")
        duplicates = detect_duplicates(split_output)
        for dup in duplicates:
            print(f"  {dup}")

    elif args.single:
        output = test_single_request(data, args.model, with_structure=not args.no_structure)
        print(output)
        print()
        stats = analyze_output(original, output)
        print_stats(stats)

    elif args.split:
        output = test_split_request(data, args.model)
        combined = "\n".join(output.values())
        for part, text in output.items():
            print(f"--- {part} ---")
            print(text)
            print()
        stats = analyze_output(original, combined)
        print_stats(stats)
        print()
        print("重複キーワード:")
        duplicates = detect_duplicates(output)
        for dup in duplicates:
            print(f"  {dup}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
