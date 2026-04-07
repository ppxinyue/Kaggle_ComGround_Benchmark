#!/usr/bin/env python3
"""
Pilot Test Script for Tacit Coordination Dataset Generator
===========================================================

Quick test with minimal items to verify the generation pipeline works.

Usage:
    python scripts/pilot_test.py

This will:
1. Generate 3 items for the Numbers domain (universal, English)
2. Save results to data/pilot/

Author: Claude Code
Date: 2026-04-07
"""

import asyncio
import json
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from task_definition import TacitCoordinationItem, DOMAINS
from generate_dataset import LLMClient, generate_items


async def main():
    """Run pilot test."""
    print("=" * 60)
    print("PILOT TEST: Numbers Domain (Universal, English)")
    print("=" * 60)

    # Initialize LLM client
    print("\nInitializing LLM client...")
    try:
        llm = LLMClient()
        print(f"[OK] LLM client initialized (model: {llm.model})")
    except Exception as e:
        print(f"[FAIL] Error initializing client: {e}")
        print("\nPlease check your .env file has:")
        print("  - ANTHROPIC_API_KEY (required)")
        print("  - ANTHROPIC_BASE_URL (optional, for proxy)")
        return

    # Generate pilot items
    print("\nGenerating pilot items (3 items)...")
    try:
        items = await generate_items(
            domain="Numbers",
            culture="universal",
            language="en",
            llm=llm,
            num_items=3,
        )

        # Save results
        output_dir = Path("data/pilot")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "Numbers_pilot.json"
        data = [item.to_dict() for item in items]
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Print summary
        print("\n" + "=" * 60)
        print("PILOT TEST COMPLETE")
        print("=" * 60)
        print(f"Domain: Numbers")
        print(f"Culture: universal")
        print(f"Language: en")
        print(f"Items generated: {len(items)}")
        print(f"Saved to: {output_file}")

        # Print sample items
        print("\nSample Items:")
        for i, item in enumerate(items, 1):
            print(f"\n  Item {i}:")
            print(f"    ID: {item.item_id}")
            print(f"    Category: {item.category}")
            print(f"    Options: {item.options}")

        print("\n" + "=" * 60)
        print("[OK] Pilot test successful! Ready for full generation.")
        print("=" * 60)

    except Exception as e:
        print(f"\n[FAIL] Error during generation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
