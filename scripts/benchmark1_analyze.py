#!/usr/bin/env python3
"""
Benchmark 1: Alignment Analysis
================================

Computes alignment metrics between LLM-generated exemplar distributions
and human normative data from Castro, Curley, & Hertzog (2021).

Metrics:
  1. Top-K overlap: Jaccard similarity of top-K exemplar sets
  2. Rank correlation: Spearman's rho between frequency rankings
  3. First-response match: Does LLM's most frequent exemplar match human #1?

Usage:
    python scripts/benchmark1_analyze.py --human data/benchmark1/human_norms.json
    python scripts/benchmark1_analyze.py --human data/benchmark1/human_norms.json -k 5

Author: Claude Code
Date: 2026-04-08
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np


# =============================================================================
# Alignment Metrics
# =============================================================================

def topk_overlap(
    human_top: List[str],
    llm_top: List[str],
    k: int = 10,
) -> float:
    """Jaccard similarity of top-K exemplar sets."""
    h_set = set(ex.lower() for ex in human_top[:k])
    l_set = set(ex.lower() for ex in llm_top[:k])
    if not h_set and not l_set:
        return 0.0
    return len(h_set & l_set) / len(h_set | l_set)


def rank_correlation(
    human_freq: Dict[str, float],
    llm_freq: Dict[str, float],
) -> Tuple[float, float]:
    """
    Spearman's rank correlation between human and LLM exemplar frequencies.
    Computed over the union of exemplars appearing in either top-20 list.
    Returns (rho, p-value).
    """
    from scipy.stats import spearmanr

    # Union of top exemplars
    human_sorted = sorted(human_freq.keys(), key=lambda x: human_freq[x], reverse=True)
    llm_sorted = sorted(llm_freq.keys(), key=lambda x: llm_freq[x], reverse=True)

    # Use top-20 from each
    all_exemplars = list(dict.fromkeys(
        [ex.lower() for ex in human_sorted[:20]] +
        [ex.lower() for ex in llm_sorted[:20]]
    ))

    if len(all_exemplars) < 3:
        return 0.0, 1.0

    # Assign ranks (lower rank = more frequent)
    human_ranks = []
    llm_ranks = []
    for ex in all_exemplars:
        # Rank = position in sorted list; if not present, assign max rank
        h_rank = next((i for i, e in enumerate(human_sorted) if e.lower() == ex), len(human_sorted))
        l_rank = next((i for i, e in enumerate(llm_sorted) if e.lower() == ex), len(llm_sorted))
        human_ranks.append(h_rank)
        llm_ranks.append(l_rank)

    rho, p = spearmanr(human_ranks, llm_ranks)
    return float(rho), float(p)


def first_response_match(
    human_top: List[str],
    llm_top: List[str],
) -> float:
    """1.0 if LLM's most frequent exemplar matches human's, else 0.0."""
    if not human_top or not llm_top:
        return 0.0
    return 1.0 if human_top[0].lower() == llm_top[0].lower() else 0.0


def normalized_frequency_correlation(
    human_freq: Dict[str, float],
    llm_freq: Dict[str, float],
) -> float:
    """
    Pearson correlation of normalized frequency vectors over shared exemplars.
    """
    from scipy.stats import pearsonr

    # Find common exemplars (case-insensitive)
    h_lower = {k.lower(): v for k, v in human_freq.items()}
    l_lower = {k.lower(): v for k, v in llm_freq.items()}
    common = set(h_lower.keys()) & set(l_lower.keys())

    if len(common) < 3:
        return 0.0

    h_vals = [h_lower[ex] for ex in common]
    l_vals = [l_lower[ex] for ex in common]

    r, _ = pearsonr(h_vals, l_vals)
    return float(r)


# =============================================================================
# Main Analysis
# =============================================================================

def analyze_benchmark1(
    human_path: Path,
    llm_dir: Path,
    k_values: List[int] = [5, 10, 20],
    output_path: Path = None,
):
    """
    Compute alignment metrics for all categories with human data.

    Args:
        human_path: Path to human normative data JSON
        llm_dir: Directory with LLM results (category_XXX.json files)
        k_values: K values for top-K overlap
        output_path: Where to save results
    """
    # Load human data
    with open(human_path, "r", encoding="utf-8") as f:
        human_data = json.load(f)

    results = []
    overall_metrics = {
        "topk_overlap": {k: [] for k in k_values},
        "rank_correlation": [],
        "first_response_match": [],
        "frequency_correlation": [],
    }

    categories_with_data = 0

    for cat_id_str, cat_info in human_data.items():
        cat_id = int(cat_id_str)
        label = cat_info["category_label"]
        human_freq = {k.lower(): v for k, v in cat_info["exemplars"].items()}
        human_top = [ex.lower() for ex in sorted(
            human_freq.keys(), key=lambda x: human_freq[x], reverse=True
        )]

        # Load LLM data
        llm_file = llm_dir / f"category_{cat_id:03d}.json"
        if not llm_file.exists():
            print(f"  [{cat_id:2d}] {label}: no LLM data, skipping")
            continue

        with open(llm_file, "r", encoding="utf-8") as f:
            llm_data = json.load(f)

        llm_freq = {k.lower(): v for k, v in llm_data["exemplar_proportions"].items()}
        llm_top = [ex.lower() for ex in sorted(
            llm_freq.keys(), key=lambda x: llm_freq[x], reverse=True
        )]

        # Compute metrics
        cat_result = {
            "category_id": cat_id,
            "category_label": label,
            "num_human_exemplars": len(human_freq),
            "num_llm_exemplars": len(llm_freq),
            "human_top1": human_top[0] if human_top else "",
            "llm_top1": llm_top[0] if llm_top else "",
        }

        # Top-K overlap
        for k in k_values:
            overlap = topk_overlap(human_top, llm_top, k)
            cat_result[f"top{k}_overlap"] = round(overlap, 4)
            overall_metrics["topk_overlap"][k].append(overlap)

        # Rank correlation
        rho, p = rank_correlation(human_freq, llm_freq)
        cat_result["rank_correlation"] = round(rho, 4)
        cat_result["rank_correlation_p"] = round(p, 4)
        overall_metrics["rank_correlation"].append(rho)

        # First response match
        match = first_response_match(human_top, llm_top)
        cat_result["first_response_match"] = match
        overall_metrics["first_response_match"].append(match)

        # Frequency correlation
        freq_corr = normalized_frequency_correlation(human_freq, llm_freq)
        cat_result["frequency_correlation"] = round(freq_corr, 4)
        overall_metrics["frequency_correlation"].append(freq_corr)

        results.append(cat_result)
        categories_with_data += 1

        print(f"  [{cat_id:2d}] {label}: top5_overlap={cat_result['top5_overlap']:.3f}, "
              f"rho={rho:.3f}, match={match}")

    # Compute averages
    summary = {
        "num_categories": categories_with_data,
        "avg_topk_overlap": {k: round(np.mean(v), 4) if v else 0 for k, v in overall_metrics["topk_overlap"].items()},
        "avg_rank_correlation": round(np.mean(overall_metrics["rank_correlation"]), 4) if overall_metrics["rank_correlation"] else 0,
        "avg_first_response_match": round(np.mean(overall_metrics["first_response_match"]), 4) if overall_metrics["first_response_match"] else 0,
        "avg_frequency_correlation": round(np.mean(overall_metrics["frequency_correlation"]), 4) if overall_metrics["frequency_correlation"] else 0,
    }

    print(f"\n{'='*50}")
    print(f"Benchmark 1: Alignment Summary ({categories_with_data} categories)")
    print(f"{'='*50}")
    for k, v in summary["avg_topk_overlap"].items():
        print(f"  Avg top-{k} overlap: {v:.4f}")
    print(f"  Avg rank correlation (Spearman): {summary['avg_rank_correlation']:.4f}")
    print(f"  Avg first-response match rate: {summary['avg_first_response_match']:.4f}")
    print(f"  Avg frequency correlation (Pearson): {summary['avg_frequency_correlation']:.4f}")

    # Save
    if output_path is None:
        output_path = llm_dir / "alignment_results.json"

    output = {"summary": summary, "per_category": results}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {output_path}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Benchmark 1: Alignment Analysis")
    parser.add_argument("--human", "-H", type=str, required=True, help="Human norms JSON")
    parser.add_argument("--llm-dir", "-L", type=str, default="data/benchmark1", help="LLM results directory")
    parser.add_argument("-k", type=str, default="5,10,20", help="K values for top-K overlap")
    parser.add_argument("--output", "-o", type=str, help="Output file")
    args = parser.parse_args()

    k_values = [int(x) for x in args.k.split(",")]
    analyze_benchmark1(
        human_path=Path(args.human),
        llm_dir=Path(args.llm_dir),
        k_values=k_values,
        output_path=Path(args.output) if args.output else None,
    )


if __name__ == "__main__":
    main()
