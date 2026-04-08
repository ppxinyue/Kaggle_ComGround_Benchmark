#!/usr/bin/env python3
"""
Benchmark 1: Category-Norm Alignment (kbench)
==============================================

Replicates Castro, Curley, & Hertzog (2021): given a category label,
the LLM freely generates exemplars. We compare frequency distributions
against human normative data.

Metrics:
  - Top-K overlap (Jaccard)
  - Spearman rank correlation
  - First-response match
  - Pearson frequency correlation

Author: Claude Code
Date: 2026-04-08
"""

import kaggle_benchmarks as kbench
import pandas as pd
import json
import re
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# =============================================================================
# 70 Category Labels (Castro, Curley, & Hertzog, 2021)
# =============================================================================

CATEGORIES_70 = [
    "A bird",
    "A building for religious services",
    "A carpenter's tool",
    "A chemical element",
    "A city",
    "A college or university",
    "A color",
    "A country",
    "A crime",
    "A disease",
    "A drug",
    "A female first name",
    "A fish",
    "A flower",
    "A football penalty",
    "A football position",
    "A football team name",
    "A four-footed animal",
    "A fruit",
    "A gardener's tool",
    "A kind of money",
    "A kitchen utensil",
    "A liquid",
    "A male first name",
    "A member of the clergy",
    "A metal",
    "A military title",
    "A musical instrument",
    "A natural earth formation",
    "A non-alcoholic beverage",
    "A part of a building",
    "A part of speech",
    "A part of the human body",
    "A precious stone",
    "A relative",
    "A science",
    "A snake",
    "A sport",
    "A state",
    "A substance for flavoring food",
    "A thing made of wood",
    "A thing taken from a burning home",
    "A thing that flies",
    "A thing that is green",
    "A thing that makes noise",
    "A thing women wear",
    "A toy",
    "A tree",
    "A type of car",
    "A type of dance",
    "A type of fabric",
    "A type of footwear",
    "A type of fuel",
    "A type of human dwelling",
    "A type of music",
    "A type of reading material",
    "A type of ship/boat",
    "A type of vehicle",
    "A unit of distance",
    "A unit of time",
    "A vegetable",
    "A weapon",
    "A weather phenomenon",
    "An alcoholic beverage",
    "An article of clothing",
    "An article of furniture",
    "An elective office",
    "An herb",
    "An insect",
    "An occupation or profession",
]


# =============================================================================
# Prompt Template & Response Parsing
# =============================================================================

def get_benchmark1_prompt(category_label: str) -> str:
    """Generate prompt for free exemplar generation."""
    return (
        f'List as many examples of "{category_label}" as you can.\n'
        f"Write one example per line. Do not number them. Do not explain.\n"
        f"Just list the examples."
    )


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
# Sub-task: Generate Exemplars for One Category
# =============================================================================

@kbench.task(store_task=False)
def generate_exemplars(llm, category_label: str) -> str:
    """
    Prompt the LLM to generate exemplars for a category.
    Returns the raw response text.
    """
    prompt = get_benchmark1_prompt(category_label)
    response = llm.prompt(prompt)
    return response


# =============================================================================
# Alignment Metrics
# =============================================================================

