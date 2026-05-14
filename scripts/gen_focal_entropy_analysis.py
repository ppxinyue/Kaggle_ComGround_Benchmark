"""
Generate focal_entropy_analysis.png / .pdf
Two-panel figure: (a) distance entropy, (b) frequency entropy.
"""

import json
import math
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from pathlib import Path

# ── paths ──────────────────────────────────────────────────────────────
ROOT = Path(r"D:\ppXinyue\2026_Kaggle")
DATA = ROOT / "data" / "benchmark2" / "item_quality.json"
OUT_DIR = ROOT / "writings" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── colour scheme ──────────────────────────────────────────────────────
CLR_DISTANCE = "#7b3294"
CLR_FREQUENCY = "#008837"

# ── load data ──────────────────────────────────────────────────────────
with open(DATA, encoding="utf-8") as f:
    items = json.load(f)

print(f"Loaded {len(items)} items")

# ── entropy helper ─────────────────────────────────────────────────────
def shannon_entropy(values):
    """Shannon entropy of *values* after normalising to probabilities."""
    total = sum(values)
    if total == 0:
        return 0.0
    probs = [v / total for v in values]
    return -sum(p * math.log2(p) for p in probs if p > 0)

# ── compute entropies ──────────────────────────────────────────────────
distance_entropies = []
frequency_entropies = []

for item in items:
    opts = item["options"]
    if len(opts) != 4:
        continue

    # distance entropy (always available)
    dists = [o["avg_distance"] for o in opts]
    distance_entropies.append(shannon_entropy(dists))

    # frequency entropy (skip items with any null)
    freqs = [o.get("corpus_frequency") for o in opts]
    if any(f is None for f in freqs):
        continue
    frequency_entropies.append(shannon_entropy(freqs))

distance_entropies = np.array(distance_entropies)
frequency_entropies = np.array(frequency_entropies)

print(f"Distance entropies: n={len(distance_entropies)}, "
      f"min={distance_entropies.min():.4f}, max={distance_entropies.max():.4f}")
print(f"Frequency entropies: n={len(frequency_entropies)}, "
      f"min={frequency_entropies.min():.4f}, max={frequency_entropies.max():.4f}")

# ── plotting ───────────────────────────────────────────────────────────
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

H_MAX = math.log2(4)  # 2.0

fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(12, 5))

# ── Panel (a): Distance entropy ────────────────────────────────────────
ax_a.hist(distance_entropies, bins=30, color=CLR_DISTANCE, edgecolor="white",
          linewidth=0.5, alpha=0.9)
ax_a.axvline(H_MAX, color="gray", ls="--", lw=1.2, label="Max (uniform)")
ax_a.legend(frameon=False, fontsize=9)
ax_a.set_xlabel("Shannon Entropy (bits)")
ax_a.set_ylabel("Count")
ax_a.set_title("(a) Distance Entropy", fontsize=12, fontweight="bold")

# auto-range x-axis
d_min, d_max = distance_entropies.min(), distance_entropies.max()
d_range = d_max - d_min
ax_a.set_xlim(d_min - 0.01 * d_range, 2.02)

# ── Panel (b): Frequency entropy ───────────────────────────────────────
ax_b.hist(frequency_entropies, bins=30, color=CLR_FREQUENCY, edgecolor="white",
          linewidth=0.5, alpha=0.9)
ax_b.axvline(H_MAX, color="gray", ls="--", lw=1.2, label="Max (uniform)")
ax_b.legend(frameon=False, fontsize=9)
ax_b.set_xlabel("Shannon Entropy (bits)")
ax_b.set_ylabel("Count")
ax_b.set_title("(b) Frequency Entropy", fontsize=12, fontweight="bold")

# auto-range x-axis
f_min, f_max = frequency_entropies.min(), frequency_entropies.max()
f_range = f_max - f_min
ax_b.set_xlim(f_min - 0.01 * f_range, 2.02)

fig.tight_layout()

for ext in ("png", "pdf"):
    out_path = OUT_DIR / f"focal_entropy_analysis.{ext}"
    fig.savefig(out_path, dpi=300 if ext == "png" else None,
                bbox_inches="tight")
    print(f"Saved {out_path}")

plt.close(fig)
