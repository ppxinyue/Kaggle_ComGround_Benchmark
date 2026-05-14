#!/usr/bin/env python3
"""
Benchmark 2: Item Quality Analysis
===================================

Evaluates the quality of coordination items BEFORE running any LLM.
Two dimensions:
  1. Embedding distance: How semantically distinct is each option?
  2. Corpus frequency: How common/frequent is each option word?

All per-option raw data is saved for later analysis.

Usage:
    python scripts/evaluate_item_quality.py

API:
    Embedding: text-embedding-3-large via OpenAI-compatible proxy
    Frequency: wordfreq library (Google Books, Wikipedia, SUBTLEX corpora)

Outputs:
    data/benchmark2/item_quality.json  -- per-item, per-option raw data
    writings/figures/item_quality_*.png/pdf  -- visualizations
"""

import json
import os
import sys
import time
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# ── Configuration ──────────────────────────────────────────────────────────

EMBEDDING_API_BASE = "https://api.openai-proxy.org/v1"
EMBEDDING_API_KEY = "sk-gUxeTE0SRBD7fNucpF8ekq4On9zgNFIyQpLJnZ23M5PDf06x"
EMBEDDING_MODEL = "text-embedding-3-large"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ITEMS_PATH = PROJECT_ROOT / "data" / "benchmark2" / "coordination_items.json"
OUTPUT_PATH = PROJECT_ROOT / "data" / "benchmark2" / "item_quality.json"
FIGURES_DIR = PROJECT_ROOT / "writings" / "figures"

# Domain taxonomy
DOMAIN_CATEGORIES = {
    "Perception": ["Colors", "Shapes", "Spatial Directions", "Extremes"],
    "Symbolism": ["Numbers", "Time Anchors", "Emotions"],
    "Biology": ["Animals", "Plants", "Fruits", "Body Parts", "Senses"],
    "Artifacts": ["Tools", "Clothing", "Vehicles", "Furniture"],
    "Places": ["Rooms", "Public Places", "Institutions", "Geographic Entities"],
    "Norms": ["Family Roles", "Occupations", "Social Norms"],
    "Culture": ["Holidays", "Food", "Drinks", "Famous People", "Media", "Brands"],
    "Digital": ["Digital Platforms", "Internet Culture"],
}

STRONG_CULTURE_DOMAINS = [
    "Public Places", "Geographic Entities", "Social Norms",
    "Holidays", "Food", "Drinks", "Famous People", "Media", "Brands",
    "Digital Platforms", "Internet Culture",
]


# ── Embedding computation ─────────────────────────────────────────────────

