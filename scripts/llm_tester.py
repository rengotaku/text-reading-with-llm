#!/usr/bin/env python3
"""汎用LLMプロンプトテスター

使用例:
    # 設定ファイルからテスト
    python scripts/llm_tester.py --config scripts/prompts/dialogue.yaml

    # インラインでテスト
    python scripts/llm_tester.py --system "翻訳者" --prompt "Hello" --model gpt-oss:20b

    # 複数プロンプトの比較
    python scripts/llm_tester.py --compare scripts/prompts/v1.yaml scripts/prompts/v2.yaml
"""

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

try:
    import ollama
except ImportError:
    print("Error: ollama package not installed. Run: pip install ollama")
    sys.exit(1)


@dataclass
class LLMRequest:
    """LLMリクエストの構成"""

    model: str
    system: str
    prompt: str
    name: str = "default"

    def to_messages(self) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": self.system},
            {"role": "user", "content": self.prompt},
        ]


@dataclass
class LLMResponse:
    """LLM応答と統計"""

    content: str
    prompt_tokens: int
    eval_tokens: int
    total_ms: int
    done_reason: str


@dataclass
class TestResult:
    """テスト結果"""

    request: LLMRequest
    response: LLMResponse
    metrics: dict[str, Any]


def load_config(config_path: str) -> dict[str, Any]:
    """YAML設定ファイルを読み込む"""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_prompt(template: str, variables: dict[str, str]) -> str:
    """テンプレートに変数を埋め込む"""
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{{{key}}}}}", value)
    return result


def call_llm(request: LLMRequest) -> LLMResponse:
    """LLMを呼び出す"""
    start_time = time.time()
    response = ollama.chat(model=request.model, messages=request.to_messages())
    elapsed_ms = int((time.time() - start_time) * 1000)

    return LLMResponse(
        content=response.get("message", {}).get("content", ""),
        prompt_tokens=response.get("prompt_eval_count", 0),
        eval_tokens=response.get("eval_count", 0),
        total_ms=elapsed_ms,
        done_reason=response.get("done_reason", "unknown"),
    )


def analyze_response(content: str, original: str = "") -> dict[str, Any]:
    """応答を分析"""
    # 発話パターン（A:/B:形式）
    utterance_pattern = re.compile(r"^([AB]):\s*(.+)$", re.MULTILINE)
    utterances = utterance_pattern.findall(content)

    metrics = {
        "char_count": len(content),
        "line_count": len(content.split("\n")),
        "utterance_count": len(utterances),
    }

    if original:
        metrics["original_chars"] = len(original)
        metrics["expansion_ratio"] = round(len(content) / len(original), 2) if original else 0

    if utterances:
        speakers = [u[0] for u in utterances]
        metrics["a_count"] = speakers.count("A")
        metrics["b_count"] = speakers.count("B")

    return metrics


def run_test(config: dict[str, Any], model_override: str | None = None) -> TestResult:
    """テストを実行"""
    model = model_override or config.get("model", "gpt-oss:20b")
    system = config.get("system", "")
    prompt_template = config.get("prompt", "")
    variables = config.get("variables", {})
    input_text = config.get("input", "")
    name = config.get("name", "test")

    # 変数を展開
    variables["input"] = input_text
    prompt = build_prompt(prompt_template, variables)

    request = LLMRequest(model=model, system=system, prompt=prompt, name=name)
    response = call_llm(request)
    metrics = analyze_response(response.content, input_text)

    return TestResult(request=request, response=response, metrics=metrics)


def print_result(result: TestResult, verbose: bool = False) -> None:
    """結果を出力"""
    print(f"=== {result.request.name} ===")
    print(f"Model: {result.request.model}")
    print()

    if verbose:
        print("--- System ---")
        print(result.request.system[:200] + "..." if len(result.request.system) > 200 else result.request.system)
        print()
        print("--- Prompt ---")
        print(result.request.prompt[:500] + "..." if len(result.request.prompt) > 500 else result.request.prompt)
        print()

    print("--- Response ---")
    print(result.response.content)
    print()

    print("--- Metrics ---")
    print(f"  Tokens: prompt={result.response.prompt_tokens}, eval={result.response.eval_tokens}")
    print(f"  Time: {result.response.total_ms}ms")
    print(f"  Done: {result.response.done_reason}")
    print(f"  Chars: {result.metrics['char_count']}")
    if "expansion_ratio" in result.metrics:
        print(f"  Expansion: {result.metrics['expansion_ratio']}x")
    if "utterance_count" in result.metrics:
        a_count = result.metrics.get("a_count", 0)
        b_count = result.metrics.get("b_count", 0)
        print(f"  Utterances: {result.metrics['utterance_count']} (A:{a_count}, B:{b_count})")
    print()


def compare_results(results: list[TestResult]) -> None:
    """複数結果を比較"""
    print("=== Comparison ===")
    print()
    headers = ["Name", "Chars", "Ratio", "Utterances", "Time(ms)", "Tokens"]
    row_format = "{:<20} {:>8} {:>8} {:>10} {:>10} {:>10}"

    print(row_format.format(*headers))
    print("-" * 70)

    for r in results:
        print(
            row_format.format(
                r.request.name[:20],
                r.metrics["char_count"],
                r.metrics.get("expansion_ratio", "-"),
                r.metrics.get("utterance_count", "-"),
                r.response.total_ms,
                r.response.eval_tokens,
            )
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="汎用LLMプロンプトテスター")
    parser.add_argument("--config", "-c", help="YAML設定ファイル")
    parser.add_argument("--compare", nargs="+", help="複数設定を比較")
    parser.add_argument("--system", "-s", help="システムプロンプト（インライン）")
    parser.add_argument("--prompt", "-p", help="ユーザープロンプト（インライン）")
    parser.add_argument("--model", "-m", default="gpt-oss:20b", help="モデル名")
    parser.add_argument("--input", "-i", help="入力テキスト")
    parser.add_argument("--verbose", "-v", action="store_true", help="詳細出力")
    parser.add_argument("--json", action="store_true", help="JSON出力")
    args = parser.parse_args()

    results: list[TestResult] = []

    if args.compare:
        # 複数設定を比較
        for config_path in args.compare:
            config = load_config(config_path)
            result = run_test(config, args.model if args.model != "gpt-oss:20b" else None)
            results.append(result)
            if not args.json:
                print_result(result, args.verbose)

        if not args.json:
            compare_results(results)

    elif args.config:
        # 設定ファイルからテスト
        config = load_config(args.config)
        result = run_test(config, args.model if args.model != "gpt-oss:20b" else None)
        results.append(result)
        if not args.json:
            print_result(result, args.verbose)

    elif args.system and args.prompt:
        # インラインテスト
        config = {
            "name": "inline",
            "model": args.model,
            "system": args.system,
            "prompt": args.prompt,
            "input": args.input or "",
        }
        result = run_test(config)
        results.append(result)
        if not args.json:
            print_result(result, args.verbose)

    else:
        parser.print_help()
        return 1

    if args.json:
        output = [
            {
                "name": r.request.name,
                "model": r.request.model,
                "response": r.response.content,
                "metrics": r.metrics,
                "tokens": {
                    "prompt": r.response.prompt_tokens,
                    "eval": r.response.eval_tokens,
                },
                "time_ms": r.response.total_ms,
            }
            for r in results
        ]
        print(json.dumps(output, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
