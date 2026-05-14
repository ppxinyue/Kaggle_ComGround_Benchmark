"""
Focal Gap Analysis Figure
─────────────────────────
Three side-by-side panels:
  (a) Distance gap histogram (purple) with arrow annotations
  (b) Frequency gap histogram (green) with arrow annotations
  (c) Per-domain mean gap bars (dual x-axes: distance purple + frequency green)
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from collections import defaultdict
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "benchmark2" / "item_quality.json"
OUT_DIR = ROOT / "writings" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Colors ─────────────────────────────────────────────────────────
CLR_DIST  = "#7b3294"   # dark purple – distance metrics
CLR_FREQ  = "#008837"   # dark green  – frequency metrics
CLR_CLEAR = "#2ca02c"   # green for "clear focal point" annotations
CLR_AMBIG = "#d62728"   # red   for "ambiguous" annotations

# ── Load data ──────────────────────────────────────────────────────
with open(DATA, encoding="utf-8") as f:
    items = json.load(f)

# ── Compute per-item gaps ──────────────────────────────────────────
distance_gaps = []
frequency_gaps = []
domain_dist_gaps = defaultdict(list)
domain_freq_gaps = defaultdict(list)

for item in items:
    opts = item["options"]

    # Distance gap: max avg_distance minus 2nd max
    dists = sorted([o["avg_distance"] for o in opts], reverse=True)
    d_gap = dists[0] - dists[1]
    distance_gaps.append(d_gap)
    domain_dist_gaps[item["domain"]].append(d_gap)

    # Frequency gap: max corpus_frequency minus 2nd max (skip nulls)
    freqs = sorted(
        [o["corpus_frequency"] for o in opts
         if o.get("corpus_frequency") is not None],
        reverse=True,
    )
    if len(freqs) >= 2:
        f_gap = freqs[0] - freqs[1]
        frequency_gaps.append(f_gap)
        domain_freq_gaps[item["domain"]].append(f_gap)

distance_gaps = np.array(distance_gaps)
frequency_gaps = np.array(frequency_gaps)

# Per-domain means (domains sorted alphabetically)
domains = sorted(domain_dist_gaps.keys())
mean_dist = np.array([np.mean(domain_dist_gaps[d]) for d in domains])
mean_freq = np.array([
    np.mean(domain_freq_gaps[d]) if d in domain_freq_gaps and domain_freq_gaps[d]
    else 0.0
    for d in domains
])

# ── Style ──────────────────────────────────────────────────────────
sns.set_style("white")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
})

# ── Figure layout: 3 panels side by side ──────────────────────────
fig = plt.figure(figsize=(18, 5))
gs = gridspec.GridSpec(
    1, 3,
    width_ratios=[1, 1, 1.3],
    wspace=0.32,
)

# ═══════════════════════════════════════════════════════════════════
# PANEL (a): Distance gap histogram (purple)
# ═══════════════════════════════════════════════════════════════════
ax_a = fig.add_subplot(gs[0, 0])

d_bins = np.linspace(0, distance_gaps.max() * 1.05, 30)
dist_med = np.median(distance_gaps)
dist_mean = distance_gaps.mean()

# Histogram bars
ax_a.hist(distance_gaps, bins=d_bins, color=CLR_DIST, alpha=0.7,
          edgecolor="white", linewidth=0.5)

# Median line
ax_a.axvline(dist_med, color=CLR_DIST, ls="--", lw=1.5, alpha=0.9)

# Arrow annotations (no legend, no shading, no text boxes)
# Get axis limits in data coordinates for positioning
d_xmax = distance_gaps.max() * 1.05
d_ymax = ax_a.get_ylim()[1] if ax_a.get_ylim()[1] > 0 else 100

# We need to draw histogram first to get proper ylim, then set arrows
# Re-draw to get proper limits
fig.canvas.draw()
d_ymax = ax_a.get_ylim()[1]

# Arrow pointing to LEFT side (small gap) — "Ambiguous"
ax_a.annotate(
    "Ambiguous",
    xy=(d_xmax * 0.05, d_ymax * 0.85),
    xytext=(d_xmax * 0.25, d_ymax * 0.85),
    fontsize=9, fontweight="bold", color=CLR_AMBIG,
    ha="center", va="center",
    arrowprops=dict(arrowstyle="->", color=CLR_AMBIG, lw=1.5),
)

# Arrow pointing to RIGHT side (large gap) — "Clear focal point"
ax_a.annotate(
    "Clear focal point",
    xy=(d_xmax * 0.85, d_ymax * 0.85),
    xytext=(d_xmax * 0.65, d_ymax * 0.85),
    fontsize=9, fontweight="bold", color=CLR_CLEAR,
    ha="center", va="center",
    arrowprops=dict(arrowstyle="->", color=CLR_CLEAR, lw=1.5),
)

ax_a.set_xlabel("Distance Gap (top1 \u2212 top2)")
ax_a.set_ylabel("Count")
ax_a.set_title("(a) Distance Gap Distribution", fontweight="bold", pad=10)
ax_a.grid(False)

# ═══════════════════════════════════════════════════════════════════
# PANEL (b): Frequency gap histogram (green)
# ═══════════════════════════════════════════════════════════════════
ax_b = fig.add_subplot(gs[0, 1])

f_bins = np.linspace(0, frequency_gaps.max() * 1.05, 30)
freq_med = np.median(frequency_gaps)
freq_mean = frequency_gaps.mean()

# Histogram bars
ax_b.hist(frequency_gaps, bins=f_bins, color=CLR_FREQ, alpha=0.7,
          edgecolor="white", linewidth=0.5)

# Median line
ax_b.axvline(freq_med, color=CLR_FREQ, ls="--", lw=1.5, alpha=0.9)

# Draw to get proper limits
fig.canvas.draw()
f_xmax = frequency_gaps.max() * 1.05
f_ymax = ax_b.get_ylim()[1]

# Arrow pointing to LEFT side (small gap) — "Ambiguous"
ax_b.annotate(
    "Ambiguous",
    xy=(f_xmax * 0.05, f_ymax * 0.85),
    xytext=(f_xmax * 0.25, f_ymax * 0.85),
    fontsize=9, fontweight="bold", color=CLR_AMBIG,
    ha="center", va="center",
    arrowprops=dict(arrowstyle="->", color=CLR_AMBIG, lw=1.5),
)

# Arrow pointing to RIGHT side (large gap) — "Clear focal point"
ax_b.annotate(
    "Clear focal point",
    xy=(f_xmax * 0.85, f_ymax * 0.85),
    xytext=(f_xmax * 0.65, f_ymax * 0.85),
    fontsize=9, fontweight="bold", color=CLR_CLEAR,
    ha="center", va="center",
    arrowprops=dict(arrowstyle="->", color=CLR_CLEAR, lw=1.5),
)

ax_b.set_xlabel("Frequency Gap (top1 \u2212 top2)")
ax_b.set_ylabel("Count")
ax_b.set_title("(b) Frequency Gap Distribution", fontweight="bold", pad=10)
ax_b.grid(False)

# ═══════════════════════════════════════════════════════════════════
# PANEL (c): Per-domain mean gap (dual x-axes)
# ═══════════════════════════════════════════════════════════════════
ax_c = fig.add_subplot(gs[0, 2])

y_pos = np.arange(len(domains))
bar_h = 0.35

# Distance gap uses the bottom x-axis (purple bars, offset up)
ax_c.barh(y_pos + bar_h / 2, mean_dist, height=bar_h, color=CLR_DIST, alpha=0.85,
          edgecolor="white", linewidth=0.4, label="Distance gap")

ax_c.set_yticks(y_pos)
ax_c.set_yticklabels(domains, fontsize=7.5)
ax_c.set_xlabel("Mean Distance Gap (top1 \u2212 top2)", color=CLR_DIST)
ax_c.tick_params(axis="x", colors=CLR_DIST)
ax_c.set_xlim(0, mean_dist.max() * 1.25)

# Frequency gap uses a twin x-axis on top (green bars, offset down)
ax_c_twin = ax_c.twiny()
ax_c_twin.barh(y_pos - bar_h / 2, mean_freq, height=bar_h, color=CLR_FREQ, alpha=0.85,
               edgecolor="white", linewidth=0.4, label="Frequency gap")

ax_c_twin.set_xlabel("Mean Frequency Gap (top1 \u2212 top2)", color=CLR_FREQ)
ax_c_twin.tick_params(axis="x", colors=CLR_FREQ)
ax_c_twin.set_xlim(0, mean_freq.max() * 1.25)

ax_c.set_title("(c) Per-Domain Mean Gap", fontweight="bold", pad=25)
ax_c.grid(False)

# Combined legend from both axes
lines_c, labels_c = ax_c.get_legend_handles_labels()
lines_t, labels_t = ax_c_twin.get_legend_handles_labels()
ax_c.legend(lines_c + lines_t, labels_c + labels_t,
            loc="lower right", fontsize=8, framealpha=0.9)

# Arrow annotations for (c) — on the bottom x-axis (distance scale)
c_xmax = mean_dist.max() * 1.25

# Arrow pointing to LEFT (small gap) — "Ambiguous"
ax_c.annotate(
    "Ambiguous",
    xy=(c_xmax * 0.03, -1.8),
    xytext=(c_xmax * 0.25, -1.8),
    fontsize=9, fontweight="bold", color=CLR_AMBIG,
    ha="center", va="center",
    arrowprops=dict(arrowstyle="->", color=CLR_AMBIG, lw=1.5),
)

# Arrow pointing to RIGHT (large gap) — "Clear focal point"
ax_c.annotate(
    "Clear focal point",
    xy=(c_xmax * 0.92, -1.8),
    xytext=(c_xmax * 0.70, -1.8),
    fontsize=9, fontweight="bold", color=CLR_CLEAR,
    ha="center", va="center",
    arrowprops=dict(arrowstyle="->", color=CLR_CLEAR, lw=1.5),
)

# Clip the arrows to be visible
ax_c.set_clip_on(False)

# ── Save ──────────────────────────────────────────────────────────
fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(OUT_DIR / f"focal_gap_analysis.{ext}", dpi=300, bbox_inches="tight")
plt.close(fig)

print(f"Saved focal_gap_analysis.png/.pdf  ({len(items)} items, {len(domains)} domains)")
print(f"  distance_gap  mean={dist_mean:.4f}  median={dist_med:.4f}  range=[{distance_gaps.min():.4f}, {distance_gaps.max():.4f}]")
print(f"  frequency_gap mean={freq_mean:.4f}  median={freq_med:.4f}  range=[{frequency_gaps.min():.4f}, {frequency_gaps.max():.4f}]")