def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Call embedding API for a batch of texts."""
    import httpx

    headers = {
        "Authorization": f"Bearer {EMBEDDING_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": EMBEDDING_MODEL,
        "input": texts,
        "encoding_format": "float",
    }

    resp = httpx.post(
        f"{EMBEDDING_API_BASE}/embeddings",
        headers=headers,
        json=payload,
        timeout=60.0,
    )
    resp.raise_for_status()
    data = resp.json()

    # Sort by index to maintain order
    embeddings = [None] * len(texts)
    for item in data["data"]:
        embeddings[item["index"]] = item["embedding"]
    return embeddings


def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    """1 - cosine_similarity."""
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 1.0
    return 1.0 - dot / (norm_a * norm_b)


def compute_pairwise_distances(embeddings: List[np.ndarray]) -> np.ndarray:
    """Compute pairwise cosine distance matrix."""
    n = len(embeddings)
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = cosine_distance(embeddings[i], embeddings[j])
            dist[i][j] = d
            dist[j][i] = d
    return dist


# ── Frequency computation ─────────────────────────────────────────────────

def get_word_frequencies(options: List[str], lang: str) -> List[Optional[float]]:
    """
    Get corpus word frequency for each option using wordfreq library.
    Returns log frequency (Zipf scale, typically 0-8) or None if not found.
    Higher = more frequent in corpus.
    """
    import wordfreq

    frequencies = []
    wordfreq_lang = "zh" if lang == "zh" else "en"

    for opt in options:
        # Try exact match first
        freq = wordfreq.zipf_frequency(opt, wordfreq_lang)

        if freq > 0:
            frequencies.append(freq)
        else:
            # Try lowercased
            freq = wordfreq.zipf_frequency(opt.lower(), wordfreq_lang)
            if freq > 0:
                frequencies.append(freq)
            else:
                # For multi-word options, average the word frequencies
                words = opt.split()
                if len(words) > 1:
                    word_freqs = []
                    for w in words:
                        wf = wordfreq.zipf_frequency(w.lower(), wordfreq_lang)
                        if wf > 0:
                            word_freqs.append(wf)
                    if word_freqs:
                        frequencies.append(np.mean(word_freqs))
                    else:
                        frequencies.append(None)
                else:
                    frequencies.append(None)

    return frequencies


# ── Main analysis ─────────────────────────────────────────────────────────

def analyze_items(items: List[dict]) -> List[dict]:
    """
    For each item, compute embedding distances and corpus frequencies
    for all options. Returns enriched item data.
    """

    # Collect all unique option texts for batch embedding
    print("Collecting unique option texts...")
    all_texts = set()
    for item in items:
        for opt in item["options"]:
            all_texts.add(opt)
    all_texts = sorted(all_texts)
    print(f"  Unique option texts: {len(all_texts)}")

    # Compute embeddings in batches
    print("Computing embeddings...")
    text_to_embedding = {}
    batch_size = 100
    for i in range(0, len(all_texts), batch_size):
        batch = all_texts[i : i + batch_size]
        try:
            embeddings = get_embeddings_batch(batch)
            for text, emb in zip(batch, embeddings):
                text_to_embedding[text] = emb
            print(f"  Batch {i // batch_size + 1}: {len(batch)} texts embedded")
        except Exception as e:
            print(f"  ERROR in batch {i // batch_size + 1}: {e}")
            time.sleep(2)
            try:
                embeddings = get_embeddings_batch(batch)
                for text, emb in zip(batch, embeddings):
                    text_to_embedding[text] = emb
                print(f"  Batch {i // batch_size + 1} (retry): OK")
            except Exception as e2:
                print(f"  FATAL: Could not embed batch: {e2}")
                for text in batch:
                    text_to_embedding[text] = None

    # Process each item
    print("Processing items...")
    results = []

    for idx, item in enumerate(items):
        options = item["options"]
        lang = item.get("language", "en")
        n_opts = len(options)

        # Get embeddings for this item's options
        embeddings = []
        for opt in options:
            emb = text_to_embedding.get(opt)
            if emb is not None:
                embeddings.append(np.array(emb))
            else:
                embeddings.append(None)

        # Compute pairwise distances
        has_all_embeddings = all(e is not None for e in embeddings)

        # Corpus frequencies
        opt_freqs = get_word_frequencies(options, lang)

        option_data = []
        for i, opt in enumerate(options):
            entry = {
                "text": opt,
                "option_index": i,
            }

            if has_all_embeddings:
                # Embedding fingerprint (first 5 dims)
                entry["embedding_fingerprint"] = embeddings[i][:5].tolist()

                # Distances to all other options
                distances_to_others = []
                for j in range(n_opts):
                    if i != j:
                        d = cosine_distance(embeddings[i], embeddings[j])
                        distances_to_others.append(float(d))

                entry["distances_to_others"] = distances_to_others
                entry["avg_distance"] = float(np.mean(distances_to_others))
                entry["min_distance"] = float(np.min(distances_to_others))
                entry["max_distance"] = float(np.max(distances_to_others))

            # Corpus frequency
            entry["corpus_frequency"] = opt_freqs[i]

            option_data.append(entry)

        # Full distance matrix
        distance_matrix = None
        if has_all_embeddings:
            dm = compute_pairwise_distances(embeddings)
            distance_matrix = dm.tolist()

        # Find most salient by each metric
        most_distant_idx = None
        most_frequent_idx = None
        if has_all_embeddings:
            avg_dists = [od.get("avg_distance", 0) for od in option_data]
            most_distant_idx = int(np.argmax(avg_dists))
        freq_vals = [od.get("corpus_frequency") or 0 for od in option_data]
        if any(v > 0 for v in freq_vals):
            most_frequent_idx = int(np.argmax(freq_vals))

        result = {
            "item_id": item.get("item_id", f"item_{idx}"),
            "domain": item.get("domain", "unknown"),
            "category": item.get("category", ""),
            "culture": item.get("culture", "universal"),
            "language": lang,
            "options": option_data,
            "distance_matrix": distance_matrix,
            "most_distant_option_index": most_distant_idx,
            "most_distant_option_text": options[most_distant_idx] if most_distant_idx is not None else None,
            "most_frequent_option_index": most_frequent_idx,
            "most_frequent_option_text": options[most_frequent_idx] if most_frequent_idx is not None else None,
        }
        results.append(result)

        if (idx + 1) % 50 == 0:
            print(f"  Processed {idx + 1}/{len(items)} items")

    return results


# ── Visualizations ─────────────────────────────────────────────────────────

def create_visualizations(results: List[dict]):
    """Generate publication-quality figures for item quality analysis."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib as mpl

    plt.style.use("seaborn-v0_8-whitegrid")
    mpl.rcParams.update({
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.labelsize": 11,
        "figure.dpi": 150,
    })

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # ── Prepare data ──────────────────────────────────────────────────

    # Flatten: all options across all items
    all_options = []
    for r in results:
        for od in r["options"]:
            entry = {**od, "domain": r["domain"], "item_id": r["item_id"],
                     "language": r["language"], "culture": r["culture"]}
            all_options.append(entry)

    # ── Fig 1: Distribution of avg_distance per option ────────────────
    avg_dists = [o["avg_distance"] for o in all_options if "avg_distance" in o]
    if avg_dists:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(avg_dists, bins=40, color="#4C72B0", edgecolor="white", alpha=0.85)
        ax.axvline(np.mean(avg_dists), color="red", linestyle="--", label=f"Mean = {np.mean(avg_dists):.3f}")
        ax.set_xlabel("Average Cosine Distance to Other Options")
        ax.set_ylabel("Count")
        ax.set_title("Item Quality: Distribution of Option Semantic Distance")
        ax.legend()
        plt.tight_layout()
        for fmt in ["png", "pdf"]:
            fig.savefig(FIGURES_DIR / f"item_quality_distance_dist.{fmt}", dpi=300)
        plt.close()
        print("  Saved: item_quality_distance_dist.png/pdf")

    # ── Fig 2: Per-domain average distance ────────────────────────────
    domain_dists = {}
    for o in all_options:
        if "avg_distance" in o:
            domain_dists.setdefault(o["domain"], []).append(o["avg_distance"])

    if domain_dists:
        domains_sorted = sorted(domain_dists.keys(),
                                key=lambda d: np.mean(domain_dists[d]))
        means = [np.mean(domain_dists[d]) for d in domains_sorted]
        sems = [np.std(domain_dists[d]) / np.sqrt(len(domain_dists[d])) for d in domains_sorted]

        fig, ax = plt.subplots(figsize=(8, 10))
        y_pos = range(len(domains_sorted))
        ax.barh(y_pos, means, xerr=sems, color="#4C72B0", edgecolor="white",
                capsize=3, alpha=0.85)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(domains_sorted, fontsize=9)
        ax.set_xlabel("Mean Average Cosine Distance (+/-SEM)")
        ax.set_title("Item Quality: Semantic Distance by Domain")
        overall_mean = np.mean(avg_dists) if avg_dists else 0
        ax.axvline(overall_mean, color="red", linestyle="--", alpha=0.5,
                    label=f"Overall mean = {overall_mean:.3f}")
        ax.legend()
        plt.tight_layout()
        for fmt in ["png", "pdf"]:
            fig.savefig(FIGURES_DIR / f"item_quality_distance_by_domain.{fmt}", dpi=300)
        plt.close()
        print("  Saved: item_quality_distance_by_domain.png/pdf")

    # ── Fig 3: Distribution of corpus frequency ───────────────────────
    freqs = [o["corpus_frequency"] for o in all_options if o.get("corpus_frequency") is not None]
    if freqs:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(freqs, bins=40, color="#DD8452", edgecolor="white", alpha=0.85)
        ax.axvline(np.mean(freqs), color="red", linestyle="--",
                    label=f"Mean = {np.mean(freqs):.2f}")
        ax.set_xlabel("Corpus Log Frequency (Zipf scale)")
        ax.set_ylabel("Count")
        ax.set_title("Item Quality: Distribution of Option Word Frequency")
        ax.legend()
        plt.tight_layout()
        for fmt in ["png", "pdf"]:
            fig.savefig(FIGURES_DIR / f"item_quality_freq_dist.{fmt}", dpi=300)
        plt.close()
        print("  Saved: item_quality_freq_dist.png/pdf")

    # ── Fig 4: Per-domain corpus frequency ────────────────────────────
    domain_freqs = {}
    for o in all_options:
        if o.get("corpus_frequency") is not None:
            domain_freqs.setdefault(o["domain"], []).append(o["corpus_frequency"])

    if domain_freqs:
        domains_sorted = sorted(domain_freqs.keys(),
                                key=lambda d: np.mean(domain_freqs[d]))
        means = [np.mean(domain_freqs[d]) for d in domains_sorted]
        sems = [np.std(domain_freqs[d]) / np.sqrt(len(domain_freqs[d])) for d in domains_sorted]

        fig, ax = plt.subplots(figsize=(8, 10))
        y_pos = range(len(domains_sorted))
        ax.barh(y_pos, means, xerr=sems, color="#DD8452", edgecolor="white",
                capsize=3, alpha=0.85)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(domains_sorted, fontsize=9)
        ax.set_xlabel("Mean Corpus Log Frequency (Zipf +/-SEM)")
        ax.set_title("Item Quality: Word Frequency by Domain")
        overall_mean = np.mean(freqs) if freqs else 0
        ax.axvline(overall_mean, color="red", linestyle="--", alpha=0.5,
                    label=f"Overall mean = {overall_mean:.2f}")
        ax.legend()
        plt.tight_layout()
        for fmt in ["png", "pdf"]:
            fig.savefig(FIGURES_DIR / f"item_quality_freq_by_domain.{fmt}", dpi=300)
        plt.close()
        print("  Saved: item_quality_freq_by_domain.png/pdf")

    # ── Fig 5: Distance vs Frequency scatter ──────────────────────────
    scatter_data = [(o["avg_distance"], o["corpus_frequency"])
                    for o in all_options
                    if "avg_distance" in o and o.get("corpus_frequency") is not None]
    if scatter_data:
        dists_s, freqs_s = zip(*scatter_data)
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(dists_s, freqs_s, alpha=0.3, s=15, color="#55A868")
        if len(scatter_data) > 10:
            z = np.polyfit(dists_s, freqs_s, 1)
            p = np.poly1d(z)
            x_line = np.linspace(min(dists_s), max(dists_s), 100)
            ax.plot(x_line, p(x_line), "r--", alpha=0.7)
            from scipy.stats import pearsonr
            r, pval = pearsonr(dists_s, freqs_s)
            ax.text(0.05, 0.95, f"r = {r:.3f} (p = {pval:.2e})",
                    transform=ax.transAxes, fontsize=10, verticalalignment="top",
                    bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
        ax.set_xlabel("Average Cosine Distance to Other Options")
        ax.set_ylabel("Corpus Log Frequency (Zipf)")
        ax.set_title("Item Quality: Semantic Distance vs Word Frequency")
        plt.tight_layout()
        for fmt in ["png", "pdf"]:
            fig.savefig(FIGURES_DIR / f"item_quality_distance_vs_freq.{fmt}", dpi=300)
        plt.close()
        print("  Saved: item_quality_distance_vs_freq.png/pdf")

    # ── Fig 6: Which option position is most distant? ─────────────────
    most_distant_counts = {"option_0": 0, "option_1": 0, "option_2": 0, "option_3": 0}
    for r in results:
        if r["most_distant_option_index"] is not None:
            key = f"option_{r['most_distant_option_index']}"
            most_distant_counts[key] += 1

    fig, ax = plt.subplots(figsize=(7, 5))
    labels = ["Option 0\n(expected focal)", "Option 1", "Option 2", "Option 3"]
    counts = [most_distant_counts[f"option_{i}"] for i in range(4)]
    colors = ["#C44E52", "#4C72B0", "#4C72B0", "#4C72B0"]
    bars = ax.bar(labels, counts, color=colors, edgecolor="white")
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                str(count), ha="center", fontsize=10)
    ax.set_ylabel("Number of Items")
    ax.set_title("Item Quality: Which Option Has Highest Semantic Distance?")
    plt.tight_layout()
    for fmt in ["png", "pdf"]:
        fig.savefig(FIGURES_DIR / f"item_quality_most_distant.{fmt}", dpi=300)
    plt.close()
    print("  Saved: item_quality_most_distant.png/pdf")

    # ── Fig 7: Which option position is most frequent? ────────────────
    most_freq_counts = {"option_0": 0, "option_1": 0, "option_2": 0, "option_3": 0}
    no_freq_count = 0
    for r in results:
        if r["most_frequent_option_index"] is not None:
            key = f"option_{r['most_frequent_option_index']}"
            most_freq_counts[key] += 1
        else:
            no_freq_count += 1

    fig, ax = plt.subplots(figsize=(7, 5))
    labels = ["Option 0\n(expected focal)", "Option 1", "Option 2", "Option 3", "Not found"]
    counts = [most_freq_counts[f"option_{i}"] for i in range(4)] + [no_freq_count]
    colors = ["#C44E52", "#4C72B0", "#4C72B0", "#4C72B0", "#BBBBBB"]
    bars = ax.bar(labels, counts, color=colors, edgecolor="white")
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                str(count), ha="center", fontsize=10)
    ax.set_ylabel("Number of Items")
    ax.set_title("Item Quality: Which Option Has Highest Corpus Frequency?")
    plt.tight_layout()
    for fmt in ["png", "pdf"]:
        fig.savefig(FIGURES_DIR / f"item_quality_most_frequent.{fmt}", dpi=300)
    plt.close()
    print("  Saved: item_quality_most_frequent.png/pdf")

    # ── Fig 8: EN vs ZH distance comparison ──────────────────────────
    en_dists = [o["avg_distance"] for o in all_options if "avg_distance" in o and o["language"] == "en"]
    zh_dists = [o["avg_distance"] for o in all_options if "avg_distance" in o and o["language"] == "zh"]

    if en_dists and zh_dists:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(en_dists, bins=30, alpha=0.6, label=f"English (n={len(en_dists)})", color="#4C72B0")
        ax.hist(zh_dists, bins=30, alpha=0.6, label=f"Chinese (n={len(zh_dists)})", color="#DD8452")
        ax.set_xlabel("Average Cosine Distance")
        ax.set_ylabel("Count")
        ax.set_title("Item Quality: Semantic Distance by Language")
        ax.legend()
        plt.tight_layout()
        for fmt in ["png", "pdf"]:
            fig.savefig(FIGURES_DIR / f"item_quality_distance_en_zh.{fmt}", dpi=300)
        plt.close()
        print("  Saved: item_quality_distance_en_zh.png/pdf")

    # ── Fig 9: EN vs ZH frequency comparison ──────────────────────────
    en_freqs = [o["corpus_frequency"] for o in all_options if o.get("corpus_frequency") is not None and o["language"] == "en"]
    zh_freqs = [o["corpus_frequency"] for o in all_options if o.get("corpus_frequency") is not None and o["language"] == "zh"]

    if en_freqs and zh_freqs:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(en_freqs, bins=30, alpha=0.6, label=f"English (n={len(en_freqs)})", color="#4C72B0")
        ax.hist(zh_freqs, bins=30, alpha=0.6, label=f"Chinese (n={len(zh_freqs)})", color="#DD8452")
        ax.axvline(np.mean(en_freqs), color="#4C72B0", linestyle="--", alpha=0.7,
                    label=f"EN mean = {np.mean(en_freqs):.2f}")
        ax.axvline(np.mean(zh_freqs), color="#DD8452", linestyle="--", alpha=0.7,
                    label=f"ZH mean = {np.mean(zh_freqs):.2f}")
        ax.set_xlabel("Corpus Log Frequency (Zipf scale)")
        ax.set_ylabel("Count")
        ax.set_title("Item Quality: Word Frequency by Language")
        ax.legend(fontsize=9)
        plt.tight_layout()
        for fmt in ["png", "pdf"]:
            fig.savefig(FIGURES_DIR / f"item_quality_freq_en_zh.{fmt}", dpi=300)
        plt.close()
        print("  Saved: item_quality_freq_en_zh.png/pdf")


