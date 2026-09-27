"""
fig3_reconfiguration.py — Section 3 组图：AI 自我范式重构
=================================================
组图布局（2 panel，并排）：
  A（左）：AI vs Statistics 入度 vs 出度散点（双向迁移；对角线=双向）
  B（右）：AI ↔ Statistics 相互引用份额反转折线（两时间点 + 两期排名）

主线：AI 不是回升驱动者，而是停滞的成熟方法枢纽，正脱离数理/统计母体、迁向医工；
其中"AI 取代 Statistics 成方法核心"（Panel B 的份额不对称）是最尖锐体现。
（subfield 级落点细节放正文/SI，图上不再铺开。）

【数据来源】./output/final/ 下：
  - s3/s3_23_ai_stats_inout.csv          （A：subfield, field_name, in_delta, out_delta）
  - s3/s3_24_ai_stats_cited_subfields.csv（B：由它提取 AI↔Stats 相互引用的
        base/end 份额 + 两期排名）

【运行】
  正式：  python fig3_reconfiguration.py
  预览：  python fig3_reconfiguration.py --demo

【输出】./figures_final/output/fig3_reconfiguration.png + .pdf
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

sys.path.insert(0, str(Path(__file__).parent))
from figstyle import (apply_base_style, panel_label, save_fig, FS,
                      C_REF, C_AI, C_STATS, abbrev_field)

DEMO = '--demo' in sys.argv
DATA = Path('./output/final')
OUT = Path(__file__).parent / 'output'
OUT.mkdir(parents=True, exist_ok=True)

# AI / Statistics 的显示全称：与 fig2 Panel C 的 y 轴（readable 模式、全显）保持一致。
AI_FULL = 'Artificial Intelligence'
STATS_FULL = 'Statistics and Probability'


def load_data():
    if DEMO:
        rng = np.random.default_rng(3)
        # AI + Stats 入出度(两者同框对比)
        infields = ['Medicine', 'Engineering', 'Social Sciences', 'Environmental',
                    'Energy', 'Health Prof', 'Arts & Hum.', 'Psychology',
                    'Physics', 'Mathematics', 'Biochem', 'Decision Sci']
        ai_in = [3.5, 2.9, 0.4, 1.3, 0.9, 0.6, -0.8, -0.9, -1.6, -1.7, -1.3, -0.9]
        ai_out = [3.2, 2.0, 1.3, 1.05, 0.95, 0.55, -1.2, -1.15, -1.9, -2.4, -1.15, -0.9]
        st_in = [3.0, 0.8, 0.2, 0.1, -0.1, 0.05, -0.1, -0.1, 0.3, 0.0, 0.2, -0.7]
        st_out = [0.6, 0.98, -0.3, 0.0, 0.05, -0.1, 0.0, -0.95, -0.05, 0.05, 0.0, 0.92]
        inout = pd.concat([
            pd.DataFrame({'subfield': 'AI', 'field_name': infields,
                          'in_delta': ai_in, 'out_delta': ai_out}),
            pd.DataFrame({'subfield': 'Statistics', 'field_name': infields,
                          'in_delta': st_in, 'out_delta': st_out}),
        ], ignore_index=True)
        # 反转对比数据：两个时间点的份额 + 两期排名
        reversal = pd.DataFrame([
            {'direction': 'Statistics → AI', 'share_base': 9.01, 'share_end': 8.78,
             'delta': -0.23, 'rank_base': 1, 'rank_end': 1, 'total': 242},
            {'direction': 'AI → Statistics', 'share_base': 3.47, 'share_end': 2.39,
             'delta': -1.08, 'rank_base': 6, 'rank_end': 9, 'total': 241},
        ])
        return inout, reversal

    inout = pd.read_csv(DATA / 's3/s3_23_ai_stats_inout.csv')  # 含 AI + Statistics
    cited = pd.read_csv(DATA / 's3/s3_24_ai_stats_cited_subfields.csv')
    cited = cited[cited['exclude_own_field'] == True]  # 含 AI + Statistics

    # 反转折线（Panel B）：从 cited 提取 AI↔Stats 相互引用的 base/end 份额 + 两期排名
    def _extract(citing, target_id):
        d = cited[cited['citing_subfield'] == citing].copy()
        # end 期排名
        de = d.sort_values('share_end', ascending=False).reset_index(drop=True)
        de['rank_end'] = de.index + 1
        # base 期排名
        db = d.sort_values('share_base', ascending=False).reset_index(drop=True)
        db['rank_base'] = db.index + 1
        re_ = de[de['target_subfield_id'] == target_id]
        rb_ = db[db['target_subfield_id'] == target_id]
        if len(re_):
            re_ = re_.iloc[0]
            rank_base = int(rb_.iloc[0]['rank_base']) if len(rb_) else -1
            return dict(share_base=re_['share_base'], share_end=re_['share_end'],
                        delta=re_['delta_share'], rank_base=rank_base,
                        rank_end=int(re_['rank_end']), total=len(d))
        return dict(share_base=0, share_end=0, delta=0, rank_base=-1,
                    rank_end=-1, total=len(d))
    AI_ID, STATS_ID = 1702, 2613
    s2a = _extract('Statistics', AI_ID)    # Statistics → AI
    a2s = _extract('AI', STATS_ID)         # AI → Statistics
    reversal = pd.DataFrame([
        {'direction': 'Statistics → AI', **s2a},
        {'direction': 'AI → Statistics', **a2s},
    ])
    return inout, reversal


def print_panelB_check(reversal):
    """Panel B 核查打印（demo / 真实都调用，打印的就是画图用的数据）。"""
    print("\n" + "=" * 70)
    print("【Panel B 核查】AI ↔ Statistics 相互引用份额（与图上同源）")
    print("=" * 70)
    print(f"  {'方向':<18} {'base份额':>9} {'base排名':>8} {'end份额':>9} {'end排名':>8} {'Δ':>8}")
    for _, r in reversal.iterrows():
        print(f"  {r['direction']:<18} {r['share_base']:>8.2f}% "
              f"{('#'+str(int(r['rank_base']))):>8} {r['share_end']:>8.2f}% "
              f"{('#'+str(int(r['rank_end']))):>8} {r['delta']:>+8.2f}")
    print("  —— 核对: Statistics→AI 当前应 8.78%/#1; AI→Statistics 应 2.39%/#9。")
    print("=" * 70 + "\n")


def main():
    apply_base_style()
    inout, reversal = load_data()

    fig = plt.figure(figsize=(11.5, 4.7))
    gs = GridSpec(1, 2, figure=fig, width_ratios=[1.0, 1.0], wspace=0.28,
                  left=0.085, right=0.97, top=0.90, bottom=0.16)
    axA = fig.add_subplot(gs[0, 0])   # Panel A: 入出度散点
    axB = fig.add_subplot(gs[0, 1])   # Panel B: 反转折线

    # ---------- Panel A: AI vs Statistics 入度 vs 出度（同框对比） ----------
    from figstyle import C_AI, C_STATS
    allv = np.r_[inout['in_delta'].values, inout['out_delta'].values]
    lim = np.nanmax(np.abs(allv)) * 1.18
    axA.plot([-lim, lim], [-lim, lim], ls=(0, (4, 3)), color=C_REF, lw=1.0,
             zorder=1)
    style = {'AI': dict(marker='o', c=C_AI, label=f'{AI_FULL} (AI)'),
             'Statistics': dict(marker='^', c=C_STATS, label=f'{STATS_FULL} (S&P)')}
    for sf, st in style.items():
        d = inout[inout['subfield'] == sf]
        axA.scatter(d['in_delta'], d['out_delta'], s=36, marker=st['marker'],
                    facecolors=st['c'], edgecolors='white', linewidths=0.5,
                    alpha=0.85, label=st['label'], zorder=3)
    axA.axhline(0, color='#ccc', lw=0.5); axA.axvline(0, color='#ccc', lw=0.5)
    axA.set_xlim(-lim, lim); axA.set_ylim(-lim, lim)
    # 标注两组各自偏离最大的点（同时收集被标点供核查打印）
    labeled_pts = []
    for sf, st in style.items():
        d = inout[inout['subfield'] == sf]
        for _, r in d.iterrows():
            off = abs(r['in_delta'] - r['out_delta'])  # 离对角线距离
            mag = max(abs(r['in_delta']), abs(r['out_delta']))
            # AI: 同时标右上(医工迁入)和左下(数理迁出)的大点; Stats: 标偏离对角线大的
            label_it = False
            if sf == 'AI':
                if mag > lim * 0.45:   # 右上+左下两端的大点都标
                    label_it = True
            else:
                if off > lim * 0.35 or abs(r['in_delta']) > lim * 0.55:
                    label_it = True
            if label_it:
                fx, fy = r['in_delta'], r['out_delta']
                # 左下象限标签朝左下偏移, 右上朝右上, 减少压线
                dx = 4 if fx >= 0 else -4
                dy = 4 if fy >= 0 else -9
                ha = 'left' if fx >= 0 else 'right'
                axA.annotate(abbrev_field(r['field_name']), (fx, fy),
                             xytext=(dx, dy), textcoords='offset points',
                             fontsize=FS['annot'] - 1.5, color=st['c'], ha=ha)
                # 象限/pattern 判定（更精细，识别单向被取用）
                if fx < 0 and fy < 0:
                    quad = '左下/双向减(迁出数理)'
                elif fx > 0 and fy > 0:
                    # 入出都正，但若出度远小于入度则是"单向被取用"
                    if fy < fx * 0.4:
                        quad = '右下偏/入>>出(单向被取用)'
                    else:
                        quad = '右上/双向增(迁入医工)'
                elif fx > 0 and fy < 0:
                    quad = '右下/入增出减(被取用)'
                else:
                    quad = '左上/入减出增'
                labeled_pts.append((sf, str(r['field_name']), fx, fy, quad))

    # === 核查打印: 图上 Panel A 实际标注了哪些点（与真实数据逐一对照）===
    print("\n" + "=" * 64)
    print("【Panel A 核查】图上实际标注的点（标签直接取自数据 field_name 列）")
    print("=" * 64)
    print(f"  {'对象':<5} {'field_name':<24} {'in_delta':>9} {'out_delta':>10}  象限/含义")
    for sf, name, fx, fy, quad in labeled_pts:
        print(f"  {sf:<5} {str(name)[:24]:<24} {fx:>9.2f} {fy:>10.2f}  {quad}")
    print("  —— 请核对: AI 落在'左下/双向减'的应为数理领域(如 Mathematics/Physics),")
    print("     '右上/双向增'的应为医工领域(如 Medicine/Engineering)。")
    print("=" * 64 + "\n")

    axA.set_xlabel('In-citation Δshare (pp)')
    axA.set_ylabel('Out-citation Δshare (pp)')
    axA.legend(loc='lower right', frameon=False, fontsize=FS['legend'] - 0.5,
               handletextpad=0.3)
    axA.grid(alpha=0.18, lw=0.5)
    panel_label(axA, 'A', dx=-0.10, dy=1.04)

    # ---------- Panel B: AI ↔ Statistics 相互引用份额的演变（反转折线） ----------
    print_panelB_check(reversal)   # 核查打印(demo/真实都打印, 与图同源)
    from figstyle import C_AI, C_STATS
    rev = reversal.copy()
    xpos = [0, 1]
    xlabels = ['2004–2013', '2014–2023']
    line_sty = [
        dict(color=C_STATS, marker='^', label='S&P → AI'),
        dict(color=C_AI, marker='o', label='AI → S&P'),
    ]
    for i, (_, r) in enumerate(rev.iterrows()):
        st = line_sty[i]
        yv = [r['share_base'], r['share_end']]
        axB.plot(xpos, yv, '-', color=st['color'], lw=2.4, marker=st['marker'],
                 ms=8, mfc=st['color'], mec='white', mew=1.2, zorder=3,
                 label=st['label'])
        # 起点: base 份额 + base 排名（标左）
        axB.text(-0.04, yv[0], f"{yv[0]:.2f}%\n(rank #{int(r['rank_base'])})",
                 va='center', ha='right', fontsize=FS['annot'], color=st['color'])
        # 终点: end 份额 + end 排名（标右，加粗）
        axB.text(1.04, yv[1], f"{yv[1]:.2f}%\n(rank #{int(r['rank_end'])})",
                 va='center', ha='left', fontsize=FS['annot'], fontweight='bold',
                 color=st['color'])
        # 斜率旁标变化量
        axB.text(0.5, (yv[0] + yv[1]) / 2 + (0.35 if i == 0 else -0.55),
                 f"Δ {r['delta']:+.2f}", ha='center', va='center',
                 fontsize=FS['annot'], color=st['color'], fontweight='bold')
    axB.set_xticks(xpos)
    axB.set_xticklabels(xlabels)
    axB.set_xlim(-0.45, 1.55)
    ymax = max(rev['share_base'].max(), rev['share_end'].max())
    axB.set_ylim(0, ymax * 1.18)
    axB.set_ylabel('Mutual out-citation share (%)')
    axB.grid(axis='y', alpha=0.2, lw=0.5)
    h, l = axB.get_legend_handles_labels()
    axB.legend(h[::-1], l[::-1], loc='lower left', frameon=False, fontsize=FS['legend'] - 0.5)
    panel_label(axB, 'B', dx=-0.14, dy=1.04)

    save_fig(fig, OUT / 'fig3_reconfiguration')
    # 同时在同一输出目录另存一份 PDF（若 save_fig 本身已输出 PDF，此处会以同名文件覆盖）
    fig.savefig(OUT / 'fig3_reconfiguration.pdf', bbox_inches='tight')
    plt.close()
    print(f"✓ fig3_reconfiguration saved {'(DEMO)' if DEMO else ''}")


if __name__ == '__main__':
    main()
