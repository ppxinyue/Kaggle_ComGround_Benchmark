import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind

# ── Load data ──────────────────────────────────────────────────
with open('data/benchmark2/item_quality.json', encoding='utf-8') as f:
    data = json.load(f)

# ── Compute per-item metrics ──────────────────────────────────
records = []
for item in data:
    lang = item['language']
    opts = item['options']

    # Filter out options with null frequency
    valid_opts = [o for o in opts if o.get('corpus_frequency') is not None]
    if len(valid_opts) < 2:
        continue

    # Distance metrics (use all 4 options - distance is always present)
    all_dists = [o['avg_distance'] for o in opts]
    sorted_dists = sorted(all_dists, reverse=True)
    dist_gap = sorted_dists[0] - sorted_dists[1]

    # Distance entropy (Shannon of the 4 avg_distance values)
    d_arr = np.array(all_dists)
    d_arr = np.maximum(d_arr, 1e-10)
    d_prob = d_arr / d_arr.sum()
    dist_entropy = -np.sum(d_prob * np.log2(d_prob))

    # Frequency metrics (use valid opts only)
    all_freqs = [o['corpus_frequency'] for o in valid_opts]
    sorted_freqs = sorted(all_freqs, reverse=True)
    freq_gap = sorted_freqs[0] - sorted_freqs[1]

    # Frequency entropy
    f_arr = np.array(all_freqs)
    f_arr = np.maximum(f_arr, 1e-10)
    f_prob = f_arr / f_arr.sum()
    freq_entropy = -np.sum(f_prob * np.log2(f_prob))

    records.append({
        'language': lang,
        'dist_gap': dist_gap,
        'freq_gap': freq_gap,
        'dist_entropy': dist_entropy,
        'freq_entropy': freq_entropy,
    })

en = [r for r in records if r['language'] == 'en']
zh = [r for r in records if r['language'] == 'zh']
print(f"EN items: {len(en)}, ZH items: {len(zh)}")

# ── Colors ────────────────────────────────────────────────────
PURPLE_EN = '#7b3294'
PURPLE_ZH = '#c2a5cf'
GREEN_EN  = '#008837'
GREEN_ZH  = '#a6dba0'

# ── Helper: significance stars ────────────────────────────────
def sig_stars(p):
    if p < 0.001:
        return '***'
    if p < 0.01:
        return '**'
    if p < 0.05:
        return '*'
    return 'n.s.'


def add_p_annotation(ax, x1, x2, y, h, p_val, stars):
    """Draw a bracket + p-value annotation."""
    ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y], lw=1.2, c='black')
    ax.text((x1 + x2) / 2, y + h, f'{stars}\np={p_val:.3f}',
            ha='center', va='bottom', fontsize=9)


# ── Figure ────────────────────────────────────────────────────
sns.set_style('whitegrid')
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# ═══ (a) Distance gap by language ═════════════════════════════
ax = axes[0, 0]
en_dg = [r['dist_gap'] for r in en]
zh_dg = [r['dist_gap'] for r in zh]

parts_en = ax.violinplot([en_dg], positions=[0], showmeans=False,
                         showmedians=False, showextrema=False)
parts_zh = ax.violinplot([zh_dg], positions=[1], showmeans=False,
                         showmedians=False, showextrema=False)
for pc in parts_en['bodies']:
    pc.set_facecolor(PURPLE_EN)
    pc.set_alpha(0.4)
    pc.set_edgecolor(PURPLE_EN)
for pc in parts_zh['bodies']:
    pc.set_facecolor(PURPLE_ZH)
    pc.set_alpha(0.4)
    pc.set_edgecolor(PURPLE_ZH)

bp = ax.boxplot([en_dg, zh_dg], positions=[0, 1], widths=0.15,
                patch_artist=True, showfliers=False,
                medianprops=dict(color='black', linewidth=1.5),
                whiskerprops=dict(linewidth=1.2),
                capprops=dict(linewidth=1.2))
