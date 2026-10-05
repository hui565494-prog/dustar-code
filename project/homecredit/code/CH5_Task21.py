from pathlib import Path

import pandas as pd


BASE_DIR = (
    Path.cwd()
    if (Path.cwd() / "data" / "application_train.csv").exists()
    else Path(__file__).resolve().parents[1]
)
DATA_PATH = BASE_DIR / "data" / "application_train.csv"
SUMMARY_PATH = BASE_DIR / "指导书code" / "tmp" / "application_train_missing_summary.csv"
OUTPUT_PATH = BASE_DIR / "指导书code" / "tmp" / "application_train_filled.csv"


def main():
    df = pd.read_csv(DATA_PATH)

    missing_df = pd.DataFrame(
        {
            "missing_count": df.isna().sum(),
            "missing_ratio": df.isna().mean(),
        }
    )
    missing_df = missing_df[missing_df["missing_count"] > 0].sort_values(
        "missing_count", ascending=False
    )

    num_cols = df.select_dtypes(include=["number"]).columns
    cat_cols = df.select_dtypes(include=["object", "category", "string"]).columns

    df[num_cols] = df[num_cols].fillna(df[num_cols].median())
    df[cat_cols] = df[cat_cols].fillna("Missing")

    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    missing_df.to_csv(SUMMARY_PATH)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"原始数据 shape: {df.shape}")
    print(f"有缺失的字段数: {len(missing_df)}")
    print(f"缺失值统计文件: {SUMMARY_PATH}")
    print(f"缺失值处理后文件: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
