from pathlib import Path
import re

import numpy as np
import pandas as pd
import lightgbm as lgb
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier


DATA_DIR = Path("data")
TRAIN_PATH = DATA_DIR / "application_train.csv"
TEST_PATH = DATA_DIR / "application_test.csv"
BUREAU_PATH = DATA_DIR / "bureau.csv"
BUREAU_BALANCE_PATH = DATA_DIR / "bureau_balance.csv"
SAMPLE_SUBMISSION_PATH = DATA_DIR / "sample_submission.csv"
OUTPUT_DIR = Path("output")
SUBMISSION_PATH = OUTPUT_DIR / "base_v3_linear_blend_submission.csv"
IMPORTANCE_PATH = OUTPUT_DIR / "base_v3_linear_blend_feature_importance.csv"
RANK_SUBMISSION_PATH = OUTPUT_DIR / "base_v3_reciprocal_rank_blend_submission.csv"
RANK_DETAIL_PATH = OUTPUT_DIR / "base_v3_reciprocal_rank_blend_details.csv"
RANDOM_STATE = 42
EPS = 1e-6
XGB_BLEND_WEIGHT = 0.5
LGB_BLEND_WEIGHT = 0.5
SPLIT_COLUMN = "is_train_split"


def build_xgb_model(
    n_estimators: int = 1500, early_stopping_rounds: int | None = 50
) -> XGBClassifier:
    params = dict(
        n_estimators=n_estimators,
        max_depth=6,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=40,
        reg_alpha=0.1,
        reg_lambda=1.0,
        objective="binary:logistic",
        eval_metric="auc",
        random_state=RANDOM_STATE,
        n_jobs=-1,
        tree_method="hist",
    )
    if early_stopping_rounds is not None:
        params["early_stopping_rounds"] = early_stopping_rounds
    return XGBClassifier(**params)


def build_lgb_model(n_estimators: int = 3000) -> LGBMClassifier:
    return LGBMClassifier(
        n_estimators=n_estimators,
        learning_rate=0.02,
        num_leaves=31,
        max_depth=-1,
        min_child_samples=40,
        subsample=0.8,
        subsample_freq=1,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        objective="binary",
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbosity=-1,
    )


def linear_blend(
    predictions: list[np.ndarray],
    weights: list[float] | None = None,
) -> np.ndarray:
    """对多个模型输出的原始预测概率进行线性加权融合。"""
    if not predictions:
        raise ValueError("predictions must contain at least one prediction array")
    if len({len(pred) for pred in predictions}) != 1:
        raise ValueError("all prediction arrays must have the same length")

    if weights is None:
        weights = [1.0] * len(predictions)
    if len(weights) != len(predictions):
        raise ValueError("weights and predictions must have the same length")

    weights_array = np.asarray(weights, dtype=float)
    if np.any(weights_array < 0) or weights_array.sum() <= 0:
        raise ValueError("weights must be non-negative and have a positive sum")
    weights_array /= weights_array.sum()

    prediction_matrix = np.column_stack(predictions)
    if not np.isfinite(prediction_matrix).all():
        raise ValueError("predictions must only contain finite values")

    blended_predictions = prediction_matrix @ weights_array
    return np.clip(blended_predictions, 0.0, 1.0)


def rank_blend(
    predictions: list[np.ndarray],
    weights: list[float] | None = None,
) -> tuple[np.ndarray, list[np.ndarray]]:
    """使用加权倒数排名（Weighted Reciprocal Rank）融合多个模型。"""
    if not predictions:
        raise ValueError("predictions must contain at least one prediction array")
    if len({len(pred) for pred in predictions}) != 1:
        raise ValueError("all prediction arrays must have the same length")

    if weights is None:
        weights = [1.0] * len(predictions)
    if len(weights) != len(predictions):
        raise ValueError("weights and predictions must have the same length")

    weights_array = np.asarray(weights, dtype=float)
    if np.any(weights_array < 0) or weights_array.sum() <= 0:
        raise ValueError("weights must be non-negative and have a positive sum")
    weights_array /= weights_array.sum()

    model_ranks = [
        pd.Series(prediction).rank(method="average", ascending=False).to_numpy()
        for prediction in predictions
    ]
    reciprocal_ranks = [1.0 / model_rank for model_rank in model_ranks]
    blended_rank_score = np.column_stack(reciprocal_ranks) @ weights_array
    return blended_rank_score, reciprocal_ranks


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    denominator = denominator.replace(0, np.nan)
    return numerator / (denominator + EPS)


