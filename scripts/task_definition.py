#!/usr/bin/env python3
"""
Tacit Coordination Dataset Generator
=====================================

Generate high-quality tacit coordination items across 36 domains,
with statistical quality analysis based on option distance and salience.

Author: Claude Code
Date: 2026-04-07
"""

import json
import asyncio
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Literal
from enum import Enum
import numpy as np


# =============================================================================
# Configuration
# =============================================================================

DOMAINS = [
    # Basic Cognitive (5 domains, 100 items)
    "Numbers", "Colors", "Shapes", "Directions", "Time",

    # Social & Cultural (12 domains, 240 items)
    "Cities", "Countries", "Famous People", "Brands", "Foods", "Drinks",
    "Holidays", "Sports", "Music", "Movies", "Animals", "Occupations",

    # Biological World (4 domains, 80 items)
    "Plants", "Body Parts", "Senses",

    # Objects & Functions (4 domains, 80 items)
    "Tools", "Vehicles", "Clothing", "Furniture",

    # Abstract Concepts (5 domains, 100 items)
    "Emotions", "Weather", "Seasons", "Arts", "Books",

    # Space & Location (3 domains, 60 items)
    "Rooms", "Buildings", "Locations",

    # Social Roles (2 domains, 40 items)
    "Family Roles",

    # Digital World (2 domains, 40 items)
    "Digital", "Tech",

    # Nature (1 domain, 20 items)
    "Nature",
]

CULTURE_TYPES = Literal["us", "china", "universal"]
LANGUAGE_TYPES = Literal["en", "zh"]

# Domains that require culture balancing
CULTURE_SENSITIVE_DOMAINS = [
    "Cities", "Countries", "Famous People", "Brands", "Foods", "Drinks",
    "Holidays", "Sports", "Music", "Movies", "Animals", "Colors"
]

# Quality filtering thresholds
QUALITY_THRESHOLDS = {
    "min_distance": 0.4,      # focal option needs to be sufficiently unique
    "focal_salience": 0.5,    # focal option salience > 50%
    "entropy": 1.2,           # entropy threshold (avoid too ambiguous)
    "max_margin": 0.2         # first option should have clear advantage
}


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
    focal_option: str                 # expected most salient option

    # Cultural context
    culture: CULTURE_TYPES
    language: LANGUAGE_TYPES

    # Quality metrics (computed after generation)
    quality_metrics: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "TacitCoordinationItem":
        return cls(**data)


@dataclass
class GenerationResult:
    """Result of item generation for a domain."""

    domain: str
    culture: CULTURE_TYPES
    language: LANGUAGE_TYPES
    items: List[TacitCoordinationItem]

    # Statistics
    total_generated: int
    passed_quality_filter: int
    avg_quality_metrics: Dict[str, float]


# =============================================================================
# Quality Metrics
# =============================================================================

@dataclass
class QualityMetrics:
    """Quality metrics for a tacit coordination item."""

    # Distance-based metrics (require embeddings)
    min_distance: float = 0.0      # min distance from focal to other options
    avg_distance: float = 0.0      # avg distance from focal to other options
    std_distance: float = 0.0      # std of all pairwise distances

    # Salience-based metrics (require LLM scoring)
    focal_salience: float = 0.0    # probability of focal option
    entropy: float = 0.0           # entropy of probability distribution
    max_margin: float = 0.0        # margin between top 2 options

    # Combined score
    quality_score: float = 0.0     # weighted combination

    def passes_filter(self, thresholds: Dict[str, float]) -> bool:
        """Check if item passes quality thresholds."""
        return (
            self.min_distance >= thresholds.get("min_distance", 0.4) and
            self.focal_salience >= thresholds.get("focal_salience", 0.5) and
            self.entropy <= thresholds.get("entropy", 1.2) and
            self.max_margin >= thresholds.get("max_margin", 0.2)
        )


