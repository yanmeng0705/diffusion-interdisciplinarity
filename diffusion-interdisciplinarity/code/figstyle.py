"""
figstyle.py — 组图统一样式（所有 figN_*.py 共享）
=================================================
定义出版级图表的统一规范：字号层级、克制配色、panel 标号、轴样式。
所有组图脚本 import 本模块，保证全文图风格一致。

设计原则（顶刊惯例）：
- 无图内标题（标题写进 figure caption，排版时单独处理）
- panel 标号 A/B/C 左上角大写粗体
- 无衬线字体 Arial，TrueType 嵌入 PDF
- 克制配色：低饱和，避免鲜红鲜绿；正负用红蓝对，方向用中性对
- 去顶部/右侧边框，刻度朝外
"""

import matplotlib as mpl
import matplotlib.pyplot as plt

# ============ 字号层级（统一一套） ============
FS = {
    'panel_label': 13,   # panel 字母 A/B/C
    'axis_label': 10,    # 轴标题
    'tick': 8.5,         # 刻度数字
    'annot': 8,          # 图内注释/数据标签
    'legend': 8.5,       # 图例
    'cbar_label': 9,     # colorbar 标题
}

# ============ 克制配色 ============
# 正/负（发散）：低饱和红蓝，替代鲜红鲜绿
C_POS = '#3B6FB6'      # 正：沉静蓝
C_NEG = '#C0504D'      # 负：砖红
# 方向对（双向检验等）：中性靛/赭
C_DIR_A = '#4E6E81'    # 方向一：靛灰
C_DIR_B = '#D08C34'    # 方向二：赭黄
# 四象限分类（低饱和）
C_QUAD = {
    'core_driver': '#2E6E4E',   # 沉绿
    'established': '#3B6FB6',    # 沉蓝
    'riser':       '#D08C34',   # 赭
    'stable_low':  '#A8A8A8',   # 灰
}
# 强调点
C_AI = '#1F4E79'       # AI 深蓝
C_STATS = '#9E2B25'    # Stats 深红
C_HIGHLIGHT = '#2E6E4E'  # 极值点绿圈
# 发散 colormap（热图）
CMAP_DIV = 'RdBu_r'
# 中性灰（散点、参考线）
C_GREY = '#6E6E6E'
C_REF = '#9DB4C8'      # 参考线浅蓝灰
C_NEUTRAL_BAR = '#7A8B99'

# ============ domain 配色（所有图统一） ============
# 键名：全称（OpenAlex 原始 domain 名称），颜色取自 fig2 定稿配色
DOMAIN_COLORS = {
    'Health Sciences':    '#C0504D',   # 砖红
    'Life Sciences':      '#2E6E4E',   # 深绿
    'Physical Sciences':  '#3B6FB6',   # 沉蓝
    'Social Sciences':    '#8B6CB0',   # 紫色
}

# ============ 全部 26 field → domain 映射（OpenAlex，全文统一） ============
# 键名 = field 全称（与 s2/s4 等 csv 中 field_name 一致），大小写敏感。
# 所有 figN 脚本共用，无需再依赖 all_topics.csv 的列名。
FIELD_TO_DOMAIN = {
    # Physical Sciences (10)
    'Computer Science':              'Physical Sciences',
    'Engineering':                   'Physical Sciences',
    'Environmental Science':         'Physical Sciences',
    'Materials Science':             'Physical Sciences',
    'Energy':                        'Physical Sciences',
    'Mathematics':                   'Physical Sciences',
    'Chemical Engineering':          'Physical Sciences',
    'Chemistry':                     'Physical Sciences',
    'Earth and Planetary Sciences':  'Physical Sciences',
    'Physics and Astronomy':         'Physical Sciences',
    # Health Sciences (6)
    'Medicine':                                       'Health Sciences',
    'Health Professions':                              'Health Sciences',
    'Nursing':                                         'Health Sciences',
    'Dentistry':                                       'Health Sciences',
    'Veterinary':                                      'Health Sciences',
    'Pharmacology, Toxicology and Pharmaceutics':      'Health Sciences',
    # Life Sciences (4)
    'Biochemistry, Genetics and Molecular Biology':    'Life Sciences',
    'Agricultural and Biological Sciences':            'Life Sciences',
    'Immunology and Microbiology':                     'Life Sciences',
    'Neuroscience':                                    'Life Sciences',
    # Social Sciences (6)
    'Social Sciences':                                 'Social Sciences',
    'Business, Management and Accounting':             'Social Sciences',
    'Economics, Econometrics and Finance':              'Social Sciences',
    'Psychology':                                      'Social Sciences',
    'Decision Sciences':                               'Social Sciences',
    'Arts and Humanities':                              'Social Sciences',
}


