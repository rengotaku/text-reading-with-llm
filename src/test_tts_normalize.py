#!/usr/bin/env python3
"""Test LLM-based TTS normalization.

Usage:
    python src/test_tts_normalize.py sample/book.md --pages 4 5
"""

import argparse
import logging
import re
import sys
from pathlib import Path

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

OLLAMA_API_URL = "http://localhost:11434/api/chat"

def split_into_raw_pages(markdown: str) -> list[tuple[int, str]]:
    """Split markdown into pages WITHOUT kana conversion.

    Returns list of (page_number, raw_text) tuples.
    """
    pattern = r"^--- Page (\d+) \(page_\d+\.png\) ---$"
    parts = re.split(pattern, markdown, flags=re.MULTILINE)

    pages = []
    for i in range(1, len(parts), 2):
        page_num = int(parts[i])
        raw_text = parts[i + 1] if i + 1 < len(parts) else ""

        # Only remove markdown formatting, keep kanji
        text = clean_markdown_only(raw_text)
        if text.strip():
            pages.append((page_num, text))
    return pages


def clean_markdown_only(text: str) -> str:
    """Clean markdown formatting only, preserve original kanji."""
    # Remove HTML comments
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    # Remove figure descriptions
    text = re.sub(r"^図は、.*$", "", text, flags=re.MULTILINE)
    # Remove page number markers
    text = re.sub(r"^.*?\d+\s*/\s*\d+\s*$", "", text, flags=re.MULTILINE)
    # Remove heading markers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)
    # Remove horizontal rules
    text = re.sub(r"^---+\s*$", "", text, flags=re.MULTILINE)
    # Remove list markers
    text = re.sub(r"^[\-\*]\s+", "", text, flags=re.MULTILINE)
    # Remove backticks
    text = re.sub(r"`([^`]*)`", r"\1", text)
    # Remove code blocks
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    # Collapse blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


SYSTEM_PROMPT = """あなたはTTS（テキスト読み上げ）用のテキスト正規化の専門家です。
入力されたテキストを、TTSで自然に聞こえるように読点（、）を適切に挿入してください。

ルール:
1. 一文が長すぎる場合は、適切な位置で読点を追加
2. 元の文意は絶対に変えない

出力は修正後のテキストのみを返してください。説明は不要です。"""


def normalize_for_tts(text: str, model: str = "gpt-oss:20b") -> str:
    """Normalize text for TTS using LLM."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"以下のテキストをTTS用に正規化してください:\n\n{text}"},
        ],
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 4096,
        },
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=180)
        response.raise_for_status()
        result = response.json()
        return result.get("message", {}).get("content", "").strip()
    except requests.RequestException as e:
        logger.error("LLM request failed: %s", e)
        return text


def main():
    parser = argparse.ArgumentParser(description="Test TTS normalization")
    parser.add_argument("input", help="Input markdown file")
    parser.add_argument("--pages", type=int, nargs="+", default=[4], help="Page numbers to test")
    parser.add_argument("--model", default="gpt-oss:20b", help="Ollama model name")
    parser.add_argument("--output-dir", default="test_output/tts_normalize", help="Output directory")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        logger.error("Input file not found: %s", input_path)
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read and parse (raw text, no kana conversion)
    logger.info("Reading: %s", input_path)
    markdown = input_path.read_text(encoding="utf-8")
    pages = split_into_raw_pages(markdown)

    # Filter pages
    target_pages = [(num, text) for num, text in pages if num in args.pages]
    if not target_pages:
        logger.error("Pages not found: %s", args.pages)
        sys.exit(1)

    logger.info("Processing %d pages with model: %s", len(target_pages), args.model)

    results = []
    for page_num, page_text in target_pages:
        logger.info("--- Page %d ---", page_num)

        # Normalize
        logger.info("Calling LLM...")
        normalized = normalize_for_tts(page_text, args.model)

        results.append({
            "page": page_num,
            "before": page_text,
            "after": normalized,
        })

        # Save individual files
        before_path = output_dir / f"page_{page_num:04d}_before.txt"
        after_path = output_dir / f"page_{page_num:04d}_after.txt"

        before_path.write_text(page_text, encoding="utf-8")
        after_path.write_text(normalized, encoding="utf-8")

        logger.info("Saved: %s", before_path)
        logger.info("Saved: %s", after_path)

    # Save comparison file
    comparison_path = output_dir / "comparison.md"
    with open(comparison_path, "w", encoding="utf-8") as f:
        f.write("# TTS Normalization Test Results\n\n")
        f.write(f"Model: `{args.model}`\n\n")

        for r in results:
            f.write(f"## Page {r['page']}\n\n")
            f.write("### Before\n\n")
            f.write("```\n")
            f.write(r["before"])
            f.write("\n```\n\n")
            f.write("### After\n\n")
            f.write("```\n")
            f.write(r["after"])
            f.write("\n```\n\n")
            f.write("---\n\n")

    logger.info("Saved comparison: %s", comparison_path)

    # Print quick diff summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for r in results:
        before_commas = r["before"].count("、")
        after_commas = r["after"].count("、")
        print(f"Page {r['page']}: 読点 {before_commas} → {after_commas} (+{after_commas - before_commas})")


if __name__ == "__main__":
    main()
