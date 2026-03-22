"""Interactive setup guide for text-reading-with-llm TTS pipeline.

Asks questions to determine the user's workflow and outputs
the recommended make commands to execute.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


def _ask(question: str, default: str = "") -> str:
    """Ask a question and return the answer."""
    if default:
        prompt = f"{question} [{default}]: "
    else:
        prompt = f"{question}: "
    answer = input(prompt).strip()
    return answer if answer else default


def _ask_yn(question: str, default: bool = False) -> bool:
    """Ask a yes/no question."""
    suffix = "[Y/n]" if default else "[y/N]"
    answer = input(f"{question} {suffix}: ").strip().lower()
    if not answer:
        return default
    return answer in ("y", "yes")


def _find_xml_candidates() -> list[str]:
    """Find XML files in common locations."""
    candidates = []
    for search_dir in [Path("input"), Path("data"), Path(".")]:
        if search_dir.exists():
            for f in sorted(search_dir.iterdir()):
                if f.suffix.lower() == ".xml" and f.is_file():
                    candidates.append(str(f))
    return candidates[:10]


@dataclass(frozen=True)
class GuideAnswers:
    """User answers from the interactive guide."""

    xml_path: str
    output_dir: str
    use_dialogue: bool
    style_id: str
    speed: str


def _ask_questions() -> GuideAnswers:
    """Ask all guide questions and return answers."""
    print()
    print("=" * 60)
    print("  text-reading-with-llm セットアップガイド")
    print("=" * 60)
    print()

    # Q1: XML file
    candidates = _find_xml_candidates()
    if candidates:
        print("検出された XML ファイル:")
        for i, c in enumerate(candidates, 1):
            print(f"  {i}. {c}")
        print()

    xml_path = _ask("Q1. 入力 XML ファイルのパスは？")
    if not xml_path:
        print("XML ファイルが指定されていません。終了します。", file=sys.stderr)
        sys.exit(1)

    if xml_path.isdigit() and candidates:
        idx = int(xml_path) - 1
        if 0 <= idx < len(candidates):
            xml_path = candidates[idx]

    if not Path(xml_path).exists():
        print(f"警告: {xml_path} が見つかりません。パスを確認してください。", file=sys.stderr)

    # Q2: Output directory
    output_dir = _ask("Q2. 出力ディレクトリは？", default="output")

    # Q3: Pipeline mode
    print()
    print("パイプラインモード:")
    print("  1. シンプルモード (xml-tts): 単一話者で読み上げ")
    print("  2. 対話モード (dialogue): LLM で対話形式に変換し複数話者で読み上げ")
    print()
    use_dialogue = _ask_yn("Q3. 対話モードを使いますか？")

    # Q4: Voice settings
    print()
    print("VOICEVOX スタイル ID 例:")
    print("  2: 四国めたん（ノーマル）")
    print("  3: ずんだもん（ノーマル）")
    print("  13: 青山龍星（ノーマル）")
    print("  詳細: https://voicevox.hiroshiba.jp/")
    print()
    style_id = _ask("Q4. スタイル ID は？", default="13")

    # Q5: Speed
    speed = _ask("Q5. 読み上げ速度は？ (0.5-2.0)", default="1.0")

    return GuideAnswers(
        xml_path=xml_path,
        output_dir=output_dir,
        use_dialogue=use_dialogue,
        style_id=style_id,
        speed=speed,
    )


def _print_commands(answers: GuideAnswers) -> None:
    """Print recommended make commands."""
    print()
    print("=" * 60)
    print("  推奨コマンド")
    print("=" * 60)
    print()

    base_vars = f'INPUT="{answers.xml_path}" OUTPUT="{answers.output_dir}"'
    voice_vars = f"STYLE_ID={answers.style_id} SPEED={answers.speed}"

    if answers.use_dialogue:
        print("# 対話パイプライン（フル実行）")
        print(f"make dialogue {base_vars}")
        print()
        print("# または、ステップごとに実行:")
        print()
        print("# 1. LLM で対話形式に変換")
        print(f"make dialogue-convert {base_vars}")
        print()
        print("# 2. 長文を分割")
        print(f"make dialogue-split {base_vars}")
        print()
        print("# 3. 読み辞書を生成")
        print(f"make gen-dict {base_vars}")
        print()
        print("# 4. クリーンテキスト生成")
        print(f"make clean-text {base_vars}")
        print()
        print("# 5. マルチ話者 TTS 実行")
        print(f"make dialogue-tts {base_vars}")
    else:
        print("# シンプルパイプライン（フル実行）")
        print(f"make run {base_vars} {voice_vars}")
        print()
        print("# または、ステップごとに実行:")
        print()
        print("# 1. 読み辞書を生成")
        print(f"make gen-dict {base_vars}")
        print()
        print("# 2. クリーンテキスト生成")
        print(f"make clean-text {base_vars}")
        print()
        print("# 3. TTS 実行")
        print(f"make xml-tts {base_vars} {voice_vars}")

    print()
    print("-" * 60)
    print("Tips:")
    print("  - make help で全コマンド一覧を表示")
    print("  - 環境構築がまだなら make setup を先に実行")
    print("-" * 60)
    print()


def main() -> None:
    """Run the interactive setup guide."""
    try:
        answers = _ask_questions()
        _print_commands(answers)
    except KeyboardInterrupt:
        print("\n\nキャンセルしました。")
        sys.exit(130)


if __name__ == "__main__":
    main()
