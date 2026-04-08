#!/usr/bin/env python3
"""
Benchmark 2: Tacit Coordination
================================

Two independent LLM agents see the same 4-option category but with options
shuffled in different random orders. They must independently choose the same
option. This tests focal-point convergence without communication -- a core
aspect of social cognition.

Design principles:
  - NO leading language in category descriptions
  - Each agent sees independently shuffled options
  - Agents are isolated via kbench.chats.new()
  - Chance level for 4 options = 0.25

kbench API usage:
  - @kbench.task(name="...") for the main task (saved)
  - @kbench.task(store_task=False) for sub-tasks (not saved)
  - kbench.chats.new("agent_A") for isolated agent contexts
  - .evaluate(llm=[...], evaluation_data=df) to run over DataFrame

Author: b2-dev on team social-cognition
Date: 2026-04-08
"""

import kaggle_benchmarks as kbench
import pandas as pd
import random
import json
import re
from pathlib import Path
from typing import List, Tuple, Optional, Dict


# =============================================================================
# 1. Domain Taxonomy Constants
# =============================================================================

DOMAIN_CATEGORIES: Dict[str, dict] = {
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

# Flat list of all 31 domains
DOMAINS: List[str] = []
for _cat_info in DOMAIN_CATEGORIES.values():
    DOMAINS.extend(_cat_info["domains"])

# Domains with strong culture dependence -- need US + China split
STRONG_CULTURE_DOMAINS: List[str] = [
    # Places (mixed category)
    "Public Places", "Geographic Entities",
    # Norms (mixed category)
    "Social Norms",
    # Culture (all strong)
    "Holidays", "Food", "Drinks",
    "Famous People", "Media", "Brands",
    # Digital (all strong)
    "Digital Platforms", "Internet Culture",
]

# Chance level for 4-option coordination
CHANCE_LEVEL: float = 0.25


# =============================================================================
# 2. Coordination Game Prompt Template
# =============================================================================

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
# 3. Response Extraction
# =============================================================================

def extract_choice(response: str, options: List[str]) -> Optional[str]:
    """
    Match the LLM response against the provided option strings.

    Matching strategy (in priority order):
      1. Exact match after whitespace normalization and case-insensitive compare
      2. The response text contains one of the options as a substring
      3. An option appears after cue phrases like "I choose", "I select", "My choice is"

    Returns the matched option string (original casing from the options list),
    or None if no match is found.
    """
    if not response or not options:
        return None

    # Normalize the response for matching
    response_stripped = response.strip()
    response_lower = response_stripped.lower()

    # Build normalized option map: normalized_lower -> original option
    option_map: Dict[str, str] = {}
    for opt in options:
        normalized = " ".join(opt.lower().split())
        option_map[normalized] = opt

    # Strategy 1: Exact match -- the entire response (normalized) equals an option
    resp_normalized = " ".join(response_lower.split())
    if resp_normalized in option_map:
        return option_map[resp_normalized]

    # Strategy 2: Check if the response is just the option text with surrounding
    # punctuation or whitespace (e.g. "**Red**" or "\"Red\"")
    cleaned = re.sub(r'^[\s*"\'`\[#>]+', "", response_stripped)
    cleaned = re.sub(r'[\s*"\'`\]#>]+$', "", cleaned)
    cleaned_lower = " ".join(cleaned.lower().split())
    if cleaned_lower in option_map:
        return option_map[cleaned_lower]

    # Strategy 3: Look for option text after common cue phrases
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
            # Strip trailing punctuation from extracted text
            extracted = re.sub(r'[.!?,;]+$', "", extracted).strip()
            extracted_norm = " ".join(extracted.lower().split())
            if extracted_norm in option_map:
                return option_map[extracted_norm]

    # Strategy 4: Check if any option appears as a substring in the response
    # Try longer options first to avoid partial matches
    sorted_options = sorted(option_map.keys(), key=len, reverse=True)
    for opt_norm in sorted_options:
        # Use word-boundary-aware matching to avoid partial word matches
        pattern = re.escape(opt_norm)
        if re.search(pattern, response_lower):
            return option_map[opt_norm]

    # Strategy 5: Fuzzy -- check if any option appears within quotes or bold markers
    quoted_matches = re.findall(r'["\'`*]([^"\'`*]+)["\'`*]', response_stripped)
    for qm in quoted_matches:
        qm_norm = " ".join(qm.lower().split())
        if qm_norm in option_map:
            return option_map[qm_norm]

    return None


# =============================================================================
# 4. Option Shuffling
# =============================================================================

def shuffle_options(options: List[str]) -> List[str]:
    """Return a random permutation of the options list."""
    return random.sample(options, len(options))


# =============================================================================
# 5. Sub-task: Single Coordination Round
# =============================================================================

@kbench.task(store_task=False)
def coordination_round(llm, category: str, options_json: str) -> bool:
    """
    Run one round of the tacit coordination game.

    Two independent agents each see the same category and options, but in
    different random orders. They must independently converge on the same
    choice.

    Args:
        llm: The LLM object provided by kbench.
        category: Neutral category description (e.g. "US Cities").
        options_json: JSON string of the 4 options list.

    Returns:
        True if both agents chose the same option, False otherwise.
    """
    # Parse options from JSON
    try:
        options: List[str] = json.loads(options_json)
    except (json.JSONDecodeError, TypeError) as e:
        raise AssertionError(f"Invalid options_json: {e!r}") from e

    assert isinstance(options, list), f"options must be a list, got {type(options)}"
    assert len(options) == 4, f"options must have exactly 4 items, got {len(options)}"
    assert all(isinstance(o, str) and o.strip() for o in options), \
        f"each option must be a non-empty string, got {options}"

    # Shuffle independently for each agent
    options_a = shuffle_options(options)
    options_b = shuffle_options(options)

    # Format options as comma-separated string
    options_str_a = ", ".join(options_a)
    options_str_b = ", ".join(options_b)

    # Build prompts
    prompt_a = COORDINATION_PROMPT.format(
        category=category,
        options_list=options_str_a,
    )
    prompt_b = COORDINATION_PROMPT.format(
        category=category,
        options_list=options_str_b,
    )

    # Prompt each agent in isolated chat contexts
    with kbench.chats.new("agent_A"):
        response_a = llm.prompt(prompt_a)

    with kbench.chats.new("agent_B"):
        response_b = llm.prompt(prompt_b)

    # Validate responses
    assert response_a is not None, "Agent A returned None response"
    assert response_b is not None, "Agent B returned None response"
    assert isinstance(response_a, str) and len(response_a.strip()) > 0, \
        f"Agent A returned empty/invalid response: {response_a!r}"
    assert isinstance(response_b, str) and len(response_b.strip()) > 0, \
        f"Agent B returned empty/invalid response: {response_b!r}"

    # Extract choices
    choice_a = extract_choice(response_a, options)
    choice_b = extract_choice(response_b, options)

    assert choice_a is not None, \
        f"Agent A's response could not be matched to any option. " \
        f"Response: {response_a!r}, Options: {options}"
    assert choice_b is not None, \
        f"Agent B's response could not be matched to any option. " \
        f"Response: {response_b!r}, Options: {options}"

    # Check coordination: choices match (case-insensitive)
    coordinated = choice_a.strip().lower() == choice_b.strip().lower()
    return coordinated


# =============================================================================
# 6. Main Task: Tacit Coordination Benchmark
# =============================================================================

# Default path for coordination items
_ITEMS_PATH = Path(__file__).resolve().parent.parent / "data" / "benchmark2" / "coordination_items.json"


@kbench.task(name="tacit_coordination")
def tacit_coordination(llm) -> Tuple[float, float]:
    """
    Run the full Tacit Coordination benchmark.

    Loads coordination items from the data file, runs pairwise coordination
    rounds, and returns aggregate metrics.

    Args:
        llm: The LLM object provided by kbench.

    Returns:
        Tuple of (coordination_rate, std):
          - coordination_rate: proportion of rounds where both agents agreed
          - std: standard deviation across items
    """
    # Load items
    items_path = _ITEMS_PATH
    if not items_path.exists():
        raise FileNotFoundError(
            f"Coordination items not found at {items_path}. "
            f"Please generate items first using scripts/generate_dataset.py"
        )

    with open(items_path, "r", encoding="utf-8") as f:
        raw_items = json.load(f)

    assert isinstance(raw_items, list), \
        f"Expected a list of items, got {type(raw_items)}"
    assert len(raw_items) > 0, "Items file is empty"

    # Build evaluation DataFrame
    rows = []
    for item in raw_items:
        assert "category" in item, f"Item missing 'category' field: {item}"
        assert "options" in item, f"Item missing 'options' field: {item}"

        options = item["options"]
        assert isinstance(options, list) and len(options) == 4, \
            f"Item options must be a list of 4, got: {options!r}"

        rows.append({
            "category": item["category"],
            "options_json": json.dumps(options, ensure_ascii=False),
            "domain": item.get("domain", "unknown"),
            "item_id": item.get("item_id", ""),
            "culture": item.get("culture", "universal"),
            "language": item.get("language", "en"),
        })

    eval_df = pd.DataFrame(rows)
    print(f"Tacit Coordination: {len(eval_df)} items loaded from {items_path}")

    # Run coordination_round over all items
    runs = coordination_round.evaluate(
        llm=[llm],
        evaluation_data=eval_df,
        n_jobs=1,
        timeout=120,
    )

    # Collect results as DataFrame
    results_df = runs.as_dataframe()

    # The coordination_round returns bool (True/False)
    # Compute coordination rate
    result_col = None
    for col in results_df.columns:
        if "result" in col.lower() or "coordination_round" in col.lower():
            result_col = col
            break

    if result_col is None:
        # Fallback: use the last column
        result_col = results_df.columns[-1]

    results = results_df[result_col].astype(float)
    coordination_rate = float(results.mean())
    std = float(results.std())

    print(f"Coordination rate: {coordination_rate:.4f} (chance = {CHANCE_LEVEL})")
    print(f"Standard deviation: {std:.4f}")

    return (coordination_rate, std)


# =============================================================================
# 7. Domain-Level Analysis
# =============================================================================

def analyze_by_domain(
    items: List[dict],
    results: List[bool],
) -> pd.DataFrame:
    """
    Break down coordination results by domain and cultural context.

    Args:
        items: List of item dicts with 'domain', 'culture', 'language' fields.
        results: List of bool results (one per item).

    Returns:
        DataFrame with per-domain coordination rates and counts.
    """
    assert len(items) == len(results), \
        f"Mismatch: {len(items)} items vs {len(results)} results"

    rows = []
    for item, result in zip(items, results):
        rows.append({
            "domain": item.get("domain", "unknown"),
            "culture": item.get("culture", "universal"),
            "language": item.get("language", "en"),
            "coordinated": int(result),
        })

    df = pd.DataFrame(rows)

    # Per-domain summary
    domain_summary = df.groupby("domain").agg(
        n_items=("coordinated", "count"),
        n_coordinated=("coordinated", "sum"),
        rate=("coordinated", "mean"),
    ).reset_index()
    domain_summary["rate"] = domain_summary["rate"].round(4)

    return domain_summary


def analyze_by_culture(
    items: List[dict],
    results: List[bool],
) -> pd.DataFrame:
    """
    Break down coordination results by culture label.

    Args:
        items: List of item dicts.
        results: List of bool results.

    Returns:
        DataFrame with per-culture coordination rates.
    """
    assert len(items) == len(results), \
        f"Mismatch: {len(items)} items vs {len(results)} results"

    rows = []
    for item, result in zip(items, results):
        culture = item.get("culture", "universal")
        # Classify into strong vs weak culture dependence
        domain = item.get("domain", "unknown")
        culture_type = "strong" if domain in STRONG_CULTURE_DOMAINS else "weak"
        rows.append({
            "culture": culture,
            "culture_type": culture_type,
            "coordinated": int(result),
        })

    df = pd.DataFrame(rows)

    culture_summary = df.groupby("culture_type").agg(
        n_items=("coordinated", "count"),
        n_coordinated=("coordinated", "sum"),
        rate=("coordinated", "mean"),
    ).reset_index()
    culture_summary["rate"] = culture_summary["rate"].round(4)

    return culture_summary


# =============================================================================
# 8. Items File Loading Utility
# =============================================================================

def load_coordination_items(path: Optional[str] = None) -> List[dict]:
    """
    Load coordination items from JSON file.

    Args:
        path: Optional path override. Defaults to data/benchmark2/coordination_items.json.

    Returns:
        List of item dicts, each with 'category', 'options', 'domain', etc.

    Raises:
        FileNotFoundError: If the items file does not exist.
    """
    items_path = Path(path) if path else _ITEMS_PATH

    if not items_path.exists():
        raise FileNotFoundError(
            f"Coordination items not found at {items_path}. "
            f"Generate items first with scripts/generate_dataset.py"
        )

    with open(items_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    assert isinstance(items, list), f"Expected list, got {type(items)}"
    return items