def apply_base_style():
    """全局 rcParams。每个组图脚本开头调用一次。"""
    mpl.rcParams.update({
        'figure.dpi': 120,
        'savefig.dpi': 300,                 # 出版级
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'Helvetica Neue',
                            'DejaVu Sans', 'Liberation Sans'],
        'font.size': FS['tick'],
        'axes.titlesize': FS['axis_label'],
        'axes.labelsize': FS['axis_label'],
        'xtick.labelsize': FS['tick'],
        'ytick.labelsize': FS['tick'],
        'legend.fontsize': FS['legend'],
        'axes.unicode_minus': False,
        'pdf.fonttype': 42,                 # TrueType 嵌入
        'ps.fonttype': 42,
        'axes.linewidth': 0.8,
        'xtick.direction': 'out',
        'ytick.direction': 'out',
        'xtick.major.width': 0.8,
        'ytick.major.width': 0.8,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'figure.facecolor': 'white',
        'savefig.facecolor': 'white',
        'savefig.bbox': 'tight',
    })


def panel_label(ax, letter, dx=-0.02, dy=1.04, fontsize=None):
    """在 ax 左上角加 panel 字母（A/B/C），大写粗体。
    dx/dy 为 axes 坐标系偏移（可微调）。"""
    ax.text(dx, dy, letter, transform=ax.transAxes,
            fontsize=fontsize or FS['panel_label'], fontweight='bold',
            va='bottom', ha='right')


def clean_axes(ax):
    """去顶部右侧边框（base style 已设，但子图保险起见再调一次）。"""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def save_fig(fig, path_noext, formats=('png', 'pdf')):
    """统一保存 png + pdf。"""
    for fmt in formats:
        fig.savefig(f"{path_noext}.{fmt}", bbox_inches='tight')


# ============ 统一的标签缩写规则（全文所有图共用） ============
# 连接词（缩写时略去）
_ABBR_CONN = {'and', '&', 'of', 'the'}

# 始终生效的显示覆盖（不受 use_aliases 影响，最高优先级）。
# 用于必须全局一致的消歧显示：例如两个易混的 Statistics 子领域。
LABEL_OVERRIDES = {
    'statistics, probability and uncertainty': 'Statistics, Prob. & Uncert.',
}

# 仅 use_aliases=True 时生效的强制简称（空间紧处用，如 x 轴 / fig3 / Panel A）。
# 空间充裕处（fig2 Panel C 的 y 轴）传 use_aliases=False，即不强制简称、显示更全。
LABEL_ALIASES = {
    'artificial intelligence': 'AI',
    'statistics and probability': 'Statistics',
}


def _norm(s):
    """别名匹配用的归一化：小写 + 折叠空白。"""
    return ' '.join(str(s).strip().lower().split())


def _abbrev_readable(raw, budget=28, nletters=3):
    """可读缩写：保留所有词，'and'→'&'，of/the 作小写连接词保留，
    首词保护，从最右词起逐个缩到 nletters 字母，直到长度 <= budget。
    尽量多保留全词，让全名轮廓可辨（用于空间充裕的 y 轴）。"""
    toks = []
    for w in raw.replace(',', ' ').split():
        toks.append('&' if w.lower() == 'and' else w)
    if not toks:
        return raw
    noabbr = {'&', 'of', 'the'}
    elig = [i for i in range(1, len(toks)) if toks[i].lower() not in noabbr]

    def render(abset):
        return ' '.join((w[:nletters].rstrip('.') + '.') if i in abset else w
                        for i, w in enumerate(toks))
    abset, s = set(), render(set())
    for i in reversed(elig):
        if len(s) <= budget:
            break
        abset.add(i)
        s = render(abset)
    return s