def topk_overlap(human_top: List[str], llm_top: List[str], k: int = 10) -> float:
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
    Returns (rho, p-value).
    """
    from scipy.stats import spearmanr

    human_sorted = sorted(human_freq.keys(), key=lambda x: human_freq[x], reverse=True)
    llm_sorted = sorted(llm_freq.keys(), key=lambda x: llm_freq[x], reverse=True)

    # Union of top-20 from each
    all_exemplars = list(dict.fromkeys(
        [ex.lower() for ex in human_sorted[:20]] +
        [ex.lower() for ex in llm_sorted[:20]]
    ))

    if len(all_exemplars) < 3:
        return 0.0, 1.0

    # Assign ranks; if not present, assign max rank
    human_ranks = []
    llm_ranks = []
    for ex in all_exemplars:
        h_rank = next((i for i, e in enumerate(human_sorted) if e.lower() == ex), len(human_sorted))
        l_rank = next((i for i, e in enumerate(llm_sorted) if e.lower() == ex), len(llm_sorted))
        human_ranks.append(h_rank)
        llm_ranks.append(l_rank)

    rho, p = spearmanr(human_ranks, llm_ranks)
    return float(rho), float(p)


def first_response_match(human_top: List[str], llm_top: List[str]) -> float:
    """1.0 if LLM's most frequent exemplar matches human's, else 0.0."""
    if not human_top or not llm_top:
        return 0.0
    return 1.0 if human_top[0].lower() == llm_top[0].lower() else 0.0


def frequency_correlation(
    human_freq: Dict[str, float],
    llm_freq: Dict[str, float],
) -> float:
    """Pearson correlation of frequency vectors over shared exemplars."""
    from scipy.stats import pearsonr

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
# Human Norms Loading
# =============================================================================

def load_human_norms(path: str = None) -> Dict:
    """
    Load human normative data from JSON.

    Expected format:
    {
      "1": {
        "category_label": "A bird",
        "exemplars": {"robin": 0.85, "sparrow": 0.72, ...}
      },
      ...
    }
    """
    if path is None:
        path = str(Path(__file__).parent.parent / "data" / "benchmark1" / "human_norms.json")
    p = Path(path)
    if not p.exists():
        print(f"Warning: Human norms file not found at {p}")
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# Main Task: Category-Norm Alignment
# =============================================================================

@kbench.task(name="category_norm_alignment")
def category_norm_alignment(llm) -> tuple[float, float]:
    """
    Run the category-norm alignment benchmark.

    For each of the 70 categories, the LLM generates exemplars freely.
    We compare the resulting frequency distribution against human norms.

    Returns:
        tuple[float, float]: (mean alignment score, standard deviation)
    """
    # Load human normative data
    human_norms = load_human_norms()

    # Create evaluation DataFrame
    df = pd.DataFrame({
        "category_label": CATEGORIES_70,
        "category_id": range(1, 71),
    })

    # Run generation sub-task over all 70 categories
    runs = generate_exemplars.evaluate(
        llm=[llm],
        evaluation_data=df,
        n_jobs=1,
        timeout=120,
    )
    eval_df = runs.as_dataframe()

    # Compute alignment scores per category
    scores = []

    for _, row in eval_df.iterrows():
        cat_label = row.get("category_label", "")
        response = row.get("result", "")

        # Parse exemplars from LLM response
        exemplars = parse_exemplars(str(response))

        # Build LLM frequency distribution
        llm_freq = {}
        for ex in exemplars:
            llm_freq[ex] = llm_freq.get(ex, 0) + 1

        # Normalize to proportions
        total = len(exemplars) if exemplars else 1
        llm_freq_norm = {k: v / total for k, v in llm_freq.items()}
        llm_top = sorted(llm_freq_norm.keys(), key=lambda x: llm_freq_norm[x], reverse=True)

        # Get human data for this category
        cat_id = CATEGORIES_70.index(cat_label) + 1 if cat_label in CATEGORIES_70 else 0
        cat_human = human_norms.get(str(cat_id), {})

        if cat_human and cat_human.get("exemplars"):
            human_freq = {k.lower(): v for k, v in cat_human["exemplars"].items()}
            human_top = sorted(human_freq.keys(), key=lambda x: human_freq[x], reverse=True)

            # Compute 4 alignment metrics
            t5 = topk_overlap(human_top, llm_top, k=5)
            rho, _ = rank_correlation(human_freq, llm_freq_norm)
            frm = first_response_match(human_top, llm_top)
            freq_r = frequency_correlation(human_freq, llm_freq_norm)

            # Composite score: average of 4 metrics (clamp negatives to 0)
            avg_score = (t5 + max(rho, 0) + frm + max(freq_r, 0)) / 4.0
            scores.append(avg_score)

            kbench.assertions.assert_true(
                len(exemplars) > 0,
                expectation=f"LLM should generate exemplars for '{cat_label}'",
            )
        else:
            # No human data available — score based on generation success only
            if exemplars:
                scores.append(0.5)  # Neutral score if no human comparison possible

    if not scores:
        return (0.0, 0.0)

    mean_score = float(np.mean(scores))
    std_score = float(np.std(scores))

    return (mean_score, std_score)


# =============================================================================
# Runner (single category, for quick testing)
# =============================================================================

@kbench.task(name="category_norm_single", store_task=False)
def category_norm_single(llm, category_label: str) -> str:
    """Run a single category generation and return parsed exemplars."""
    prompt = get_benchmark1_prompt(category_label)
    response = llm.prompt(prompt)
    exemplars = parse_exemplars(response)

    kbench.assertions.assert_true(
        len(exemplars) > 0,
        expectation=f"LLM should generate at least one exemplar for '{category_label}'",
    )

    return json.dumps(exemplars, ensure_ascii=False)
