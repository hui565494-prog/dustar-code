from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


BASE_DIR = (
    Path.cwd()
    if (Path.cwd() / "data" / "application_train.csv").exists()
    else Path(__file__).resolve().parents[1]
)
DATA_PATH = BASE_DIR / "data" / "application_train.csv"
TRAIN_PATH = BASE_DIR / "指导书code" / "tmp" / "application_train_split_train.csv"
VALID_PATH = BASE_DIR / "指导书code" / "tmp" / "application_train_split_valid.csv"


def main():
    df = pd.read_csv(DATA_PATH)
    train_df, valid_df = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df["TARGET"],
    )

    TRAIN_PATH.parent.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(TRAIN_PATH, index=False)
    valid_df.to_csv(VALID_PATH, index=False)

    print(f"训练集 shape: {train_df.shape}")
    print(f"验证集 shape: {valid_df.shape}")
    print(f"训练集文件: {TRAIN_PATH}")
    print(f"验证集文件: {VALID_PATH}")


if __name__ == "__main__":
    main()
