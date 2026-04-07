#!/usr/bin/env python3
"""
Test suite for Tacit Coordination Dataset Generator
====================================================

Test data structures, quality metrics, and prompt generation.
"""

import pytest
import numpy as np
from task_definition import (
    TacitCoordinationItem,
    QualityMetrics,
    compute_distance_metrics,
    compute_salience_metrics,
    get_generation_prompt,
    generate_domain_report,
    QUALITY_THRESHOLDS,
    CULTURE_TYPES,
    LANGUAGE_TYPES,
    DOMAINS,
)


# =============================================================================
# Test Data Structures
# =============================================================================

def test_item_creation():
    """Test creating a TacitCoordinationItem."""
    item = TacitCoordinationItem(
        item_id="test_001",
        domain="Numbers",
        category="Numbers 1-10",
        options=["1", "3", "7", "10"],
        focal_option="7",
        culture="universal",
        language="en"
    )

    assert item.item_id == "test_001"
    assert item.domain == "Numbers"
    assert len(item.options) == 4
    assert item.focal_option == "7"
    assert item.culture == "universal"
    assert item.language == "en"


def test_item_serialization():
    """Test item to_dict and from_dict."""
    item = TacitCoordinationItem(
        item_id="test_002",
        domain="Cities",
        category="US Cities",
        options=["New York", "Los Angeles", "Chicago", "Houston"],
        focal_option="New York",
        culture="us",
        language="en"
    )

    # Convert to dict and back
    item_dict = item.to_dict()
    item_restored = TacitCoordinationItem.from_dict(item_dict)

    assert item_restored.item_id == item.item_id
    assert item_restored.domain == item.domain
    assert item_restored.options == item.options


def test_quality_metrics_creation():
    """Test creating QualityMetrics."""
    metrics = QualityMetrics(
        min_distance=0.5,
        avg_distance=0.7,
        std_distance=0.2,
        focal_salience=0.8,
        entropy=0.9,
        max_margin=0.4
    )

    assert metrics.min_distance == 0.5
    assert metrics.focal_salience == 0.8
    assert metrics.quality_score == 0.0  # default


def test_quality_metrics_passes_filter():
    """Test QualityMetrics.passes_filter()."""
    # Should pass
    good_metrics = QualityMetrics(
        min_distance=0.5,
        avg_distance=0.7,
        focal_salience=0.8,
        entropy=0.9,
        max_margin=0.4
    )
    assert good_metrics.passes_filter(QUALITY_THRESHOLDS)

    # Should fail (low distance)
    bad_distance = QualityMetrics(
        min_distance=0.3,  # below threshold
        avg_distance=0.7,
        focal_salience=0.8,
        entropy=0.9,
        max_margin=0.4
    )
    assert not bad_distance.passes_filter(QUALITY_THRESHOLDS)

    # Should fail (low salience)
    bad_salience = QualityMetrics(
        min_distance=0.5,
        avg_distance=0.7,
        focal_salience=0.4,  # below threshold
        entropy=0.9,
        max_margin=0.4
    )
    assert not bad_salience.passes_filter(QUALITY_THRESHOLDS)


# =============================================================================
# Test Distance Metrics
# =============================================================================

def test_compute_distance_metrics():
    """Test distance-based quality metrics computation."""
    # Mock embeddings (4 options, 3 dimensions)
    # focal (index 2) is distant from others
    embeddings = np.array([
        [0.9, 0.1, 0.1],  # option 0
        [0.8, 0.2, 0.1],  # option 1
        [0.1, 0.1, 0.9],  # option 2 (focal - very different!)
        [0.85, 0.15, 0.1]  # option 3
    ])

    options = ["A", "B", "C", "D"]
    focal = "C"  # index 2

    metrics = compute_distance_metrics(focal, options, embeddings)

    assert "min_distance" in metrics
    assert "avg_distance" in metrics
    assert "std_distance" in metrics
    assert metrics["min_distance"] > 0.4  # focal should be distant


def test_distance_metrics_similar_options():
    """Test distance metrics when all options are similar."""
    # All options are similar
    embeddings = np.array([
        [0.9, 0.1, 0.0],
        [0.8, 0.2, 0.0],
        [0.85, 0.15, 0.0],
        [0.88, 0.12, 0.0]
    ])

    options = ["A", "B", "C", "D"]
    focal = "A"

    metrics = compute_distance_metrics(focal, options, embeddings)

    # All distances should be small
    assert metrics["min_distance"] < 0.3
    assert metrics["avg_distance"] < 0.3


# =============================================================================
# Test Salience Metrics
# =============================================================================

