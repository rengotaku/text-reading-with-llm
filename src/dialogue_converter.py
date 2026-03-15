"""書籍セクションを対話形式に変換するモジュール。

LLMを使用してセクション内容を博士と助手の2人対話形式に変換する。
"""

import argparse
import json
import logging
import os
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal

from src.xml_parser import ContentItem, parse_book2_xml

logger = logging.getLogger(__name__)

# デフォルトモデル
DEFAULT_MODEL = "gpt-oss:20b"


@dataclass
class Utterance:
    """対話内の個々の発言。

    Attributes:
        speaker: 話者ID ("A"=博士, "B"=助手)
        text: 発言テキスト
    """

    speaker: Literal["A", "B"]
    text: str


@dataclass
class DialogueBlock:
    """LLM変換後の対話ブロック。

    Attributes:
        section_number: 元のセクション番号
        section_title: 元のセクションタイトル
        introduction: 導入テキスト（narrator用）
        dialogue: 対話発言リスト
        conclusion: 結論テキスト（narrator用）
    """

    section_number: str
    section_title: str
    introduction: str
    dialogue: list[Utterance]
    conclusion: str


@dataclass
class ConversionResult:
    """変換処理の結果。

    Attributes:
        success: 変換成功フラグ
        dialogue_block: 変換結果（成功時）
        error_message: エラーメッセージ（失敗時）
        processing_time_sec: 処理時間（秒）
        input_char_count: 入力文字数
        was_split: 分割処理されたか
    """

    success: bool
    dialogue_block: DialogueBlock | None
    error_message: str | None
    processing_time_sec: float
    input_char_count: int
    was_split: bool


@dataclass
class Section:
    """ContentItemリストから抽出されたセクション。

    Attributes:
        number: セクション番号
        title: セクションタイトル
        paragraphs: 段落テキストのリスト
        chapter_number: 所属するチャプター番号
    """

    number: str
    title: str
    paragraphs: list[str] = field(default_factory=list)
    chapter_number: int | None = None


def extract_sections(items: list[ContentItem]) -> list[Section]:
    """ContentItemリストからセクション単位に抽出する。

    level=2の見出しをセクション区切りとして使用する。
    level=1のチャプター見出しはスキップする。

    Args:
        items: xml_parserから取得したContentItemリスト

    Returns:
        Sectionオブジェクトのリスト
    """
    if not items:
        return []

    sections: list[Section] = []
    current_section: Section | None = None

    for item in items:
        if item.item_type == "heading" and item.heading_info is not None:
            # level=2がセクション見出し
            if item.heading_info.level == 2:
                if current_section is not None:
                    sections.append(current_section)
                current_section = Section(
                    number=item.heading_info.number,
                    title=item.heading_info.title,
                    paragraphs=[],
                    chapter_number=item.chapter_number,
                )
            # level=1はチャプター見出し（スキップ）
        elif item.item_type in ("paragraph", "list_item"):
            if current_section is not None:
                current_section.paragraphs.append(item.text)

    if current_section is not None:
        sections.append(current_section)

    return sections


