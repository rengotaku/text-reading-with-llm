#!/usr/bin/env python3
"""Generate reading dictionary from book using LLM.

Usage:
    python src/generate_reading_dict.py sample/book.md --model gpt-oss:20b
"""

import argparse
import json
import logging
import sys
import xml.etree.ElementTree as ET
from itertools import groupby
from pathlib import Path

import requests

from src.dict_manager import get_dict_path, load_dict, save_dict
from src.llm_reading_generator import extract_technical_terms
from src.text_cleaner import split_into_pages
from src.xml2_parser import parse_book2_xml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

OLLAMA_API_URL = "http://localhost:11434/api/chat"


def ollama_chat(model: str, messages: list[dict], max_retries: int = 3, timeout: int = 120) -> dict:
    """Call Ollama chat API."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.3,  # Low temperature for consistent output
            "num_predict": 2048,
        },
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.warning("Attempt %d failed: %s", attempt + 1, e)
            if attempt == max_retries - 1:
                raise

    return {}


def _warmup_model(model: str, timeout: int = 300) -> None:
    """Warm up the Ollama model by sending a minimal request.

    Args:
        model: Ollama model name
        timeout: Timeout in seconds for model loading (default: 300)
    """
    logger.info("Warming up model: %s", model)
    # Send minimal request to trigger model loading
    messages = [{"role": "user", "content": "ping"}]
    ollama_chat(model, messages, timeout=timeout)
    logger.info("Model ready")


def generate_readings_batch(
    terms: list[str],
    model: str,
    batch_size: int = 30,
) -> dict[str, str]:
    """Generate readings for terms in batches."""
    all_readings = {}

    # Warm up model before processing first batch
    _warmup_model(model)

    for i in range(0, len(terms), batch_size):
        batch = terms[i : i + batch_size]
        logger.info(
            "Processing batch %d/%d (%d terms)",
            i // batch_size + 1,
            (len(terms) + batch_size - 1) // batch_size,
            len(batch),
        )

        terms_list = "\n".join(f"- {term}" for term in batch)
        prompt = f"""以下の技術用語・略語の日本語での読み方をカタカナで答えてください。
TTSで自然に聞こえる読みにしてください。

用語リスト:
{terms_list}

JSON形式で出力してください。例:
{{"SRE": "エスアールイー", "API": "エーピーアイ"}}

注意:
- 必ずカタカナで出力
- 略語は一文字ずつ読む（SRE→エスアールイー、AWS→エーダブリューエス）
- 固有名詞は一般的な読み方で（Google→グーグル）
- 英単語はカタカナ読みで（Service→サービス、Error→エラー）

JSON出力:"""

        messages = [
            {
                "role": "system",
                "content": (
                    "あなたは技術用語の読み方を教える専門家です。正確なカタカナ読みをJSON形式で出力してください。"
                ),
            },
            {"role": "user", "content": prompt},
        ]

        try:
            response = ollama_chat(model, messages)
            response_text = response.get("message", {}).get("content", "")

            # Extract JSON from response
            import re

            # Try to find JSON object in response
            json_match = re.search(r"\{[\s\S]*\}", response_text)
            if json_match:
                try:
                    readings = json.loads(json_match.group())
                    valid_readings = {k: v for k, v in readings.items() if isinstance(v, str) and v}
                    all_readings.update(valid_readings)
                    logger.info("  Got %d readings", len(valid_readings))
                except json.JSONDecodeError as e:
                    logger.warning("  Failed to parse JSON: %s", e)
            else:
                logger.warning("  No JSON found in response")

        except Exception as e:
            logger.error("  Batch failed: %s", e)

    return all_readings


def main():
    parser = argparse.ArgumentParser(description="Generate reading dictionary using LLM")
    parser.add_argument("input", help="Input markdown file")
    parser.add_argument("--model", default="gpt-oss:20b", help="Ollama model name")
    parser.add_argument("--output", type=Path, default=None, help="Output dictionary path (default: auto-hash)")
    parser.add_argument("--batch-size", type=int, default=30, help="Terms per LLM request")
    parser.add_argument("--merge", action="store_true", help="Merge with existing dictionary")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        logger.error("Input file not found: %s", input_path)
        sys.exit(1)

    # Determine output path (hash-based by default)
    if args.output:
        output_path = args.output
    else:
        try:
            output_path = get_dict_path(input_path)
        except ET.ParseError as e:
            logger.error("Failed to parse XML file: %s", e)
            sys.exit(1)
    logger.info("Dictionary path: %s", output_path)

    # Load existing dictionary if merging or if auto-hash file exists
    existing = {}
    if args.merge or (args.output is None and output_path.exists()):
        existing = load_dict(input_path) if args.output is None else {}
        if args.output and args.output.exists():
            with open(args.output, encoding="utf-8") as f:
                existing = json.load(f)
    logger.info("Existing dictionary: %d entries", len(existing))

    # Read and parse book based on file extension
    logger.info("Reading: %s", input_path)
    all_terms = set()

    if input_path.suffix == ".xml":
        # XML flow: parse → group by chapter → extract terms
        try:
            items = parse_book2_xml(input_path)
        except ET.ParseError as e:
            logger.error("Failed to parse XML file: %s", e)
            sys.exit(1)

        logger.info("Parsed %d content items from XML", len(items))

        # Group by chapter_number and extract terms from each group
        # Sort first to ensure groupby works correctly
        sorted_items = sorted(items, key=lambda x: x.chapter_number if x.chapter_number is not None else -1)
        for chapter_num, group in groupby(sorted_items, key=lambda x: x.chapter_number):
            # Combine all text from items in this chapter
            chapter_items = list(group)
            combined_text = " ".join(item.text for item in chapter_items)

            # Extract terms from combined text
            terms = extract_technical_terms(combined_text)
            all_terms.update(terms)

        logger.info("Extracted terms from %d chapter groups", len(set(item.chapter_number for item in items)))

    elif input_path.suffix == ".md":
        # MD flow: existing logic (unchanged)
        markdown = input_path.read_text(encoding="utf-8")
        pages = split_into_pages(markdown)
        logger.info("Found %d pages", len(pages))

        # Extract all technical terms
        for page in pages:
            terms = extract_technical_terms(page.text)
            all_terms.update(terms)

    else:
        # Unsupported file extension
        logger.error("Unsupported file extension: %s (only .xml and .md are supported)", input_path.suffix)
        sys.exit(1)

    logger.info("Found %d unique technical terms", len(all_terms))

    # Filter out terms already in dictionary
    new_terms = [t for t in sorted(all_terms) if t not in existing]
    logger.info("New terms to process: %d", len(new_terms))

    if not new_terms:
        logger.info("No new terms to process")
        if existing:
            # Save existing to new path if needed
            save_dict(existing, input_path)
        return

    # Generate readings
    logger.info("Generating readings with %s...", args.model)
    new_readings = generate_readings_batch(new_terms, args.model, args.batch_size)
    logger.info("Generated %d readings", len(new_readings))

    # Merge and save
    final_dict = {**existing, **new_readings}
    save_dict(final_dict, input_path)
    logger.info("Total dictionary entries: %d", len(final_dict))


if __name__ == "__main__":
    main()