bp['boxes'][0].set_facecolor(PURPLE_EN)
bp['boxes'][0].set_alpha(0.7)
bp['boxes'][1].set_facecolor(PURPLE_ZH)
bp['boxes'][1].set_alpha(0.7)

t_dg, p_dg = ttest_ind(en_dg, zh_dg)
ymax = max(max(en_dg), max(zh_dg))
add_p_annotation(ax, 0, 1, ymax * 1.05, ymax * 0.04, p_dg, sig_stars(p_dg))

ax.set_xticks([0, 1])
ax.set_xticklabels(['English', 'Chinese'], fontsize=11)
ax.set_ylabel('Distance Gap (top1 - top2)', fontsize=11)
ax.set_title('(a) Distance Gap by Language', fontsize=12, fontweight='bold')

# ═══ (b) Frequency gap by language ════════════════════════════
ax = axes[0, 1]
en_fg = [r['freq_gap'] for r in en]
zh_fg = [r['freq_gap'] for r in zh]

parts_en = ax.violinplot([en_fg], positions=[0], showmeans=False,
                         showmedians=False, showextrema=False)
parts_zh = ax.violinplot([zh_fg], positions=[1], showmeans=False,
                         showmedians=False, showextrema=False)
for pc in parts_en['bodies']:
    pc.set_facecolor(GREEN_EN)
    pc.set_alpha(0.4)
    pc.set_edgecolor(GREEN_EN)
for pc in parts_zh['bodies']:
    pc.set_facecolor(GREEN_ZH)
    pc.set_alpha(0.4)
    pc.set_edgecolor(GREEN_ZH)

bp = ax.boxplot([en_fg, zh_fg], positions=[0, 1], widths=0.15,
                patch_artist=True, showfliers=False,
                medianprops=dict(color='black', linewidth=1.5),
                whiskerprops=dict(linewidth=1.2),
                capprops=dict(linewidth=1.2))
bp['boxes'][0].set_facecolor(GREEN_EN)
bp['boxes'][0].set_alpha(0.7)
bp['boxes'][1].set_facecolor(GREEN_ZH)
bp['boxes'][1].set_alpha(0.7)

t_fg, p_fg = ttest_ind(en_fg, zh_fg)
ymax = max(max(en_fg), max(zh_fg))
add_p_annotation(ax, 0, 1, ymax * 1.05, ymax * 0.04, p_fg, sig_stars(p_fg))

ax.set_xticks([0, 1])
ax.set_xticklabels(['English', 'Chinese'], fontsize=11)
ax.set_ylabel('Frequency Gap (top1 - top2)', fontsize=11)
ax.set_title('(b) Frequency Gap by Language', fontsize=12, fontweight='bold')

# ═══ (c) Distance entropy by language ═════════════════════════
ax = axes[1, 0]
en_de = [r['dist_entropy'] for r in en]
zh_de = [r['dist_entropy'] for r in zh]

box_data = [en_de, zh_de]
bp = ax.boxplot(box_data, positions=[0, 1], widths=0.35,
                patch_artist=True, showfliers=False,
                medianprops=dict(color='black', linewidth=1.5),
                whiskerprops=dict(linewidth=1.2),
                capprops=dict(linewidth=1.2))
bp['boxes'][0].set_facecolor(PURPLE_EN)
bp['boxes'][0].set_alpha(0.5)
bp['boxes'][1].set_facecolor(PURPLE_ZH)
bp['boxes'][1].set_alpha(0.5)

# Strip (jittered points)
np.random.seed(42)
jitter_en = np.random.normal(0, 0.04, len(en_de))
jitter_zh = np.random.normal(1, 0.04, len(zh_de))
ax.scatter(jitter_en, en_de, color=PURPLE_EN, alpha=0.35, s=18, zorder=3,
           edgecolors='none')
