# -*- coding: utf-8 -*-
"""列普查：application_train 的 122 列到底长什么样。只读，不建模。"""
import pandas as pd
import collections

p = r"D:\Dustar_code\project\homecredit\data\application_train.csv"
df = pd.read_csv(p, nrows=1000)          # 只读 1000 行拿列名和类型，够用
cols = list(df.columns)

print(f"application_train：共 {len(cols)} 列")
num = df.select_dtypes(include="number").columns
cat = df.select_dtypes(include="object").columns
print(f"  数值列 {len(num)}    类别列(object) {len(cat)}")

print("\n【按列名前缀分组】—— 前缀就是数据方给的『族』")
pref = collections.Counter(c.split("_")[0] for c in cols)
for k, v in pref.most_common():
    print(f"  {k:<12} {v:>4} 列")

print("\n【类别列(object) 各自的取值个数】")
for c in cat:
    print(f"  {c:<38} {df[c].nunique()} 个取值")
