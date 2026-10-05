# -*- coding: utf-8 -*-
"""把 Home Credit 切成迷你版：砍规模，留结构。"""
import pandas as pd, os

d = r"D:\Dustar_code\project\homecredit\data"
outdir = r"D:\Dustar_code\python\pandas\mini"
os.makedirs(outdir, exist_ok=True)

# --- 主表：2000 个客户，只留 8 列 ---
app = pd.read_csv(
    d + r"\application_train.csv",
    nrows=2000,
    usecols=[
        "SK_ID_CURR",
        "TARGET",
        "CODE_GENDER",
        "NAME_EDUCATION_TYPE",
        "NAME_INCOME_TYPE",
        "AMT_INCOME_TOTAL",
        "AMT_CREDIT",
        "DAYS_BIRTH",
    ],
)
app.to_csv(outdir + r"\app_small.csv", index=False)
print("app_small.csv ", app.shape)

# --- 副表：这些客户在征信局里的记录（一个客户多行）---
ids = set(app["SK_ID_CURR"])
bur = pd.read_csv(
    d + r"\bureau.csv",
    usecols=[
        "SK_ID_CURR",
        "SK_ID_BUREAU",
        "CREDIT_ACTIVE",
        "DAYS_CREDIT",
        "AMT_CREDIT_SUM",
    ],
)
bur_small = bur[bur["SK_ID_CURR"].isin(ids)]
bur_small.to_csv(outdir + r"\hist_small.csv", index=False)
print("hist_small.csv", bur_small.shape)

print("\n写到:", outdir)
