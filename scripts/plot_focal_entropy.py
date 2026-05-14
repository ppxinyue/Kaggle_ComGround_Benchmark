"""
Plot focal entropy analysis: entropy distributions + 2D item landscape.
Left panel: overlapping histograms of distance entropy and frequency entropy.
Right panel: 2D scatter of items colored by domain.
"""

import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D
import seaborn as sns
from pathlib import Path
from collections import Counter

# ── Load data ──────────────────────────────────────────────────────────────
data_path = Path(r"D:\ppXinyue\2026_Kaggle\data\benchmark2\item_quality.json")
with open(data_path, encoding="utf-8") as f:
    items = json.load(f)
print(f"Loaded {len(items)} items")

# ── Shannon entropy helper ─────────────────────────────────────────────────
def shannon_entropy(values):
    """H = -sum(p_i * log2(p_i)) where p_i = value_i / sum(values)."""
    values = np.array(values, dtype=float)
    if values.sum() <= 0:
        return np.nan
    p = values / values.sum()
    p = p[p > 0]  # avoid log(0)
    return -np.sum(p * np.log2(p))

# ── Compute entropy per item ───────────────────────────────────────────────
distance_entropies = []
frequency_entropies = []
domains = []
item_ids = []

for item in items:
    opts = item["options"]
    # Filter: skip items with null or missing frequencies
    freqs = [o.get("corpus_frequency") for o in opts]
    if any(f is None for f in freqs):
        continue
    dists = [o.get("avg_distance") for o in opts]
    if any(d is None for d in dists):
        continue

    d_ent = shannon_entropy(dists)
    f_ent = shannon_entropy(freqs)
    if np.isnan(d_ent) or np.isnan(f_ent):
        continue

    distance_entropies.append(d_ent)
    frequency_entropies.append(f_ent)
    domains.append(item["domain"])
    item_ids.append(item["item_id"])

distance_entropies = np.array(distance_entropies)
frequency_entropies = np.array(frequency_entropies)
domains = np.array(domains)
item_ids = np.array(item_ids)
n = len(distance_entropies)
print(f"Valid items with both entropies: {n}")
print(f"Unique domains: {len(np.unique(domains))}")

# ── Style setup ────────────────────────────────────────────────────────────
sns.set_style("whitegrid")
COLOR_DIST = "#7b3294"
COLOR_FREQ = "#008837"

# ── Create figure ──────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# ═══════════════════════════════════════════════════════════════════════════
# LEFT PANEL: Overlapping entropy histograms
# ═══════════════════════════════════════════════════════════════════════════
bins = np.linspace(0, 2.05, 42)  # 0 to just past 2.0
ax1.hist(distance_entropies, bins=bins, color=COLOR_DIST, alpha=0.6,
         label="Distance entropy", edgecolor="white", linewidth=0.5)
ax1.hist(frequency_entropies, bins=bins, color=COLOR_FREQ, alpha=0.6,
         label="Frequency entropy", edgecolor="white", linewidth=0.5)
# Max entropy line
ax1.axvline(x=2.0, color="gray", linestyle="--", linewidth=1.2, label="Max entropy (2.0 bits)")
ax1.set_xlabel("Shannon Entropy (bits)", fontsize=12)
ax1.set_ylabel("Number of Items", fontsize=12)
ax1.set_title("Entropy Distribution of Option Distributions", fontsize=13, fontweight="bold")
ax1.legend(fontsize=10, framealpha=0.9)
ax1.set_xlim(0, 2.1)

# ═══════════════════════════════════════════════════════════════════════════
# RIGHT PANEL: 2D item landscape colored by domain
# ═══════════════════════════════════════════════════════════════════════════

# Build domain → index mapping (sorted alphabetically for stability)
unique_domains = sorted(np.unique(domains))
domain_to_idx = {d: i for i, d in enumerate(unique_domains)}
n_domains = len(unique_domains)
print(f"Domains ({n_domains}): {unique_domains}")

# Use tab20 (20) + tab20b (20) = 40 distinct colors
tab20 = plt.cm.tab20(np.linspace(0, 1, 20))
tab20b = plt.cm.tab20b(np.linspace(0, 1, 20))
all_colors = np.vstack([tab20, tab20b])
# Cycle if needed
while len(all_colors) < n_domains:
    all_colors = np.vstack([all_colors, tab20])
domain_colors = {d: all_colors[i % len(all_colors)] for i, d in enumerate(unique_domains)}

point_colors = np.array([domain_colors[d] for d in domains])

