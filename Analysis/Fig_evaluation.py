# -*- coding: utf-8 -*-
"""
旭日图 matplotlib 版 —— 每一圈的内外半径完全由你指定
------------------------------------------------------
和 Plotly 版最大的区别：这里 LEVEL_RADII 里每一圈的宽度是你自己写死的数字，
第一圈（大类）想要多宽就改第一个 tuple 就行，跟其它圈完全独立，
不会像 Plotly 那样被自动等分挤没。
"""

import textwrap
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge

plt.rcParams["font.family"] = "DejaVu Serif"   # 换成 Times New Roman / 宋体 等你需要的字体

# ========== 1. 数据内容（和之前一样，改这里的文字/结构） ==========
CENTER_TEXT = "DS-QA"

DATA = {
    # "Data Summary": [
    #     "Data Accuracy", "Data Context", "Summary Statistics", 
    #     "Intepretation Accuracy", "Intepretation Clarity"
    # ],

    # "Data Visualization and EDA": [
    #     "Completeness", 
    #     "Aesthetic Mapping", "Geometric Object", "Scales & Coordinate System",
    #     "Visualization Validity"
    # ],

    "Linear Regression": [
        "Numerical Accuracy", "Model Interpretation", "P-value",
        "R-squared value & RMSE", "Result Intepretation"
    ],

    "Logistic Regression": [
        "Numerical Accuracy", "Model Interpretation", "P-value",
        "Confusion Matrix", "Result Intepretation"
    ],

    "PCA": [
        "Suitable Variable Selection", "Number of Components Justified", "Standardization ",
        "Correct Variance/Cum. Variance Explanation", "Visual Evidence"
    ],

    "Clustering": [
        "Number of Clusters Justified", "Method Consistency", "Cluster Characteristics",
        "Validation metrics", "Visual Evidence"
    ],

    "Hypotesis Testing": [
        "Correct Test", "Null and Alternative Hypotheses Statement", "P-value\nTest Statistics",
        "Contextual Conclusion"
    ]
}

BRANCH_COLORS = [
    "#F6D186", "#F3C4A4", "#F3B6C8", "#D6BEEC", "#B6D0F0", "#B8E0B0",
    #"#A8DADC", "#D9C89E"
]

# ========== 2. 每一圈的 (内半径, 外半径) —— 想加宽第一圈就改这里第一个元组 ==========
# depth0 = 大类圈（当前设得比其它圈宽很多，方便放长文字）
# depth1 = 子类别圈
# depth2 = 最外层具体指标圈
LEVEL_RADII = [
    (0.55, 1.0),   # depth 0：大类，内半径0.55(留白)，外半径1.55 —— 宽度=1.0，很宽
    (1.0, 1.55),   # depth 1：子类别，宽度=0.5
    (1.55, 2.0),   # depth 2：具体指标，宽度=0.4
]
FIG_SIZE_LIMIT = LEVEL_RADII[-1][1] * 1.15   # 画布留白

# 每一圈的字体大小：[depth0(大类), depth1(子类别), depth2(最外圈指标)]
# 想让最外圈字更大，就改最后一个数字
FONT_SIZES = [15, 10, 15]
# 弧太窄时是否允许自动再缩小字号避免文字重叠压线（False = 完全用上面固定的数字，不自动缩放）
AUTO_SHRINK = True
MIN_FONT_SIZE = 15
# ================================================================


def count_leaves(content):
    """递归统计一个节点下有多少个叶子（用来按比例分配角度）"""
    if content is None:
        return 1
    if isinstance(content, list):
        if len(content) == 0:
            return 1
        return sum(1 for _ in content)
    if isinstance(content, dict):
        return sum(count_leaves(v) for v in content.values())
    return 1


def text_rotation(mid_angle, depth):
    """depth0(大类)保持水平更好读；更深的圈沿半径方向摆放，避免倒着看"""
    if depth == 0:
        return 0
    rot = mid_angle
    if 90 < mid_angle < 270:
        rot += 180
    return rot


def draw_node(ax, label, content, depth, theta1, theta2, color, alpha):
    has_children = isinstance(content, dict) and len(content) > 0
    has_children = has_children or (isinstance(content, list) and len(content) > 0)

    inner, outer = LEVEL_RADII[depth]
    if not has_children:
        # 没有下一级了：这个楔形直接撑到最外圈，和原图里
        # "Data Cleaning Completeness" 这种大块叶子一样
        outer = LEVEL_RADII[-1][1]

    wedge = Wedge((0, 0), outer, theta1, theta2, width=outer - inner,
                   facecolor=color, alpha=alpha, edgecolor="white", linewidth=1.8)
    ax.add_patch(wedge)

    mid_angle = (theta1 + theta2) / 2
    mid_radius = (inner + outer) / 2
    import math
    x = mid_radius * math.cos(math.radians(mid_angle))
    y = mid_radius * math.sin(math.radians(mid_angle))

    span = theta2 - theta1
    fontsize = FONT_SIZES[depth]
    if AUTO_SHRINK and depth > 0:
        # 弧长太窄时才往下压字号，绝不会超过你设定的 FONT_SIZES 上限
        fontsize = max(MIN_FONT_SIZE, min(fontsize, span / 3))
    wrap_width = 14 if depth == 0 else 18
    wrapped = "\n".join(
        line for part in label.split("\n") for line in textwrap.wrap(part, wrap_width) or [part]
    )

    ax.text(x, y, wrapped, ha="center", va="center",
            rotation=text_rotation(mid_angle, depth),
            rotation_mode="anchor", fontsize=fontsize, color="black")

    if not has_children:
        return

    local_total = count_leaves(content)
    theta = theta1
    if isinstance(content, dict):
        for child_label, child_content in content.items():
            child_leaves = count_leaves(child_content)
            child_span = span * child_leaves / local_total
            draw_node(ax, child_label, child_content, depth + 1,
                      theta, theta + child_span, color, alpha)
            theta += child_span
    elif isinstance(content, list):
        for leaf_label in content:
            child_span = span * 1 / local_total
            draw_node(ax, leaf_label, None, depth + 1,
                      theta, theta + child_span, color, alpha)
            theta += child_span


fig, ax = plt.subplots(figsize=(11, 11), subplot_kw=dict(aspect="equal"))

total_leaves = sum(count_leaves(v) for v in DATA.values())
theta = 0
for i, (cat_label, cat_content) in enumerate(DATA.items()):
    span = 360 * count_leaves(cat_content) / total_leaves
    draw_node(ax, cat_label, cat_content, 0, theta, theta + span,
              BRANCH_COLORS[i % len(BRANCH_COLORS)], alpha=1.0)
    theta += span

# 中心白圆 + 文字
ax.add_patch(plt.Circle((0, 0), LEVEL_RADII[0][0], facecolor="white",
                         edgecolor="none", zorder=5))
ax.text(0, 0, CENTER_TEXT, ha="center", va="center", fontsize=15,
        fontweight="bold", zorder=6)

ax.set_xlim(-FIG_SIZE_LIMIT, FIG_SIZE_LIMIT)
ax.set_ylim(-FIG_SIZE_LIMIT, FIG_SIZE_LIMIT)
ax.axis("off")
plt.tight_layout()
plt.savefig("sunburst_matplotlib.png", dpi=200, bbox_inches="tight")
print("done")