# -*- coding: utf-8 -*-
"""从真实的 application_train 里切一个小样本：300 行 × 8 列，全真数据。"""
import pandas as pd

src = r"D:\Dustar_code\project\homecredit\data\application_train.csv"

# 挑 8 列：目标 + 几个有代表性的列（类别 / 数值，含缺失和怪值）
cols = ["TARGET", "NAME_CONTRACT_TYPE", "CODE_GENDER", "NAME_EDUCATION_TYPE",
        "OCCUPATION_TYPE", "AMT_INCOME_TOTAL", "AMT_CREDIT", "DAYS_EMPLOYED"]

df = pd.read_csv(src, usecols=cols)          # 只读这 8 列，快
sample = df.sample(n=300, random_state=42).reset_index(drop=True)
sample.to_csv("homecredit_小样本.csv", index=False)

print("已生成：homecredit_小样本.csv")
print("形状（行, 列）:", sample.shape)
print()
print(sample.head(8).to_string(index=False))
print()
print("每列缺失数：")
print(sample.isnull().sum().to_string())
print()
print("TARGET 分布（0=正常, 1=坏客户）：")
print(sample["TARGET"].value_counts().to_string())
