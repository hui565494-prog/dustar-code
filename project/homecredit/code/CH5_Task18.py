import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import gaussian_kde

warnings.filterwarnings("ignore")


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "tmp" / "application_train_visual.csv"
HTML_PATH = BASE_DIR / "tmp" / "kde_selected_features.html"


TIME_FEATURES = [
    "AGE_YEARS",
    "EMPLOYED_YEARS",
    "REGISTRATION_YEARS",
]

EXT_SOURCE_FEATURES = [
    "EXT_SOURCE_1",
    "EXT_SOURCE_2",
    "EXT_SOURCE_3",
]

TARGET_COLORS = {
    0: "#2563eb",
    1: "#dc2626",
}


def kde_values(series, points=300):
    """Return KDE x/y values after dropping missing and invalid values."""
    data = (
        pd.to_numeric(series, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
    )

    if data.nunique() < 2:
        return None, None

    x_values = np.linspace(data.min(), data.max(), points)
    y_values = gaussian_kde(data)(x_values)
    return x_values, y_values


def add_kde_trace(fig, series, name, color=None, dash=None):
    x_values, y_values = kde_values(series)
    if x_values is None:
        print(f"跳过 {name}: 有效取值不足，无法计算 KDE")
        return

    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=y_values,
            mode="lines",
            name=name,
            line=dict(color=color, dash=dash),
        )
    )


# 构建特征比较图
def build_feature_compare_figure(app, title, features):
    fig = go.Figure()

    for feature in features:
        add_kde_trace(fig, app[feature], feature)

    fig.update_layout(
        title=title,
        xaxis_title="Feature value",
        yaxis_title="Density",
        height=600,
        width=1000,
        legend_title_text="Feature",
        legend=dict(
            x=0.98,
            y=0.98,
            xanchor="right",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.7)",
        ),
        margin=dict(t=70, l=70, r=40, b=60),
    )
    return fig


# 构建按 TARGET 分组的特征比较图
def build_target_compare_figure(app, feature):
    fig = go.Figure()

    for target_value in [0, 1]:
        target_data = app.loc[app["TARGET"] == target_value, feature]
        add_kde_trace(
            fig,
            target_data,
            name=f"TARGET={target_value}",
            color=TARGET_COLORS[target_value],
        )
    fig.update_layout(
        title=f"{feature} KDE by TARGET",
        xaxis_title=feature,
        yaxis_title="Density",
        height=600,
        width=1000,
        legend_title_text="TARGET",
        legend=dict(
            x=0.98,
            y=0.98,
            xanchor="right",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.7)",
        ),
        margin=dict(t=70, l=70, r=40, b=60),
    )
    return fig


def save_figures(figures, html_path):
    html_path.parent.mkdir(parents=True, exist_ok=True)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(
            "<html><head><meta charset='utf-8'><title>KDE Selected Features</title></head><body>\n"
        )
        for index, fig in enumerate(figures):
            f.write(fig.to_html(include_plotlyjs=(index == 0), full_html=False))
            f.write("\n<hr>\n")
        f.write("</body></html>\n")


def main():
    app = pd.read_csv(DATA_PATH)

    required_columns = [
        "TARGET",
        *TIME_FEATURES,
        *EXT_SOURCE_FEATURES,
    ]  # 将需要用到的列名放在一个列表里
    missing_columns = [col for col in required_columns if col not in app.columns]
    if missing_columns:
        raise ValueError(f"数据缺少必要字段: {missing_columns}")

    figures = []

    # 1. AGE / EMPLOYED / REGISTRATION 三条曲线画在同一张图里。
    figures.append(
        build_feature_compare_figure(
            app,
            "AGE / EMPLOYED / REGISTRATION KDE",
            TIME_FEATURES,
        )
    )

    # 2. AGE / EMPLOYED / REGISTRATION 分别按 TARGET=0/1 画三张图。
    for feature in TIME_FEATURES:
        figures.append(build_target_compare_figure(app, feature))

    # 3. EXT_SOURCE_1 / EXT_SOURCE_2 / EXT_SOURCE_3 三条曲线画在同一张图里。
    figures.append(
        build_feature_compare_figure(
            app,
            "EXT_SOURCE_1 / EXT_SOURCE_2 / EXT_SOURCE_3 KDE",
            EXT_SOURCE_FEATURES,
        )
    )

    # 4. EXT_SOURCE_1 / EXT_SOURCE_2 / EXT_SOURCE_3 分别按 TARGET=0/1 画三张图。
    for feature in EXT_SOURCE_FEATURES:
        figures.append(build_target_compare_figure(app, feature))

    save_figures(figures, HTML_PATH)

    print(f"已经保存 HTML 文件: {HTML_PATH}")
    print(f"完成 {len(figures)} 张 KDE 图绘制")


if __name__ == "__main__":
    main()