def abbrev_field(name, threshold=18, nletters=3, use_aliases=True, mode='compact'):
    """field / subfield 轴标签的统一缩写规则。

    - LABEL_OVERRIDES 命中 → 固定显示（始终生效，最高优先级）；
    - use_aliases 且命中 LABEL_ALIASES → 强制简称；
    - 全称长度 <= threshold → 原样全显；
    - 否则按 mode 缩写：
        'compact' （默认，x 轴等紧凑处）：首词全拼 + 第二实词缩写，丢弃其余 → 最短。
        'readable'（空间充裕的 y 轴）：保留所有词、从右往左按需缩 → 全名轮廓可辨。

    仅用于显示。任何 domain 归类、列/行排序、数据匹配都必须基于全称，
    不要使用本函数的输出。
    """
    raw = str(name).strip()
    key = _norm(raw)
    if key in LABEL_OVERRIDES:          # 始终生效（最高优先级）
        return LABEL_OVERRIDES[key]
    if use_aliases:
        alias = LABEL_ALIASES.get(key)
        if alias is not None:
            return alias
    if len(raw) <= threshold:
        return raw
    if mode == 'readable':
        return _abbrev_readable(raw, budget=threshold, nletters=nletters)
    words = [w for w in raw.replace(',', ' ').split()
             if w.lower() not in _ABBR_CONN]
    if not words:
        return raw
    if len(words) == 1:
        return words[0]
    return f"{words[0]} {words[1][:nletters].rstrip('.')}."


def abbrev_pairs(names, threshold=18, nletters=3, use_aliases=True, mode='compact'):
    """返回 [(显示, 全称), ...]，仅含被缩写者，按出现顺序去重。供 caption 用。"""
    seen, out = set(), []
    for n in names:
        full = str(n)
        disp = abbrev_field(full, threshold, nletters, use_aliases, mode)
        if disp != full and full not in seen:
            seen.add(full)
            out.append((disp, full))
    return out


def label_collisions(names, threshold=18, nletters=3, use_aliases=True, mode='compact'):
    """检测撞名：不同全称 → 同一显示标签。返回 {显示: [全称, ...]}（仅含冲突项）。"""
    uniq = list(dict.fromkeys(str(n) for n in names))
    rev = {}
    for n in uniq:
        rev.setdefault(abbrev_field(n, threshold, nletters, use_aliases, mode),
                       []).append(n)
    return {d: ns for d, ns in rev.items() if len(ns) > 1}


def print_abbrev_legend(names, title='缩写对照', threshold=18, nletters=3,
                        use_aliases=True, mode='compact'):
    """统一格式打印『轴上显示 = 全称』对照（仅列被缩写者）+ 撞名警告，供 caption 用。"""
    pairs = abbrev_pairs(names, threshold, nletters, use_aliases, mode)
    print("\n" + "=" * 64)
    print(f"【{title}】轴上显示 = 全称（仅列被缩写者）")
    print("=" * 64)
    if not pairs:
        print("  （无被缩写项，全部全显）")
    for disp, full in pairs:
        print(f"  {disp:<28} = {full}")
    collisions = label_collisions(names, threshold, nletters, use_aliases, mode)
    if collisions:
        print("  " + "-" * 60)
        print("  ⚠ 撞名警告：不同全称缩成同一标签，请在 LABEL_OVERRIDES 中区分 ↓")
        for disp, fulls in collisions.items():
            print(f"    [{disp}]  <=  {' ｜ '.join(fulls)}")
    print("=" * 64 + "\n")