def analyze_structure(
    paragraphs: list[str],
    model: str = DEFAULT_MODEL,
    ollama_chat_func: Callable[..., Any] | None = None,
) -> dict[str, list[str]]:
    """LLMを使用して段落をintroduction/dialogue/conclusionに分類する。

    Args:
        paragraphs: 分類対象の段落テキストリスト
        model: Ollamaモデル名
        ollama_chat_func: Ollama chat API呼び出し関数

    Returns:
        {"introduction": [...], "dialogue": [...], "conclusion": [...]} の辞書

    Raises:
        TimeoutError: LLM呼び出しがタイムアウトした場合（再送出）
    """
    paragraphs_text = "\n".join(f"{i + 1}. {p}" for i, p in enumerate(paragraphs))

    prompt = f"""以下のセクションの段落を、introduction（導入）、dialogue（本論）、
conclusion（結論）の3つに分類してください。

段落リスト:
{paragraphs_text}

分類ルール:
- introduction: セクションの導入・背景説明（通常は最初の1〜2段落）
- dialogue: 主要な内容・説明（博士と助手の対話に変換する部分）
- conclusion: まとめ・結論（通常は最後の1〜2段落）

JSON形式で出力してください。各段落のテキストをそのままリストに入れてください:
{{"introduction": ["段落テキスト..."], "dialogue": ["段落テキスト..."],
"conclusion": ["段落テキスト..."]}}

JSON出力:"""

    system_content = (
        "あなたは書籍コンテンツの構造分析の専門家です。段落をintroduction/dialogue/conclusionに分類してください。"
    )
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": prompt},
    ]

    if ollama_chat_func is None:
        return {"introduction": [], "dialogue": list(paragraphs), "conclusion": []}

    logger.debug("[analyze_structure] LLM呼び出し開始 (model=%s)", model)
    response = ollama_chat_func(model=model, messages=messages)

    try:
        response_text = response.get("message", {}).get("content", "")
        logger.debug(
            "[analyze_structure] LLM応答 (len=%d): %s",
            len(response_text),
            response_text[:500] + "..." if len(response_text) > 500 else response_text,
        )

        if not response_text:
            logger.warning("[analyze_structure] LLM応答が空です")
            return {"introduction": [], "dialogue": list(paragraphs), "conclusion": []}

        # JSONを検索して抽出
        json_match = re.search(r"\{[^{}]*\}", response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            logger.debug("[analyze_structure] 抽出されたJSON: %s", json_str[:300])
            parsed = json.loads(json_str)
            result: dict[str, list[str]] = {
                "introduction": parsed.get("introduction", []),
                "dialogue": parsed.get("dialogue", []),
                "conclusion": parsed.get("conclusion", []),
            }
            logger.info(
                "[analyze_structure] パース成功: intro=%d, dialogue=%d, conclusion=%d",
                len(result["introduction"]),
                len(result["dialogue"]),
                len(result["conclusion"]),
            )
            return result
        else:
            logger.warning("[analyze_structure] JSONが見つかりませんでした")
            logger.warning("[analyze_structure] LLM応答: %s", response_text[:1000])
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning("[analyze_structure] JSONパース失敗: %s", e)
        logger.warning("[analyze_structure] 失敗した応答: %s", response_text[:1000])

    return {"introduction": [], "dialogue": list(paragraphs), "conclusion": []}


def generate_dialogue(
    dialogue_paragraphs: list[str],
    model: str = DEFAULT_MODEL,
    ollama_chat_func: Callable[..., Any] | None = None,
    introduction: str = "",
    conclusion: str = "",
) -> list[Utterance]:
    """LLMを使用してA/B発話の対話を生成する。

    Args:
        dialogue_paragraphs: 対話に変換する段落テキストリスト
        model: Ollamaモデル名
        ollama_chat_func: Ollama chat API呼び出し関数
        introduction: 導入テキスト（コンテキスト用）
        conclusion: 結論テキスト（コンテキスト用）

    Returns:
        Utteranceオブジェクトのリスト

    Raises:
        ConnectionError: ネットワークエラー時（再送出）
    """
    content_text = "\n".join(dialogue_paragraphs)

    context_parts = []
    if introduction:
        context_parts.append(f"【導入】\n{introduction}")
    context_parts.append(f"【本論（対話に変換する内容）】\n{content_text}")
    if conclusion:
        context_parts.append(f"【結論】\n{conclusion}")

    full_context = "\n\n".join(context_parts)

    prompt = f"""以下のテキストを、博士（A）と助手（B）の自然な対話形式に変換してください。

{full_context}

変換ルール:
- A（博士）: 説明役。概念や仕組みを詳しく説明する
- B（助手）: 質問役。疑問点を聞いたり、理解を確認したりする
- 自然な会話の流れで、内容をわかりやすく伝える
- A→B→A→B...の順番で交互に発話する

JSON配列形式で出力してください:
[{{"speaker": "A", "text": "発話テキスト"}}, {{"speaker": "B", "text": "発話テキスト"}}, ...]

JSON出力:"""

    system_content = (
        "あなたは書籍コンテンツを対話形式に変換する専門家です。博士と助手の自然な会話として変換してください。"
    )
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": prompt},
    ]

    if ollama_chat_func is None:
        return []

    logger.debug("[generate_dialogue] LLM呼び出し開始 (model=%s)", model)
    response = ollama_chat_func(model=model, messages=messages)

    try:
        response_text = response.get("message", {}).get("content", "")
        logger.debug(
            "[generate_dialogue] LLM応答 (len=%d): %s",
            len(response_text),
            response_text[:500] + "..." if len(response_text) > 500 else response_text,
        )

        if not response_text:
            logger.warning("[generate_dialogue] LLM応答が空です")
            return []

        # JSON配列を検索して抽出
        json_match = re.search(r"\[.*\]", response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            logger.debug("[generate_dialogue] 抽出されたJSON: %s", json_str[:500])
            parsed = json.loads(json_str)
            utterances: list[Utterance] = []
            for item in parsed:
                speaker = item.get("speaker", "")
                text = item.get("text", "")
                if speaker in ("A", "B") and text:
                    utterances.append(Utterance(speaker=speaker, text=text))
            logger.info("[generate_dialogue] パース成功: %d 発話生成", len(utterances))
            return utterances
        else:
            logger.warning("[generate_dialogue] JSON配列が見つかりませんでした")
            logger.warning("[generate_dialogue] LLM応答: %s", response_text[:1000])
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning("[generate_dialogue] JSONパース失敗: %s", e)
        logger.warning("[generate_dialogue] 失敗した応答: %s", response_text[:1000])

    return []


def to_dialogue_xml(block: DialogueBlock) -> str:
    """DialogueBlockをXML文字列にシリアライズする。

    data-model.mdで定義された対話XMLスキーマに従う。

    Args:
        block: シリアライズするDialogueBlockオブジェクト

    Returns:
        XML文字列
    """
    # dialogue-section ルート要素
    root = ET.Element("dialogue-section")
    root.set("number", block.section_number)
    root.set("title", block.section_title)

    # introduction要素
    intro_elem = ET.SubElement(root, "introduction")
    intro_elem.set("speaker", "narrator")
    intro_elem.text = block.introduction or ""

    # dialogue要素
    dialogue_elem = ET.SubElement(root, "dialogue")
    for utterance in block.dialogue:
        utt_elem = ET.SubElement(dialogue_elem, "utterance")
        utt_elem.set("speaker", utterance.speaker)
        utt_elem.text = utterance.text

    # conclusion要素
    conclusion_elem = ET.SubElement(root, "conclusion")
    conclusion_elem.set("speaker", "narrator")
    conclusion_elem.text = block.conclusion or ""

    # XML文字列に変換（UTF-8エンコード）
    return ET.tostring(root, encoding="unicode")


SPLIT_THRESHOLD = 4000


def should_split(section: Section) -> bool:
    """セクションの全段落文字数の合計が分割閾値を超えるか判定する。

    Args:
        section: 判定対象のSectionオブジェクト

    Returns:
        全段落の合計文字数が4,000文字を超える場合はTrue、それ以外はFalse
    """
    if section is None:
        return False
    total_chars = sum(len(p) for p in section.paragraphs)
    return total_chars > SPLIT_THRESHOLD


def split_by_heading(section: Section) -> list[Section]:
    """セクションを段落内の見出し（## で始まる行）単位で分割する。

    各段落を走査し、"## " で始まる段落を分割点として新しいサブセクションを作成する。
    元のセクション番号にサフィックス（-1, -2, ...）を付与して順序を保持する。

    Args:
        section: 分割対象のSectionオブジェクト

    Returns:
        分割後のSectionオブジェクトのリスト
    """
    if section is None:
        return []

    if not section.paragraphs:
        return [section]

    # 見出し行の位置を特定する
    heading_indices = [i for i, p in enumerate(section.paragraphs) if p.startswith("## ")]

    if not heading_indices:
        # 見出しがない場合はそのまま返す
        return [section]

    # 分割点リスト: [0, h1, h2, ...] の開始インデックスをグループ化する
    split_starts = [0] + heading_indices
    parts: list[tuple[int, int]] = []
    for i, start in enumerate(split_starts):
        end = split_starts[i + 1] if i + 1 < len(split_starts) else len(section.paragraphs)
        parts.append((start, end))

    # 各パートがSplitThreshold以下になるようにセクションを構築する
    result: list[Section] = []
    part_index = 1

    for start, end in parts:
        paragraphs = section.paragraphs[start:end]
        # 先頭が見出し行の場合はタイトルとして使用し、段落には含めない
        if paragraphs and paragraphs[0].startswith("## "):
            sub_title = paragraphs[0][3:].strip()  # "## " を除去
            sub_paragraphs = paragraphs[1:]
        else:
            sub_title = section.title
            sub_paragraphs = paragraphs

        # 空のサブセクション（段落なし）はスキップ
        if not sub_paragraphs:
            continue

        sub_section = Section(
            number=f"{section.number}-{part_index}",
            title=sub_title if sub_title else section.title,
            paragraphs=sub_paragraphs,
            chapter_number=section.chapter_number,
        )
        result.append(sub_section)
        part_index += 1

    # 分割結果が空の場合は元のセクションを返す
    if not result:
        return [section]

    return result


def convert_section(
    section: Section,
    model: str = DEFAULT_MODEL,
    ollama_chat_func: Callable[..., Any] | None = None,
) -> ConversionResult:
    """セクションを対話形式に変換する統合関数。

    Args:
        section: 変換対象のSectionオブジェクト
        model: Ollamaモデル名
        ollama_chat_func: Ollama chat API呼び出し関数

    Returns:
        ConversionResultオブジェクト
    """
    start_time = time.time()
    input_char_count = sum(len(p) for p in section.paragraphs)

    # 分割が必要かどうかを判定
    was_split = should_split(section)

    # 変換対象セクションの決定（分割する場合は最初のサブセクションを使用）
    if was_split:
        sub_sections = split_by_heading(section)
        target_section = sub_sections[0] if sub_sections else section
    else:
        target_section = section

    try:
        # 構造分析
        structure = analyze_structure(
            target_section.paragraphs,
            model=model,
            ollama_chat_func=ollama_chat_func,
        )

        introduction_text = "\n".join(structure.get("introduction", []))
        conclusion_text = "\n".join(structure.get("conclusion", []))
        dialogue_paragraphs = structure.get("dialogue", [])

        # 対話生成
        utterances = generate_dialogue(
            dialogue_paragraphs=dialogue_paragraphs,
            model=model,
            ollama_chat_func=ollama_chat_func,
            introduction=introduction_text,
            conclusion=conclusion_text,
        )

        dialogue_block = DialogueBlock(
            section_number=section.number,
            section_title=section.title,
            introduction=introduction_text,
            dialogue=utterances,
            conclusion=conclusion_text,
        )

        processing_time = time.time() - start_time

        return ConversionResult(
            success=True,
            dialogue_block=dialogue_block,
            error_message=None,
            processing_time_sec=processing_time,
            input_char_count=input_char_count,
            was_split=was_split,
        )

    except Exception as e:
        processing_time = time.time() - start_time
        logger.error("セクション変換に失敗しました: %s", e)

        return ConversionResult(
            success=False,
            dialogue_block=None,
            error_message=str(e),
            processing_time_sec=processing_time,
            input_char_count=input_char_count,
            was_split=was_split,
        )


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """CLI引数を解析する。

    Args:
        args: コマンドライン引数リスト（Noneの場合はsys.argvを使用）

    Returns:
        解析済みのNamespaceオブジェクト
    """
    parser = argparse.ArgumentParser(
        description="書籍XMLを対話形式に変換するツール",
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="入力XMLファイルパス",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="./output",
        help="出力ディレクトリ（デフォルト: ./output）",
    )
    parser.add_argument(
        "-m",
        "--model",
        default=DEFAULT_MODEL,
        help=f"Ollamaモデル名（デフォルト: {DEFAULT_MODEL}）",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=3500,
        dest="max_chars",
        help="分割なしの最大文字数（デフォルト: 3500）",
    )
    parser.add_argument(
        "--split-threshold",
        type=int,
        default=4000,
        dest="split_threshold",
        help="分割閾値（デフォルト: 4000）",
    )
    parser.add_argument(
        "--num-predict",
        type=int,
        default=1500,
        dest="num_predict",
        help="LLMトークン上限（デフォルト: 1500）",
    )
    parser.add_argument(
        "-c",
        "--chapter",
        type=int,
        default=None,
        help="対象チャプター番号（省略時は全チャプター）",
    )
    parser.add_argument(
        "-s",
        "--section",
        type=int,
        default=None,
        help="対象セクション番号（省略時は全セクション）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        dest="dry_run",
        help="プレビューモード（変換を実行しない）",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="詳細ログを出力（DEBUGレベル）",
    )
    return parser.parse_args(args)


def main() -> int:
    """CLIエントリーポイント。

    Returns:
        終了コード:
          0: 成功
          1: 入力ファイルエラー
          2: LLM接続エラー
          3: 変換エラー
    """
    args = parse_args()

    # ログレベル設定
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s",
    )

    # 入力ファイルのバリデーション
    input_path = args.input
    if not input_path:
        logger.error("入力ファイルパスが空です")
        return 1

    if not os.path.exists(input_path):
        logger.error("入力ファイルが見つかりません: %s", input_path)
        return 1

    if os.path.isdir(input_path):
        logger.error("入力パスにディレクトリが指定されました: %s", input_path)
        return 1

    # XMLパース
    try:
        content_items = parse_book2_xml(input_path)
    except ET.ParseError as e:
        logger.error("XMLパースエラー: %s", e)
        return 1

    # セクション抽出
    sections = extract_sections(content_items)

    # チャプター・セクションフィルタリング
    if args.chapter is not None:
        sections = [s for s in sections if s.chapter_number == args.chapter]

    if args.section is not None:
        filtered = []
        for s in sections:
            try:
                section_num = int(s.number.split(".")[1]) if "." in s.number else int(s.number)
                if section_num == args.section:
                    filtered.append(s)
            except (ValueError, IndexError):
                pass
        sections = filtered

    # dry-runモード: 変換せずに対象セクションを表示
    if args.dry_run:
        logger.info("[dry-run] 対象セクション数: %d", len(sections))
        for section in sections:
            logger.info("[dry-run] セクション %s: %s", section.number, section.title)
        return 0

    # セクションがない場合は正常終了
    if not sections:
        logger.info("変換対象セクションが見つかりませんでした")
        return 0

    # 出力ディレクトリを作成
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 各セクションを変換
    dialogue_blocks: list[DialogueBlock] = []
    conversion_log: list[dict[str, Any]] = []

    # Ollama をインポート
    try:
        import ollama

        ollama_chat_func = ollama.chat
    except ImportError:
        logger.error("ollama パッケージがインストールされていません")
        return 2

    try:
        for section in sections:
            logger.info("変換中: セクション %s - %s", section.number, section.title)
            result = convert_section(
                section=section,
                model=args.model,
                ollama_chat_func=ollama_chat_func,
            )
            log_entry: dict[str, Any] = {
                "section_number": section.number,
                "section_title": section.title,
                "success": result.success,
                "processing_time_sec": result.processing_time_sec,
                "input_char_count": result.input_char_count,
                "was_split": result.was_split,
                "error_message": result.error_message,
            }
            conversion_log.append(log_entry)

            if not result.success:
                logger.error(
                    "セクション %s の変換に失敗しました: %s",
                    section.number,
                    result.error_message,
                )
                _write_conversion_log(output_dir, conversion_log)
                return 3

            if result.dialogue_block is not None:
                dialogue_blocks.append(result.dialogue_block)

    except ConnectionError as e:
        logger.error("LLM接続エラー: %s", e)
        return 2
    except Exception as e:
        logger.error("予期しないエラー: %s", e)
        return 3

    # dialogue_book.xml を書き出す
    dialogue_book_path = output_dir / "dialogue_book.xml"
    root_elem = ET.Element("dialogue-book")
    for block in dialogue_blocks:
        block_xml_str = to_dialogue_xml(block)
        block_elem = ET.fromstring(block_xml_str)
        root_elem.append(block_elem)
    tree = ET.ElementTree(root_elem)
    ET.indent(tree, space="  ")
    tree.write(str(dialogue_book_path), encoding="unicode", xml_declaration=False)

    # conversion_log.json を書き出す
    _write_conversion_log(output_dir, conversion_log)

    logger.info("変換完了: %d セクション → %s", len(dialogue_blocks), output_dir)
    return 0


def _write_conversion_log(output_dir: Path, log: list[dict[str, Any]]) -> None:
    """変換ログをJSONファイルに書き出す。

    Args:
        output_dir: 出力ディレクトリ
        log: 変換ログのリスト
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "conversion_log.json"
    with open(str(log_path), "w", encoding="utf-8") as f:
        json.dump({"conversions": log}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import sys

    sys.exit(main())
