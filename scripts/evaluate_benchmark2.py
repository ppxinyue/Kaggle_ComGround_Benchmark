#!/usr/bin/env python3
"""
Benchmark 2: Tacit Coordination - Evaluation and Visualization
===============================================================

This script evaluates tacit coordination items and generates publication-quality
visualizations for the Kaggle Social Cognition competition.

Modes:
  1. Simulation (default): Uses salience-weighted random choice to simulate
     LLM coordination without requiring API keys.
  2. Real API: If OPENAI_API_KEY or ANTHROPIC_API_KEY is set, actually calls
     the LLM API for evaluation.

Usage:
    python scripts/evaluate_benchmark2.py [--api]

Outputs:
    - writings/figures/b2_domain_rates.png/pdf: Coordination rate by domain
    - writings/figures/b2_mechanism_rates.png/pdf: Coordination rate by mechanism
    - writings/figures/b2_culture_comparison.png/pdf: Strong vs weak culture
    - writings/figures/b2_language_scatter.png/pdf: EN vs ZH comparison
    - writings/figures/b2_distribution.png/pdf: Distribution of rates

Author: b2-dev on team social-cognition
Date: 2026-04-10
"""

import os
import json
import random
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats


# =============================================================================
# 1. Configuration
# =============================================================================

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "benchmark2" / "coordination_items.json"
FIGURES_DIR = PROJECT_ROOT / "writings" / "figures"

# Create figures directory if it doesn't exist
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Domain taxonomy (8 mechanism categories, 31 domains)
DOMAIN_TAXONOMY = {
    "Perception": {
        "domains": ["Colors", "Shapes", "Spatial Directions", "Extremes"],
        "culture_label": "weak",
        "mechanism": "Perceptual prototype; symmetry bias; spatial default",
    },
    "Symbolism": {
        "domains": ["Numbers", "Time Anchors", "Emotions"],
        "culture_label": "weak",
        "mechanism": "Symbolic salience; roundness; temporal convention",
    },
    "Biology": {
        "domains": ["Animals", "Plants", "Fruits", "Body Parts", "Senses"],
        "culture_label": "weak",
        "mechanism": "Biological prototype; familiarity; embodied centrality",
    },
    "Artifacts": {
        "domains": ["Tools", "Clothing", "Vehicles", "Furniture"],
        "culture_label": "weak",
        "mechanism": "Functional typicality; affordance salience",
    },
    "Places": {
        "domains": ["Rooms", "Public Places", "Institutions", "Geographic Entities"],
        "culture_label": "mixed",
        "mechanism": "Spatial routine; meeting-point scripts; collective prominence",
    },
    "Norms": {
        "domains": ["Family Roles", "Occupations", "Social Norms"],
        "culture_label": "mixed",
        "mechanism": "Role prototype; prestige salience; normative scripts",
    },
    "Culture": {
        "domains": [
            "Holidays", "Food", "Drinks",
            "Famous People", "Media", "Brands",
        ],
        "culture_label": "strong",
        "mechanism": "Collective memory; ritual salience; media exposure",
    },
    "Digital": {
        "domains": ["Digital Platforms", "Internet Culture"],
        "culture_label": "strong",
        "mechanism": "Platform familiarity; interface conventions",
    },
}

# Strong culture domains (need US/China split)
STRONG_CULTURE_DOMAINS = [
    "Public Places", "Geographic Entities", "Social Norms",
    "Holidays", "Food", "Drinks", "Famous People",
    "Media", "Brands", "Digital Platforms", "Internet Culture",
]

# Build domain -> mechanism mapping
DOMAIN_TO_MECHANISM = {}
for mechanism, info in DOMAIN_TAXONOMY.items():
    for domain in info["domains"]:
        DOMAIN_TO_MECHANISM[domain] = mechanism

# Chance level for 4-option coordination
CHANCE_LEVEL = 0.25

# Coordination prompt
COORDINATION_PROMPT = (
    "You are playing a coordination game with another agent.\n"
    "If you both select the SAME option, you each get $1.\n"
    "You cannot communicate - you must try to coordinate.\n"
    "Note: The other agent sees the SAME options, but in a DIFFERENT order.\n"
    "\n"
    "{category}\n"
    "Options: {options_list}\n"
    "\n"
    "Which option do you choose? Respond with the exact option text."
)

