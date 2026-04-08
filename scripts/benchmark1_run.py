#!/usr/bin/env python3
"""
Benchmark 1: Run LLM on 70 Category Norms
==========================================

Runs free-generation for each of the 70 categories multiple times
to build LLM exemplar frequency distributions.

Usage:
    python scripts/benchmark1_run.py --runs 100
    python scripts/benchmark1_run.py --categories 1-10 --runs 50

Author: Claude Code
Date: 2026-04-08
"""

import os
import json
import asyncio
import argparse
import re
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from dotenv import load_dotenv

from benchmark1_definition import (
    CATEGORIES_70,
    CategoryNormItem,
    get_benchmark1_prompt,
    create_empty_items,
)

load_dotenv()


# =============================================================================
# LLM Client (reuse from benchmark2)
# =============================================================================

class LLMClient:
    """LLM client supporting Anthropic-compatible APIs."""

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        base_url = os.getenv("ANTHROPIC_BASE_URL")
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in .env")

        from anthropic import AsyncAnthropic
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self._client = AsyncAnthropic(**kwargs)

    async def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        response = await self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text


# =============================================================================
# Response Parsing
# =============================================================================

def parse_exemplars(response: str) -> List[str]:
    """Parse LLM response into a list of exemplar strings."""
    lines = response.strip().split("\n")
    exemplars = []
    for line in lines:
        # Strip numbering, bullets, whitespace
        cleaned = re.sub(r'^[\d\.\-\*\)]+\s*', '', line.strip())
        cleaned = cleaned.strip().lower()
        if cleaned and len(cleaned) > 1:
            exemplars.append(cleaned)
    return exemplars


# =============================================================================
# Run Benchmark
# =============================================================================

async def run_benchmark1(
    llm: LLMClient,
    num_runs: int = 100,
    categories: List[int] = None,
    output_dir: Path = Path("data/benchmark1"),
    temperature: float = 0.7,
):
    """
    Run free-generation for each category, multiple times.

    Args:
        num_runs: Number of LLM calls per category (simulating N participants)
        categories: List of category IDs (1-70). None = all.
        output_dir: Where to save results.
        temperature: LLM sampling temperature.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if categories is None:
        categories = list(range(1, 71))

    print(f"Benchmark 1: Category-Norm Replication")
    print(f"  Categories: {len(categories)}")
    print(f"  Runs per category: {num_runs}")
    print(f"  Model: {llm.model}")
    print(f"  Output: {output_dir}")
    print()

    for cat_id in categories:
        label = CATEGORIES_70[cat_id - 1]
        prompt = get_benchmark1_prompt(label)

        cat_file = output_dir / f"category_{cat_id:03d}.json"

        # Skip if already done
        if cat_file.exists():
            with open(cat_file, "r", encoding="utf-8") as f:
                existing = json.load(f)
            if len(existing.get("responses", [])) >= num_runs:
                print(f"  [{cat_id:2d}/70] {label}: already done ({len(existing['responses'])} runs)")
                continue

        print(f"  [{cat_id:2d}/70] {label} ...")

        responses = []
        for run_id in range(num_runs):
            try:
                raw = await llm.generate(prompt, temperature=temperature)
                exemplars = parse_exemplars(raw)
                responses.append({
                    "run_id": run_id,
                    "exemplars": exemplars,
                    "raw_response": raw,
                })
            except Exception as e:
                print(f"    Run {run_id} error: {e}")
                continue

            if run_id % 20 == 19:
                await asyncio.sleep(0.5)

        # Compute frequency distribution
        freq = {}
        for resp in responses:
            # Each unique exemplar per response gets one count
            seen = set()
            for ex in resp["exemplars"]:
                if ex not in seen:
                    freq[ex] = freq.get(ex, 0) + 1
                    seen.add(ex)

        # Normalize to proportions
        total = len(responses)
        proportions = {k: v / total for k, v in freq.items()}
        sorted_exemplars = sorted(proportions.keys(), key=lambda x: proportions[x], reverse=True)

        result = {
            "category_id": cat_id,
            "category_label": label,
            "num_runs": total,
            "model": llm.model,
            "exemplar_frequencies": freq,
            "exemplar_proportions": proportions,
            "top_exemplars": sorted_exemplars[:20],
            "responses": responses,
        }

        with open(cat_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"    Done: {total} runs, {len(freq)} unique exemplars")
        print(f"    Top 5: {sorted_exemplars[:5]}")

        await asyncio.sleep(1)

    # Save combined summary
    print("\nGenerating summary...")
    summary = {"generated_at": datetime.now().isoformat(), "categories": []}
    for cat_id in categories:
        cat_file = output_dir / f"category_{cat_id:03d}.json"
        if cat_file.exists():
            with open(cat_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            summary["categories"].append({
                "category_id": data["category_id"],
                "category_label": data["category_label"],
                "num_runs": data["num_runs"],
                "num_unique_exemplars": len(data["exemplar_frequencies"]),
                "top5": data["top_exemplars"][:5],
            })

    with open(output_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"Summary saved to {output_dir / 'summary.json'}")


# =============================================================================
# CLI
# =============================================================================

def parse_categories(s: str) -> List[int]:
    """Parse category range string like '1-10' or '1,3,5'."""
    if "-" in s:
        start, end = s.split("-")
        return list(range(int(start), int(end) + 1))
    return [int(x) for x in s.split(",")]


def main():
    parser = argparse.ArgumentParser(description="Benchmark 1: Category-Norm Replication")
    parser.add_argument("--runs", "-n", type=int, default=100, help="LLM calls per category")
    parser.add_argument("--categories", "-c", type=str, help="Category IDs (e.g., 1-10 or 1,3,5)")
    parser.add_argument("--output", "-o", type=str, default="data/benchmark1")
    parser.add_argument("--temperature", "-t", type=float, default=0.7)
    args = parser.parse_args()

    cats = parse_categories(args.categories) if args.categories else None
    llm = LLMClient()
    asyncio.run(run_benchmark1(
        llm=llm,
        num_runs=args.runs,
        categories=cats,
        output_dir=Path(args.output),
        temperature=args.temperature,
    ))


if __name__ == "__main__":
    main()
