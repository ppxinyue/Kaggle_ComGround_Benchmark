#!/usr/bin/env python3
"""
Tacit Coordination Dataset Generator - Data Structures & Prompts
================================================================

Key design decisions:
- Generation agent only picks 4 similar options (NO focal_option)
- Evaluation is separate: embedding distances + google frequency
- All items are kept (no quality filtering)
- Metrics are for visualization/analysis only

Author: Claude Code
Date: 2026-04-07
"""

import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Literal
import numpy as np


# =============================================================================
# Configuration
# =============================================================================

# ---------------------------------------------------------------------------
# Domain taxonomy: 8 categories, 28 domains
# Organized by the cognitive mechanism that supports tacit coordination.
# Each domain has a culture_label: "strong" = needs US+China split;
#                                   "weak"   = universal items suffice.
# ---------------------------------------------------------------------------

DOMAIN_CATEGORIES = {
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
        "culture_label": "mixed",   # Public Places + Geographic Entities are strong
        "mechanism": "Spatial routine; meeting-point scripts; collective prominence",
    },
    "Norms": {
        "domains": ["Family Roles", "Occupations", "Social Norms"],
        "culture_label": "mixed",   # Social Norms is strong
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

# Flat list of all 31 domains (preserves category order)
DOMAINS = []
for _cat_info in DOMAIN_CATEGORIES.values():
    DOMAINS.extend(_cat_info["domains"])

CULTURE_TYPES = Literal["us", "china", "universal"]
LANGUAGE_TYPES = Literal["en", "zh"]

# Domains with strong culture dependence → need US + China split
STRONG_CULTURE_DOMAINS = [
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

# Domains with weak culture dependence → universal items
WEAK_CULTURE_DOMAINS = [d for d in DOMAINS if d not in STRONG_CULTURE_DOMAINS]

# Backward-compatible alias
CULTURE_SENSITIVE_DOMAINS = STRONG_CULTURE_DOMAINS


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class TacitCoordinationItem:
    """A single tacit coordination item."""

    # Metadata
    item_id: str
    domain: str
    category: str                     # NO leading language!
    options: List[str]                # exactly 4 options

    # Cultural context
    culture: str                      # "us", "china", or "universal"
    language: str                     # "en" or "zh"

    # Evaluation metrics (computed post-generation, for visualization only)
    metrics: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "TacitCoordinationItem":
        return cls(**data)


# =============================================================================
# Generation Prompts
# =============================================================================

def _get_domain_info(domain: str) -> dict:
    """Look up category and mechanism for a domain."""
    for cat_name, cat_info in DOMAIN_CATEGORIES.items():
        if domain in cat_info["domains"]:
            return {"category": cat_name, "mechanism": cat_info["mechanism"]}
    return {"category": "Unknown", "mechanism": ""}


def get_generation_prompt(
    domain: str,
    culture: str,
    language: str,
    num_items: int = 5
) -> str:
    """
    Generate prompt for LLM-based item generation.

    CRITICAL:
    - Category must NOT contain leading language
    - NO focal_option - just 4 similar options
    - Options should be roughly equally plausible
    """
    culture_instruction = {
        "us": "American cultural context",
        "china": "Chinese cultural context",
        "universal": "Universal (cross-cultural) context"
    }[culture]

    language_instruction = {
        "en": "Generate in English",
        "zh": "Generate in Chinese (Simplified)"
    }[language]

    domain_info = _get_domain_info(domain)
    mechanism_hint = domain_info["mechanism"]

    return f"""Generate {num_items} tacit coordination items for the "{domain}" domain.

**Context**: {culture_instruction}
**Language**: {language_instruction}
**Coordination mechanism**: {mechanism_hint}

**What is a tacit coordination item?**
Two players must independently choose the SAME option from 4 choices to win.
They cannot communicate. So the question is: which option would most people naturally gravitate toward?

**Requirements**:
1. Category must be NEUTRAL - NO leading words like:
   - "most famous", "most popular", "best", "traditional", "typical", "most important"
   - Use neutral names: "US Cities", "Chinese Breakfast Foods", "Primary Colors"

2. Each item has exactly 4 options that are:
   - At the same semantic level (all cities, all colors, all numbers, etc.)
   - Roughly equally plausible on the surface
   - But one will naturally stand out to most people due to cultural salience

3. Do NOT indicate which option is the "focal" or "most salient" one.
   Just provide the category and 4 options.

**Output Format** (valid JSON only, no other text):
```json
[
  {{
    "category": "neutral category description",
    "options": ["optionA", "optionB", "optionC", "optionD"]
  }}
]
```

Generate {num_items} diverse items within the "{domain}" domain.
Make sure the items cover different aspects/subcategories of {domain}.

Output ONLY valid JSON array."""


# =============================================================================
# Embedding Distance Computation
# =============================================================================

def compute_pairwise_distances(
    embeddings: np.ndarray  # shape: (4, embedding_dim)
) -> Dict[str, float]:
    """
    Compute pairwise cosine distances between all 4 option embeddings.

    Returns:
        Dictionary with distance metrics:
        - distance_matrix: 4x4 pairwise distances (flattened upper triangle)
        - avg_distance: average pairwise distance
        - min_distance: minimum pairwise distance (closest pair)
        - max_distance: maximum pairwise distance (farthest pair)
        - most_isolated_idx: index of option farthest from all others
    """
    from sklearn.metrics.pairwise import cosine_similarity

    # Pairwise cosine similarity -> distance
    sim_matrix = cosine_similarity(embeddings)
    dist_matrix = 1 - sim_matrix

    # Upper triangle (excluding diagonal)
    upper_indices = np.triu_indices(4, k=1)
    pairwise_dists = dist_matrix[upper_indices]

    # Most isolated option: highest average distance to others
    avg_dist_per_option = []
    for i in range(4):
        dists_to_others = [dist_matrix[i][j] for j in range(4) if j != i]
        avg_dist_per_option.append(np.mean(dists_to_others))
    most_isolated_idx = int(np.argmax(avg_dist_per_option))

    return {
        "pairwise_distances": pairwise_dists.tolist(),
        "avg_distance": float(np.mean(pairwise_dists)),
        "min_distance": float(np.min(pairwise_dists)),
        "max_distance": float(np.max(pairwise_dists)),
        "most_isolated_idx": most_isolated_idx,
    }
