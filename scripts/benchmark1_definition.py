#!/usr/bin/env python3
"""
Benchmark 1: Human Category-Norm Replication
=============================================

Replicates the semantic category generation task from:
  Castro, N., Curley, L., & Hertzog, C. (2021).
  "Category norm update: A revised compilation of 70 semantic categories."

Task: LLM generates as many exemplars as possible for each category label.
Comparison: LLM exemplar frequency distributions vs. human normative data.

Author: Claude Code
Date: 2026-04-08
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
import json

# =============================================================================
# The 70 Category Labels (from Castro, Curley, & Hertzog, 2021)
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
# Data Structures
# =============================================================================

@dataclass
class CategoryNormItem:
    """A single category from the 70-item norm list."""

    category_id: int                          # 1-70
    category_label: str                       # e.g., "A fruit"

    # Human normative data (loaded from external file)
    human_exemplars: Dict[str, float] = field(default_factory=dict)
    # exemplar_name → frequency (proportion of participants who named it)

    human_top_exemplars: List[str] = field(default_factory=list)
    # Ordered list of exemplars by decreasing frequency

    # LLM results (populated during evaluation)
    llm_responses: List[Dict] = field(default_factory=list)
    # List of {run_id: int, exemplars: [str]} for each LLM call

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CategoryNormItem":
        return cls(**data)


# =============================================================================
# Prompt Template
# =============================================================================

def get_benchmark1_prompt(category_label: str) -> str:
    """
    Generate prompt for free exemplar generation.
    Minimal modification from the original human task.
    """
    return f"""List as many examples of "{category_label}" as you can.
Write one example per line. Do not number them. Do not explain.
Just list the examples."""


# =============================================================================
# Human Data Loading
# =============================================================================

def load_human_norms(path: str) -> Dict[int, CategoryNormItem]:
    """
    Load human normative data from a JSON file.

    Expected format:
    {
      "1": {
        "category_label": "A bird",
        "exemplars": {
          "robin": 0.85,
          "sparrow": 0.72,
          ...
        }
      },
      ...
    }

    Exemplar values are proportions (0-1) of participants who named each item.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = {}
    for cat_id_str, cat_data in data.items():
        cat_id = int(cat_id_str)
        exemplars = cat_data.get("exemplars", {})
        sorted_exemplars = sorted(exemplars.keys(), key=lambda x: exemplars[x], reverse=True)

        items[cat_id] = CategoryNormItem(
            category_id=cat_id,
            category_label=cat_data.get("category_label", CATEGORIES_70[cat_id - 1]),
            human_exemplars=exemplars,
            human_top_exemplars=sorted_exemplars,
        )

    return items


def create_empty_items() -> Dict[int, CategoryNormItem]:
    """Create items without human data (for initial LLM data collection)."""
    return {
        i: CategoryNormItem(category_id=i, category_label=label)
        for i, label in enumerate(CATEGORIES_70, 1)
    }
