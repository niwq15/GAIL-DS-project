"""
Sunburst Chart Template

旭日图 / 多层环形层级图 (Sunburst Chart) 生成模板
--------------------------------------------------
只需要改下面 DATA 这个嵌套字典里的文字/结构，图就会自动重新排布。
每个顶层 key 是一个"任务大类"，会自动分配一个底色；
其下可以是：
  - 一个 list（叶子节点，直接铺满到最外圈）
  - 一个 dict（继续往下再分一层子类别）
支持 "深度不一致" 的分支（比如某个大类下有的子项直接到叶子，
有的子项还要再往下分一层），这正是原图里橙色/绿色扇区的结构。
"""

import plotly.graph_objects as go

# ========== 1. 在这里改你的文字内容 ==========
CENTER_TEXT = "6 task types<br><b style='font-size:22px'>DataSciBench</b><br>25 aggregate functions"

DATA = {
    "Data Exploration &<br>Statistics Understand": [
        "Data Accuracy", "Data Integrity", "Data Consistency",
        "Data Validity", "Data Uniformity",
    ],
    "Data Cleaning &<br>Preprocessing": {
        "Data Quality Score": [
            "Normalization<br>Range Check", "Data Completeness", "DataFrame Shape<br>Validation",
        ],
        "Data Cleaning Completeness": [],   # 空list = 该子类本身就是叶子，撑满到最外圈
    },
    "Interpre. & RG": [
        "Result Comple.", "Report Quality", "Report Comple.",
    ],
    "DM & PR": [
        "Clustering Validity", "Silhouette Score",
    ],
    "Data Visualization": {
        "Visualization Completeness": [],
        "Plot Validity": [],
        "Visualization Quality": ["Title Verification"],
    },
    "Predictive Modeling": {
        "Model Accuracy": ["MAE", "R-squared Value"],
        "Clustering Validity": [],
    },
}

# 每个大类的底色（可自由换成 hex 色号）
BRANCH_COLORS = [
    "#F6D186", "#F3C4A4", "#F3B6C8", "#D6BEEC", "#B6D0F0", "#B8E0B0",
]
# ================================================


def build_hierarchy(data, colors):
    ids, labels, parents, colors_out = [], [], [], []
    color_map = {}

    def walk(node_label, node_content, parent_id, path, color):
        this_id = path
        ids.append(this_id)
        labels.append(node_label)
        parents.append(parent_id)
        colors_out.append(color)

        if isinstance(node_content, dict):
            for child_label, child_content in node_content.items():
                walk(child_label, child_content, this_id, f"{path}/{child_label}", color)
        elif isinstance(node_content, list):
            for child_label in node_content:
                child_id = f"{path}/{child_label}"
                ids.append(child_id)
                labels.append(child_label)
                parents.append(this_id)
                colors_out.append(color)

    for i, (top_label, top_content) in enumerate(data.items()):
        color = colors[i % len(colors)]
        walk(top_label, top_content, "", top_label, color)

    return ids, labels, parents, colors_out


ids, labels, parents, colors_out = build_hierarchy(DATA, BRANCH_COLORS)

fig = go.Figure(go.Sunburst(
    ids=ids,
    labels=labels,
    parents=parents,
    branchvalues="total",
    marker=dict(
        colors=colors_out,
        line=dict(color="white", width=2),
    ),
    insidetextorientation="radial",
    sort=False,
    textfont=dict(family="Times New Roman, Georgia, serif", size=13, color="black"),
))

fig.update_layout(
    width=950, height=950,
    margin=dict(t=20, l=20, r=20, b=20),
    paper_bgcolor="white",
)

# 因为 Sunburst 本身没有 hole 参数，用一个白色圆形图层盖住中心，
# 再在上面叠加文字，做出"中心留白+文字"的视觉效果
HOLE_RADIUS = 0.1  # 相对画布的半径比例，越大中心留白越大
fig.add_shape(
    type="circle", xref="paper", yref="paper",
    x0=0.5 - HOLE_RADIUS, y0=0.5 - HOLE_RADIUS,
    x1=0.5 + HOLE_RADIUS, y1=0.5 + HOLE_RADIUS,
    fillcolor="white", line=dict(color="white", width=0), layer="above",
)
fig.add_annotation(
    text=CENTER_TEXT, x=0.5, y=0.5, xref="paper", yref="paper",
    font=dict(family="Times New Roman, Georgia, serif", size=15, color="black"),
    showarrow=False, align="center",
)

fig.write_html("sunburst_chart.html")
try:
    fig.write_image("sunburst_chart.png", scale=3)
except Exception as e:
    print("PNG导出跳过（本机没有Chrome内核，本地运行 pip install -U kaleido 后会自动可用）:", e)
print("done")
