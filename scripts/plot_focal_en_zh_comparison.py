"""
Generate publication-quality figure: focal_en_zh_comparison.png/pdf

Left panel:  EN vs ZH gap comparison (violin plot with inner box)
Right panel: EN vs ZH entropy comparison (box plot with jittered scatter)
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy import stats
import seaborn as sns

# ── Load data ──────────────────────────────────────────────────────────
with open("data/benchmark2/item_quality.json", encoding="utf-8") as f:
    items = json.load(f)

print(f"Total items: {len(items)}")

# ── Helper functions ───────────────────────────────────────────────────

def compute_gap(values):
    """Top1 - Top2 gap from a list of numeric values (filter None)."""
    clean = sorted([v for v in values if v is not None], reverse=True)
    if len(clean) < 2:
        return None
    return clean[0] - clean[1]


def compute_entropy(values):
    """Shannon entropy (bits) from a list of numeric values (filter None/<=0)."""
    clean = [v for v in values if v is not None and v > 0]
    if len(clean) < 2:
        return None
    total = sum(clean)
    if total == 0:
        return None
    probs = np.array(clean) / total
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs))


def p_to_stars(p):
    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    else:
        return "n.s."


# ── Compute metrics per item ──────────────────────────────────────────
records = {"en": [], "zh": []}

for item in items:
    lang = item["language"]
    if lang not in ("en", "zh"):
        continue

    opts = item["options"]
    avg_dists = [o["avg_distance"] for o in opts]
    freqs = [o.get("corpus_frequency") for o in opts]

    dist_gap = compute_gap(avg_dists)
    freq_gap = compute_gap(freqs)

    dist_entropy = compute_entropy(avg_dists)
    freq_entropy = compute_entropy(freqs)

    records[lang].append({
        "dist_gap": dist_gap,
        "freq_gap": freq_gap,
        "dist_entropy": dist_entropy,
        "freq_entropy": freq_entropy,
    })

print(f"EN items: {len(records['en'])}, ZH items: {len(records['zh'])}")

# ── Prepare arrays ────────────────────────────────────────────────────
en_dist_gap = np.array([r["dist_gap"] for r in records["en"] if r["dist_gap"] is not None])
zh_dist_gap = np.array([r["dist_gap"] for r in records["zh"] if r["dist_gap"] is not None])
en_freq_gap = np.array([r["freq_gap"] for r in records["en"] if r["freq_gap"] is not None])
zh_freq_gap = np.array([r["freq_gap"] for r in records["zh"] if r["freq_gap"] is not None])

en_dist_ent = np.array([r["dist_entropy"] for r in records["en"] if r["dist_entropy"] is not None])
zh_dist_ent = np.array([r["dist_entropy"] for r in records["zh"] if r["dist_entropy"] is not None])
en_freq_ent = np.array([r["freq_entropy"] for r in records["en"] if r["freq_entropy"] is not None])
zh_freq_ent = np.array([r["freq_entropy"] for r in records["zh"] if r["freq_entropy"] is not None])

# ── Significance tests ────────────────────────────────────────────────
t_dist_gap, p_dist_gap = stats.ttest_ind(en_dist_gap, zh_dist_gap, equal_var=False)
t_freq_gap, p_freq_gap = stats.ttest_ind(en_freq_gap, zh_freq_gap, equal_var=False)
t_dist_ent, p_dist_ent = stats.ttest_ind(en_dist_ent, zh_dist_ent, equal_var=False)
t_freq_ent, p_freq_ent = stats.ttest_ind(en_freq_ent, zh_freq_ent, equal_var=False)

print(f"\nSignificance tests (Welch's t-test):")
print(f"  Distance gap:  t={t_dist_gap:.3f}, p={p_dist_gap:.4f}  (EN n={len(en_dist_gap)}, ZH n={len(zh_dist_gap)})")
print(f"  Frequency gap: t={t_freq_gap:.3f}, p={p_freq_gap:.4f}  (EN n={len(en_freq_gap)}, ZH n={len(zh_freq_gap)})")
print(f"  Distance entropy: t={t_dist_ent:.3f}, p={p_dist_ent:.4f}")
print(f"  Frequency entropy: t={t_freq_ent:.3f}, p={p_freq_ent:.4f}")

# ── Style ──────────────────────────────────────────────────────────────
sns.set_style("whitegrid")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.labelsize": 13,
    "axes.titlesize": 14,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "legend.fontsize": 10,
    "figure.dpi": 150,
})

COLOR_EN = "#4472C4"   # blue
COLOR_ZH = "#ED7D31"   # orange

# ═══════════════════════════════════════════════════════════════════════
# LEFT PANEL: Violin plot of gaps
# ═══════════════════════════════════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

positions = [0, 1, 3, 4]

parts = ax1.violinplot(
    [en_dist_gap, zh_dist_gap, en_freq_gap, zh_freq_gap],
    positions=positions,
    widths=0.7,
    showmeans=False,
    showmedians=False,
    showextrema=False,
)

# Color the violin bodies
for i, body in enumerate(parts["bodies"]):
    body.set_facecolor(COLOR_EN if i in (0, 2) else COLOR_ZH)
    body.set_edgecolor("black")
    body.set_linewidth(0.8)
    body.set_alpha(0.6)

# Overlay box plots inside violins
bp = ax1.boxplot(
    [en_dist_gap, zh_dist_gap, en_freq_gap, zh_freq_gap],
    positions=positions,
    widths=0.15,
    showfliers=False,
    patch_artist=True,
    zorder=3,
)

box_colors = [COLOR_EN, COLOR_ZH, COLOR_EN, COLOR_ZH]
for patch, color in zip(bp["boxes"], box_colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.8)
    patch.set_edgecolor("black")
    patch.set_linewidth(0.8)
for element in ["whiskers", "caps", "medians"]:
    for line in bp[element]:
        line.set_color("black")
        line.set_linewidth(1.2)

# X-axis: custom labels with EN/ZH sub-labels
ax1.set_xticks([0.5, 3.5])
ax1.set_xticklabels(["Distance Gap", "Frequency Gap"], fontsize=12, fontweight="bold")
ax1.set_xlim(-0.8, 4.8)
ax1.set_ylabel("Gap (top1 $-$ top2)", fontsize=13)
ax1.set_title("EN vs ZH: Focal Option Gap Comparison", fontsize=14, fontweight="bold", pad=12)

# EN/ZH sub-labels using blended transform (x=data, y=axes fraction -0.06)
from matplotlib.transforms import blended_transform_factory
trans1 = blended_transform_factory(ax1.transData, ax1.transAxes)
for x, label, color in [(0, "EN", COLOR_EN), (1, "ZH", COLOR_ZH),
                          (3, "EN", COLOR_EN), (4, "ZH", COLOR_ZH)]:
    ax1.text(x, -0.06, label, transform=trans1, ha="center", va="top",
             fontsize=9, color=color, fontweight="bold")

# Sample size annotations
for x, n in [(0, len(en_dist_gap)), (1, len(zh_dist_gap)),
             (3, len(en_freq_gap)), (4, len(zh_freq_gap))]:
    ax1.text(x, -0.12, f"n={n}", transform=trans1, ha="center", va="top",
             fontsize=8, color="gray")

# Significance brackets
def add_sig_bracket(ax, x1, x2, y, p_val, h=0.003):
    stars = p_to_stars(p_val)
    ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y], lw=1.2, c="black")
    ax.text((x1 + x2) / 2, y + h * 1.1, f"p = {p_val:.3f} {stars}",
            ha="center", va="bottom", fontsize=9)

y_gap_max = max(en_dist_gap.max(), zh_dist_gap.max(), en_freq_gap.max(), zh_freq_gap.max())
add_sig_bracket(ax1, 0, 1, y_gap_max * 0.96, p_dist_gap, h=y_gap_max * 0.015)
add_sig_bracket(ax1, 3, 4, y_gap_max * 0.96, p_freq_gap, h=y_gap_max * 0.015)

# ═══════════════════════════════════════════════════════════════════════
# RIGHT PANEL: Box plot of entropy
# ═══════════════════════════════════════════════════════════════════════

entropy_data = [en_dist_ent, zh_dist_ent, en_freq_ent, zh_freq_ent]
entropy_positions = [0, 1, 3, 4]

bp2 = ax2.boxplot(
    entropy_data,
    positions=entropy_positions,
    widths=0.5,
    patch_artist=True,
    showfliers=True,
    flierprops=dict(marker="o", markersize=3, alpha=0.4),
    zorder=3,
)

for i, patch in enumerate(bp2["boxes"]):
    color = COLOR_EN if i in (0, 2) else COLOR_ZH
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
    patch.set_edgecolor("black")
    patch.set_linewidth(0.8)

for element in ["whiskers", "caps", "medians"]:
    for line in bp2[element]:
        line.set_color("black")
        line.set_linewidth(1.2)

# Overlay jittered scatter for individual data points
np.random.seed(42)
for i, (data, pos) in enumerate(zip(entropy_data, entropy_positions)):
    jitter = np.random.normal(0, 0.06, size=len(data))
    color = COLOR_EN if i in (0, 2) else COLOR_ZH
    ax2.scatter(pos + jitter, data, alpha=0.15, s=12, color=color, zorder=2, edgecolors="none")

# Max entropy reference line (4 options -> H_max = log2(4) = 2.0)
ax2.axhline(y=2.0, color="red", linestyle="--", linewidth=1.2, alpha=0.7,
            label="$H_{\\mathrm{max}}$ = 2.0 bits")

ax2.set_xticks([0.5, 3.5])
ax2.set_xticklabels(["Distance Entropy", "Frequency Entropy"], fontsize=12, fontweight="bold")
ax2.set_xlim(-0.8, 4.8)
ax2.set_ylabel("Shannon Entropy (bits)", fontsize=13)
ax2.set_title("EN vs ZH: Distribution Entropy Comparison", fontsize=14, fontweight="bold", pad=12)
ax2.legend(loc="lower right", fontsize=10)

# EN/ZH sub-labels
trans2 = blended_transform_factory(ax2.transData, ax2.transAxes)
for x, label, color in [(0, "EN", COLOR_EN), (1, "ZH", COLOR_ZH),
                          (3, "EN", COLOR_EN), (4, "ZH", COLOR_ZH)]:
    ax2.text(x, -0.06, label, transform=trans2, ha="center", va="top",
             fontsize=9, color=color, fontweight="bold")

# Sample size annotations
for x, data in zip(entropy_positions, entropy_data):
    ax2.text(x, -0.12, f"n={len(data)}", transform=trans2, ha="center", va="top",
             fontsize=8, color="gray")

# Significance brackets for entropy
y_ent_max = max(arr.max() for arr in entropy_data if len(arr) > 0)
add_sig_bracket(ax2, 0, 1, y_ent_max * 1.01, p_dist_ent, h=y_ent_max * 0.015)
add_sig_bracket(ax2, 3, 4, y_ent_max * 1.01, p_freq_ent, h=y_ent_max * 0.015)

ax2.set_ylim(bottom=0)

# ── Final layout & save ────────────────────────────────────────────────
fig.tight_layout(pad=2.0)

out_png = "writings/figures/focal_en_zh_comparison.png"
out_pdf = "writings/figures/focal_en_zh_comparison.pdf"

fig.savefig(out_png, dpi=300, bbox_inches="tight")
fig.savefig(out_pdf, bbox_inches="tight")
plt.close(fig)

print(f"\nSaved: {out_png}")
print(f"Saved: {out_pdf}")
print("Done.")