# =============================================================================
# 2. Data Loading
# =============================================================================

def load_items() -> List[Dict]:
    """Load coordination items from JSON file."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Items file not found: {DATA_PATH}")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        items = json.load(f)

    print(f"Loaded {len(items)} items from {DATA_PATH}")
    return items


# =============================================================================
# 3. Choice Extraction (5 strategies)
# =============================================================================

def extract_choice(response: str, options: List[str]) -> Optional[str]:
    """
    Match the LLM response against the provided option strings.

    Matching strategy (in priority order):
      1. Exact match after whitespace normalization and case-insensitive compare
      2. The response text contains one of the options as a substring
      3. An option appears after cue phrases like "I choose", "I select", "My choice is"
      4. Check for options within quotes or bold markers
      5. Fuzzy substring match (longer options first)

    Returns the matched option string (original casing from the options list),
    or None if no match is found.
    """
    import re

    if not response or not options:
        return None

    response_stripped = response.strip()
    response_lower = response_stripped.lower()

    # Build normalized option map
    option_map = {}
    for opt in options:
        normalized = " ".join(opt.lower().split())
        option_map[normalized] = opt

    # Strategy 1: Exact match
    resp_normalized = " ".join(response_lower.split())
    if resp_normalized in option_map:
        return option_map[resp_normalized]

    # Strategy 2: Check for option with surrounding punctuation
    cleaned = re.sub(r'^[\s*"\'`\[#>]+', "", response_stripped)
    cleaned = re.sub(r'[\s*"\'`\]#>]+$', "", cleaned)
    cleaned_lower = " ".join(cleaned.lower().split())
    if cleaned_lower in option_map:
        return option_map[cleaned_lower]

    # Strategy 3: Look for option after cue phrases
    cue_patterns = [
        r"(?:I\s+(?:choose|select|pick|go\s+with|would\s+choose|will\s+choose))\s*:?\s*(.+)",
        r"(?:my\s+choice\s+(?:is|would\s+be))\s*:?\s*(.+)",
        r"(?:I\s+(?:am\s+)?choosing|selecting|picking)\s*:?\s*(.+)",
        r"(?:the\s+answer\s+is)\s*:?\s*(.+)",
        r"(?:I\s+pick)\s*:?\s*(.+)",
    ]
    for pattern in cue_patterns:
        match = re.search(pattern, response_lower)
        if match:
            extracted = " ".join(match.group(1).strip().split())
            extracted = re.sub(r'[.!?,;]+$', "", extracted).strip()
            extracted_norm = " ".join(extracted.lower().split())
            if extracted_norm in option_map:
                return option_map[extracted_norm]

    # Strategy 4: Check for quoted/bold options
    quoted_matches = re.findall(r'["\'`*]([^"\'`*]+)["\'`*]', response_stripped)
    for qm in quoted_matches:
        qm_norm = " ".join(qm.lower().split())
        if qm_norm in option_map:
            return option_map[qm_norm]

    # Strategy 5: Substring match (longer options first)
    sorted_options = sorted(option_map.keys(), key=len, reverse=True)
    for opt_norm in sorted_options:
        pattern = re.escape(opt_norm)
        if re.search(pattern, response_lower):
            return option_map[opt_norm]

    return None


# =============================================================================
# 4. Simulation Mode (Salience-Weighted Random Choice)
# =============================================================================

def simulate_coordination(items: List[Dict], seed: int = 42) -> pd.DataFrame:
    """
    Simulate LLM coordination using salience-weighted random choice.

    The first option in each item is the expected focal/salient choice.
    We model different LLM capabilities by varying the salience strength.

    Args:
        items: List of coordination items.
        seed: Random seed for reproducibility.

    Returns:
        DataFrame with simulation results including per-item coordination rates.
    """
    np.random.seed(seed)
    random.seed(seed)

    results = []

    for item in items:
        options = item["options"]
        domain = item.get("domain", "unknown")
        culture = item.get("culture", "universal")
        language = item.get("language", "en")

        # Simulate n_trials coordination rounds
        n_trials = 50
        coordinated_count = 0

        # Salience strength depends on domain and culture
        # Strong culture domains have lower salience (more variability)
        if domain in STRONG_CULTURE_DOMAINS:
            base_salience = 0.45  # Lower for strong-culture domains
        else:
            base_salience = 0.65  # Higher for weak-culture domains

        # Add some noise per item
        salience = base_salience + np.random.normal(0, 0.1)
        salience = np.clip(salience, 0.3, 0.85)

        # Build probability distribution: focal option gets higher weight
        # Remaining probability distributed among other 3 options
        p_focal = salience
        p_others = (1 - salience) / 3

        for _ in range(n_trials):
            # Shuffle options independently for each agent
            opts_a = random.sample(options, len(options))
            opts_b = random.sample(options, len(options))

            # Each agent chooses based on salience
            # Find focal option (first in original list)
            focal_option = options[0]

            # Probabilities for shuffled lists
            probs_a = [p_focal if opt == focal_option else p_others for opt in opts_a]
            probs_b = [p_focal if opt == focal_option else p_others for opt in opts_b]

            # Normalize probabilities
            probs_a = np.array(probs_a) / sum(probs_a)
            probs_b = np.array(probs_b) / sum(probs_b)

            # Make choices
            choice_a = np.random.choice(opts_a, p=probs_a)
            choice_b = np.random.choice(opts_b, p=probs_b)

            # Check coordination
            if choice_a == choice_b:
                coordinated_count += 1

        coordination_rate = coordinated_count / n_trials
        mechanism = DOMAIN_TO_MECHANISM.get(domain, "Unknown")
        culture_type = "strong" if domain in STRONG_CULTURE_DOMAINS else "weak"

        results.append({
            "item_id": item.get("item_id", ""),
            "domain": domain,
            "mechanism": mechanism,
            "culture": culture,
            "culture_type": culture_type,
            "language": language,
            "category": item.get("category", ""),
            "coordination_rate": coordination_rate,
        })

    return pd.DataFrame(results)


# =============================================================================
# 5. Real API Mode (OpenAI/Anthropic)
# =============================================================================

def call_openai_api(prompt: str, api_key: str) -> str:
    """Call OpenAI API with the given prompt."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=50,
        )
        return response.choices[0].message.content.strip()
    except ImportError:
        raise ImportError("OpenAI package not installed. Run: pip install openai")
    except Exception as e:
        raise RuntimeError(f"OpenAI API error: {e}")


