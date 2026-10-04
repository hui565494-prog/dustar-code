# -*- coding: utf-8 -*-
"""把 122 个列名按前缀摆在一起 —— 让『族』这件事自己露出来。"""
import pandas as pd
import collections

p = r"D:\Dustar_code\project\homecredit\data\application_train.csv"
cols = list(pd.read_csv(p, nrows=1).columns)

g = collections.defaultdict(list)
for c in cols:
    g[c.split("_")[0]].append(c)

print(f"列名共 {len(cols)} 个。把名字按前缀摆在一起看：\n")
for k, v in sorted(g.items(), key=lambda kv: -len(kv[1])):
    print(f"[{k}]  {len(v)} 列")
    print("    " + ", ".join(v))
