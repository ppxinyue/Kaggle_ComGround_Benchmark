"""
Redraw item_clarity_distance.png and item_clarity_frequency.png
Stacked horizontal bar charts: 4 option segments per item, shaded by category color.
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
import matplotlib.patches as mpatches
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
BASE = Path(r"D:\ppXinyue\2026_Kaggle")
DATA = BASE / "data" / "benchmark2" / "item_quality.json"
OUT  = BASE / "writings" / "figures"

# ── Domain → mechanism category mapping ────────────────────────────────
CATEGORY_ORDER = [
    "Perception",
    "Symbolism",
    "Biology",
    "Artifacts",
    "Places",
    "Norms",
    "Culture",
    "Digital",
]

DOMAIN_TO_CAT = {
    # Perception
    "Colors": "Perception",
    "Shapes": "Perception",
    "Spatial Directions": "Perception",
    "Extremes": "Perception",
    # Symbolism
    "Numbers": "Symbolism",
    "Time Anchors": "Symbolism",
    "Emotions": "Symbolism",
    # Biology
    "Animals": "Biology",
    "Plants": "Biology",
    "Fruits": "Biology",
    "Body Parts": "Biology",
    "Senses": "Biology",
    # Artifacts
    "Tools": "Artifacts",
    "Clothing": "Artifacts",
    "Vehicles": "Artifacts",
    "Furniture": "Artifacts",
    # Places
    "Rooms": "Places",
    "Public Places": "Places",
    "Institutions": "Places",
    "Geographic Entities": "Places",
    # Norms
    "Family Roles": "Norms",
    "Occupations": "Norms",
    "Social Norms": "Norms",
    # Culture
    "Holidays": "Culture",
    "Food": "Culture",
    "Drinks": "Culture",
    "Famous People": "Culture",
    "Media": "Culture",
    "Brands": "Culture",
    # Digital
    "Digital Platforms": "Digital",
    "Internet Culture": "Digital",
}

CATEGORY_COLORS = {
    "Perception": "#e41a1c",
    "Symbolism": "#377eb8",
    "Biology":  "#4daf4a",
    "Artifacts": "#984ea3",
    "Places":   "#ff7f00",
    "Norms":    "#a65628",
    "Culture":  "#f781bf",
    "Digital":  "#999999",
}


def make_shades(hex_color, n=4):
    """Return n shades from darkest to lightest based on a base colour."""
    r, g, b = to_rgb(hex_color)
    shades = []
    for i in range(n):
        # lerp towards white; darkest → lightest
        t = 0.70 * i / (n - 1)  # 0.0 … 0.70  (strong gradient)
        shade = (r + (1 - r) * t, g + (1 - g) * t, b + (1 - b) * t)
        shades.append(shade)
    return shades


# ── Load data ──────────────────────────────────────────────────────────
with open(DATA, encoding="utf-8") as f:
    raw = json.load(f)

# Enrich items with category
for item in raw:
    item["_cat"] = DOMAIN_TO_CAT.get(item["domain"], "Unknown")

# ── Sorting key ────────────────────────────────────────────────────────
def sort_key(item):
    cat_idx = CATEGORY_ORDER.index(item["_cat"])
    return (cat_idx, item["domain"], -max(o["avg_distance"] for o in item["options"]))

sorted_items = sorted(raw, key=sort_key)


# ── Drawing helper ─────────────────────────────────────────────────────
def draw_figure(items, value_key, filename_prefix, xlabel, title,
                skip_null=False, figsize=(8, 10)):
    """
    value_key: 'avg_distance' or 'corpus_frequency'
    """
    if skip_null:
        items = [it for it in items
                 if all(o.get("corpus_frequency") is not None for o in it["options"])]

    n = len(items)
    bar_height = 0.82
    fig, ax = plt.subplots(figsize=figsize)

    # Track category boundaries for labels & separators
    prev_cat = None
    cat_start = 0
    y = n  # top of chart; we draw downward

    # For right-margin domain labels
    domain_labels = []  # (y_midpoint, domain_name)

    for idx, item in enumerate(items):
        cat = item["_cat"]
        domain = item["domain"]

        # Category transition
        if cat != prev_cat:
            if prev_cat is not None:
                # Horizontal separator line
                ax.axhline(y=y + 0.5, color="black", linewidth=0.4, zorder=5)
            cat_start = idx
            prev_cat = cat

        # Domain tracking for right labels
        if idx == 0 or items[idx - 1]["domain"] != domain:
            domain_start_y = y
        if idx == n - 1 or items[idx + 1]["domain"] != domain:
            domain_end_y = y
            domain_labels.append(((domain_start_y + domain_end_y) / 2, domain))

        # Get 4 option values, sort descending
        vals = [o[value_key] for o in item["options"]]
        vals_sorted = sorted(vals, reverse=True)

        shades = make_shades(CATEGORY_COLORS[cat], 4)

        left = 0
        for seg_i, v in enumerate(vals_sorted):
            ax.barh(y, v, height=bar_height, left=left, color=shades[seg_i],
                    edgecolor="none", linewidth=0)
            left += v

        y -= 1

    # ── Category labels on left margin ─────────────────────────────────
    prev_cat = None
    cat_start_idx = 0
    for idx, item in enumerate(items):
        cat = item["_cat"]
        if cat != prev_cat:
            if prev_cat is not None:
                y_mid = (n - cat_start_idx) + (cat_start_idx - idx) / 2
                ax.text(
                    -0.01, y_mid, prev_cat,
                    transform=ax.get_yaxis_transform(),
                    ha="right", va="center",
                    fontsize=9, fontweight="bold",
                    rotation=90,
                    color=CATEGORY_COLORS[prev_cat],
                )
            cat_start_idx = idx
            prev_cat = cat
    # Last category
    y_mid = (n - cat_start_idx) / 2
    ax.text(
        -0.01, y_mid, prev_cat,
        transform=ax.get_yaxis_transform(),
        ha="right", va="center",
        fontsize=9, fontweight="bold",
        rotation=90,
        color=CATEGORY_COLORS[prev_cat],
    )

    # ── Domain labels on right margin ──────────────────────────────────
    for ym, dname in domain_labels:
        ax.text(
            1.005, ym, dname,
            transform=ax.get_yaxis_transform(),
            ha="left", va="center",
            fontsize=9, fontstyle="italic", color="#333333",
        )

    # ── Axes cosmetics ─────────────────────────────────────────────────
    ax.set_xlim(0, None)
    ax.set_ylim(0, n + 1)
    ax.set_yticks([])
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.invert_yaxis()  # items top-to-bottom

    plt.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"{filename_prefix}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {filename_prefix}.png / .pdf  ({n} items)")


# ── Figure 1: Distance ────────────────────────────────────────────────
draw_figure(
    sorted_items,
    value_key="avg_distance",
    filename_prefix="item_clarity_distance",
    xlabel="Average Cosine Distance",
    title="Item Clarity: Distance by Category",
)

# ── Figure 2: Frequency (skip nulls) ──────────────────────────────────
draw_figure(
    sorted_items,
    value_key="corpus_frequency",
    filename_prefix="item_clarity_frequency",
    xlabel="Corpus Log Frequency (Zipf)",
    title="Item Clarity: Frequency by Category",
    skip_null=True,
)

print("Done.")
