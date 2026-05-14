"""
Publication-quality figure: Focal Entropy Analysis (3 subplots)
(a) Distance entropy distribution  (higher entropy = more ambiguous)
(b) Frequency entropy distribution (higher entropy = more ambiguous)
(c) 2D item landscape colored by mechanism category
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
BASE = Path(r"D:\ppXinyue\2026_Kaggle")
DATA = BASE / "data" / "benchmark2" / "item_quality.json"
OUT  = BASE / "writings" / "figures"

# ── Mechanism category mapping ─────────────────────────────────────────
MECHANISM_MAP = {
    "Colors": "Perception", "Shapes": "Perception",
    "Spatial Directions": "Perception", "Extremes": "Perception",
    "Numbers": "Symbolism", "Time Anchors": "Symbolism", "Emotions": "Symbolism",
    "Animals": "Biology", "Plants": "Biology", "Fruits": "Biology",
    "Body Parts": "Biology", "Senses": "Biology",
    "Tools": "Artifacts", "Clothing": "Artifacts",
    "Vehicles": "Artifacts", "Furniture": "Artifacts",
    "Rooms": "Places", "Public Places": "Places",
    "Institutions": "Places", "Geographic Entities": "Places",
    "Family Roles": "Norms", "Occupations": "Norms", "Social Norms": "Norms",
    "Holidays": "Culture", "Food": "Culture", "Drinks": "Culture",
    "Famous People": "Culture", "Media": "Culture", "Brands": "Culture",
    "Digital Platforms": "Digital", "Internet Culture": "Digital",
}

MECH_ORDER = ["Perception", "Symbolism", "Biology", "Artifacts",
              "Places", "Norms", "Culture", "Digital"]

MECH_COLORS = {
    "Perception": "#e41a1c",
    "Symbolism": "#377eb8",
    "Biology":  "#4daf4a",
    "Artifacts": "#984ea3",
    "Places":   "#ff7f00",
    "Norms":    "#a65628",
    "Culture":  "#f781bf",
    "Digital":  "#999999",
}

# Consistent metric colors
COLOR_DIST = "#7b3294"       # purple for distance
COLOR_FREQ = "#008837"       # green for frequency
COLOR_CLEAR = "#2ca02c"      # green for "clear focal" annotation
COLOR_AMBIG = "#d62728"      # red for "ambiguous" annotation


def shannon_entropy(values):
    arr = np.array(values, dtype=float)
    arr = arr[arr > 0]
    if len(arr) == 0:
        return np.nan
    p = arr / arr.sum()
    return -np.sum(p * np.log2(p))


def main():
    # ── Load data ────────────────────────────────────────────────────────
    with open(DATA, encoding="utf-8") as f:
        items = json.load(f)

    # ── Compute entropy per item ─────────────────────────────────────────
    records = []
    for item in items:
        opts = item["options"]
        domain = item["domain"]
        mechanism = MECHANISM_MAP.get(domain, "Other")

        avg_dists = [o["avg_distance"] for o in opts]
        h_dist = shannon_entropy(avg_dists)

        freqs = [o.get("corpus_frequency") for o in opts]
        if any(f is None for f in freqs):
            h_freq = np.nan
        else:
            h_freq = shannon_entropy(freqs)

        records.append({
            "domain": domain,
            "mechanism": mechanism,
            "h_dist": h_dist,
            "h_freq": h_freq,
        })

    h_dists = np.array([r["h_dist"] for r in records])
    h_freqs = np.array([r["h_freq"] for r in records])
    valid_freq = h_freqs[~np.isnan(h_freqs)]

    max_entropy = np.log2(4)  # 2.0
    dist_median = np.median(h_dists)
    freq_median = np.median(valid_freq)

    # ── Plot setup ───────────────────────────────────────────────────────
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 11,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "legend.fontsize": 8,
    })

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # ═════════════════════════════════════════════════════════════════════
    # (a) Distance entropy distribution
    # Higher entropy → options are equally distant → ambiguous
    # Lower entropy  → one option stands out     → clear focal point
    # ═════════════════════════════════════════════════════════════════════
    ax1 = axes[0]
    h_min = h_dists.min()
    bins_d = np.linspace(h_min - 0.02, max_entropy + 0.01, 35)

    # Histogram
    n1, _, _ = ax1.hist(h_dists, bins=bins_d, color=COLOR_DIST, alpha=0.75,
                         edgecolor="white", linewidth=0.5)
    y1_max = n1.max() * 1.05
    y1_peak = n1.max()

    # Max entropy reference line (no label)
    ax1.axvline(max_entropy, color="black", linestyle="--", linewidth=1.2)

    # Arrow annotations
    ax1.annotate("Clear focal point",
                 xy=(h_min + 0.08, y1_peak * 0.45),
                 xytext=(h_min - 0.02, y1_peak * 0.85),
                 arrowprops=dict(arrowstyle="->", color=COLOR_CLEAR, lw=1.5),
                 fontsize=9, color=COLOR_CLEAR, fontweight="bold")
    ax1.annotate("Ambiguous",
                 xy=(max_entropy - 0.05, y1_peak * 0.45),
                 xytext=(max_entropy + 0.02, y1_peak * 0.85),
                 arrowprops=dict(arrowstyle="->", color=COLOR_AMBIG, lw=1.5),
                 fontsize=9, color=COLOR_AMBIG, fontweight="bold")

    ax1.set_xlabel("Distance Entropy (bits)")
    ax1.set_ylabel("Number of Items")
    ax1.set_title("(a) Distance Entropy", fontweight="bold")
    ax1.set_ylim(0, y1_max)

    # ═════════════════════════════════════════════════════════════════════
    # (b) Frequency entropy distribution
    # Same logic: higher entropy → ambiguous, lower → clear focal
    # ═════════════════════════════════════════════════════════════════════
    ax2 = axes[1]
    f_min = valid_freq.min()
    bins_f = np.linspace(f_min - 0.02, max_entropy + 0.01, 35)

    # Histogram
    n2, _, _ = ax2.hist(valid_freq, bins=bins_f, color=COLOR_FREQ, alpha=0.75,
                         edgecolor="white", linewidth=0.5)
    y2_max = n2.max() * 1.05
    y2_peak = n2.max()

    # Max entropy reference line (no label)
    ax2.axvline(max_entropy, color="black", linestyle="--", linewidth=1.2)

    # Arrow annotations
    ax2.annotate("Clear focal point",
                 xy=(f_min + 0.08, y2_peak * 0.45),
                 xytext=(f_min - 0.02, y2_peak * 0.85),
                 arrowprops=dict(arrowstyle="->", color=COLOR_CLEAR, lw=1.5),
                 fontsize=9, color=COLOR_CLEAR, fontweight="bold")
    ax2.annotate("Ambiguous",
                 xy=(max_entropy - 0.05, y2_peak * 0.45),
                 xytext=(max_entropy + 0.02, y2_peak * 0.85),
                 arrowprops=dict(arrowstyle="->", color=COLOR_AMBIG, lw=1.5),
                 fontsize=9, color=COLOR_AMBIG, fontweight="bold")

    ax2.set_xlabel("Frequency Entropy (bits)")
    ax2.set_ylabel("Number of Items")
    ax2.set_title("(b) Frequency Entropy", fontweight="bold")
    ax2.set_ylim(0, y2_max)

    # ═════════════════════════════════════════════════════════════════════
    # (c) 2D Item Landscape by mechanism category
    # ═════════════════════════════════════════════════════════════════════
    ax3 = axes[2]

    for mech in MECH_ORDER:
        mask = np.array([r["mechanism"] == mech for r in records])
        if not mask.any():
            continue
        x = h_dists[mask]
        y = h_freqs[mask]
        valid = ~np.isnan(y)
        ax3.scatter(x[valid], y[valid], alpha=0.55, s=25,
                    color=MECH_COLORS[mech], label=mech, edgecolors="none")

    # Quadrant dividers using medians
    ax3.axhline(freq_median, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)
    ax3.axvline(dist_median, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)

    # Quadrant labels — same style as (a)(b)
    ax3.text(0.05, 0.05, "Clear focal\npoint",
             transform=ax3.transAxes, fontsize=9, ha="left", va="bottom",
             color=COLOR_CLEAR, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9, edgecolor=COLOR_CLEAR))
    ax3.text(0.95, 0.95, "Ambiguous",
             transform=ax3.transAxes, fontsize=9, ha="right", va="top",
             color=COLOR_AMBIG, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9, edgecolor=COLOR_AMBIG))
    ax3.text(0.95, 0.05, "Focal by\ndistance only",
             transform=ax3.transAxes, fontsize=8, ha="right", va="bottom",
             color="#666666", fontstyle="italic")
    ax3.text(0.05, 0.95, "Focal by\nfrequency only",
             transform=ax3.transAxes, fontsize=8, ha="left", va="top",
             color="#666666", fontstyle="italic")

    ax3.set_xlabel("Distance Entropy (bits)")
    ax3.set_ylabel("Frequency Entropy (bits)")
    ax3.set_title("(c) 2D Item Landscape", fontweight="bold")
    ax3.legend(frameon=True, fancybox=True, shadow=False, loc="center left",
               title="Category", title_fontsize=8, ncol=1,
               bbox_to_anchor=(0.0, 0.45), fontsize=7)

    # ── Save ─────────────────────────────────────────────────────────────
    fig.tight_layout(w_pad=2.5)
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"focal_entropy_analysis.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved: {OUT}/focal_entropy_analysis.png and .pdf")
    print(f"  Distance entropy: mean={h_dists.mean():.4f}, median={dist_median:.4f}")
    print(f"  Frequency entropy: mean={np.nanmean(h_freqs):.4f}, median={freq_median:.4f}")
    print(f"  Items with valid freq: {len(valid_freq)} / {len(records)}")


if __name__ == "__main__":
    main()