def one_hot_encode(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    if not columns:
        return df
    return pd.get_dummies(df, columns=columns, dummy_na=False)


def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [
        (
            "_".join([str(part) for part in col if str(part) != ""]).strip("_").upper()
            if isinstance(col, tuple)
            else str(col)
        )
        for col in df.columns
    ]
    return df


def sanitize_feature_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    sanitized_columns: list[str] = []
    name_counts: dict[str, int] = {}

    for col in df.columns:
        # LightGBM 会将特征名写入 JSON，因此仅保留安全的 ASCII 字符。
        base_name = re.sub(r"[^A-Za-z0-9_]+", "_", str(col)).strip("_")
        if not base_name:
            base_name = "feature"

        duplicate_index = name_counts.get(base_name, 0)
        name_counts[base_name] = duplicate_index + 1
        sanitized_name = (
            base_name if duplicate_index == 0 else f"{base_name}__{duplicate_index}"
        )
        sanitized_columns.append(sanitized_name)

    df.columns = sanitized_columns
    return df


def add_application_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # 无效值替换为np.nan
    df["DAYS_EMPLOYED"] = df["DAYS_EMPLOYED"].replace(365243, np.nan)
    # 计算年龄和工作年限
    age_years = (-df["DAYS_BIRTH"]) / 365
    employed_years = (-df["DAYS_EMPLOYED"]) / 365

    ratio_features = {
        "CREDIT_INCOME_RATIO": safe_divide(df["AMT_CREDIT"], df["AMT_INCOME_TOTAL"]),
        "ANNUITY_INCOME_RATIO": safe_divide(df["AMT_ANNUITY"], df["AMT_INCOME_TOTAL"]),
        "ANNUITY_CREDIT_RATIO": safe_divide(df["AMT_ANNUITY"], df["AMT_CREDIT"]),
        "GOODS_INCOME_RATIO": safe_divide(
            df["AMT_GOODS_PRICE"], df["AMT_INCOME_TOTAL"]
        ),
        "CREDIT_GOODS_RATIO": safe_divide(df["AMT_CREDIT"], df["AMT_GOODS_PRICE"]),
        "INCOME_PER_FAM_MEMBER": safe_divide(
            df["AMT_INCOME_TOTAL"], df["CNT_FAM_MEMBERS"]
        ),
        "INCOME_PER_CHILD_FACTOR": safe_divide(
            df["AMT_INCOME_TOTAL"], 1 + df["CNT_CHILDREN"]
        ),
        "CHILDREN_RATIO": safe_divide(df["CNT_CHILDREN"], df["CNT_FAM_MEMBERS"]),
        "EMPLOYED_BIRTH_RATIO": safe_divide(df["DAYS_EMPLOYED"], df["DAYS_BIRTH"]),
        "REGISTRATION_BIRTH_RATIO": safe_divide(
            df["DAYS_REGISTRATION"], df["DAYS_BIRTH"]
        ),
        "ID_PUBLISH_BIRTH_RATIO": safe_divide(df["DAYS_ID_PUBLISH"], df["DAYS_BIRTH"]),
        "PHONE_CHANGE_BIRTH_RATIO": safe_divide(
            df["DAYS_LAST_PHONE_CHANGE"], df["DAYS_BIRTH"]
        ),
        "CAR_AGE_BIRTH_RATIO": safe_divide(df["OWN_CAR_AGE"], -df["DAYS_BIRTH"]),
        "CAR_AGE_EMPLOYED_RATIO": safe_divide(df["OWN_CAR_AGE"], -df["DAYS_EMPLOYED"]),
        "INCOME_REGION_RATIO": safe_divide(
            df["AMT_INCOME_TOTAL"], df["REGION_POPULATION_RELATIVE"]
        ),
        "CREDIT_TERM_PROXY": safe_divide(df["AMT_CREDIT"], df["AMT_ANNUITY"]),
        "GOODS_CREDIT_GAP_RATIO": safe_divide(
            df["AMT_CREDIT"] - df["AMT_GOODS_PRICE"], df["AMT_CREDIT"]
        ),
    }
    for feature_name, values in ratio_features.items():
        df[feature_name] = values

    diff_features = {
        "CREDIT_GOODS_DIFF": df["AMT_CREDIT"] - df["AMT_GOODS_PRICE"],
        "EMPLOYED_REGISTRATION_DIFF": df["DAYS_EMPLOYED"] - df["DAYS_REGISTRATION"],
        "ID_REGISTRATION_DIFF": df["DAYS_ID_PUBLISH"] - df["DAYS_REGISTRATION"],
        "PHONE_EMPLOYED_DIFF": df["DAYS_LAST_PHONE_CHANGE"] - df["DAYS_EMPLOYED"],
        "EXT_SOURCE_SPREAD": df[["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]].max(
            axis=1
        )
        - df[["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]].min(axis=1),
    }
    for feature_name, values in diff_features.items():
        df[feature_name] = values

    df["AGE_YEARS"] = age_years
    df["EMPLOYED_YEARS"] = employed_years

    ext_sources = ["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]
    df["EXT_SOURCES_MEAN"] = df[ext_sources].mean(axis=1)
    df["EXT_SOURCES_MEDIAN"] = df[ext_sources].median(axis=1)
    df["EXT_SOURCES_MIN"] = df[ext_sources].min(axis=1)
    df["EXT_SOURCES_MAX"] = df[ext_sources].max(axis=1)
    df["EXT_SOURCES_STD"] = df[ext_sources].std(axis=1)
    df["EXT_SOURCES_PRODUCT"] = (
        df["EXT_SOURCE_1"] * df["EXT_SOURCE_2"] * df["EXT_SOURCE_3"]
    )
    df["EXT_SOURCE_1_2_DIFF"] = df["EXT_SOURCE_1"] - df["EXT_SOURCE_2"]
    df["EXT_SOURCE_1_3_DIFF"] = df["EXT_SOURCE_1"] - df["EXT_SOURCE_3"]
    df["EXT_SOURCE_2_3_DIFF"] = df["EXT_SOURCE_2"] - df["EXT_SOURCE_3"]
    df["EXT_SOURCE_1_2_RATIO"] = safe_divide(df["EXT_SOURCE_1"], df["EXT_SOURCE_2"])
    df["EXT_SOURCE_1_3_RATIO"] = safe_divide(df["EXT_SOURCE_1"], df["EXT_SOURCE_3"])
    df["EXT_SOURCE_2_3_RATIO"] = safe_divide(df["EXT_SOURCE_2"], df["EXT_SOURCE_3"])

    missing_indicator_cols = [
        "EXT_SOURCE_1",
        "EXT_SOURCE_2",
        "EXT_SOURCE_3",
        "OWN_CAR_AGE",
        "OCCUPATION_TYPE",
        "DAYS_LAST_PHONE_CHANGE",
        "AMT_ANNUITY",
        "AMT_GOODS_PRICE",
        "OBS_30_CNT_SOCIAL_CIRCLE",
        "DEF_30_CNT_SOCIAL_CIRCLE",
        "OBS_60_CNT_SOCIAL_CIRCLE",
        "DEF_60_CNT_SOCIAL_CIRCLE",
        "AMT_REQ_CREDIT_BUREAU_HOUR",
        "AMT_REQ_CREDIT_BUREAU_DAY",
        "AMT_REQ_CREDIT_BUREAU_WEEK",
        "AMT_REQ_CREDIT_BUREAU_MON",
        "AMT_REQ_CREDIT_BUREAU_QRT",
        "AMT_REQ_CREDIT_BUREAU_YEAR",
    ]
    for col in missing_indicator_cols:
        df[f"{col}_IS_MISSING"] = df[col].isna().astype(np.int8)

    document_cols = [col for col in df.columns if col.startswith("FLAG_DOCUMENT_")]
    address_cols = [
        "REG_REGION_NOT_LIVE_REGION",
        "REG_REGION_NOT_WORK_REGION",
        "LIVE_REGION_NOT_WORK_REGION",
        "REG_CITY_NOT_LIVE_CITY",
        "REG_CITY_NOT_WORK_CITY",
        "LIVE_CITY_NOT_WORK_CITY",
    ]
    contact_cols = [
        "FLAG_MOBIL",
        "FLAG_EMP_PHONE",
        "FLAG_WORK_PHONE",
        "FLAG_PHONE",
        "FLAG_EMAIL",
    ]
    bureau_request_cols = [
        "AMT_REQ_CREDIT_BUREAU_HOUR",
        "AMT_REQ_CREDIT_BUREAU_DAY",
        "AMT_REQ_CREDIT_BUREAU_WEEK",
        "AMT_REQ_CREDIT_BUREAU_MON",
        "AMT_REQ_CREDIT_BUREAU_QRT",
        "AMT_REQ_CREDIT_BUREAU_YEAR",
    ]

    df["FLAG_DOCUMENT_SUM"] = df[document_cols].sum(axis=1)
    df["ADDRESS_MISMATCH_SUM"] = df[address_cols].sum(axis=1)
    df["CONTACT_FLAGS_SUM"] = df[contact_cols].sum(axis=1)
    df["CREDIT_BUREAU_REQUEST_SUM"] = df[bureau_request_cols].sum(axis=1)
    df["SOCIAL_CIRCLE_OBS_SUM"] = (
        df["OBS_30_CNT_SOCIAL_CIRCLE"] + df["OBS_60_CNT_SOCIAL_CIRCLE"]
    )
    df["SOCIAL_CIRCLE_DEF_SUM"] = (
        df["DEF_30_CNT_SOCIAL_CIRCLE"] + df["DEF_60_CNT_SOCIAL_CIRCLE"]
    )
    df["SOCIAL_CIRCLE_DEF_OBS_RATIO"] = safe_divide(
        df["DEF_30_CNT_SOCIAL_CIRCLE"] + df["DEF_60_CNT_SOCIAL_CIRCLE"],
        df["OBS_30_CNT_SOCIAL_CIRCLE"] + df["OBS_60_CNT_SOCIAL_CIRCLE"],
    )

    age_bins = pd.qcut(
        age_years.rank(method="first"), q=5, labels=False, duplicates="drop"
    )
    income_bins = pd.qcut(
        df["AMT_INCOME_TOTAL"].rank(method="first"),
        q=5,
        labels=False,
        duplicates="drop",
    )
    ext_bins = pd.qcut(
        df["EXT_SOURCES_MEAN"].rank(method="first"),
        q=5,
        labels=False,
        duplicates="drop",
    )
    df["AGE_BIN"] = age_bins.astype("Int64").astype("string").fillna("UNKNOWN")
    df["INCOME_BIN"] = income_bins.astype("Int64").astype("string").fillna("UNKNOWN")
    df["EXT_SOURCE_BIN"] = ext_bins.astype("Int64").astype("string").fillna("UNKNOWN")

    cross_features = {
        "INCOME_EDUCATION_CROSS": ["NAME_INCOME_TYPE", "NAME_EDUCATION_TYPE"],
        "FAMILY_GENDER_CROSS": ["NAME_FAMILY_STATUS", "CODE_GENDER"],
        "ORG_OCCUPATION_CROSS": ["ORGANIZATION_TYPE", "OCCUPATION_TYPE"],
        "HOUSING_FAMILY_CROSS": ["NAME_HOUSING_TYPE", "NAME_FAMILY_STATUS"],
        "AGE_EDUCATION_CROSS": ["AGE_BIN", "NAME_EDUCATION_TYPE"],
    }
    for feature_name, cols in cross_features.items():
        df[feature_name] = (
            df[cols[0]].astype(str).fillna("UNKNOWN")
            + "__"
            + df[cols[1]].astype(str).fillna("UNKNOWN")
        )

    return df


def build_bureau_features() -> pd.DataFrame:
    bureau = pd.read_csv(BUREAU_PATH)
    bureau_balance = pd.read_csv(BUREAU_BALANCE_PATH)

    bureau_balance_status = pd.get_dummies(bureau_balance["STATUS"], prefix="STATUS")
    bureau_balance = pd.concat(
        [bureau_balance[["SK_ID_BUREAU", "MONTHS_BALANCE"]], bureau_balance_status],
        axis=1,
    )

    bb_agg = bureau_balance.groupby("SK_ID_BUREAU").agg(
        {
            "MONTHS_BALANCE": ["min", "max", "size"],
            **{col: ["mean"] for col in bureau_balance_status.columns},
        }
    )
    bb_agg = flatten_columns(bb_agg)
    bb_agg.columns = [f"BB_{col}" for col in bb_agg.columns]

    bureau = bureau.merge(bb_agg, how="left", left_on="SK_ID_BUREAU", right_index=True)

    bureau["DEBT_CREDIT_RATIO"] = safe_divide(
        bureau["AMT_CREDIT_SUM_DEBT"], bureau["AMT_CREDIT_SUM"]
    )
    bureau["OVERDUE_DEBT_RATIO"] = safe_divide(
        bureau["AMT_CREDIT_SUM_OVERDUE"], bureau["AMT_CREDIT_SUM_DEBT"]
    )
    bureau["OVERDUE_CREDIT_RATIO"] = safe_divide(
        bureau["AMT_CREDIT_SUM_OVERDUE"], bureau["AMT_CREDIT_SUM"]
    )
    bureau["CREDIT_ENDDATE_DIFF"] = (
        bureau["DAYS_CREDIT_ENDDATE"] - bureau["DAYS_CREDIT"]
    )
    bureau["ENDDATE_FACT_DIFF"] = bureau["DAYS_ENDDATE_FACT"] - bureau["DAYS_CREDIT"]
    bureau["UPDATE_CREDIT_DIFF"] = bureau["DAYS_CREDIT_UPDATE"] - bureau["DAYS_CREDIT"]

    bureau["HAS_OVERDUE"] = (bureau["CREDIT_DAY_OVERDUE"].fillna(0) > 0).astype(np.int8)
    bureau["HAS_DEBT"] = (bureau["AMT_CREDIT_SUM_DEBT"].fillna(0) > 0).astype(np.int8)

    cat_cols = bureau.select_dtypes(
        include=["object", "string", "category"]
    ).columns.tolist()
    bureau = one_hot_encode(bureau, cat_cols)

    bb_cols = [col for col in bureau.columns if col.startswith("BB_")]
    cat_dummy_cols = [
        col
        for col in bureau.columns
        if col.startswith("CREDIT_ACTIVE_")
        or col.startswith("CREDIT_CURRENCY_")
        or col.startswith("CREDIT_TYPE_")
    ]
    aggregations: dict[str, list[str]] = {
        "SK_ID_BUREAU": ["count"],
        "DAYS_CREDIT": ["min", "max", "mean"],
        "DAYS_CREDIT_ENDDATE": ["min", "max", "mean"],
        "DAYS_ENDDATE_FACT": ["min", "max", "mean"],
        "DAYS_CREDIT_UPDATE": ["mean", "max"],
        "CREDIT_DAY_OVERDUE": ["max", "mean", "sum"],
        "AMT_CREDIT_MAX_OVERDUE": ["max", "mean"],
        "AMT_CREDIT_SUM": ["sum", "mean", "max"],
        "AMT_CREDIT_SUM_DEBT": ["sum", "mean", "max"],
        "AMT_CREDIT_SUM_OVERDUE": ["sum", "mean", "max"],
        "AMT_CREDIT_SUM_LIMIT": ["sum", "mean", "max"],
        "AMT_ANNUITY": ["mean", "max"],
        "CNT_CREDIT_PROLONG": ["sum", "mean"],
        "DEBT_CREDIT_RATIO": ["mean", "max"],
        "OVERDUE_DEBT_RATIO": ["mean", "max"],
        "OVERDUE_CREDIT_RATIO": ["mean", "max"],
        "CREDIT_ENDDATE_DIFF": ["min", "max", "mean"],
        "ENDDATE_FACT_DIFF": ["min", "max", "mean"],
        "UPDATE_CREDIT_DIFF": ["min", "max", "mean"],
        "HAS_OVERDUE": ["mean", "sum"],
        "HAS_DEBT": ["mean", "sum"],
    }
    for col in bb_cols + cat_dummy_cols:
        aggregations[col] = ["mean"]

    bureau_agg = bureau.groupby("SK_ID_CURR").agg(aggregations)
    bureau_agg = flatten_columns(bureau_agg)
    bureau_agg.columns = [f"BURO_{col}" for col in bureau_agg.columns]

    if "CREDIT_ACTIVE_Active" in bureau.columns:
        active = bureau[bureau["CREDIT_ACTIVE_Active"] == 1]
        active_agg = active.groupby("SK_ID_CURR").agg(
            {
                "SK_ID_BUREAU": ["count"],
                "AMT_CREDIT_SUM": ["sum", "mean", "max"],
                "AMT_CREDIT_SUM_DEBT": ["sum", "mean", "max"],
                "AMT_CREDIT_SUM_OVERDUE": ["sum", "mean", "max"],
                "CREDIT_DAY_OVERDUE": ["max", "mean"],
                "DEBT_CREDIT_RATIO": ["mean", "max"],
                "OVERDUE_DEBT_RATIO": ["mean", "max"],
                "OVERDUE_CREDIT_RATIO": ["mean", "max"],
                "DAYS_CREDIT": ["min", "max", "mean"],
                "DAYS_CREDIT_ENDDATE": ["min", "max", "mean"],
                "BB_MONTHS_BALANCE_SIZE": ["mean", "max"],
            }
        )
        active_agg = flatten_columns(active_agg)
        active_agg.columns = [f"ACTIVE_{col}" for col in active_agg.columns]
        bureau_agg = bureau_agg.join(active_agg, how="left")

    if "CREDIT_ACTIVE_Closed" in bureau.columns:
        closed = bureau[bureau["CREDIT_ACTIVE_Closed"] == 1]
        closed_agg = closed.groupby("SK_ID_CURR").agg(
            {
                "SK_ID_BUREAU": ["count"],
                "AMT_CREDIT_SUM": ["sum", "mean", "max"],
                "AMT_CREDIT_SUM_DEBT": ["sum", "mean", "max"],
                "AMT_CREDIT_SUM_OVERDUE": ["sum", "mean", "max"],
                "CREDIT_DAY_OVERDUE": ["max", "mean"],
                "DEBT_CREDIT_RATIO": ["mean", "max"],
                "OVERDUE_DEBT_RATIO": ["mean", "max"],
                "OVERDUE_CREDIT_RATIO": ["mean", "max"],
                "DAYS_CREDIT": ["min", "max", "mean"],
                "DAYS_ENDDATE_FACT": ["min", "max", "mean"],
                "BB_MONTHS_BALANCE_SIZE": ["mean", "max"],
            }
        )
        closed_agg = flatten_columns(closed_agg)
        closed_agg.columns = [f"CLOSED_{col}" for col in closed_agg.columns]
        bureau_agg = bureau_agg.join(closed_agg, how="left")

    return bureau_agg


def preprocess_application(
    train_df: pd.DataFrame, test_df: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_features = train_df.drop(columns=["TARGET"]).copy()
    test_features = test_df.copy()

    merged = pd.concat(
        [
            train_features.assign(**{SPLIT_COLUMN: 1}),
            test_features.assign(**{SPLIT_COLUMN: 0}),
        ],
        axis=0,
        ignore_index=True,
        sort=False,
    )

    merged = add_application_features(merged)

    bureau_features = build_bureau_features()
    merged = merged.merge(
        bureau_features, how="left", left_on="SK_ID_CURR", right_index=True
    )

    numeric_cols = merged.select_dtypes(include=["number"]).columns.difference(
        [SPLIT_COLUMN]
    )
    categorical_cols = merged.select_dtypes(
        include=["object", "string", "category"]
    ).columns

    merged[numeric_cols] = merged[numeric_cols].replace([np.inf, -np.inf], np.nan)
    merged[numeric_cols] = merged[numeric_cols].fillna(merged[numeric_cols].median())
    merged[categorical_cols] = merged[categorical_cols].fillna("UNKNOWN")

    merged_encoded = pd.get_dummies(merged, columns=categorical_cols, dummy_na=False)
    nullable_bool_cols = merged_encoded.select_dtypes(include=["boolean"]).columns
    if len(nullable_bool_cols) > 0:
        merged_encoded[nullable_bool_cols] = merged_encoded[nullable_bool_cols].astype(
            np.int8
        )
    merged_encoded = sanitize_feature_names(merged_encoded)

    train_processed = (
        merged_encoded[merged_encoded[SPLIT_COLUMN] == 1]
        .drop(columns=[SPLIT_COLUMN])
        .reset_index(drop=True)
    )
    test_processed = (
        merged_encoded[merged_encoded[SPLIT_COLUMN] == 0]
        .drop(columns=[SPLIT_COLUMN])
        .reset_index(drop=True)
    )
    return train_processed, test_processed


def main() -> None:
    train_df = pd.read_csv(TRAIN_PATH)
    test_df = pd.read_csv(TEST_PATH)
    sample_submission = pd.read_csv(SAMPLE_SUBMISSION_PATH)

    y = train_df["TARGET"].copy()
    test_ids = test_df["SK_ID_CURR"].copy()

    train_processed, test_processed = preprocess_application(train_df, test_df)
    X = train_processed.drop(columns=["SK_ID_CURR"])
    X_test = test_processed.drop(columns=["SK_ID_CURR"])

    X_train, X_valid, y_train, y_valid = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    xgb_model = build_xgb_model()
    xgb_model.fit(
        X_train,
        y_train,
        eval_set=[(X_valid, y_valid)],
        verbose=100,
    )

    lgb_model = build_lgb_model()
    lgb_model.fit(
        X_train,
        y_train,
        eval_set=[(X_valid, y_valid)],
        eval_metric="auc",
        callbacks=[lgb.early_stopping(50), lgb.log_evaluation(100)],
    )

    xgb_valid_pred = xgb_model.predict_proba(X_valid)[:, 1]
    lgb_valid_pred = lgb_model.predict_proba(X_valid)[:, 1]
    blend_weights = [XGB_BLEND_WEIGHT, LGB_BLEND_WEIGHT]
    blended_valid_pred = linear_blend(
        [xgb_valid_pred, lgb_valid_pred],
        weights=blend_weights,
    )
    rank_blended_valid_pred, _ = rank_blend(
        [xgb_valid_pred, lgb_valid_pred],
        weights=blend_weights,
    )
    print(f"XGBoost validation ROC-AUC: {roc_auc_score(y_valid, xgb_valid_pred):.6f}")
    print(f"LightGBM validation ROC-AUC: {roc_auc_score(y_valid, lgb_valid_pred):.6f}")
    print(
        f"Linear blend validation ROC-AUC: {roc_auc_score(y_valid, blended_valid_pred):.6f}"
    )
    print(
        "Reciprocal rank blend validation ROC-AUC: "
        f"{roc_auc_score(y_valid, rank_blended_valid_pred):.6f}"
    )

    feature_importance = pd.DataFrame(
        {
            "feature": X.columns,
            "xgboost_importance": xgb_model.feature_importances_,
            "lightgbm_importance": lgb_model.feature_importances_,
        }
    ).sort_values("lightgbm_importance", ascending=False)

    xgb_best_iteration = (
        xgb_model.best_iteration + 1
        if xgb_model.best_iteration is not None
        else xgb_model.n_estimators
    )
    lgb_best_iteration = lgb_model.best_iteration_ or lgb_model.n_estimators

    final_xgb_model = build_xgb_model(
        n_estimators=xgb_best_iteration,
        early_stopping_rounds=None,
    )
    final_xgb_model.fit(X, y, verbose=False)

    final_lgb_model = build_lgb_model(n_estimators=lgb_best_iteration)
    final_lgb_model.fit(X, y, callbacks=[lgb.log_evaluation(0)])

    xgb_test_pred = final_xgb_model.predict_proba(X_test)[:, 1]
    lgb_test_pred = final_lgb_model.predict_proba(X_test)[:, 1]
    test_pred = linear_blend(
        [xgb_test_pred, lgb_test_pred],
        weights=blend_weights,
    )
    rank_test_pred, (xgb_reciprocal_rank, lgb_reciprocal_rank) = rank_blend(
        [xgb_test_pred, lgb_test_pred],
        weights=blend_weights,
    )

    submission = sample_submission[["SK_ID_CURR"]].copy()
    submission["SK_ID_CURR"] = test_ids.values
    submission["TARGET"] = test_pred

    rank_submission = submission[["SK_ID_CURR"]].copy()
    rank_submission["TARGET"] = rank_test_pred

    rank_details = pd.DataFrame(
        {
            "SK_ID_CURR": test_ids.values,
            "xgb_probability": xgb_test_pred,
            "xgb_rank": pd.Series(xgb_test_pred).rank(
                method="average", ascending=False
            ),
            "xgb_reciprocal_rank": xgb_reciprocal_rank,
            "lgb_probability": lgb_test_pred,
            "lgb_rank": pd.Series(lgb_test_pred).rank(
                method="average", ascending=False
            ),
            "lgb_reciprocal_rank": lgb_reciprocal_rank,
            "rank_blend_score": rank_test_pred,
            "final_rank": pd.Series(rank_test_pred).rank(
                method="average", ascending=False
            ),
        }
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    submission.to_csv(SUBMISSION_PATH, index=False)
    rank_submission.to_csv(RANK_SUBMISSION_PATH, index=False)
    rank_details.to_csv(RANK_DETAIL_PATH, index=False)
    feature_importance.to_csv(IMPORTANCE_PATH, index=False)

    print(f"Train shape after encoding: {train_processed.shape}")
    print(f"Test shape after encoding: {test_processed.shape}")
    print(f"Submission file saved to: {SUBMISSION_PATH}")
    print(f"Rank submission file saved to: {RANK_SUBMISSION_PATH}")
    print(f"Rank detail file saved to: {RANK_DETAIL_PATH}")
    print(f"Feature importance saved to: {IMPORTANCE_PATH}")


if __name__ == "__main__":
    main()
