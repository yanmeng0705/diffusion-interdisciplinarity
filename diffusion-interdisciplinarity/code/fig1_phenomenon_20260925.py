"""
fig1_phenomenon.py — Section 1 组图：宏观现象 + 两段贡献者对照
=================================================
组图布局（2 panel）：
  A（左）：全网 RI 的 U 型时序曲线
  B（右）：下降段 vs 回升段 field 贡献对照哑铃图（领域换手）
       - 端点：rise=靛灰（图例首位）、decline=赭黄
       - 行序按 rise 降序，连线浅灰
       - 百分比分母各除本段总量，decline 端符号翻转（负=加剧下滑）
       - corr=+0.486 标右下

【数据来源】读取 code_final 已跑出的 csv（本地 ./output/final/ 下）：
  - s1/s1_RI_timeseries.csv              （A：每窗口 RI 均值/SE）
  - s4/s4_30_decline_vs_rise.csv         （B：两段贡献对照）

【运行】
  正式：  python fig1_phenomenon.py            （读真实 csv）
  预览版式：python fig1_phenomenon.py --demo   （用模拟数据，仅看排版）

【输出】./figures_final/output/fig1_phenomenon.png + .pdf
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

sys.path.insert(0, str(Path(__file__).parent))
from figstyle import (apply_base_style, panel_label, save_fig, FS,
                      C_POS, C_NEG, C_GREY, C_REF, C_DIR_A, C_DIR_B,
                      DOMAIN_COLORS, FIELD_TO_DOMAIN, abbrev_field,
                      print_abbrev_legend)

DEMO = '--demo' in sys.argv
DATA = Path('./output/final')
OUT = Path(__file__).parent / 'output'
OUT.mkdir(parents=True, exist_ok=True)


# ============ 数据加载（真实 / demo） ============
def load_data():
    if DEMO:
        rng = np.random.default_rng(1)
        windows = ['1989-1993', '1994-1998', '1999-2003', '2004-2008',
                   '2009-2013', '2014-2018', '2019-2023']
        ri = [0.612, 0.596, 0.575, 0.555, 0.547, 0.559, 0.586]
        ts = pd.DataFrame({'year': windows, 'RI_mean': ri,
                           'RI_se': [0.010, 0.010, 0.010, 0.009, 0.009, 0.009, 0.009]})
        fields = ['Medicine', 'Social Sciences', 'Biochemistry, Genetics and Molecular Biology',
                  'Agricultural and Biological Sciences', 'Business, Management and Accounting',
                  'Computer Science', 'Environmental Science', 'Health Professions',
                  'Economics, Econometrics and Finance', 'Neuroscience', 'Psychology',
                  'Chemistry', 'Earth and Planetary Sciences', 'Physics and Astronomy',
                  'Energy', 'Materials Science', 'Engineering']
        cvals = [0.0097, 0.0035, 0.0024, 0.0024, 0.0020, 0.0017, 0.0011, 0.0011,
                 0.0011, 0.0009, 0.0008, -0.0002, -0.0003, -0.0004, -0.0006,
                 -0.0006, -0.0017]
        dec = rng.normal(-0.0015, 0.0012, len(fields))
        rise = np.array(cvals)
        dec[0] = 0.0014   # Medicine 下降段也正
        cmp = pd.DataFrame({'field_name': fields, 'contrib_decline': dec,
                            'contrib_rise': rise})
        return ts, cmp
    ts = pd.read_csv(DATA / 's1/s1_RI_timeseries.csv')
    cmp = pd.read_csv(DATA / 's4/s4_30_decline_vs_rise.csv')
    return ts, cmp


# ============ 主函数 ============
def main():
    apply_base_style()
    ts, cmp = load_data()

    # ============================================================
    # 尺寸：13.0 × 5.0（更宽更矮）
    # width_ratios: A 比 B 宽 25%（A=1.25, B=1.0），U 型曲线更舒展
    # ============================================================
    fig = plt.figure(figsize=(13.0, 5.0))
    gs = GridSpec(1, 2, figure=fig, width_ratios=[1.25, 1.0], wspace=0.28,
                  left=0.07, right=0.98, top=0.92, bottom=0.16)
    axA = fig.add_subplot(gs[0, 0])
    axB = fig.add_subplot(gs[0, 1])

    # ---------- Panel A: U 型曲线 ----------
    x = np.arange(len(ts))
    axA.errorbar(x, ts['RI_mean'], yerr=ts['RI_se'], fmt='-o',
                 color='#222', lw=1.6, ms=5, capsize=3, mfc='white',
                 mec='#222', mew=1.2, zorder=3)
    trough = int(np.argmin(ts['RI_mean'].values))
    axA.axvline(trough, color='k', ls=(0, (4, 3)), lw=1.0, alpha=0.7, zorder=1)
    axA.set_xticks(x)
    axA.set_xticklabels(ts['year'], rotation=0)
    axA.set_ylabel('Relative interdisciplinarity (RI)')
    axA.set_xlabel('Period')
    axA.grid(axis='y', alpha=0.25, lw=0.6)
    axA.margins(x=0.02)
    panel_label(axA, 'A', dx=-0.10, dy=1.02)

    # ---------- Panel B: 哑铃图（decline vs rise 两段贡献对照，领域换手） ----------
    dfb = cmp.sort_values('contrib_rise', ascending=False).reset_index(drop=True)

    # 两段相关性
    corr = dfb['contrib_decline'].corr(dfb['contrib_rise'])

    # 转百分比
    rise_total = dfb['contrib_rise'].sum()
    decline_total_abs = abs(dfb['contrib_decline'].sum())
    dfb['rise_pct'] = dfb['contrib_rise'] / rise_total * 100
    dfb['decline_pct'] = dfb['contrib_decline'] / decline_total_abs * 100

    print("\n[Fig1 Panel B] 哑铃图（按 rise 降序；百分比与图同源）:")
    print(f"  分母: rise 段总 ΔRI={rise_total:+.5f} | decline 段总 ΔRI={dfb['contrib_decline'].sum():+.5f}（取|·|做分母）")
    print("  符号约定: rise%>0=推高回升; decline%<0=加剧下滑(下滑贡献大), decline%>0=支撑(逆下降段)")
    print(f"  {'field':32s} {'decline%':>9} {'rise%':>9}  pattern")
    for _, r in dfb.iterrows():
        pat = r.get('pattern', '')
        print(f"  {str(r['field_name'])[:32]:32s} {r['decline_pct']:>8.2f}% "
              f"{r['rise_pct']:>8.2f}%  {pat}")
    print(f"  ── 两段贡献 corr = {corr:+.3f}（正相关 → 非镜像反弹 → 领域换手）")

    yb = np.arange(len(dfb))[::-1]   # 顶部 = rise 最高（Medicine）

    # 连线（浅灰）
    for yi, (_, r) in zip(yb, dfb.iterrows()):
        axB.plot([r['decline_pct'], r['rise_pct']], [yi, yi],
                 color='#C2C2C2', lw=1.2, zorder=2, solid_capstyle='round')

    # 端点：rise = 靛灰（叙事重心，图例首位），decline = 赭黄
    axB.scatter(dfb['rise_pct'], yb, s=34, c=C_DIR_A,
                edgecolors='white', linewidths=0.5, zorder=3,
                label='Rise segment')
    axB.scatter(dfb['decline_pct'], yb, s=34, c=C_DIR_B,
                edgecolors='white', linewidths=0.5, zorder=3,
                label='Decline segment')
    axB.axvline(0, color='#888', lw=0.7, zorder=1)

    axB.set_yticks(yb)
    axB.set_yticklabels([abbrev_field(f) for f in dfb['field_name']],
                        fontsize=FS['tick'] - 0.5)
    axB.set_ylim(-0.8, len(dfb) - 0.2)
    axB.set_xlabel('Contribution to segment ΔRI (%)')
    print_abbrev_legend(dfb['field_name'], title='Fig1 B 纵轴(field)缩写对照')

    # 大刻度每10% + 小刻度每2% + 双层网格
    allpct = np.r_[dfb['rise_pct'].values, dfb['decline_pct'].values]
    x_min, x_max = allpct.min(), allpct.max()
    major_ticks = np.arange(np.floor(x_min / 10) * 10, np.ceil(x_max / 10) * 10 + 1, 10)
    minor_ticks = np.arange(np.floor(x_min / 2) * 2, np.ceil(x_max / 2) * 2 + 1, 2)
    axB.set_xticks(major_ticks)
    axB.set_xticks(minor_ticks, minor=True)
    axB.grid(axis='x', which='major', alpha=0.20, lw=0.5, color='#666')
    axB.grid(axis='x', which='minor', alpha=0.10, lw=0.5, linestyle='--', color='#888')
    span = x_max - x_min
    axB.set_xlim(x_min - span * 0.04, x_max + span * 0.06)

    # corr 标注（右下角）
    axB.text(0.97, 0.03, f'$r$ = {corr:+.2f}\n(decline vs rise)',
             transform=axB.transAxes, ha='right', va='bottom',
             fontsize=FS['annot'], color='#444')
    # legend 放顶部右侧空白区
    axB.legend(loc='upper right', bbox_to_anchor=(1.0, 0.5),
               frameon=False, fontsize=FS['legend'] + 1)
    panel_label(axB, 'B', dx=-0.22, dy=1.02)

    # ---------- 保存 ----------
    save_fig(fig, OUT / 'fig1_phenomenon')
    # 同时在同一输出目录另存一份 PDF（若 save_fig 本身已输出 PDF，此处会以同名文件覆盖）
    fig.savefig(OUT / 'fig1_phenomenon.pdf', bbox_inches='tight')
    plt.close()
    print(f"\n✓ fig1_phenomenon saved to {OUT}/ {'(DEMO data)' if DEMO else ''}")


if __name__ == '__main__':
    main()
