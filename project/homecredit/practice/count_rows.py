# -*- coding: utf-8 -*-
"""数一数每张 csv 有多少行 —— 用来回答『Excel 能不能打开』。"""
import pandas as pd, glob, os, time

d = r"D:\Dustar_code\project\homecredit\data"
LIMIT = 1048576  # Excel 单表最大行数

for f in sorted(glob.glob(os.path.join(d, "*.csv"))):
    name = os.path.basename(f)
    t = time.time()
    try:
        rows = pd.read_csv(f, usecols=[0], low_memory=False).shape[0]
        flag = "  <-- 超过 Excel 上限" if rows > LIMIT else ""
        print(f"{name:<38} {rows:>10,} 行  ({time.time()-t:.0f}s){flag}")
    except Exception as e:
        print(f"{name:<38} 读取失败: {e}")
