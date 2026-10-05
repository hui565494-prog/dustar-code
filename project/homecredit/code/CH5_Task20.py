from pathlib import Path

import pandas as pd


BASE_DIR = (
    Path.cwd()
    if (Path.cwd() / "data" / "application_train.csv").exists()
    else Path(__file__).resolve().parents[1]
)
DATA_PATH = BASE_DIR / "data" / "application_train.csv"
OUTPUT_PATH = BASE_DIR / "指导书code" / "tmp" / "application_train_encoded.csv"


def encode_categorical_columns(df: pd.DataFrame) -> pd.DataFrame:
    cat_cols = df.select_dtypes(include=["object", "category", "string"]).columns
    binary_cols = [col for col in cat_cols if df[col].dropna().nunique() == 2]
    multi_cols = [col for col in cat_cols if col not in binary_cols]

    for col in binary_cols:
        values = sorted(df[col].dropna().unique())
        df[col] = df[col].map({values[0]: 0, values[1]: 1})

    return pd.get_dummies(df, columns=multi_cols, dummy_na=True)


def main():
    df = pd.read_csv(DATA_PATH)
    encoded_df = encode_categorical_columns(df.copy())

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    encoded_df.to_csv(OUTPUT_PATH, index=False)

    print(f"原始数据 shape: {df.shape}")
    print(f"编码后数据 shape: {encoded_df.shape}")
    print(f"输出文件: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
