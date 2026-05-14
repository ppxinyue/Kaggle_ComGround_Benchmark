"""
Publication-quality figure: Focal Entropy Analysis
Three panels:
  (a) Distance entropy histogram (purple) with horizontal arrow annotations
  (b) Frequency entropy histogram (green) with horizontal arrow annotations
  (c) 2D item landscape colored by mechanism category
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib
matplotlib.use('Agg')
import seaborn as sns

# ── Colors (same as focal_gap_analysis) ──────────────────────────────────────
CLR_DIST  = "#7b3294"   # dark purple – distance metrics
CLR_FREQ  = "#008837"   # dark green  – frequency metrics
CLR_CLEAR = "#2ca02c"   # green  for "clear focal point"
CLR_AMBIG = "#d62728"   # red    for "ambiguous"

# ── Mechanism category mapping ──────────────────────────────────────────────
MECHANISM_MAP = {
    "Colors": "Perception",
    "Shapes": "Perception",
    "Spatial Directions": "Perception",
    "Extremes": "Perception",
    "Numbers": "Symbolism",
    "Time Anchors": "Symbolism",
    "Emotions": "Symbolism",
    "Animals": "Biology",
    "Plants": "Biology",
    "Fruits": "Biology",
    "Body Parts": "Biology",
    "Senses": "Biology",
    "Tools": "Artifacts",
    "Clothing": "Artifacts",
    "Vehicles": "Artifacts",
    "Furniture": "Artifacts",
    "Rooms": "Places",
    "Public Places": "Places",
    "Institutions": "Places",
    "Geographic Entities": "Places",
    "Family Roles": "Norms",
    "Occupations": "Norms",
    "Social Norms": "Norms",
    "Holidays": "Culture",
    "Food": "Culture",
    "Drinks": "Culture",
    "Famous People": "Culture",
    "Media": "Culture",
    "Brands": "Culture",
    "Digital Platforms": "Digital",
    "Internet Culture": "Digital",
}

MECH_ORDER = ["Perception", "Symbolism", "Biology", "Artifacts",
              "Places", "Norms", "Culture", "Digital"]


def shannon_entropy(values):
    """Compute Shannon entropy from a list of positive values."""
    arr = np.array(values, dtype=float)
    arr = arr[arr > 0]
    if len(arr) == 0:
        return np.nan
    p = arr / arr.sum()
    return -np.sum(p * np.log2(p))


def main():
    # ── Load data ───────────────────────────────────────────────────────────
    with open("data/benchmark2/item_quality.json", encoding="utf-8") as f:
        items = json.load(f)

    # ── Compute entropy per item ────────────────────────────────────────────
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

    # ── Plot setup ──────────────────────────────────────────────────────────
    sns.set_style("white")
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "legend.fontsize": 9,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
    })

    fig = plt.figure(figsize=(18, 5))
    gs = gridspec.GridSpec(1, 3, width_ratios=[1, 1, 1.3], wspace=0.32)

    # ═══════════════════════════════════════════════════════════════════════
    # PANEL (a): Distance entropy histogram (purple)
    # ═══════════════════════════════════════════════════════════════════════
    ax_a = fig.add_subplot(gs[0, 0])

    d_bins = np.linspace(h_dists.min() - 0.002, max_entropy + 0.002, 35)
    ax_a.hist(h_dists, bins=d_bins, color=CLR_DIST, alpha=0.7,
              edgecolor="white", linewidth=0.5)

    dist_med = np.median(h_dists)
    ax_a.axvline(dist_med, color=CLR_DIST, ls="--", lw=1.5, alpha=0.9)

    ax_a.set_xlabel("Distance Entropy (bits)")
    ax_a.set_ylabel("Count")
    ax_a.set_title("(a) Distance Entropy Distribution", fontweight="bold", pad=10)
    ax_a.grid(False)

    # Horizontal arrow annotations
    fig.canvas.draw()
    a_xlim = ax_a.get_xlim()
    a_ylim = ax_a.get_ylim()
    a_y = a_ylim[1] * 0.85

    ax_a.annotate(
        "Ambiguous",
        xy=(a_xlim[1] - 0.03 * (a_xlim[1] - a_xlim[0]), a_y),
        xytext=(a_xlim[1] - 0.22 * (a_xlim[1] - a_xlim[0]), a_y),
        fontsize=9, fontweight="bold", color=CLR_AMBIG,
        ha="center", va="center",
        arrowprops=dict(arrowstyle="->", color=CLR_AMBIG, lw=1.5),
    )

    ax_a.annotate(
        "Clear focal point",
        xy=(a_xlim[0] + 0.03 * (a_xlim[1] - a_xlim[0]), a_y),
        xytext=(a_xlim[0] + 0.22 * (a_xlim[1] - a_xlim[0]), a_y),
        fontsize=9, fontweight="bold", color=CLR_CLEAR,
        ha="center", va="center",
        arrowprops=dict(arrowstyle="->", color=CLR_CLEAR, lw=1.5),
    )

    # Max entropy label
    ax_a.axvline(max_entropy, color="black", linestyle="--", linewidth=1.0, alpha=0.5)
    ax_a.text(max_entropy - 0.001, a_ylim[1] * 0.95,
              f"Max={max_entropy:.1f}", fontsize=8, va="top", ha="right")

    # ═══════════════════════════════════════════════════════════════════════
    # PANEL (b): Frequency entropy histogram (green)
    # ═══════════════════════════════════════════════════════════════════════
    ax_b = fig.add_subplot(gs[0, 1])

    f_bins = np.linspace(valid_freq.min() - 0.01, max_entropy + 0.005, 35)
    ax_b.hist(valid_freq, bins=f_bins, color=CLR_FREQ, alpha=0.7,
              edgecolor="white", linewidth=0.5)

    freq_med = np.median(valid_freq)
    ax_b.axvline(freq_med, color=CLR_FREQ, ls="--", lw=1.5, alpha=0.9)

    ax_b.set_xlabel("Frequency Entropy (bits)")
    ax_b.set_ylabel("Count")
    ax_b.set_title("(b) Frequency Entropy Distribution", fontweight="bold", pad=10)
    ax_b.grid(False)

    # Horizontal arrow annotations
    fig.canvas.draw()
    b_xlim = ax_b.get_xlim()
    b_ylim = ax_b.get_ylim()
    b_y = b_ylim[1] * 0.85

    ax_b.annotate(
        "Ambiguous",
        xy=(b_xlim[1] - 0.03 * (b_xlim[1] - b_xlim[0]), b_y),
        xytext=(b_xlim[1] - 0.22 * (b_xlim[1] - b_xlim[0]), b_y),
        fontsize=9, fontweight="bold", color=CLR_AMBIG,
        ha="center", va="center",
        arrowprops=dict(arrowstyle="->", color=CLR_AMBIG, lw=1.5),
    )

    ax_b.annotate(
        "Clear focal point",
        xy=(b_xlim[0] + 0.03 * (b_xlim[1] - b_xlim[0]), b_y),
        xytext=(b_xlim[0] + 0.22 * (b_xlim[1] - b_xlim[0]), b_y),
        fontsize=9, fontweight="bold", color=CLR_CLEAR,
        ha="center", va="center",
        arrowprops=dict(arrowstyle="->", color=CLR_CLEAR, lw=1.5),
    )

    # Max entropy label
    ax_b.axvline(max_entropy, color="black", linestyle="--", linewidth=1.0, alpha=0.5)
    ax_b.text(max_entropy - 0.001, b_ylim[1] * 0.95,
              f"Max={max_entropy:.1f}", fontsize=8, va="top", ha="right")

    # ═══════════════════════════════════════════════════════════════════════
    # PANEL (c): 2D Item Landscape
    # ═══════════════════════════════════════════════════════════════════════
    ax_c = fig.add_subplot(gs[0, 2])

    cmap = sns.color_palette("Set2", n_colors=len(MECH_ORDER))
    mech_colors = {m: cmap[i] for i, m in enumerate(MECH_ORDER)}

    for mech in MECH_ORDER:
        mask = np.array([r["mechanism"] == mech for r in records])
        if not mask.any():
            continue
        x = h_dists[mask]
        y = h_freqs[mask]
        valid = ~np.isnan(y)
        ax_c.scatter(x[valid], y[valid], alpha=0.6, s=30,
                    color=mech_colors[mech], label=mech, edgecolors="none")

    dist_p25 = np.percentile(h_dists, 25)
    freq_p25 = np.nanpercentile(h_freqs, 25)

    ax_c.axhline(freq_p25, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
    ax_c.axvline(dist_p25, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
    ax_c.grid(False)

    # Quadrant labels — horizontal arrows
    xlim = ax_c.get_xlim()
    ylim = ax_c.get_ylim()
    c_ymid_lo = ylim[0] + 0.12 * (ylim[1] - ylim[0])
    c_ymid_hi = ylim[1] - 0.12 * (ylim[1] - ylim[0])

    ax_c.annotate(
        "Clear focal point",
        xy=(xlim[0] + 0.05 * (xlim[1] - xlim[0]), c_ymid_lo),
        xytext=(xlim[0] + 0.22 * (xlim[1] - xlim[0]), c_ymid_lo),
        fontsize=9, fontweight="bold", color=CLR_CLEAR,
        ha="center", va="center",
        arrowprops=dict(arrowstyle="->", color=CLR_CLEAR, lw=1.5),
    )

    ax_c.annotate(
        "Ambiguous",
        xy=(xlim[1] - 0.05 * (xlim[1] - xlim[0]), c_ymid_hi),
        xytext=(xlim[1] - 0.22 * (xlim[1] - xlim[0]), c_ymid_hi),
        fontsize=9, fontweight="bold", color=CLR_AMBIG,
        ha="center", va="center",
        arrowprops=dict(arrowstyle="->", color=CLR_AMBIG, lw=1.5),
    )

    ax_c.text(xlim[1] - 0.03 * (xlim[1] - xlim[0]), ylim[0] + 0.06 * (ylim[1] - ylim[0]),
             "Focal by\ndistance", fontsize=8,
             ha="right", va="bottom", style="italic", color="#888888")

    ax_c.text(xlim[0] + 0.03 * (xlim[1] - xlim[0]), ylim[1] - 0.06 * (ylim[1] - ylim[0]),
             "Focal by\nfrequency", fontsize=8,
             ha="left", va="top", style="italic", color="#888888")

    ax_c.set_xlabel("Distance Entropy (bits)")
    ax_c.set_ylabel("Frequency Entropy (bits)")
    ax_c.set_title("(c) 2D Item Landscape", fontweight="bold", pad=10)
    ax_c.legend(frameon=True, fancybox=True, shadow=False, loc="center left",
               title="Mechanism", title_fontsize=9, ncol=1,
               bbox_to_anchor=(0.0, 0.45))

    # ── Save ────────────────────────────────────────────────────────────────
    fig.tight_layout()
    out_dir = "writings/figures"
    fig.savefig(f"{out_dir}/focal_entropy_analysis.png", dpi=300, bbox_inches="tight")
    fig.savefig(f"{out_dir}/focal_entropy_analysis.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_dir}/focal_entropy_analysis.png and .pdf")

    # ── Summary stats ───────────────────────────────────────────────────────
    print(f"\nDistance entropy: mean={h_dists.mean():.4f}, std={h_dists.std():.4f}")
    print(f"Frequency entropy: mean={np.nanmean(h_freqs):.4f}, std={np.nanstd(h_freqs):.4f}")
    print(f"Items with valid freq: {np.sum(~np.isnan(h_freqs))} / {len(records)}")
    print(f"Quadrant dividers (P25): dist={dist_p25:.4f}, freq={freq_p25:.4f}")


if __name__ == "__main__":
    main()
