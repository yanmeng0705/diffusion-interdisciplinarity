"""
fig2_mechanism.py — Section 2 组图：回升的驱动机制（双向融合 + 两组命运对比）
=================================================
组图布局（左列上下 2 panel + 右列整列 1 panel）：
  A（左上）：双视角象限散点（分出 core_driver / established 两组）
  C（左下）：双向融合对照条形（技术领域 forward vs reverse，支持自适应 Error Bar）
  B（右列整列，高瘦竖图）：core_driver + established 引方热图转置
              （subfield 当列 / x 轴，26 个 field 当行 / y 轴，
               按 OpenAlex 4 大 domain 聚类排序，共色阶 → 两组命运直接对比）

【数据来源】./output/final/ 下：
  - s2/s2_12_quadrant.csv               （A：四象限）
  - s3/s3_22_bidirectional.csv          （C：双向）
  - s3/s3_20_indegree_share_change.csv  （B：引方 Δshare 长表）
  - s2/s2_14_established.csv            （B：established 名单, 按 RI 降序）

【运行】 正式：python fig2_mechanism.py    预览：python fig2_mechanism.py --demo
【输出】./figures_final/output/fig2_mechanism.png + .pdf
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

sys.path.insert(0, str(Path(__file__).parent))
from figstyle import (apply_base_style, panel_label, save_fig, FS,
                      C_QUAD, C_AI, C_STATS, C_HIGHLIGHT, C_DIR_A, C_DIR_B,
                      CMAP_DIV, DOMAIN_COLORS, abbrev_field, print_abbrev_legend)

DEMO = '--demo' in sys.argv
DATA = Path('./output/final')
OUT = Path(__file__).parent / 'output'
OUT.mkdir(parents=True, exist_ok=True)

AI_ID, STATS_ID = 1702, 2613
N_TOP = 10
SUBFIELD_LABEL_TH = 28

# Panel C error bar 取自 s3_22 的哪套离散度列: 'se' | 'ci95' | 'std' | None
# 当前用 sem 看效果; 改成 'ci95' / 'std' 即切换, 无需动其它代码。
ERRBAR = 'se'


def load_data():
    if DEMO:
        rng = np.random.default_rng(2)
        n = 252
        ri = np.clip(rng.beta(3, 2, n) * 0.8 + 0.2, 0.2, 1.0)
        dri = rng.normal(0.02, 0.05, n)
        quad = pd.DataFrame({'subfield_id': range(n), 'RI_end': ri, 'delta_RI': dri})
        xcut, ycut = np.median(ri), np.median(dri)
        def asg(r):
            hx, hy = r['RI_end'] >= xcut, r['delta_RI'] >= ycut
            return ('core_driver' if hx and hy else 'established' if hx
                    else 'riser' if hy else 'stable_low')
        quad['quadrant'] = quad.apply(asg, axis=1)
        quad['subfield_name'] = [f'sf{i}' for i in range(n)]
        quad['field_name'] = 'demo'
        quad.loc[0, ['subfield_id', 'RI_end', 'delta_RI', 'quadrant', 'subfield_name']] = \
            [AI_ID, 0.982, -0.016, 'established', 'Artificial Intelligence']
        quad.loc[1, ['subfield_id', 'RI_end', 'delta_RI', 'quadrant', 'subfield_name']] = \
            [STATS_ID, 0.924, -0.0004, 'established', 'Statistics and Probability']
        quad.loc[2, ['RI_end', 'delta_RI', 'quadrant', 'subfield_name']] = \
            [0.971, 0.105, 'core_driver', 'Health, Toxicology and Mutagenesis']
        tech = ['Engineering', 'Environmental Science', 'Materials Science',
                'Energy', 'Computer Science']
        bidi = pd.DataFrame({'tech_field': tech,
                             'forward_mean': [1.57, 1.08, 0.54, 0.26, 0.29],
                             'reverse_mean': [0.96, 0.87, 0.44, 0.20, 0.47],
                             'forward_se': [0.12, 0.09, 0.06, 0.04, 0.05],
                             'reverse_se': [0.10, 0.08, 0.05, 0.03, 0.06],
                             'forward_std': [1.05, 0.78, 0.52, 0.35, 0.44],
                             'reverse_std': [0.87, 0.70, 0.44, 0.26, 0.52],
                             'forward_ci95': [0.235, 0.176, 0.118, 0.078, 0.098],
                             'reverse_ci95': [0.196, 0.157, 0.098, 0.059, 0.118]})
        fields = ['Medicine', 'Social Sciences', 'Engineering',
                  'Arts and Humanities', 'Computer Science',
                  'Biochemistry, Genetics and Molecular Biology',
                  'Agricultural and Biological Sciences', 'Environmental Science',
                  'Physics and Astronomy', 'Materials Science',
                  'Business, Management and Accounting', 'Chemistry',
                  'Earth and Planetary Sciences', 'Mathematics',
                  'Immunology and Microbiology', 'Neuroscience',
                  'Chemical Engineering', 'Energy',
                  'Economics, Econometrics and Finance',
                  'Pharmacology, Toxicology and Pharmaceutics', 'Psychology',
                  'Health Professions', 'Nursing', 'Decision Sciences',
                  'Veterinary', 'Dentistry']
        cd = quad[quad['quadrant'] == 'core_driver']['subfield_id'].tolist()[:N_TOP]
        est = quad[quad['quadrant'] == 'established'].sort_values(
            'RI_end', ascending=False)['subfield_id'].tolist()[:N_TOP]
        rows = []
        for grp, sids in [('cd', cd), ('est', est)]:
            for sid in sids:
                for j, f in enumerate(fields):
                    base = (1.2 if j < 5 else -0.4) if grp == 'cd' else rng.normal(0, 0.9)
                    rows.append({'subfield_id': sid, 'source_field_id': j,
                                 'source_field_name': f,
                                 'delta_share': rng.normal(base, 0.8)})
        longdf = pd.DataFrame(rows)
        cd_real = ['Infectious Diseases', 'Business and International Management',
                   'Finance', 'Political Science and International Relations',
                   'Health, Toxicology and Mutagenesis',
                   'Endocrinology, Diabetes and Metabolism', 'Forestry',
                   'Urban Studies', 'Radiology, Nuclear Medicine and Imaging',
                   'Strategy and Management']
        est_real = ['Artificial Intelligence', 'Statistics and Probability',
                    'Safety, Risk, Reliability and Quality',
                    'History and Philosophy of Science', 'Automotive Engineering',
                    'Conservation', 'Building and Construction',
                    'Statistics, Probability and Uncertainty',
                    'Control and Systems Engineering',
                    'Statistical and Nonlinear Physics']
        cd_names = {s: cd_real[i] for i, s in enumerate(cd)}
        est_names = {s: est_real[i] for i, s in enumerate(est)}
        for s, nm in {**cd_names, **est_names}.items():
            quad.loc[quad['subfield_id'] == s, 'subfield_name'] = nm
        return quad, bidi, longdf, cd, est

    quad = pd.read_csv(DATA / 's2/s2_12_quadrant.csv')
    bidi = pd.read_csv(DATA / 's3/s3_22_bidirectional.csv')
    longdf = pd.read_csv(DATA / 's3/s3_20_indegree_share_change.csv')
    cd = quad.loc[quad['quadrant'] == 'core_driver'].sort_values(
        'delta_RI', ascending=False)['subfield_id'].tolist()[:N_TOP]
    est_df = pd.read_csv(DATA / 's2/s2_14_established.csv')
    ri_col = 'RI_end' if 'RI_end' in est_df.columns else \
        [c for c in est_df.columns if 'RI' in c][0]
    est_df = est_df.sort_values(ri_col, ascending=False)
    est = est_df['subfield_id'].tolist()[:N_TOP]
    return quad, bidi, longdf, cd, est


def _build_matrix(longdf, ids, col_order=None):
    sub = longdf[longdf['subfield_id'].isin(ids)]
    mat = sub.pivot_table(index='subfield_id', columns='source_field_name',
                          values='delta_share', fill_value=0)
    mat = mat.reindex([i for i in ids if i in mat.index])
    if col_order is not None:
        mat = mat.reindex(columns=col_order, fill_value=0)
    return mat


def main():
    apply_base_style()
    quad, bidi, longdf, cd_ids, est_ids = load_data()
    name_of = quad.set_index('subfield_id')['subfield_name'].to_dict()

    fig = plt.figure(figsize=(13.5, 11.5))
    gs = GridSpec(2, 2, figure=fig, width_ratios=[1.0, 0.95],
                  height_ratios=[0.82, 1.0], hspace=0.32, wspace=0.26,
                  left=0.12, right=0.915, top=0.96, bottom=0.15)
    axA = fig.add_subplot(gs[0, 0])
    axC_bar = fig.add_subplot(gs[1, 0])
    axB = fig.add_subplot(gs[:, 1])

    # ==================== Panel A ====================
    xcut = quad['RI_end'].median(); ycut = quad['delta_RI'].median()
    labels = {'core_driver': 'Core driver', 'established': 'Mature hub',
              'riser': 'Riser', 'stable_low': 'Stable-low'}
    for q, c in C_QUAD.items():
        sub = quad[quad['quadrant'] == q]
        axA.scatter(sub['RI_end'], sub['delta_RI'], s=13, c=c, alpha=0.55,
                    edgecolors='none', label=labels[q])
    axA.axvline(xcut, color='#bbb', ls=(0, (4, 3)), lw=0.7)
    axA.axhline(ycut, color='#bbb', ls=(0, (4, 3)), lw=0.7)
    axA.axhline(0, color='#888', lw=0.5, alpha=0.5)

    offsets = {
        AI_ID: ((-6, -10), 'top'),
        STATS_ID: ((-6, 8), 'bottom')
    }
    for sid, col in [(AI_ID, C_AI), (STATS_ID, C_STATS)]:
        r = quad[quad['subfield_id'] == sid]
        if len(r):
            r = r.iloc[0]
            disp_nm = abbrev_field(str(r['subfield_name']), threshold=SUBFIELD_LABEL_TH,
                                   use_aliases=False, mode='readable')
            axA.scatter(r['RI_end'], r['delta_RI'], s=70, facecolors='none',
                        edgecolors=col, linewidths=1.6, zorder=6)

            offset_xy, va_align = offsets.get(sid, ((-6, 4), 'bottom'))
            axA.annotate(disp_nm, (r['RI_end'], r['delta_RI']),
                         xytext=offset_xy, textcoords='offset points',
                         ha='right', va=va_align,
                         fontsize=FS['annot'] - 1, fontweight='bold', color=col)

    # ------------------ 第一象限（Core driver）双极值点动态标注 ------------------
    cd_quad = quad[quad['quadrant'] == 'core_driver']

    # 1. 标注 ΔRI 最大的点（Infectious Diseases：文本改为向右侧显示，绝对留在第一象限内）
    cd_max_dri = cd_quad.sort_values('delta_RI', ascending=False)
    if len(cd_max_dri):
        r_dri = cd_max_dri.iloc[0]
        disp_nm_dri = abbrev_field(str(r_dri['subfield_name']), threshold=SUBFIELD_LABEL_TH,
                                   use_aliases=False, mode='readable')
        axA.scatter(r_dri['RI_end'], r_dri['delta_RI'], s=70, facecolors='none',
                    edgecolors=C_HIGHLIGHT, linewidths=1.6, zorder=6)
        axA.annotate(disp_nm_dri, (r_dri['RI_end'], r_dri['delta_RI']),
                     xytext=(6, 4), textcoords='offset points', ha='left', va='bottom',
                     fontsize=FS['annot'] - 1, color=C_HIGHLIGHT)

    # 2. 标注 ΔRI 第二大的点（与 Panel B 一致：core driver 按 ΔRI 取前两名；
    #    mature hub 按 RI 取前两名即 AI 与 S&P，已在上方标注）
    if len(cd_max_dri) > 1:
        r_dri2 = cd_max_dri.iloc[1]
        disp_nm_dri2 = abbrev_field(str(r_dri2['subfield_name']), threshold=SUBFIELD_LABEL_TH,
                                    use_aliases=False, mode='readable')
        axA.scatter(r_dri2['RI_end'], r_dri2['delta_RI'], s=70, facecolors='none',
                    edgecolors=C_HIGHLIGHT, linewidths=1.6, zorder=6)
        axA.annotate(disp_nm_dri2, (r_dri2['RI_end'], r_dri2['delta_RI']),
                     xytext=(6, 4), textcoords='offset points', ha='left', va='bottom',
                     fontsize=FS['annot'] - 1, color=C_HIGHLIGHT)
    # ---------------------------------------------------------------------------

    axA.set_xlabel('Interdisciplinarity level RI')
    axA.set_ylabel('Change ΔRI')

    leg = axA.legend(loc='lower right', frameon=True, framealpha=0.85, edgecolor='none',
                     facecolor='white', fontsize=FS['legend'] + 0.5,
                     handletextpad=0.3, labelspacing=0.25)

    handles = getattr(leg, "legend_handles", getattr(leg, "legendHandles", []))
    for h in handles:
        h.set_alpha(1.0)
        h.set_sizes([35])
    axA.grid(alpha=0.18, lw=0.5)
    panel_label(axA, 'A', dx=-0.10, dy=1.02)

    # ==================== Panel C ====================
    x = np.arange(len(bidi))
    w = 0.38
    # 按 ERRBAR 选离散度列(se/ci95/std); 列缺失则不画 error bar。
    if ERRBAR:
        fcol, rcol = f'forward_{ERRBAR}', f'reverse_{ERRBAR}'
        yerr_f = bidi[fcol] if fcol in bidi.columns else None
        yerr_r = bidi[rcol] if rcol in bidi.columns else None
    else:
        yerr_f = yerr_r = None
    error_config = {'ecolor': '#444444', 'lw': 0.8, 'capsize': 2, 'alpha': 0.8}

    axC_bar.bar(x - w/2, bidi['forward_mean'], w, color=C_DIR_A, yerr=yerr_f, error_kw=error_config,
                label='Forward: technical -> core driver')
    axC_bar.bar(x + w/2, bidi['reverse_mean'], w, color=C_DIR_B, yerr=yerr_r, error_kw=error_config,
                label='Reverse: core driver -> technical')
    axC_bar.axhline(0, color='#444', lw=0.6)
    axC_bar.set_xticks(x)
    axC_bar.set_xticklabels([abbrev_field(t) for t in bidi['tech_field']],
                            rotation=20, ha='right', fontsize=FS['tick'] - 0.5)
    axC_bar.set_ylabel('Mean Δshare (pp)')
    axC_bar.legend(loc='upper right', frameon=False, fontsize=FS['legend'] + 0.5)
    axC_bar.grid(axis='y', alpha=0.2, lw=0.5)
    panel_label(axC_bar, 'C', dx=-0.10, dy=1.04)

    # ==================== Panel B ====================
    matC = _build_matrix(longdf, cd_ids)
    matD_full = _build_matrix(longdf, est_ids)
    all_cols = sorted(set(matC.columns) | set(matD_full.columns))

    DOMAIN_ORDER = ['Social', 'Life', 'Health', 'Physical']
    DOMAIN_KW = {
        'Physical': ['engineer', 'comput', 'material', 'energy', 'environ',
                     'chemistr', 'physic', 'earth', 'planet', 'mathemat', 'math'],
        'Health':   ['medicine', 'nursing', 'dentist', 'health prof',
                     'pharmacol', 'veterin'],
        'Life':     ['biochem', 'genetic', 'immunolog', 'microbiol',
                     'neurosci', 'agricultur', 'biolog'],
        'Social':   ['social', 'psycholog', 'business', 'manage', 'econom',
                     'arts', 'humanit', 'decision'],
    }
    def domain_of(col):
        c = str(col).lower()
        if 'biochem' in c:
            return 'Life'
        for dom in DOMAIN_ORDER:
            if any(kw in c for kw in DOMAIN_KW[dom]):
                return dom
        return 'Social'

    cmean = matC.reindex(columns=all_cols, fill_value=0).mean()
    PHYSICAL_T2B = [
        'Earth and Planetary Sciences', 'Chemical Engineering', 'Chemistry',
        'Physics and Astronomy', 'Mathematics', 'Computer Science',
        'Energy', 'Materials Science', 'Environmental Science', 'Engineering'
    ]

    def intra_key(c):
        if domain_of(c) == 'Physical':
            for i, expected in enumerate(PHYSICAL_T2B):
                if str(c).strip() == expected or str(c).strip().startswith(expected[:10]):
                    return i
            return 999
        else:
            return cmean.get(c, 0)

    field_order = sorted(all_cols,
                         key=lambda c: (DOMAIN_ORDER.index(domain_of(c)), intra_key(c)))
    field_dom = [domain_of(c) for c in field_order]

    print("\n" + "=" * 64)
    print("【Fig2 B 纵轴核查】field 的 domain 归属（学科大类聚类）")
    print("=" * 64)
    cur = None
    for c in field_order:
        d = domain_of(c)
        if d != cur:
            print(f"  --- {d} Sciences ---")
            cur = d
        print(f"      {c}")
    print("=" * 64 + "\n")

    matC = matC.reindex(columns=field_order, fill_value=0)
    matD = _build_matrix(longdf, est_ids, col_order=field_order)
    both = np.concatenate([matC.values.ravel(), matD.values.ravel()])
    vmax = np.nanpercentile(np.abs(both), 95)

    nC, nD = len(matC), len(matD)
    gap = 1
    pre = np.full((nC + gap + nD, len(field_order)), np.nan)
    pre[:nC, :] = matC.values
    pre[nC + gap:, :] = matD.values
    full = pre.T

    subfield_names = ([abbrev_field(name_of.get(i, '?'), threshold=SUBFIELD_LABEL_TH,
                                    use_aliases=False, mode='readable') for i in matC.index]
                      + [''] * gap
                      + [abbrev_field(name_of.get(i, '?'), threshold=SUBFIELD_LABEL_TH,
                                      use_aliases=False, mode='readable') for i in matD.index])

    cmap = plt.get_cmap(CMAP_DIV).copy()
    cmap.set_bad('white')
    im = axB.imshow(full, aspect='auto', cmap=cmap, vmin=-vmax, vmax=vmax)
    field_labels = [abbrev_field(c) for c in field_order]

    axB.set_xticks(range(len(subfield_names)))
    axB.set_xticklabels(subfield_names, rotation=55, ha='right', va='top',
                        rotation_mode='anchor', fontsize=FS['tick'] - 0.5)

    sub_fulls = ([str(name_of.get(i, '?')) for i in matC.index]
                 + [str(name_of.get(i, '?')) for i in matD.index])
    print_abbrev_legend(sub_fulls, title='Fig2 B 横轴(subfield)缩写对照',
                        threshold=SUBFIELD_LABEL_TH, use_aliases=False, mode='readable')
    print_abbrev_legend(field_order, title='Fig2 B 纵轴(field)缩写对照')

    axB.set_yticks(range(len(field_labels)))
    axB.set_yticklabels(field_labels, fontsize=FS['tick'])
    axB.axvline(nC + gap / 2 - 0.5, color='#333', lw=1.2)

    DOMAIN_FULL = {'Physical': 'Physical Sciences', 'Health': 'Health Sciences',
                   'Life': 'Life Sciences', 'Social': 'Social Sciences'}
    bounds = []
    start = 0
    for k in range(1, len(field_dom) + 1):
        if k == len(field_dom) or field_dom[k] != field_dom[start]:
            bounds.append((field_dom[start], start, k - 1))
            if k < len(field_dom):
                axB.axhline(k - 0.5, color='#888', lw=0.8, ls=(0, (3, 2)), xmin=-0.02, clip_on=False)
            start = k

    ncols = len(subfield_names)
    for dom, lo, hi in bounds:
        mid = (lo + hi) / 2
        # dom 是简称（如 'Physical'），DOMAIN_FULL[dom] 是全称（如 'Physical Sciences'）
        color = DOMAIN_COLORS.get(DOMAIN_FULL[dom], '#888888')
        axB.text(1.015, mid, DOMAIN_FULL[dom], transform=axB.get_yaxis_transform(),
                 ha='left', va='center', rotation=90,
                 fontsize=FS['annot'], fontweight='bold', color=color)

    for i in range(full.shape[0]):
        for j in range(full.shape[1]):
            v = full[i, j]
            if not np.isnan(v) and abs(v) > vmax:
                axB.text(j, i, f"{v:+.0f}", ha='center', va='center',
                        fontsize=FS['annot'] - 2.5, fontweight='bold', color='white')

    axB.text((nC / 2) / ncols, -0.15 , 'Top 10 Core drivers',
             transform=axB.transAxes, va='top', ha='center',
             fontsize=FS['axis_label'] - 0.5, fontweight='bold', color='#2E6E4E')
    axB.text(1 - (nD / 2) / ncols, -0.15, 'Top 10 Mature hubs',
             transform=axB.transAxes, va='top', ha='center',
             fontsize=FS['axis_label'] - 0.5, fontweight='bold', color='#3B6FB6')
    panel_label(axB, 'B', dx=-0.10, dy=1.012)

    cb = fig.colorbar(im, ax=axB, fraction=0.025, pad=0.09, location='right')
    cb.ax.tick_params(labelsize=FS['tick'] - 1)
    cb.ax.set_xlabel('Δshare (pp)', fontsize=FS['cbar_label'], labelpad=15)

    save_fig(fig, OUT / 'fig2_mechanism')
    # 同时在同一输出目录另存一份 PDF（若 save_fig 本身已输出 PDF，此处会以同名文件覆盖）
    fig.savefig(OUT / 'fig2_mechanism.pdf', bbox_inches='tight')
    plt.close()
    print(f"✓ fig2_mechanism saved {'(DEMO)' if DEMO else ''}")


if __name__ == '__main__':
    main()
