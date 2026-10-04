# -*- coding: utf-8 -*-
"""玩具示例：原始表 -> 模型输入。与 HomeCredit 项目无关，仅用于看清骨架。"""
import pandas as pd
import numpy as np

L = "=" * 64
def title(s):
    print(); print(L); print(s); print(L)

# ---------- 0. 原始数据 ----------
title("0) 原始数据：两张表")
app = pd.DataFrame({
    "客户ID": ["C1","C2","C3","C4","C5","C6","C7","C8"],
    "性别":   ["男","女","男","女","男","女","男","女"],
    "年龄":   [30, 45, 22, 35, 50, 29, 41, 33],
    "收入":   [5000, 8000, np.nan, 6000, 9000, 4000, 7000, 5500],
    "TARGET": [0, 1, 0, 0, 1, 0, 0, 1],
})
pay = pd.DataFrame({
    "客户ID": ["C1","C1","C2","C3","C4","C4","C4","C5","C7","C8","C8"],
    "金额":   [100, 200, 50, 300, 150, 80, 20, 500, 60, 90, 110],
    "逾期天数": [5, -3, 0, 30, 2, 0, -1, 10, 0, 3, 0],
})
print("app（申请表）  一行 = 一个客户：")
print(app.to_string(index=False))
print()
print("pay（还款表）  一行 = 一次还款（C1/C4/C8 有多行）：")
print(pay.to_string(index=False))

# ---------- a. 粒度 ----------
title("a) 读表：先答『每张表的一行是什么』")
print("app ：一行 = 一个客户   （申请级）")
print("pay ：一行 = 一次还款   （账户/月度级 —— 一个客户被摊成多行）")
print("两张表的『一行』不一样 —— 这就是后面必须做『聚合』的原因。")

# ---------- c. 预处理 ----------
title("c) 预处理：文字 -> 数")
app["性别"] = app["性别"].map({"男": 1, "女": 0})
print("性别 男/女 -> 1/0：")
print(app[["客户ID", "性别"]].to_string(index=False))

# ---------- d. 造列 ----------
title("d) 造列（特征工程）：造原始数据里没有的列")
app["收入_每岁"] = app["收入"] / app["年龄"]
print("新列『收入_每岁』= 收入 / 年龄：")
print(app[["客户ID", "收入", "年龄", "收入_每岁"]].to_string(index=False))
print("注意：这一列原始数据里根本不存在，是你算出来的。")

# ---------- e. 聚合 ----------
title("e) 聚合（核心）：多行 -> 一行")
g = pay.groupby("客户ID").agg(
    还款次数=("金额", "size"),
    还款总额=("金额", "sum"),
    逾期次数=("逾期天数", lambda s: int((s < 0).sum())),
    最差天数=("逾期天数", "min"),
).reset_index()
print("把 pay 里『一个客户的多次还款』压成『一个客户一行』：")
print(g.to_string(index=False))
print("C1 原来的 2 行、C4 的 3 行 —— 现在都只剩 1 行。")

# ---------- 合并 ----------
title("结果：拼成一张『一行一个客户、每列一个数』的表")
final = app.merge(g, on="客户ID", how="left")
for c in ["还款次数", "还款总额", "逾期次数"]:
    final[c] = final[c].fillna(0)
print(final.to_string(index=False))
print()
print("左半（性别/年龄/收入/收入_每岁）= 模型输入 x 的各维")
print("最后一列 TARGET = 要预测的答案 y")
print("=> 这张表，就是 BP 里那个 x（你手写 BP 时现成拿到的输入向量，就是这么造出来的）")