# ── Summary Statistics ─────────────────────────────────────────────────────

def print_summary(results: List[dict]):
    """Print summary statistics for the quality analysis."""
    print("\n" + "=" * 80)
    print("ITEM QUALITY SUMMARY")
    print("=" * 80)

    # Overall
    all_dists = []
    all_freqs = []
    for r in results:
        for od in r["options"]:
            if "avg_distance" in od:
                all_dists.append(od["avg_distance"])
            if od.get("corpus_frequency") is not None:
                all_freqs.append(od["corpus_frequency"])

    print(f"\nTotal items: {len(results)}")
    print(f"Total options analyzed: {len(all_dists)}")

    print(f"\nEMBEDDING DISTANCES:")
    print(f"  Mean avg_distance: {np.mean(all_dists):.4f} +/- {np.std(all_dists):.4f}")
    print(f"  Range: [{np.min(all_dists):.4f}, {np.max(all_dists):.4f}]")

    if all_freqs:
        print(f"\nCORPUS FREQUENCY (Zipf scale, higher = more common):")
        print(f"  Mean: {np.mean(all_freqs):.2f} +/- {np.std(all_freqs):.2f}")
        print(f"  Range: [{np.min(all_freqs):.2f}, {np.max(all_freqs):.2f}]")
        no_freq = sum(1 for r in results for o in r["options"] if o.get("corpus_frequency") is None)
        print(f"  Options with no frequency data: {no_freq}")

    # Option-0 alignment analysis
    both_align = 0
    dist_only = 0
    freq_only = 0
    neither = 0

    for r in results:
        md = r["most_distant_option_index"]
        mf = r["most_frequent_option_index"]
        is_dist = (md == 0)
        is_freq = (mf == 0)

        if is_dist and is_freq:
            both_align += 1
        elif is_dist:
            dist_only += 1
        elif is_freq:
            freq_only += 1
        else:
            neither += 1

    total = len(results)
    print(f"\nOPTION-0 (expected focal) IS ALSO:")
    print(f"  Most semantically distant: {dist_only + both_align}/{total} ({(dist_only + both_align) / total * 100:.1f}%)")
    print(f"  Most corpus-frequent:     {freq_only + both_align}/{total} ({(freq_only + both_align) / total * 100:.1f}%)")
    print(f"  Both:                      {both_align}/{total} ({both_align / total * 100:.1f}%)")
    print(f"  Neither:                   {neither}/{total} ({neither / total * 100:.1f}%)")

    # Per-domain
    print(f"\n{'Domain':<25} {'n':>5} {'Mean Dist':>10} {'Mean Freq':>10}")
    print("-" * 55)
    domain_data = {}
    for r in results:
        domain_data.setdefault(r["domain"], []).append(r)

    for domain in sorted(domain_data.keys(), key=lambda d: np.mean([
        o["avg_distance"] for r in domain_data[d] for o in r["options"] if "avg_distance" in o
    ]), reverse=True):
        items_d = domain_data[domain]
        dists_d = [o["avg_distance"] for r in items_d for o in r["options"] if "avg_distance" in o]
        freqs_d = [o["corpus_frequency"] for r in items_d for o in r["options"] if o.get("corpus_frequency")]
        mean_dist = np.mean(dists_d) if dists_d else 0
        mean_freq = np.mean(freqs_d) if freqs_d else 0
        print(f"{domain:<25} {len(items_d):>5} {mean_dist:>10.4f} {mean_freq:>10.2f}")

    print("=" * 80)


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    print("=" * 80)
    print("BENCHMARK 2: ITEM QUALITY ANALYSIS")
    print("=" * 80)
    print(f"\nEmbedding API: {EMBEDDING_API_BASE}")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
    print(f"Frequency source: wordfreq library (Google Books, Wikipedia, SUBTLEX)")
    print(f"Items: {ITEMS_PATH}")

    # Load items
    with open(ITEMS_PATH, "r", encoding="utf-8") as f:
        items = json.load(f)
    print(f"Loaded {len(items)} items")

    # Check if we already have results (skip API calls if so)
    if OUTPUT_PATH.exists():
        print(f"\nFound existing results at {OUTPUT_PATH}")
        with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
            results = json.load(f)
        print(f"  Loaded {len(results)} item results")

        if len(results) == len(items):
            print("  All items already analyzed. Skipping API calls.")
            print("  Delete item_quality.json to re-run from scratch.")
        else:
            print(f"  Incomplete ({len(results)}/{len(items)}). Re-running...")
            results = analyze_items(items)
    else:
        print("\nRunning analysis...")
        results = analyze_items(items)

    # Save results
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved results to {OUTPUT_PATH}")

    # Print summary
    print_summary(results)

    # Generate visualizations
    print("\nGenerating visualizations...")
    create_visualizations(results)

    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()