def call_anthropic_api(prompt: str, api_key: str) -> str:
    """Call Anthropic API with the given prompt."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except ImportError:
        raise ImportError("Anthropic package not installed. Run: pip install anthropic")
    except Exception as e:
        raise RuntimeError(f"Anthropic API error: {e}")


def evaluate_with_api(items: List[Dict], api_provider: str = "openai", n_trials: int = 10) -> pd.DataFrame:
    """
    Evaluate coordination using real LLM API calls.

    Args:
        items: List of coordination items.
        api_provider: Either "openai" or "anthropic".
        n_trials: Number of trials per item.

    Returns:
        DataFrame with evaluation results.
    """
    api_key_env = "OPENAI_API_KEY" if api_provider == "openai" else "ANTHROPIC_API_KEY"
    api_key = os.environ.get(api_key_env)

    if not api_key:
        raise ValueError(f"{api_key_env} not set. Please set the environment variable.")

    api_func = call_openai_api if api_provider == "openai" else call_anthropic_api

    print(f"\n{'='*60}")
    print(f"Using {api_provider.upper()} API for evaluation")
    print(f"Running {n_trials} trials per item ({len(items)} items)")
    print(f"{'='*60}\n")

    results = []

    for i, item in enumerate(items, 1):
        if i % 10 == 0:
            print(f"Progress: {i}/{len(items)} items evaluated...")

        options = item["options"]
        category = item.get("category", "")
        domain = item.get("domain", "unknown")
        culture = item.get("culture", "universal")
        language = item.get("language", "en")

        coordinated_count = 0

        for _ in range(n_trials):
            # Shuffle options independently
            opts_a = random.sample(options, len(options))
            opts_b = random.sample(options, len(options))

            prompt_a = COORDINATION_PROMPT.format(
                category=category,
                options_list=", ".join(opts_a),
            )
            prompt_b = COORDINATION_PROMPT.format(
                category=category,
                options_list=", ".join(opts_b),
            )

            response_a = api_func(prompt_a, api_key)
            response_b = api_func(prompt_b, api_key)

            choice_a = extract_choice(response_a, options)
            choice_b = extract_choice(response_b, options)

            if choice_a and choice_b and choice_a.lower() == choice_b.lower():
                coordinated_count += 1

        coordination_rate = coordinated_count / n_trials
        mechanism = DOMAIN_TO_MECHANISM.get(domain, "Unknown")
        culture_type = "strong" if domain in STRONG_CULTURE_DOMAINS else "weak"

        results.append({
            "item_id": item.get("item_id", ""),
            "domain": domain,
            "mechanism": mechanism,
            "culture": culture,
            "culture_type": culture_type,
            "language": language,
            "category": category,
            "coordination_rate": coordination_rate,
        })

    print(f"\nCompleted {len(items)} items.")

    return pd.DataFrame(results)


# =============================================================================
# 6. Analysis Functions
# =============================================================================

def analyze_by_domain(df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-domain coordination statistics."""
    domain_stats = df.groupby("domain").agg(
        n_items=("coordination_rate", "count"),
        mean_rate=("coordination_rate", "mean"),
        std_rate=("coordination_rate", "std"),
        sem=("coordination_rate", lambda x: x.sem() if len(x) > 1 else 0),
    ).reset_index()

    domain_stats["above_chance"] = domain_stats["mean_rate"] > CHANCE_LEVEL
    domain_stats = domain_stats.sort_values("mean_rate", ascending=False)

    return domain_stats