ax.scatter(jitter_zh, zh_de, color=PURPLE_ZH, alpha=0.35, s=18, zorder=3,
           edgecolors='none')

ax.axhline(y=2.0, color='grey', linestyle='--', linewidth=1, alpha=0.7)
ax.text(1.45, 2.0, 'H = 2.0\n(max)', va='center', fontsize=8, color='grey')

t_de, p_de = ttest_ind(en_de, zh_de)
ymax = max(max(en_de), max(zh_de))
add_p_annotation(ax, 0, 1, ymax * 1.02, 0.03, p_de, sig_stars(p_de))

ax.set_xticks([0, 1])
ax.set_xticklabels(['English', 'Chinese'], fontsize=11)
ax.set_ylabel('Shannon Entropy (bits)', fontsize=11)
ax.set_title('(c) Distance Entropy by Language', fontsize=12, fontweight='bold')

# ═══ (d) Frequency entropy by language ════════════════════════
ax = axes[1, 1]
en_fe = [r['freq_entropy'] for r in en]
zh_fe = [r['freq_entropy'] for r in zh]

box_data = [en_fe, zh_fe]
bp = ax.boxplot(box_data, positions=[0, 1], widths=0.35,
                patch_artist=True, showfliers=False,
                medianprops=dict(color='black', linewidth=1.5),
                whiskerprops=dict(linewidth=1.2),
                capprops=dict(linewidth=1.2))
bp['boxes'][0].set_facecolor(GREEN_EN)
bp['boxes'][0].set_alpha(0.5)
bp['boxes'][1].set_facecolor(GREEN_ZH)
bp['boxes'][1].set_alpha(0.5)

jitter_en = np.random.normal(0, 0.04, len(en_fe))
jitter_zh = np.random.normal(1, 0.04, len(zh_fe))
ax.scatter(jitter_en, en_fe, color=GREEN_EN, alpha=0.35, s=18, zorder=3,
           edgecolors='none')
ax.scatter(jitter_zh, zh_fe, color=GREEN_ZH, alpha=0.35, s=18, zorder=3,
           edgecolors='none')

ax.axhline(y=2.0, color='grey', linestyle='--', linewidth=1, alpha=0.7)
ax.text(1.45, 2.0, 'H = 2.0\n(max)', va='center', fontsize=8, color='grey')

t_fe, p_fe = ttest_ind(en_fe, zh_fe)
ymax = max(max(en_fe), max(zh_fe))
add_p_annotation(ax, 0, 1, ymax * 1.02, 0.03, p_fe, sig_stars(p_fe))

ax.set_xticks([0, 1])
ax.set_xticklabels(['English', 'Chinese'], fontsize=11)
ax.set_ylabel('Shannon Entropy (bits)', fontsize=11)
ax.set_title('(d) Frequency Entropy by Language', fontsize=12, fontweight='bold')

# ── Final layout ──────────────────────────────────────────────
plt.tight_layout(pad=2.0)

out_png = 'writings/figures/focal_en_zh_comparison.png'
out_pdf = 'writings/figures/focal_en_zh_comparison.pdf'
fig.savefig(out_png, dpi=300, bbox_inches='tight')
fig.savefig(out_pdf, bbox_inches='tight')
plt.close()

print(f"\nSaved: {out_png}")
print(f"Saved: {out_pdf}")
print(f"\nT-test results:")
print(f"  (a) Distance gap:     t={t_dg:.3f}, p={p_dg:.4f}  {sig_stars(p_dg)}")
print(f"  (b) Frequency gap:    t={t_fg:.3f}, p={p_fg:.4f}  {sig_stars(p_fg)}")
print(f"  (c) Distance entropy: t={t_de:.3f}, p={p_de:.4f}  {sig_stars(p_de)}")
print(f"  (d) Frequency entropy: t={t_fe:.3f}, p={p_fe:.4f}  {sig_stars(p_fe)}")
