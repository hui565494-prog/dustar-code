import warnings
from pathlib import Path

import pandas as pd
import plotly.express as px

warnings.filterwarnings("ignore")


PROJECT_DIR = (
    Path.cwd()
    if (Path.cwd() / "data" / "application_train.csv").exists()
    else Path(__file__).resolve().parents[1]
)
BASE_DIR = PROJECT_DIR / "指导书code"
DATA_PATH = BASE_DIR / "tmp" / "application_train_visual.csv"
FALLBACK_DATA_PATH = BASE_DIR / "tmp" / "application_train_visual_pie.csv"
HTML_PATH = BASE_DIR / "tmp" / "pie_selected_categories.html"

PIE_COLS = [
    "OCCUPATION_TYPE",
    "TARGET",
    "FLAG_OWN_CAR",
]


def build_pie_figure(app, col):
    plot_df = app[[col]].copy()
    plot_df[col] = plot_df[col].fillna("Missing").astype(str)

    count_df = (
        plot_df.groupby(col)
        .size()
        .reset_index(name="COUNT")
        .sort_values("COUNT", ascending=False)
    )

    fig = px.pie(
        count_df,
        names=col,
        values="COUNT",
        title=f"{col} 占比",
        hole=0.35,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate=f"{col}: %{{label}}<br>数量: %{{value}}<br>占比: %{{percent}}<extra></extra>",
    )
    is_occupation_type = col == "OCCUPATION_TYPE"

    fig.update_layout(
        height=600,
        width=1050 if is_occupation_type else 900,
        legend_title_text=col,
        legend=dict(
            x=1.08 if is_occupation_type else 0.98,
            y=0.98,
            xanchor="right",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.7)",
        ),
        margin=dict(t=70, l=40, r=170 if is_occupation_type else 40, b=40),
    )
    return fig


def save_figures(figures, html_path):
    html_path.parent.mkdir(parents=True, exist_ok=True)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(
            "<html><head><meta charset='utf-8'><title>Pie Selected Categories</title></head><body>\n"
        )
        for index, fig in enumerate(figures):
            f.write(fig.to_html(include_plotlyjs=(index == 0), full_html=False))
            f.write("\n<hr>\n")
        f.write("</body></html>\n")


def main():
    app = pd.read_csv(DATA_PATH)

    missing_columns = [col for col in PIE_COLS if col not in app.columns]
    if missing_columns and FALLBACK_DATA_PATH.exists():
        app = pd.read_csv(FALLBACK_DATA_PATH)
        missing_columns = [col for col in PIE_COLS if col not in app.columns]

    if missing_columns:
        raise ValueError(
            f"数据缺少必要字段: {missing_columns}，请先运行 task2_visual_preprocess.py"
        )

    figures = [build_pie_figure(app, col) for col in PIE_COLS]
    save_figures(figures, HTML_PATH)

    print(f"已经保存 HTML 文件: {HTML_PATH}")
    print(f"完成 {len(figures)} 张饼图绘制")


if __name__ == "__main__":
    main()