def compute_distance_metrics(
    focal: str,
    options: List[str],
    embeddings: np.ndarray  # shape: (4, embedding_dim)
) -> Dict[str, float]:
    """
    Compute distance-based quality metrics.

    Assumption: Models tend to choose options that are semantically
    distant from other options (most unique).

    Args:
        focal: The focal option text
        options: List of all 4 options
        embeddings: Pre-computed embeddings for all options

    Returns:
        Dictionary with min_distance, avg_distance, std_distance
    """
    from sklearn.metrics.pairwise import cosine_similarity

    # Find focal index
    focal_idx = options.index(focal)
    focal_emb = embeddings[focal_idx].reshape(1, -1)
    other_embs = np.delete(embeddings, focal_idx, axis=0)

    # Distances from focal to other options
    distances = 1 - cosine_similarity(focal_emb, other_embs)[0]

    # All pairwise distances
    all_distances = 1 - cosine_similarity(embeddings, embeddings)
    # Get upper triangle (excluding diagonal)
    all_distances = all_distances[np.triu_indices(4, k=1)]

    return {
        "min_distance": float(np.min(distances)),
        "avg_distance": float(np.mean(distances)),
        "std_distance": float(np.std(all_distances))
    }


def compute_salience_metrics(
    category: str,
    options: List[str],
    focal: str,
    llm_scores: List[float]  # pre-computed LLM salience scores
) -> Dict[str, float]:
    """
    Compute salience-based quality metrics using LLM scoring.

    Args:
        category: Category description
        options: List of 4 options
        focal: Focal option
        llm_scores: Raw LLM scores for each option

    Returns:
        Dictionary with focal_salience, entropy, max_margin
    """
    # Convert to softmax probabilities
    scores = np.array(llm_scores)
    exp_scores = np.exp(scores - np.max(scores))  # for numerical stability
    probs = exp_scores / np.sum(exp_scores)

    # Find focal index
    focal_idx = options.index(focal)

    # Sort probabilities for margin calculation
    sorted_probs = np.sort(probs)[::-1]

    return {
        "focal_salience": float(probs[focal_idx]),
        "entropy": float(-np.sum(probs * np.log(probs + 1e-10))),
        "max_margin": float(sorted_probs[0] - sorted_probs[1])
    }


# =============================================================================
# Generation Prompts
# =============================================================================

def get_generation_prompt(
    domain: str,
    culture: CULTURE_TYPES,
    language: LANGUAGE_TYPES,
    num_items: int = 5
) -> str:
    """
    Generate prompt for LLM-based item generation.

    CRITICAL: Category must NOT contain leading language!
    """
    culture_instruction = {
        "us": "American cultural context",
        "china": "Chinese cultural context",
        "universal": "Universal (cross-cultural) context"
    }[culture]

    language_instruction = {
        "en": "Generate in English",
        "zh": "Generate in Chinese"
    }[language]

    return f"""Generate {num_items} tacit coordination items for the {domain} domain.

**Context**: {culture_instruction}
**Language**: {language_instruction}

**Requirements**:
1. Category should be descriptive but NOT leading. AVOID phrases like:
   - "most famous", "most popular", "best", "traditional", "typical"
   - Instead use neutral category names: "US Cities", "Chinese Breakfast", etc.

2. Each item has exactly 4 options:
   - 1 focal option: the most salient/obvious choice
   - 3 distractor options: plausible but less salient

3. The focal option should be:
   - Culturally recognizable to people from {culture} background
   - Clearly more salient than distractors (not ambiguous)

**Output Format** (valid JSON only):
```json
[
  {{
    "category": "neutral category description (NO leading words!)",
    "options": ["option1", "option2", "option3", "option4"],
    "focal_option": "the most salient option",
    "rationale": "brief explanation of why this is the focal option"
  }}
]
```

Generate {num_items} diverse items within the {domain} domain.

**Important**:
- For culture-sensitive domains (Cities, Foods, etc.), ensure items reflect {culture} context
- For universal domains (Numbers, Shapes, etc.), items should work cross-culturally
- Options should be at the same semantic level (e.g., all cities, not mixing city/state)
- Distractors should be plausible but clearly less salient than focal

Output ONLY valid JSON. No additional text."""


