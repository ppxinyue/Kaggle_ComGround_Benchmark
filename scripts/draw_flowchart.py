"""
Recreate the benchmark pipeline flowchart from flowchart.drawio using matplotlib.
Saves to writings/figures/flowchart.png
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from pathlib import Path

OUT = Path(r"D:\ppXinyue\2026_Kaggle\writings\figures\flowchart.png")

fig, ax = plt.subplots(figsize=(10, 7.5))
ax.set_xlim(0, 10)
ax.set_ylim(0, 7.5)
ax.axis('off')

# Style constants
BOX_STYLE = "round,pad=0.15"
FILL_WHITE = "#ffffff"
FILL_GRAY = "#f0f0f0"
EDGE_COLOR = "#333333"
FONT_TITLE = 11
FONT_BOX = 9
FONT_SMALL = 8
FONT_RESULT = 10

def draw_box(ax, x, y, w, h, text, fill=FILL_WHITE, bold=False, fontsize=FONT_BOX):
    fs = fontsize
    fw = "bold" if bold else "normal"
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle=BOX_STYLE, facecolor=fill, edgecolor=EDGE_COLOR, linewidth=1.2)
    ax.add_patch(box)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, fontweight=fw,
            fontfamily="sans-serif", color="#222222")
    return (x, y)

def draw_arrow(ax, start, end, color=EDGE_COLOR):
    ax.annotate("", xy=end, xytext=start,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.3,
                                connectionstyle="arc3,rad=0"))

def draw_diamond(ax, x, y, w, h, text):
    diamond = plt.Polygon([(x, y+h/2), (x+w/2, y), (x, y-h/2), (x-w/2, y)],
                          facecolor=FILL_WHITE, edgecolor=EDGE_COLOR, linewidth=1.2)
    ax.add_patch(diamond)
    ax.text(x, y, text, ha="center", va="center", fontsize=FONT_SMALL,
            fontfamily="sans-serif", color="#222222")

# ── Section titles ──────────────────────────────────────────────────
ax.text(2.5, 7.1, "Benchmark 1: Category-Norm Replication",
        ha="center", va="center", fontsize=FONT_TITLE, fontweight="bold",
        fontfamily="sans-serif", color="#333333")
ax.text(7.5, 7.1, "Benchmark 2: Tacit Coordination",
        ha="center", va="center", fontsize=FONT_TITLE, fontweight="bold",
        fontfamily="sans-serif", color="#333333")

# ── Benchmark 1 column (left) ──────────────────────────────────────
b1_x = 2.5
draw_box(ax, b1_x, 6.4, 3.6, 0.5, "70 Category Labels\n(Castro et al., 2021)")
draw_arrow(ax, (b1_x, 6.15), (b1_x, 5.75))

draw_box(ax, b1_x, 5.5, 3.6, 0.5, "LLM Free Generation\n(N = 100 per category)")
draw_arrow(ax, (b1_x, 5.25), (b1_x, 4.85))

draw_box(ax, b1_x, 4.6, 3.6, 0.5, "Exemplar Frequency Distribution")
draw_arrow(ax, (b1_x, 4.35), (b1_x, 3.95))

draw_box(ax, b1_x, 3.7, 3.6, 0.5, "Alignment Metrics", fill=FILL_GRAY, bold=True)
ax.text(b1_x + 2.1, 3.7, "Top-K | Spearman ρ\nFRM | Pearson r",
        ha="left", va="center", fontsize=FONT_SMALL, color="#666666",
        fontfamily="sans-serif")
draw_arrow(ax, (b1_x, 3.45), (b1_x, 2.95))

draw_box(ax, b1_x, 2.7, 3.6, 0.5, "Model–Human Alignment Score",
         fill=FILL_GRAY, bold=True, fontsize=FONT_RESULT)

# ── Benchmark 2 column (right) ─────────────────────────────────────
b2_x = 7.5
draw_box(ax, b2_x, 6.4, 3.6, 0.5, "31 Domains × 8 Categories")
draw_arrow(ax, (b2_x, 6.15), (b2_x, 5.75))

draw_box(ax, b2_x, 5.5, 3.6, 0.5, "Item Generation\n(4 options per item)")
draw_arrow(ax, (b2_x, 5.25), (b2_x, 4.85))

draw_box(ax, b2_x, 4.6, 3.6, 0.5, "Coordination Game", fill=FILL_GRAY, bold=True)

# Split into Agent A and Agent B
ax.annotate("", xy=(6.6, 3.9), xytext=(b2_x - 0.3, 4.35),
            arrowprops=dict(arrowstyle="-|>", color=EDGE_COLOR, lw=1.3))
ax.annotate("", xy=(8.4, 3.9), xytext=(b2_x + 0.3, 4.35),
            arrowprops=dict(arrowstyle="-|>", color=EDGE_COLOR, lw=1.3))

draw_box(ax, 6.6, 3.6, 1.6, 0.45, "Agent A\n(shuffled)")
draw_box(ax, 8.4, 3.6, 1.6, 0.45, "Agent B\n(shuffled)")

# Arrows from agents to diamond
ax.annotate("", xy=(7.2, 2.85), xytext=(6.6, 3.37),
            arrowprops=dict(arrowstyle="-|>", color=EDGE_COLOR, lw=1.3))
ax.annotate("", xy=(7.8, 2.85), xytext=(8.4, 3.37),
            arrowprops=dict(arrowstyle="-|>", color=EDGE_COLOR, lw=1.3))

draw_diamond(ax, 7.5, 2.6, 1.4, 0.5, "Same\nChoice?")
draw_arrow(ax, (7.5, 2.35), (7.5, 1.85))

draw_box(ax, b2_x, 1.6, 3.6, 0.5, "Coordination Rate",
         fill=FILL_GRAY, bold=True, fontsize=FONT_RESULT)
ax.text(b2_x + 2.1, 1.6, "Σ 1[cᵢ=cⱼ] / C(N,2)",
        ha="left", va="center", fontsize=FONT_SMALL, color="#666666",
        fontfamily="sans-serif")

# ── Bottom shared box ───────────────────────────────────────────────
draw_box(ax, 5.0, 0.5, 6.5, 0.55, "Cross-Model Comparison  |  Cultural Specificity Analysis",
         fill=FILL_GRAY, bold=True, fontsize=FONT_RESULT)

# Arrows to bottom box
ax.annotate("", xy=(3.5, 0.78), xytext=(b1_x, 2.45),
            arrowprops=dict(arrowstyle="-|>", color=EDGE_COLOR, lw=1.3))
ax.annotate("", xy=(6.5, 0.78), xytext=(b2_x, 1.35),
            arrowprops=dict(arrowstyle="-|>", color=EDGE_COLOR, lw=1.3))

# ── Divider line between columns ────────────────────────────────────
ax.plot([5.0, 5.0], [0.0, 7.0], color="#cccccc", linewidth=0.8, linestyle="--")

# ── Save ────────────────────────────────────────────────────────────
fig.tight_layout()
fig.savefig(OUT, dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(OUT.with_suffix(".pdf"), dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"Saved: {OUT} and .pdf")
