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

DOMAINS = [
    # Basic Cognitive (5 domains)
    "Numbers", "Colors", "Shapes", "Directions", "Time",

    # Social & Cultural (12 domains)
    "Cities", "Countries", "Famous People", "Brands", "Foods", "Drinks",
    "Holidays", "Sports", "Music", "Movies", "Animals", "Occupations",

    # Biological World (3 domains)
    "Plants", "Body Parts", "Senses",

    # Objects & Functions (4 domains)
    "Tools", "Vehicles", "Clothing", "Furniture",

    # Abstract Concepts (5 domains)
    "Emotions", "Weather", "Seasons", "Arts", "Books",

    # Space & Location (3 domains)
    "Rooms", "Buildings", "Locations",

    # Social Roles (1 domain)
    "Family Roles",

    # Digital World (2 domains)
    "Digital", "Tech",

    # Nature (1 domain)
    "Nature",
]

CULTURE_TYPES = Literal["us", "china", "universal"]
LANGUAGE_TYPES = Literal["en", "zh"]

# Domains that require culture balancing (US + China)
CULTURE_SENSITIVE_DOMAINS = [
    "Cities", "Countries", "Famous People", "Brands", "Foods", "Drinks",
    "Holidays", "Sports", "Music", "Movies", "Animals", "Colors"
]


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

    return f"""Generate {num_items} tacit coordination items for the "{domain}" domain.

**Context**: {culture_instruction}
**Language**: {language_instruction}

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
