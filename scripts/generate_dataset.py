#!/usr/bin/env python3
"""
Tacit Coordination Dataset Generator
=====================================

Generation pipeline:
  1. LLM generates items: {category, options: [4 items]}  (NO focal_option)
  2. All items are saved (no quality filtering)
  3. Evaluation (embedding + frequency) is done separately via evaluate_dataset.py

Usage:
    python scripts/generate_dataset.py -d Numbers -c universal -l en -n 20
    python scripts/generate_dataset.py --all-domains -o data/raw

Author: Claude Code
Date: 2026-04-07
"""

import os
import json
import asyncio
import argparse
import re
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

from task_definition import (
    TacitCoordinationItem,
    DOMAINS,
    CULTURE_SENSITIVE_DOMAINS,
    get_generation_prompt,
)

load_dotenv()


# =============================================================================
# LLM Client
# =============================================================================

class LLMClient:
    """LLM client supporting Anthropic-compatible APIs (including Z.AI proxy)."""

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        base_url = os.getenv("ANTHROPIC_BASE_URL")
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in .env")

        try:
            from anthropic import AsyncAnthropic
            kwargs = {"api_key": api_key}
            if base_url:
                kwargs["base_url"] = base_url
            self._client = AsyncAnthropic(**kwargs)
        except ImportError:
            raise ImportError("anthropic not installed. Run: pip install anthropic")

    async def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 4000) -> str:
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

def parse_generation_response(response: str) -> List[Dict]:
    """Parse LLM response into list of {category, options} dicts."""
    response = response.strip()

    # Strip markdown code blocks
    if "```" in response:
        match = re.search(r"```(?:json)?\s*(.*?)```", response, re.DOTALL)
        if match:
            response = match.group(1).strip()

    try:
        data = json.loads(response)
        if isinstance(data, list):
            return data
        return [data]
    except json.JSONDecodeError:
        # Try to find JSON array in response
        match = re.search(r"\[.*\]", response, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                if isinstance(data, list):
                    return data
            except json.JSONDecodeError:
                pass
    return []


# =============================================================================
# Item Generation
# =============================================================================

async def generate_items(
    domain: str,
    culture: str,
    language: str,
    llm: LLMClient,
    num_items: int = 20,
    batch_size: int = 5,
    max_attempts: int = 10,
) -> List[TacitCoordinationItem]:
    """
    Generate items for a single domain/culture/language combination.

    Keeps ALL generated items (no filtering).
    """
    print(f"\n{'='*50}")
    print(f"Generating: {domain} | {culture} | {language}")
    print(f"Target: {num_items} items")
    print(f"{'='*50}")

    all_items: List[TacitCoordinationItem] = []
    attempts = 0

    while len(all_items) < num_items and attempts < max_attempts:
        attempts += 1
        needed = num_items - len(all_items)
        batch = min(batch_size, needed)

        print(f"  Batch {attempts}: requesting {batch} items...")

        prompt = get_generation_prompt(domain, culture, language, num_items=batch)
        try:
            response = await llm.generate(prompt, temperature=0.8)
            parsed = parse_generation_response(response)
        except Exception as e:
            print(f"    Error: {e}")
            continue

        if not parsed:
            print("    Warning: no valid JSON parsed")
            continue

        for idx, item_data in enumerate(parsed):
            options = item_data.get("options", [])
            category = item_data.get("category", domain)

            # Validate: must have exactly 4 options
            if len(options) != 4:
                print(f"    Skip: {len(options)} options (need 4)")
                continue

            # Validate: all options unique
            if len(set(options)) != 4:
                print(f"    Skip: duplicate options")
                continue

            item_id = f"{domain}_{culture}_{language}_{len(all_items):03d}"
            item = TacitCoordinationItem(
                item_id=item_id,
                domain=domain,
                category=category,
                options=options,
                culture=culture,
                language=language,
            )
            all_items.append(item)
            print(f"    + [{len(all_items):3d}/{num_items}] {category}: {options}")

        if len(all_items) < num_items:
            await asyncio.sleep(0.5)

    print(f"  Done: {len(all_items)} items generated")
    return all_items


# =============================================================================
# Full Dataset Pipeline
# =============================================================================

async def generate_full_dataset(
    output_dir: Path,
    target_items_per_domain: int = 20,
    domains: Optional[List[str]] = None,
    skip_existing: bool = False,
):
    """Generate the full dataset across all domains."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    llm = LLMClient()
    domains_to_generate = domains or DOMAINS

    print(f"Domains to generate: {len(domains_to_generate)}")
    print(f"Items per domain-culture-language: {target_items_per_domain}")
    print(f"Output: {output_dir}")

    all_items: List[TacitCoordinationItem] = []

    for domain in domains_to_generate:
        # Determine culture configs
        if domain in CULTURE_SENSITIVE_DOMAINS:
            configs = [
                ("us", "en"),
                ("china", "zh"),
            ]
        else:
            configs = [
                ("universal", "en"),
                ("universal", "zh"),
            ]

        for culture, language in configs:
            output_file = output_dir / f"{domain}_{culture}_{language}.json"
            if skip_existing and output_file.exists():
                print(f"\nSkipping existing: {output_file.name}")
                # Load existing items
                with open(output_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                all_items.extend([TacitCoordinationItem.from_dict(d) for d in existing])
                continue

            n = target_items_per_domain // len(configs)
            items = await generate_items(domain, culture, language, llm, num_items=n)
            all_items.extend(items)

            # Save per-file
            data = [item.to_dict() for item in items]
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  Saved: {output_file.name}")

            await asyncio.sleep(1)

    # Save combined dataset
    combined_path = output_dir / "all_items.json"
    combined_data = [item.to_dict() for item in all_items]
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)

    # Save summary
    summary = {
        "generated_at": datetime.now().isoformat(),
        "total_items": len(all_items),
        "total_domains": len(domains_to_generate),
        "items_per_domain": target_items_per_domain,
        "domains": domains_to_generate,
    }
    with open(output_dir / "generation_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"Generation complete!")
    print(f"  Total items: {len(all_items)}")
    print(f"  Combined: {combined_path}")
    print(f"{'='*60}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Generate Tacit Coordination Dataset")
    parser.add_argument("--domain", "-d", type=str, help="Single domain to generate")
    parser.add_argument("--all-domains", "-a", action="store_true", help="Generate all domains")
    parser.add_argument("--culture", "-c", type=str, choices=["us", "china", "universal"])
    parser.add_argument("--language", "-l", type=str, choices=["en", "zh"])
    parser.add_argument("--output", "-o", type=str, default="data/raw")
    parser.add_argument("--num-items", "-n", type=int, default=20, help="Items per domain")
    parser.add_argument("--skip-existing", "-s", action="store_true")
    args = parser.parse_args()

    if args.domain:
        # Single domain mode
        if not args.culture or not args.language:
            print("Error: --culture and --language required for single domain mode")
            return
        asyncio.run(generate_full_dataset(
            output_dir=Path(args.output),
            target_items_per_domain=args.num_items,
            domains=[args.domain],
            skip_existing=args.skip_existing,
        ))
    elif args.all_domains:
        asyncio.run(generate_full_dataset(
            output_dir=Path(args.output),
            target_items_per_domain=args.num_items,
            skip_existing=args.skip_existing,
        ))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
