#!/usr/bin/env python3
"""
Item Strip Analysis Figure — Stacked Bar Chart
===============================================
For each of the 410 items:
  - Sort 4 options by avg_distance ascending
  - Bottom 3 (light purple) stacked, top 1 (dark purple) on top
  - Items sorted left-to-right by focal gap (descending = clearest focal on left)
"""

import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# ── Config ──────────────────────────────────────────────────
ROOT = Path(r"D:\ppXinyue\2026_Kaggle")
DATA = ROOT / "data" / "benchmark2" / "item_quality.json"
OUT_DIR = ROOT / "writings" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Load data ───────────────────────────────────────────────
with open(DATA, "r", encoding="utf-8") as f:
    items = json.load(f)

print(f"Loaded {len(items)} items")

# ── Compute per-item metrics ────────────────────────────────
records = []
for it in items:
    dists = sorted([o["avg_distance"] for o in it["options"]])
    # dists[0] <= dists[1] <= dists[2] <= dists[3]
    gap = dists[3] - dists[2]  # how much the top option stands out
    sum_lower3 = dists[0] + dists[1] + dists[2]
    max_dist = dists[3]
    records.append({
        "gap": gap,
        "sum_lower3": sum_lower3,
        "max_dist": max_dist,
        "total": sum_lower3 + max_dist,
    })

# Sort by gap descending (clearest focal on the left)
records.sort(key=lambda r: r["gap"], reverse=True)

sum_lower3 = np.array([r["sum_lower3"] for r in records])
max_dists = np.array([r["max_dist"] for r in records])

print(f"Gap range: {records[0]['gap']:.4f} (clearest) to {records[-1]['gap']:.4f} (most ambiguous)")

# ── Plot ────────────────────────────────────────────────────
sns.set_style("whitegrid")

DARK_PURPLE = "#7b3294"
LIGHT_PURPLE = "#c2a5cf"

fig, ax = plt.subplots(figsize=(10, 7))

x = np.arange(len(records))
bar_width = 1.0

# Bottom segment: 3 lower-distance options (light purple)
ax.bar(x, sum_lower3, width=bar_width, color=LIGHT_PURPLE,
       edgecolor="none", linewidth=0, label="3 lower-distance options")

# Top segment: highest-distance option (dark purple), stacked
ax.bar(x, max_dists, width=bar_width, bottom=sum_lower3,
       color=DARK_PURPLE, edgecolor="none", linewidth=0,
       label="Most distant option (focal candidate)")

# ── Axes & Labels ──────────────────────────────────────────
ax.set_ylabel("Sum of Average Distances", fontsize=13)
ax.set_xlabel("Items (sorted by focal gap)", fontsize=13)

# Remove individual x-tick labels (too many items)
ax.set_xticks([])
ax.tick_params(axis="x", length=0)

# ── Annotations ─────────────────────────────────────────────
ax.annotate("Clear focal point \u2192",
            xy=(0.02, 0.95), xycoords="axes fraction",
            fontsize=12, fontstyle="italic", color=DARK_PURPLE,
            ha="left", va="top")
ax.annotate("\u2190 Ambiguous",
            xy=(0.98, 0.95), xycoords="axes fraction",
            fontsize=12, fontstyle="italic", color="#666666",
            ha="right", va="top")

# ── Legend ──────────────────────────────────────────────────
ax.legend(loc="upper right", fontsize=10, framealpha=0.9,
          edgecolor="#D1D5DB")

# ── Spine styling ──────────────────────────────────────────
for spine in ax.spines.values():
    spine.set_linewidth(0.5)
    spine.set_color("#D1D5DB")

plt.tight_layout()

# ── Save ────────────────────────────────────────────────────
png_path = OUT_DIR / "item_strip_analysis.png"
pdf_path = OUT_DIR / "item_strip_analysis.pdf"

fig.savefig(png_path, dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(pdf_path, bbox_inches="tight", facecolor="white")
plt.close(fig)

print(f"Saved: {png_path}")
print(f"Saved: {pdf_path}")
print("Done.")