# =============================================================================
# Analysis and Reporting
# =============================================================================

@dataclass
class DomainReport:
    """Quality report for a single domain."""

    domain: str
    total_items: int
    passed_filter: int
    pass_rate: float

    avg_metrics: Dict[str, float]
    median_metrics: Dict[str, float]

    quality_distribution: Dict[str, List[float]]  # metric_name -> values

    failed_items: List[Dict]  # items that failed with reasons


def generate_domain_report(
    items: List[TacitCoordinationItem],
    domain: str
) -> DomainReport:
    """Generate quality report for a domain."""
    passed = [item for item in items if item.quality_metrics.get("passes_filter", False)]
    failed = [item for item in items if not item.quality_metrics.get("passes_filter", False)]

    # Collect metrics
    all_metrics = {}
    for metric_name in ["min_distance", "avg_distance", "focal_salience", "entropy", "max_margin"]:
        values = [item.quality_metrics.get(metric_name, 0) for item in items]
        all_metrics[metric_name] = values

    # Compute aggregates
    avg_metrics = {k: np.mean(v) for k, v in all_metrics.items()}
    median_metrics = {k: np.median(v) for k, v in all_metrics.items()}

    return DomainReport(
        domain=domain,
        total_items=len(items),
        passed_filter=len(passed),
        pass_rate=len(passed) / len(items) if items else 0,
        avg_metrics=avg_metrics,
        median_metrics=median_metrics,
        quality_distribution=all_metrics,
        failed_items=[{**item.to_dict(), "fail_reason": _get_fail_reason(item)} for item in failed]
    )


def _get_fail_reason(item: TacitCoordinationItem) -> str:
    """Get reason why item failed quality filter."""
    m = item.quality_metrics
    reasons = []

    if m.get("min_distance", 1) < QUALITY_THRESHOLDS["min_distance"]:
        reasons.append("low_distance")
    if m.get("focal_salience", 1) < QUALITY_THRESHOLDS["focal_salience"]:
        reasons.append("low_salience")
    if m.get("entropy", 0) > QUALITY_THRESHOLDS["entropy"]:
        reasons.append("high_entropy")
    if m.get("max_margin", 1) < QUALITY_THRESHOLDS["max_margin"]:
        reasons.append("low_margin")

    return ", ".join(reasons) if reasons else "unknown"


# =============================================================================
# Main Pipeline
# =============================================================================

async def generate_dataset(
    output_dir: Path,
    target_items_per_domain: int = 20,
    generation_overhead: float = 1.25  # Generate 25% more for filtering
) -> Dict[str, DomainReport]:
    """
    Main pipeline for generating the tacit coordination dataset.

    Args:
        output_dir: Directory to save output files
        target_items_per_domain: Target number of items per domain
        generation_overhead: Multiplier for initial generation (to account for filtering)

    Returns:
        Dictionary of domain reports
    """
    # This is a skeleton - implementation requires:
    # 1. LLM client (OpenAI, Anthropic, etc.)
    # 2. Embedding model (for distance metrics)
    # 3. Async execution framework

    reports = {}

    # TODO: Implement actual generation pipeline
    # 1. For each domain, culture, language combination:
    #    a. Generate items using LLM
    #    b. Compute quality metrics
    #    c. Filter by quality thresholds
    #    d. If not enough items, regenerate
    # 2. Aggregate reports
    # 3. Save to JSON files

    return reports


if __name__ == "__main__":
    # Example usage
    print("Tacit Coordination Dataset Generator")
    print("=" * 50)
    print(f"Total domains: {len(DOMAINS)}")
    print(f"Target items per domain: 20")
    print(f"Total target items: {len(DOMAINS) * 20}")
    print(f"\nCulture-sensitive domains: {len(CULTURE_SENSITIVE_DOMAINS)}")
    print(f"Universal domains: {len(DOMAINS) - len(CULTURE_SENSITIVE_DOMAINS)}")