def test_compute_salience_metrics():
    """Test salience-based quality metrics computation."""
    category = "US Cities"
    options = ["New York", "Los Angeles", "Chicago", "Houston"]
    focal = "New York"  # index 0

    # LLM scores where focal has highest score
    llm_scores = [5.0, 2.0, 1.5, 1.0]

    metrics = compute_salience_metrics(category, options, focal, llm_scores)

    assert "focal_salience" in metrics
    assert "entropy" in metrics
    assert "max_margin" in metrics

    # Focal should have highest salience
    assert metrics["focal_salience"] > 0.5

    # Margin should be positive
    assert metrics["max_margin"] > 0


def test_salience_metrics_ambiguous():
    """Test salience metrics with ambiguous choice."""
    category = "Numbers 1-10"
    options = ["3", "5", "7", "9"]
    focal = "7"

    # Similar scores (ambiguous)
    llm_scores = [3.0, 3.5, 4.0, 3.2]

    metrics = compute_salience_metrics(category, options, focal, llm_scores)

    # Should have moderate salience (not very high due to ambiguity)
    # Higher entropy due to similar scores
    assert metrics["entropy"] > 1.0


# =============================================================================
# Test Prompt Generation
# =============================================================================

def test_generation_prompt_us_culture():
    """Test prompt generation for US culture."""
    prompt = get_generation_prompt("Cities", "us", "en", num_items=5)

    assert "Cities" in prompt
    assert "American cultural context" in prompt
    assert "Generate in English" in prompt
    assert "5 tacit coordination items" in prompt
    assert "NOT leading" in prompt
    assert "most famous" in prompt  # as example of what NOT to do


def test_generation_prompt_china_culture():
    """Test prompt generation for China culture."""
    prompt = get_generation_prompt("Foods", "china", "zh", num_items=3)

    assert "Foods" in prompt
    assert "Chinese cultural context" in prompt
    assert "Generate in Chinese" in prompt
    assert "3 tacit coordination items" in prompt


def test_generation_prompt_universal():
    """Test prompt generation for universal culture."""
    prompt = get_generation_prompt("Numbers", "universal", "en", num_items=5)

    assert "Numbers" in prompt
    assert "Universal" in prompt
    assert "cross-cultural" in prompt


def test_generation_prompt_has_warnings():
    """Test that prompt includes warnings about leading language."""
    prompt = get_generation_prompt("Cities", "us", "en")

    # Should warn against leading language
    assert "NOT leading" in prompt
    assert "most famous" in prompt
    assert "traditional" in prompt
    assert "typical" in prompt


# =============================================================================
# Test Domain Report
# =============================================================================

def test_generate_domain_report():
    """Test domain report generation."""
    # Create mock items
    items = [
        TacitCoordinationItem(
            item_id="test_001",
            domain="Numbers",
            category="Numbers 1-10",
            options=["1", "3", "7", "10"],
            focal_option="7",
            culture="universal",
            language="en",
            quality_metrics={
                "min_distance": 0.5,
                "avg_distance": 0.7,
                "focal_salience": 0.8,
                "entropy": 0.9,
                "max_margin": 0.4,
                "passes_filter": True
            }
        ),
        TacitCoordinationItem(
            item_id="test_002",
            domain="Numbers",
            category="Numbers 1-5",
            options=["1", "2", "3", "4"],
            focal_option="3",
            culture="universal",
            language="en",
            quality_metrics={
                "min_distance": 0.2,  # fails
                "avg_distance": 0.5,
                "focal_salience": 0.8,
                "entropy": 0.9,
                "max_margin": 0.4,
                "passes_filter": False
            }
        )
    ]

    report = generate_domain_report(items, "Numbers")

    assert report.domain == "Numbers"
    assert report.total_items == 2
    assert report.passed_filter == 1
    assert report.pass_rate == 0.5
    assert len(report.failed_items) == 1


# =============================================================================
# Test Constants
# =============================================================================

def test_domains_not_empty():
    """Test that DOMAINS list is not empty."""
    assert len(DOMAINS) > 0
    assert "Numbers" in DOMAINS
    assert "Cities" in DOMAINS


def test_quality_thresholds():
    """Test quality thresholds are reasonable."""
    assert "min_distance" in QUALITY_THRESHOLDS
    assert "focal_salience" in QUALITY_THRESHOLDS
    assert "entropy" in QUALITY_THRESHOLDS
    assert "max_margin" in QUALITY_THRESHOLDS

    # Thresholds should be in reasonable ranges
    assert 0 <= QUALITY_THRESHOLDS["min_distance"] <= 1
    assert 0 <= QUALITY_THRESHOLDS["focal_salience"] <= 1
    assert 0 <= QUALITY_THRESHOLDS["entropy"] <= np.log(4)  # max entropy for 4 items


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    print("Running tests...")
    pytest.main([__file__, "-v"])
