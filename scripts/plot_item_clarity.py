"""
Generate Item Clarity figures: stacked horizontal bar charts showing
distance and frequency distributions across all items.
"""

import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────
DATA_PATH = Path(r"D:\ppXinyue\2026_Kaggle\data\benchmark2\item_quality.json")
OUT_DIR   = Path(r"D:\ppXinyue\2026_Kaggle\writings\figures")
DPI = 300

# Colors: smallest value -> lightest, largest value -> darkest
# Stack order left-to-right: largest first (darkest) ... smallest last (lightest)
COLORS_ASC = ['#d0d0d0', '#878787', '#4d4d4d', '#1a1a1a']   # index 0=smallest, 3=largest
# When stacking left-to-right with largest first, we reverse:
STACK_COLORS = list(reversed(COLORS_ASC))  # [darkest, ..., lightest]


def load_items(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_distance_data(items):
    """Extract avg_distance arrays for every item. Returns (values_matrix, domains, item_count)."""
    records = []
    for item in items:
        dists = sorted([opt['avg_distance'] for opt in item['options']])
        records.append({
            'item_id': item['item_id'],
            'domain': item['domain'],
            'values': dists,  # [smallest, ..., largest]
        })
    # Sort by largest distance DESCENDING (top = highest max distance)
    records.sort(key=lambda r: r['values'][-1], reverse=True)
    return records


def build_frequency_data(items):
    """Extract corpus_frequency arrays. Skip items with any null."""
    records = []
    for item in items:
        freqs_raw = [opt['corpus_frequency'] for opt in item['options']]
        if any(v is None for v in freqs_raw):
            continue
        freqs = sorted(freqs_raw)
        records.append({
            'item_id': item['item_id'],
            'domain': item['domain'],
            'values': freqs,
        })
    # Sort by largest frequency DESCENDING
    records.sort(key=lambda r: r['values'][-1], reverse=True)
    return records


def plot_stacked_hbar(records, x_label, title, filename):
    n = len(records)
    fig, ax = plt.subplots(figsize=(10, 14))

    # Build the stacked bars: for each item, stack segments left-to-right
    # Segment order: largest (darkest) first, then decreasing
    # So we reverse the sorted-ascending values: [largest, ..., smallest]
    y_pos = np.arange(n)

    for i, rec in enumerate(records):
        vals = rec['values']  # ascending [smallest, ..., largest]
        # Reverse so we stack: largest, 2nd, 3rd, smallest
        rev_vals = list(reversed(vals))

        # Build cumulative x-positions
        left = 0
        for seg_idx, seg_val in enumerate(rev_vals):
            ax.barh(i, seg_val, left=left, height=1.0, color=STACK_COLORS[seg_idx],
                    edgecolor='none', linewidth=0)
            left += seg_val

    # Domain labels on right margin
    domains = []
    current_domain = None
    domain_start = None
    for i, rec in enumerate(records):
        d = rec['domain']
        if d != current_domain:
            if current_domain is not None:
                domains.append((current_domain, (domain_start + i - 1) / 2.0))
            current_domain = d
            domain_start = i
    # Last domain
    if current_domain is not None:
        domains.append((current_domain, (domain_start + n - 1) / 2.0))

    # Add domain annotations on right side
    x_max = ax.get_xlim()[1]
    for domain_name, y_mid in domains:
        ax.annotate(domain_name, xy=(x_max, y_mid), xytext=(5, 0),
                    textcoords='offset points', fontsize=5, va='center',
                    ha='left', color='#333333', annotation_clip=False)

    # Extend right margin to fit domain labels
    fig.subplots_adjust(right=0.82)

    ax.set_ylim(-0.5, n - 0.5)
    ax.set_yticks([])  # No y tick labels for 410 items
    ax.set_xlabel(x_label, fontsize=11)
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.invert_yaxis()  # Top items at top of figure
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    plt.tight_layout(rect=[0, 0, 0.82, 1])

    # Save PNG and PDF
    png_path = OUT_DIR / f"{filename}.png"
    pdf_path = OUT_DIR / f"{filename}.pdf"
    fig.savefig(png_path, dpi=DPI, bbox_inches='tight')
    fig.savefig(pdf_path, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {png_path}")
    print(f"Saved: {pdf_path}")


def main():
    items = load_items(DATA_PATH)
    print(f"Loaded {len(items)} items")

    # Figure 1: Distance distribution
    dist_records = build_distance_data(items)
    print(f"Distance figure: {len(dist_records)} items")
    plot_stacked_hbar(
        dist_records,
        x_label="Average Cosine Distance",
        title="Item Clarity: Distance Distribution",
        filename="item_clarity_distance"
    )

    # Figure 2: Frequency distribution
    freq_records = build_frequency_data(items)
    print(f"Frequency figure: {len(freq_records)} items (after null filter)")
    plot_stacked_hbar(
        freq_records,
        x_label="Corpus Log Frequency (Zipf)",
        title="Item Clarity: Frequency Distribution",
        filename="item_clarity_frequency"
    )

    print("Done.")


if __name__ == '__main__':
    main()