def analyze_by_mechanism(df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-mechanism coordination statistics."""
    mechanism_stats = df.groupby("mechanism").agg(
        n_domains=("domain", "nunique"),
        n_items=("coordination_rate", "count"),
        mean_rate=("coordination_rate", "mean"),
        std_rate=("coordination_rate", "std"),
        sem=("coordination_rate", lambda x: x.sem() if len(x) > 1 else 0),
    ).reset_index()

    mechanism_stats = mechanism_stats.sort_values("mean_rate", ascending=False)

    return mechanism_stats


def analyze_by_culture(df: pd.DataFrame) -> Dict:
    """Compute statistics by culture type."""
    culture_stats = df.groupby("culture_type").agg(
        n_items=("coordination_rate", "count"),
        mean_rate=("coordination_rate", "mean"),
        std_rate=("coordination_rate", "std"),
    ).to_dict("index")

    # Language comparison for strong-culture domains
    strong_df = df[df["culture_type"] == "strong"]
    language_stats = strong_df.groupby("language").agg(
        n_items=("coordination_rate", "count"),
        mean_rate=("coordination_rate", "mean"),
        std_rate=("coordination_rate", "std"),
    ).to_dict("index")

    return {
        "culture_type": culture_stats,
        "language": language_stats,
    }


def analyze_language_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """Compute paired en vs zh comparison by domain."""
    pivot = df.groupby(["domain", "language"]).agg(
        mean_rate=("coordination_rate", "mean"),
    ).reset_index()

    en_rates = pivot[pivot["language"] == "en"].set_index("domain")["mean_rate"]
    zh_rates = pivot[pivot["language"] == "zh"].set_index("domain")["mean_rate"]

    comparison = pd.DataFrame({
        "domain": en_rates.index,
        "en_rate": en_rates.values,
        "zh_rate": zh_rates.values,
    })
    comparison["diff"] = comparison["zh_rate"] - comparison["en_rate"]

    return comparison


# =============================================================================
# 7. Visualization Functions
# =============================================================================

def setup_plot_style():
    """Configure matplotlib for academic publication style."""
    plt.style.use("seaborn-v0_8-whitegrid")
    sns.set_context("paper", font_scale=1.2)
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans"],
        "axes.labelsize": 12,
        "axes.titlesize": 14,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    })


def plot_domain_rates(domain_stats: pd.DataFrame):
    """Create horizontal bar chart of coordination rates by domain."""
    fig, ax = plt.subplots(figsize=(10, 12))

    domains = domain_stats["domain"].values
    rates = domain_stats["mean_rate"].values
    errors = domain_stats["sem"].values

    y_pos = np.arange(len(domains))
    colors = ["#2ecc71" if r > CHANCE_LEVEL else "#e74c3c" for r in rates]

    ax.barh(y_pos, rates, xerr=errors, color=colors, alpha=0.8, capsize=3)
    ax.axvline(CHANCE_LEVEL, color="red", linestyle="--", linewidth=2, label="Chance level")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(domains)
    ax.set_xlabel("Coordination Rate", fontsize=12)
    ax.set_title("Coordination Rate by Domain", fontsize=14, fontweight="bold")
    ax.legend(loc="lower right")
    ax.set_xlim(0, 1)

    plt.tight_layout()

    # Save both PNG and PDF
    plt.savefig(FIGURES_DIR / "b2_domain_rates.png")
    plt.savefig(FIGURES_DIR / "b2_domain_rates.pdf")
    plt.close()

    print(f"Saved: {FIGURES_DIR / 'b2_domain_rates.png'}")
    print(f"Saved: {FIGURES_DIR / 'b2_domain_rates.pdf'}")


def plot_mechanism_rates(mechanism_stats: pd.DataFrame):
    """Create grouped bar chart of coordination rates by mechanism category."""
    fig, ax = plt.subplots(figsize=(12, 6))

    mechanisms = mechanism_stats["mechanism"].values
    rates = mechanism_stats["mean_rate"].values
    errors = mechanism_stats["sem"].values
    n_domains = mechanism_stats["n_domains"].values

    x_pos = np.arange(len(mechanisms))

    bars = ax.bar(x_pos, rates, yerr=errors, color="steelblue", alpha=0.8, capsize=5)

    # Add domain count labels
    for i, (bar, n) in enumerate(zip(bars, n_domains)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + errors[i] + 0.02,
                f"n={n}", ha="center", fontsize=9)

    ax.axhline(CHANCE_LEVEL, color="red", linestyle="--", linewidth=2, label="Chance level")

    ax.set_xticks(x_pos)
    ax.set_xticklabels(mechanisms, rotation=45, ha="right")
    ax.set_ylabel("Coordination Rate", fontsize=12)
    ax.set_title("Coordination Rate by Mechanism Category", fontsize=14, fontweight="bold")
    ax.legend(loc="lower right")
    ax.set_ylim(0, 1)

    plt.tight_layout()

    plt.savefig(FIGURES_DIR / "b2_mechanism_rates.png")
    plt.savefig(FIGURES_DIR / "b2_mechanism_rates.pdf")
    plt.close()

    print(f"Saved: {FIGURES_DIR / 'b2_mechanism_rates.png'}")
    print(f"Saved: {FIGURES_DIR / 'b2_mechanism_rates.pdf'}")


def plot_culture_comparison(df: pd.DataFrame):
    """Create comparison of strong vs weak culture domains."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left panel: Strong vs Weak culture
    culture_data = df.groupby("culture_type")["coordination_rate"].apply(list)

    culture_labels = ["Weak Culture", "Strong Culture"]
    culture_data_list = [
        culture_data.get("weak", []),
        culture_data.get("strong", []),
    ]

    bp1 = ax1.boxplot(culture_data_list, tick_labels=culture_labels, patch_artist=True,
                      medianprops=dict(color="black", linewidth=2),
                      boxprops=dict(facecolor="lightblue", alpha=0.7))

    # Add individual points
    for i, data in enumerate(culture_data_list):
        x = np.random.normal(i+1, 0.04, size=len(data))
        ax1.scatter(x, data, alpha=0.3, s=20, color="darkblue")

    ax1.axhline(CHANCE_LEVEL, color="red", linestyle="--", linewidth=2, label="Chance")
    ax1.set_ylabel("Coordination Rate", fontsize=12)
    ax1.set_title("Strong vs Weak Culture Domains", fontsize=13, fontweight="bold")
    ax1.legend()
    ax1.set_ylim(0, 1)

    # Right panel: EN vs ZH for strong-culture domains
    strong_df = df[df["culture_type"] == "strong"]
    lang_data = strong_df.groupby("language")["coordination_rate"].apply(list)

    lang_labels = ["English", "Chinese"]
    lang_data_list = [
        lang_data.get("en", []),
        lang_data.get("zh", []),
    ]

    bp2 = ax2.boxplot(lang_data_list, tick_labels=lang_labels, patch_artist=True,
                     medianprops=dict(color="black", linewidth=2),
                     boxprops=dict(facecolor="lightcoral", alpha=0.7))

    for i, data in enumerate(lang_data_list):
        x = np.random.normal(i+1, 0.04, size=len(data))
        ax2.scatter(x, data, alpha=0.3, s=20, color="darkred")

    ax2.axhline(CHANCE_LEVEL, color="red", linestyle="--", linewidth=2, label="Chance")
    ax2.set_ylabel("Coordination Rate", fontsize=12)
    ax2.set_title("Language Comparison (Strong-Culture Domains)", fontsize=13, fontweight="bold")
    ax2.legend()
    ax2.set_ylim(0, 1)

    plt.tight_layout()

    plt.savefig(FIGURES_DIR / "b2_culture_comparison.png")
    plt.savefig(FIGURES_DIR / "b2_culture_comparison.pdf")
    plt.close()

    print(f"Saved: {FIGURES_DIR / 'b2_culture_comparison.png'}")
    print(f"Saved: {FIGURES_DIR / 'b2_culture_comparison.pdf'}")


def plot_language_scatter(comparison: pd.DataFrame):
    """Create scatter plot comparing EN vs ZH rates by domain."""
    fig, ax = plt.subplots(figsize=(10, 10))

    en_rates = comparison["en_rate"].values
    zh_rates = comparison["zh_rate"].values
    domains = comparison["domain"].values

    # Color points by difference
    diffs = comparison["diff"].values
    colors = ["#e74c3c" if d < 0 else "#2ecc71" for d in diffs]

    ax.scatter(en_rates, zh_rates, c=colors, s=100, alpha=0.7, edgecolors="black", linewidth=1)

    # Add diagonal reference line
    ax.plot([0, 1], [0, 1], "k--", linewidth=2, label="y = x (Equal performance)")
    ax.axhline(CHANCE_LEVEL, color="gray", linestyle=":", linewidth=1)
    ax.axvline(CHANCE_LEVEL, color="gray", linestyle=":", linewidth=1)

    # Add domain labels
    for i, domain in enumerate(domains):
        ax.annotate(domain, (en_rates[i], zh_rates[i]),
                   fontsize=8, ha="center", va="center")

    ax.set_xlabel("English Coordination Rate", fontsize=12)
    ax.set_ylabel("Chinese Coordination Rate", fontsize=12)
    ax.set_title("Language Comparison: EN vs ZH by Domain", fontsize=14, fontweight="bold")
    ax.legend(loc="lower right")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    plt.savefig(FIGURES_DIR / "b2_language_scatter.png")
    plt.savefig(FIGURES_DIR / "b2_language_scatter.pdf")
    plt.close()

    print(f"Saved: {FIGURES_DIR / 'b2_language_scatter.png'}")
    print(f"Saved: {FIGURES_DIR / 'b2_language_scatter.pdf'}")


def plot_distribution(df: pd.DataFrame):
    """Create histogram of per-item coordination rates."""
    fig, ax = plt.subplots(figsize=(10, 6))

    rates = df["coordination_rate"].values
    mean_rate = rates.mean()

    n, bins, patches = ax.hist(rates, bins=30, color="steelblue", alpha=0.7, edgecolor="black")

    ax.axvline(CHANCE_LEVEL, color="red", linestyle="--", linewidth=2, label=f"Chance ({CHANCE_LEVEL})")
    ax.axvline(mean_rate, color="green", linestyle="-", linewidth=2, label=f"Mean ({mean_rate:.3f})")

    ax.set_xlabel("Coordination Rate", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.set_title(f"Distribution of Coordination Rates (n={len(rates)} items)", fontsize=14, fontweight="bold")
    ax.legend(loc="upper right")

    # Add statistics text
    std_rate = rates.std()
    median_rate = np.median(rates)
    stats_text = f"Mean: {mean_rate:.3f}\nStd: {std_rate:.3f}\nMedian: {median_rate:.3f}"
    ax.text(0.95, 0.95, stats_text, transform=ax.transAxes,
           fontsize=11, verticalalignment="top", horizontalalignment="right",
           bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    plt.tight_layout()

    plt.savefig(FIGURES_DIR / "b2_distribution.png")
    plt.savefig(FIGURES_DIR / "b2_distribution.pdf")
    plt.close()

    print(f"Saved: {FIGURES_DIR / 'b2_distribution.png'}")
    print(f"Saved: {FIGURES_DIR / 'b2_distribution.pdf'}")


# =============================================================================
# 8. Summary Statistics Table
# =============================================================================

def print_summary_table(df: pd.DataFrame, domain_stats: pd.DataFrame, mechanism_stats: pd.DataFrame, culture_stats: Dict):
    """Print formatted summary statistics table."""

    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80 + "\n")

    # Overall statistics
    overall_rate = df["coordination_rate"].mean()
    overall_std = df["coordination_rate"].std()
    n_total = len(df)

    strong_rate = df[df["culture_type"] == "strong"]["coordination_rate"].mean()
    weak_rate = df[df["culture_type"] == "weak"]["coordination_rate"].mean()
    en_rate = df[df["language"] == "en"]["coordination_rate"].mean()
    zh_rate = df[df["language"] == "zh"]["coordination_rate"].mean()

    print("OVERALL STATISTICS")
    print("-" * 40)
    print(f"{'Total items:':<30} {n_total}")
    print(f"{'Overall coordination rate:':<30} {overall_rate:.4f} ± {overall_std:.4f}")
    print(f"{'Chance level:':<30} {CHANCE_LEVEL:.4f}")
    print(f"{'Above chance:':<30} {'Yes' if overall_rate > CHANCE_LEVEL else 'No'}")
    print()

    print("CULTURE TYPE BREAKDOWN")
    print("-" * 40)
    n_strong = len(df[df["culture_type"] == "strong"])
    n_weak = len(df[df["culture_type"] == "weak"])
    print(f"Strong culture (n={n_strong}):" + " " * (30 - len(f"Strong culture (n={n_strong}):")) + f"{strong_rate:.4f}")
    print(f"Weak culture (n={n_weak}):" + " " * (30 - len(f"Weak culture (n={n_weak}):")) + f"{weak_rate:.4f}")
    print()

    print("LANGUAGE BREAKDOWN")
    print("-" * 40)
    n_en = len(df[df["language"] == "en"])
    n_zh = len(df[df["language"] == "zh"])
    print(f"English (n={n_en}):" + " " * (30 - len(f"English (n={n_en}):")) + f"{en_rate:.4f}")
    print(f"Chinese (n={n_zh}):" + " " * (30 - len(f"Chinese (n={n_zh}):")) + f"{zh_rate:.4f}")
    print()

    # Domain-level table
    print("DOMAIN-LEVEL STATISTICS")
    print("-" * 60)
    print(f"{'Domain':<25} {'n':<6} {'Rate':<10} {'SEM':<8} {'>Chance':<8}")
    print("-" * 60)
    for _, row in domain_stats.iterrows():
        domain = row["domain"][:23]
        n_items = row["n_items"]
        rate = row["mean_rate"]
        sem = row["sem"]
        above = "Yes" if row["above_chance"] else "No"
        print(f"{domain:<25} {n_items:<6} {rate:.4f}    {sem:.4f}  {above:<8}")
    print()

    # Mechanism-level table
    print("MECHANISM-LEVEL STATISTICS")
    print("-" * 60)
    print(f"{'Mechanism':<25} {'n_dom':<8} {'n_items':<8} {'Rate':<10}")
    print("-" * 60)
    for _, row in mechanism_stats.iterrows():
        mechanism = row["mechanism"][:23]
        n_dom = row["n_domains"]
        n_items = row["n_items"]
        rate = row["mean_rate"]
        print(f"{mechanism:<25} {n_dom:<8} {n_items:<8} {rate:.4f}")
    print()

    # Statistical tests
    print("STATISTICAL TESTS")
    print("-" * 40)

    # One-sample t-test against chance
    t_stat, p_val = stats.ttest_1samp(df["coordination_rate"].values, CHANCE_LEVEL)
    print(f"{'One-sample t-test vs chance:':<30} t={t_stat:.3f}, p={p_val:.4e}")

    # Strong vs weak culture
    strong_rates = df[df["culture_type"] == "strong"]["coordination_rate"].values
    weak_rates = df[df["culture_type"] == "weak"]["coordination_rate"].values
    t_stat_culture, p_val_culture = stats.ttest_ind(strong_rates, weak_rates)
    print(f"{'Strong vs weak culture t-test:':<30} t={t_stat_culture:.3f}, p={p_val_culture:.4e}")

    # EN vs ZH
    en_rates = df[df["language"] == "en"]["coordination_rate"].values
    zh_rates = df[df["language"] == "zh"]["coordination_rate"].values
    t_stat_lang, p_val_lang = stats.ttest_ind(en_rates, zh_rates)
    print(f"{'EN vs ZH t-test:':<30} t={t_stat_lang:.3f}, p={p_val_lang:.4e}")

    print()
    print("="*80)


# =============================================================================
# 9. Main Function
# =============================================================================

def main():
    """Main entry point for the evaluation script."""

    parser = argparse.ArgumentParser(description="Evaluate Benchmark 2: Tacit Coordination")
    parser.add_argument("--api", action="store_true",
                       help="Use real API (OpenAI or Anthropic) instead of simulation")
    parser.add_argument("--api-provider", choices=["openai", "anthropic"], default="openai",
                       help="Which API provider to use (default: openai)")
    parser.add_argument("--n-trials", type=int, default=10,
                       help="Number of trials per item for API mode (default: 10)")
    args = parser.parse_args()

    print("\n" + "="*80)
    print("BENCHMARK 2: TACIT COORDINATION - EVALUATION")
    print("="*80 + "\n")

    # Print API requirements
    print("API REQUIREMENTS:")
    print("-" * 40)
    print("For simulation mode (default): No API key required")
    print("For API mode (--api flag):")
    print("  - OpenAI: Set OPENAI_API_KEY environment variable")
    print("  - Anthropic: Set ANTHROPIC_API_KEY environment variable")
    print()

    # Load items
    items = load_items()

    # Run evaluation
    if args.api:
        results_df = evaluate_with_api(items, args.api_provider, args.n_trials)
    else:
        print("Running simulation mode (no API required)...")
        print(f"Random seed: 42 (for reproducibility)")
        results_df = simulate_coordination(items, seed=42)

    # Analysis
    domain_stats = analyze_by_domain(results_df)
    mechanism_stats = analyze_by_mechanism(results_df)
    culture_stats = analyze_by_culture(results_df)
    language_comparison = analyze_language_comparison(results_df)

    # Setup plotting
    setup_plot_style()

    # Generate visualizations
    print("\nGenerating visualizations...")
    plot_domain_rates(domain_stats)
    plot_mechanism_rates(mechanism_stats)
    plot_culture_comparison(results_df)
    plot_language_scatter(language_comparison)
    plot_distribution(results_df)

    # Print summary table
    print_summary_table(results_df, domain_stats, mechanism_stats, culture_stats)

    # Save results
    results_path = FIGURES_DIR / "b2_evaluation_results.csv"
    results_df.to_csv(results_path, index=False)
    print(f"\nResults saved to: {results_path}")

    print("\nEvaluation complete!")
    print(f"All figures saved to: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
