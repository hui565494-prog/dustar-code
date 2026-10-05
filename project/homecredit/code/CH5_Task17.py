import warnings
import pandas as pd
import plotly.express as px

# 忽略警告信息
warnings.filterwarnings("ignore")
# 1. 读取训练集
app_train = pd.read_csv("data/application_train.csv")
# 2. 指定绘制的类别列
category_cols = [
    "NAME_INCOME_TYPE",
    "NAME_EDUCATION_TYPE",
    "NAME_FAMILY_STATUS",
]
# 3. 三张图保存到同一个 HTML 文件中
html_path = "指导书code/tmp/category_bar_by_target.html"
# 存放绘图对象
fig_list = []

for col in category_cols:
    plot_df = app_train[[col, "TARGET"]].copy()  # 复制需要用到的列，避免修改原始数据
    plot_df[col] = plot_df[col].fillna("Missing")  # 缺失值单独显示成 Missing
    # 统计每个类别在 TARGET=0 和 TARGET=1 下分别有多少条数据
    count_df = plot_df.groupby([col, "TARGET"]).size().reset_index(name="COUNT")
    # 按每个类别的总数量从大到小排序
    total_count_df = (
        count_df.groupby(col)["COUNT"]
        .sum()
        .reset_index()
        .sort_values("COUNT", ascending=False)
    )
    category_order = total_count_df[col].tolist()
    count_df["TARGET"] = count_df["TARGET"].map(
        {
            0: "Target = 0",
            1: "Target = 1",
        }
    )
    # 绘制分组柱形图：同一个类别下，用不同颜色区分 TARGET=0/1
    fig = px.bar(
        count_df,
        x=col,
        y="COUNT",
        color="TARGET",
        barmode="group",
        text="COUNT",
        title=f"{col} 在不同 Target 下的类别数量",
        labels={
            col: "类别",
            "COUNT": "数量",
            "TARGET": "Target",
        },
        color_discrete_map={
            "Target = 0": "#4C78A8",
            "Target = 1": "#F58518",
        },
        category_orders={col: category_order},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_tickangle=-30,
        yaxis_title="数量",
        xaxis_title="类别",
        xaxis_title_standoff=5,
        bargap=0.25,
        legend_title_text="Target",
        legend=dict(
            x=0.98,
            y=0.98,
            xanchor="right",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.7)",
        ),
        margin=dict(t=60),
        height=600,
        width=1000,
    )
    fig_list.append(fig)

# 先写入第一张图，并加载 plotly.js
fig_list[0].write_html(
    html_path,
    include_plotlyjs=True,
    full_html=True,
)

# 再把后两张图追加到同一个 HTML 文件
with open(html_path, "a", encoding="utf-8") as f:
    for fig in fig_list[1:]:
        f.write(fig.to_html(include_plotlyjs=False, full_html=False))

print(f"已经保存 HTML 文件：{html_path}")
print("完成 3 张按 Target=0/1 区分颜色的类别柱形图。")