# Median lines as quadrant dividers
med_d = np.median(distance_entropies)
med_f = np.median(frequency_entropies)

# Plot scatter
scatter = ax2.scatter(distance_entropies, frequency_entropies,
                      c=point_colors, s=40, alpha=0.7, edgecolors="white", linewidth=0.3)

# Quadrant dividers
ax2.axvline(x=med_d, color="gray", linestyle="--", linewidth=1.0, alpha=0.7)
ax2.axhline(y=med_f, color="gray", linestyle="--", linewidth=1.0, alpha=0.7)

# Quadrant labels
label_props = dict(fontsize=9, fontstyle="italic", alpha=0.6, ha="center", va="center",
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7, edgecolor="none"))
ax2.text(med_d / 2, med_f / 2, "Clear focal", **label_props)
ax2.text(med_d + (2.0 - med_d) / 2, med_f + (2.0 - med_f) / 2, "Ambiguous", **label_props)

ax2.set_xlabel("Distance Entropy (bits)", fontsize=12)
ax2.set_ylabel("Frequency Entropy (bits)", fontsize=12)
ax2.set_title("2D Item Landscape by Domain", fontsize=13, fontweight="bold")
ax2.set_xlim(0, 2.1)
ax2.set_ylim(0, 2.1)

# ── Annotate representative domains ────────────────────────────────────────
# Compute per-domain mean entropies
domain_stats = {}
for d in unique_domains:
    mask = domains == d
    domain_stats[d] = {
        "mean_d": distance_entropies[mask].mean(),
        "mean_f": frequency_entropies[mask].mean(),
        "count": mask.sum(),
        "d_ent_all": distance_entropies[mask],
        "f_ent_all": frequency_entropies[mask],
    }

# "Clearest" = lowest combined (mean_d + mean_f) / 2
# "Most ambiguous" = highest combined
combined = {d: (s["mean_d"] + s["mean_f"]) / 2 for d, s in domain_stats.items()}
sorted_domains = sorted(combined.keys(), key=lambda d: combined[d])

top5_clear = sorted_domains[:5]
top5_ambig = sorted_domains[-5:]

annotate_domains = top5_clear + top5_ambig
print(f"Top-5 clearest: {top5_clear}")
print(f"Top-5 most ambiguous: {top5_ambig}")

# For annotation, pick the most central item in each domain
for d in annotate_domains:
    s = domain_stats[d]
    # Pick the item closest to domain centroid
    cx, cy = s["mean_d"], s["mean_f"]
    dists_to_center = np.sqrt((s["d_ent_all"] - cx)**2 + (s["f_ent_all"] - cy)**2)
    best_idx = np.argmin(dists_to_center)
    # Get actual index in the full arrays
    domain_mask = domains == d
    domain_indices = np.where(domain_mask)[0]
    actual_idx = domain_indices[best_idx]

    x = distance_entropies[actual_idx]
    y = frequency_entropies[actual_idx]

    # Offset to reduce overlap
    offset_x = 15 if x < med_d else -15
    offset_y = 15 if y < med_f else -15

    ax2.annotate(
        d,
        xy=(x, y),
        xytext=(offset_x, offset_y),
        textcoords="offset points",
        fontsize=7.5,
        fontweight="bold",
        alpha=0.85,
        arrowprops=dict(arrowstyle="-", color="gray", alpha=0.5, lw=0.8),
        color=domain_colors[d],
    )

# ── Build a compact legend with colored patches ────────────────────────────
# Show all 31 domains in a compact multi-column legend outside the plot
legend_elements = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor=domain_colors[d],
           markersize=6, label=d, linestyle="None")
    for d in unique_domains
]
legend = ax2.legend(
    handles=legend_elements,
    loc="upper left",
    bbox_to_anchor=(1.02, 1.0),
    fontsize=6.5,
    ncol=2,
    title="Domain",
    title_fontsize=8,
    framealpha=0.9,
    borderpad=0.5,
    handletextpad=0.3,
    columnspacing=0.8,
)

# ── Final layout ───────────────────────────────────────────────────────────
plt.tight_layout()
# Make room for the legend on the right
fig.subplots_adjust(right=0.72)

# ── Save ───────────────────────────────────────────────────────────────────
out_dir = Path(r"D:\ppXinyue\2026_Kaggle\writings\figures")
out_dir.mkdir(parents=True, exist_ok=True)

for ext in ("png", "pdf"):
    out_path = out_dir / f"focal_entropy_analysis.{ext}"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    print(f"Saved: {out_path}")

plt.close(fig)
print("Done.")
