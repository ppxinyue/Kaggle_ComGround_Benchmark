"""
Social Cognition Benchmarks for Kaggle AGI Competition
=======================================================

Benchmark 1: Category-Norm Alignment
  - Replicates Castro, Curley, & Hertzog (2021) category generation task
  - 70 categories, compares LLM vs human exemplar distributions
  - Metrics: Top-K overlap, Spearman correlation, first-response match

Benchmark 2: Tacit Coordination
  - Two-agent coordination game with shuffled options
  - 31 domains across 8 cognitive mechanism categories
  - Tests focal-point convergence without communication
"""

from benchmarks.benchmark1_category_norms import (
    generate_exemplars,
    category_norm_alignment,
    CATEGORIES_70,
)
from benchmarks.benchmark2_coordination import (
    coordination_round,
    tacit_coordination,
    DOMAIN_CATEGORIES,
    STRONG_CULTURE_DOMAINS,
)
