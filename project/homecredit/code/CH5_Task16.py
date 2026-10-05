from pathlib import Path
import numpy as np
import pandas as pd
import warnings

warnings.filterwarnings("ignore")

# 读取主表数据
base_dir = (
    Path.cwd()
    if (Path.cwd() / "data" / "application_train.csv").exists()
    else Path(__file__).resolve().parents[1]
)
data_path = base_dir / "data" / "application_train.csv"
app_train = pd.read_csv(data_path)

# 复制一份数据，专门用于可视化分析
app = app_train.copy()

# 处理 DAYS_EMPLOYED 中的异常值
app["DAYS_EMPLOYED"] = app["DAYS_EMPLOYED"].replace(365243, np.nan)

# 将天数类字段转成更容易理解的年数
app["AGE_YEARS"] = -app["DAYS_BIRTH"] / 365
app["EMPLOYED_YEARS"] = -app["DAYS_EMPLOYED"] / 365
app["REGISTRATION_YEARS"] = -app["DAYS_REGISTRATION"] / 365

# 构造几个适合画图分析的比例特征
app["CREDIT_INCOME_RATIO"] = app["AMT_CREDIT"] / app["AMT_INCOME_TOTAL"]
app["ANNUITY_INCOME_RATIO"] = app["AMT_ANNUITY"] / app["AMT_INCOME_TOTAL"]
app["CREDIT_ANNUITY_RATIO"] = app["AMT_CREDIT"] / app["AMT_ANNUITY"]
app["GOODS_CREDIT_RATIO"] = app["AMT_GOODS_PRICE"] / app["AMT_CREDIT"]

# 汇总 EXT_SOURCE 信息
ext_cols = ["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]
app["EXT_SOURCE_MEAN"] = app[ext_cols].mean(axis=1)
app["EXT_SOURCE_MIN"] = app[ext_cols].min(axis=1)
app["EXT_SOURCE_MAX"] = app[ext_cols].max(axis=1)

# 统计每个样本的缺失情况，方便后面画缺失值与违约的关系
app["MISSING_COUNT"] = app.isnull().sum(axis=1)
app["MISSING_RATE"] = app.isnull().mean(axis=1)

# 只保留本脚本中用到的字段和新生成的字段
save_cols = [
    "SK_ID_CURR",
    "TARGET",
    "OCCUPATION_TYPE",
    "FLAG_OWN_CAR",
    "DAYS_BIRTH",
    "DAYS_EMPLOYED",
    "DAYS_REGISTRATION",
    "AGE_YEARS",
    "EMPLOYED_YEARS",
    "REGISTRATION_YEARS",
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "AMT_GOODS_PRICE",
    "CREDIT_INCOME_RATIO",
    "ANNUITY_INCOME_RATIO",
    "CREDIT_ANNUITY_RATIO",
    "GOODS_CREDIT_RATIO",
    "EXT_SOURCE_1",
    "EXT_SOURCE_2",
    "EXT_SOURCE_3",
    "EXT_SOURCE_MEAN",
    "EXT_SOURCE_MIN",
    "EXT_SOURCE_MAX",
    "MISSING_COUNT",
    "MISSING_RATE",
]

# 保存预处理后的数据
out_dir = base_dir / "指导书code" / "tmp"
out_dir.mkdir(exist_ok=True)
out_path = out_dir / "application_train_visual.csv"
try:
    app[save_cols].to_csv(out_path, index=False)
except PermissionError:
    out_path = out_dir / "application_train_visual_pie.csv"
    app[save_cols].to_csv(out_path, index=False)
    print("原 application_train_visual.csv 可能被占用，已改写备用文件")

print("可视化预处理完成")
print("输出文件：", out_path)
print("保存字段数：", len(save_cols))
print("数据规模：", app[save_cols].shape)
