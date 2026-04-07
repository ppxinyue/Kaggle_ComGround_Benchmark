#!/usr/bin/env python3
"""
Tacit Coordination Dataset Evaluator
=====================================

Computes objective metrics for each item (NO filtering):
  1. Embedding distances: pairwise cosine distances between 4 options
  2. Google frequency: search result counts for each option

All metrics are stored as metadata for visualization/analysis only.

Usage:
    python scripts/evaluate_dataset.py -i data/raw/all_items.json -o data/evaluated
    python scripts/evaluate_dataset.py -i data/raw/Numbers_universal_en.json

Author: Claude Code
Date: 2026-04-07
"""

import os
import json
import argparse
import asyncio
import aiohttp
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

from task_definition import TacitCoordinationItem, compute_pairwise_distances

load_dotenv()


# =============================================================================
# Embedding Evaluator
# =============================================================================

class EmbeddingEvaluator:
    """
    Compute embeddings using OpenAI text-embedding-3-large.
    Widely recognized as SOTA for semantic similarity.
    """

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.startswith("#"):
            # Fallback to local model
            print("No OPENAI_API_KEY found, using local sentence-transformers...")
            self._mode = "local"
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            self.model_name = "all-MiniLM-L6-v2"
        else:
            self._mode = "openai"
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=api_key)
            self.model_name = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
        print(f"  Embedding model: {self.model_name}")

    async def get_embeddings(self, texts: List[str]) -> np.ndarray:
        if self._mode == "local":
            return self._model.encode(texts, convert_to_numpy=True)
        else:
            response = await self._client.embeddings.create(
                model=self.model_name,
                input=texts,
            )
            return np.array([item.embedding for item in response.data])

    async def evaluate_item(self, item: TacitCoordinationItem) -> Dict:
        """Compute embedding distance metrics for a single item."""
        embeddings = await self.get_embeddings(item.options)
        metrics = compute_pairwise_distances(embeddings)

        # Add per-option distance to all others
        from sklearn.metrics.pairwise import cosine_similarity
        sim = cosine_similarity(embeddings)
        dist = 1 - sim

        per_option_avg = []
        for i in range(4):
            avg = np.mean([dist[i][j] for j in range(4) if j != i])
            per_option_avg.append(float(avg))

        metrics["per_option_avg_distance"] = per_option_avg
        metrics["embedding_model"] = self.model_name
        return metrics


# =============================================================================
# Google Frequency Evaluator
# =============================================================================

class GoogleFrequencyEvaluator:
    """
    Estimate relative frequency of each option using Google search result counts.

    Uses Google Custom Search JSON API.
    Requires GOOGLE_API_KEY and GOOGLE_CX environment variables.

    Fallback: uses a simple heuristic if no API key.
    """

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY", "")
        self.cx = os.getenv("GOOGLE_CX", "")
        self._session = None
        self._available = bool(self.api_key and self.cx)
        if self._available:
            print("  Google Search API: available")
        else:
            print("  Google Search API: not configured (set GOOGLE_API_KEY + GOOGLE_CX)")

    async def _get_session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def get_search_count(self, query: str) -> int:
        """Get approximate Google search result count for a query."""
        if not self._available:
            return -1

        session = await self._get_session()
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.cx,
            "q": query,
            "num": 1,  # We only need the totalResults count
        }
        try:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return int(data.get("searchInformation", {}).get("totalResults", "0"))
                return -1
        except Exception as e:
            print(f"    Google API error for '{query}': {e}")
            return -1

    async def evaluate_item(self, item: TacitCoordinationItem) -> Dict:
        """Get search result counts for each option."""
        if not self._available:
            return {"google_counts": [-1] * 4, "google_available": False}

        counts = []
        for opt in item.options:
            count = await self.get_search_count(opt)
            counts.append(count)
            await asyncio.sleep(0.3)  # Rate limiting

        # Normalize to relative frequencies
        valid_counts = [c for c in counts if c > 0]
        if valid_counts:
            total = sum(valid_counts)
            freqs = [c / total if c > 0 else 0 for c in counts]
        else:
            freqs = [0.25] * 4

        return {
            "google_counts": counts,
            "google_frequencies": freqs,
            "google_most_frequent_idx": int(np.argmax(counts)) if valid_counts else -1,
            "google_available": True,
        }

    async def close(self):
        if self._session:
            await self._session.close()


# =============================================================================
# Main Evaluation Pipeline
# =============================================================================

async def evaluate_dataset(
    input_path: Path,
    output_path: Optional[Path] = None,
    embedding: bool = True,
    frequency: bool = True,
):
    """
    Evaluate all items in a dataset file.

    Metrics are added to each item's `metrics` field.
    All items are kept regardless of metric values.
    """
    # Load items
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = [TacitCoordinationItem.from_dict(d) for d in data]
    print(f"Loaded {len(items)} items from {input_path}")

    # Initialize evaluators
    emb_eval = EmbeddingEvaluator() if embedding else None
    freq_eval = GoogleFrequencyEvaluator() if frequency else None

    # Evaluate each item
    for i, item in enumerate(items):
        metrics = {}
        print(f"  [{i+1}/{len(items)}] {item.category}: {item.options}")

        if emb_eval:
            try:
                emb_metrics = await emb_eval.evaluate_item(item)
                metrics["embedding"] = emb_metrics
                print(f"    Embedding OK (avg_dist={emb_metrics['avg_distance']:.3f})")
            except Exception as e:
                print(f"    Embedding FAILED: {e}")
                metrics["embedding"] = {"error": str(e)}

        if freq_eval:
            try:
                freq_metrics = await freq_eval.evaluate_item(item)
                metrics["frequency"] = freq_metrics
                if freq_metrics.get("google_available"):
                    print(f"    Frequency OK (counts={freq_metrics['google_counts']})")
                else:
                    print(f"    Frequency: API not configured")
            except Exception as e:
                print(f"    Frequency FAILED: {e}")
                metrics["frequency"] = {"error": str(e)}

        item.metrics = metrics

        # Rate limiting for embeddings
        if emb_eval and item.metrics.get("embedding", {}).get("embedding_model", "").startswith("text-embedding"):
            await asyncio.sleep(0.1)

    # Clean up
    if freq_eval:
        await freq_eval.close()

    # Save results
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_evaluated.json"

    output_data = [item.to_dict() for item in items]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    # Print summary
    print(f"\n{'='*50}")
    print(f"Evaluation complete!")
    print(f"  Items evaluated: {len(items)}")
    print(f"  Output: {output_path}")

    if emb_eval:
        avg_dists = [
            item.metrics.get("embedding", {}).get("avg_distance", 0)
            for item in items
            if "embedding" in item.metrics and "avg_distance" in item.metrics.get("embedding", {})
        ]
        if avg_dists:
            print(f"  Avg embedding distance: {np.mean(avg_dists):.3f}")

    print(f"{'='*50}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Evaluate Tacit Coordination Dataset")
    parser.add_argument("--input", "-i", type=str, required=True, help="Input JSON file")
    parser.add_argument("--output", "-o", type=str, help="Output JSON file (default: <input>_evaluated.json)")
    parser.add_argument("--no-embedding", action="store_true", help="Skip embedding evaluation")
    parser.add_argument("--no-frequency", action="store_true", help="Skip frequency evaluation")
    args = parser.parse_args()

    asyncio.run(evaluate_dataset(
        input_path=Path(args.input),
        output_path=Path(args.output) if args.output else None,
        embedding=not args.no_embedding,
        frequency=not args.no_frequency,
    ))


if __name__ == "__main__":
    main()
