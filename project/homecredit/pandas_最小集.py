# -*- coding: utf-8 -*-
"""
《数据工程综合实践》最小 Pandas 集
—— 用你已经会的东西，解释你要用的东西

用法：直接运行  python pandas_最小集.py
不需要任何数据文件，数据在代码里现造。

作者注：你已经能用纯 NumPy 手写反向传播并在 MNIST 上训练。
        所以这份文件不解释"什么是梯度""什么是损失"。
        它只做一件事：把你熟悉的 NumPy 操作，翻译成 Pandas 的写法。
        凡是我写「和 NumPy 完全一样」的地方，就是真的完全一样。
"""

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np
import pandas as pd

# 让打印好看一点
pd.set_option("display.width", 100)
pd.set_option("display.max_columns", 20)


def 分节(n, title):
    print("\n" + "=" * 70)
    print(f"【{n}】{title}")
    print("=" * 70)


# ======================================================================
分节(0, "心智模型：一句话")
# ======================================================================
print(
    """
    Pandas 的 DataFrame  ≈  「带列名的 NumPy 二维数组」

    记住这三句话，剩下全是查语法：
      · 取一列        ≈ arr[:, 3]            只是把下标 3 换成列名
      · 布尔筛选      ≈ arr[arr[:,3] > 0]    一模一样，只是写成 df[df["列"]>0]
      · 多出来的两样  ① 缺失值(NaN)有专门语义  ② 分组聚合(groupby)是一行搞定
                       这两样 NumPy 里没有好用的对应物，所以要新学。

    你的项目里 90% 的活 = 取列 + 布尔筛选 + 分组聚合 + 拼表
"""
)

# ======================================================================
分节(1, "读表 / 存表")
# ======================================================================
print(
    """
    # NumPy 里你要这样（没有列名，只能靠下标数）
    data = np.loadtxt("x.csv", delimiter=",", skiprows=1)

    # Pandas
    df = pd.read_csv("application_train.csv")   # 一行读进来，列名自动带上
    df.to_csv("out.csv", index=False)           # 存出去；index=False 表示不写行号列

    ★ 后面项目里每次提交 Kaggle 都要 to_csv，格式是 SK_ID_CURR,TARGET 两列
"""
)

# 造数据：完全仿照 Home Credit 的结构
# —— application（申请级：一个客户一行）
# —— bureau（征信账户级：一个客户多行）
申请 = pd.DataFrame(
    {
        "SK_ID_CURR": [100001, 100002, 100003, 100004],
        "AMT_CREDIT": [500000.0, 1200000.0, 250000.0, np.nan],
        "NAME_INCOME_TYPE": ["Working", "Pensioner", "Working", "Commercial"],
        "TARGET": [0, 1, 0, 1],
    }
)

征信 = pd.DataFrame(
    {
        "SK_ID_CURR": [100001, 100001, 100001, 100002, 100003, 100003],
        "SK_ID_BUREAU": [1, 2, 3, 4, 5, 6],
        "AMT_CREDIT_SUM": [50000.0, 30000.0, 20000.0, 900000.0, 100000.0, 50000.0],
        "CREDIT_ACTIVE": ["Active", "Closed", "Active", "Active", "Closed", "Active"],
    }
)

print("申请表（一个客户一行）:")
print(申请)
print("\n征信表（一个客户多行）:")
print(征信)

# ======================================================================
分节(2, "看表：先搞清楚拿到手的是什么")
# ======================================================================
print(
    f"申请.shape            → {申请.shape}        # 和 NumPy 完全一样，只是返回 (行, 列)"
)
print(f"申请.columns.tolist() → {申请.columns.tolist()}")
print(
    f'申请["SK_ID_CURR"].nunique() → {申请["SK_ID_CURR"].nunique()}   # 有多少个不重复的客户'
)
print("\n申请.head(2)  （前两行，调试时天天用）:")
print(申请.head(2))

# ======================================================================
分节(3, "选列 / 筛行：和 NumPy 一模一样")
# ======================================================================
ids_np = 申请["SK_ID_CURR"].to_numpy()  # Pandas Series → NumPy 数组
credit_np = 申请["AMT_CREDIT"].to_numpy()

print("NumPy 的写法（你熟）:")
print(f"  整个二维数组:        arr.shape = ...")
print(f"  取第 3 列:           arr[:, 2]           → {credit_np}")
print(
    f"  布尔掩码筛行:        arr[arr[:,2] > 400000] → {credit_np[credit_np > 400000]}"
)

print("\nPandas 的写法（同一个意思）:")
print(f'  df["AMT_CREDIT"]                  → 一列，就是 arr[:, 2]')
print(f'  df[df["AMT_CREDIT"] > 400000]     → 筛行，就是布尔掩码')
print()
print(申请[申请["AMT_CREDIT"] > 400000])
print("\n  ★ 多条件要用 & 而不是 and，每个条件要加括号：")
print('    df[(df["a"] > 1) & (df["b"] < 5)]')

# ======================================================================
分节(4, "算：sum / mean / value_counts")
# ======================================================================
print(
    f'申请["AMT_CREDIT"].mean()  → {申请["AMT_CREDIT"].mean():.1f}     # 注意：NaN 会被自动跳过'
)
print(f'申请["AMT_CREDIT"].sum()   → {申请["AMT_CREDIT"].sum():.1f}')
print(
    f'申请["TARGET"].sum()       → {申请["TARGET"].sum()}        # 数 1 的个数，正样本数'
)
print('\n申请["TARGET"].value_counts()  （数每个值出现几次）:')
print(申请["TARGET"].value_counts())

print("\n  NumPy 对照：np.unique(arr, return_counts=True)")
u, c = np.unique(申请["TARGET"].to_numpy(), return_counts=True)
print(f"    np.unique 结果 → 值 {u}, 次数 {c}")

# ======================================================================
分节(5, "缺失值：这是 Pandas 比 NumPy 多出来的一层语义")
# ======================================================================
print("在 Home Credit 里，EXT_SOURCE_1 有一半是空的。空值不能直接进模型。\n")
print(
    f'申请["AMT_CREDIT"].isna()   → {申请["AMT_CREDIT"].isna().tolist()}   # True 表示这格是空的'
)
print(
    f'申请["AMT_CREDIT"].isna().sum() → {申请["AMT_CREDIT"].isna().sum()}          # 总共空了几格'
)
print(
    f'申请["AMT_CREDIT"].isna().mean() → {申请["AMT_CREDIT"].isna().mean():.2f}       # 缺失率（0.25 = 25%）'
)
print("\n填掉它（指导书里用中位数填数值列，用字符串 'Missing' 填类别列）:")
print(f'  申请["AMT_CREDIT"].fillna(申请["AMT_CREDIT"].median()).tolist()')
print(f'  → {申请["AMT_CREDIT"].fillna(申请["AMT_CREDIT"].median()).tolist()}')

print(
    """
    ★ 指导书里的一个关键判断（实验任务21的说明原文意思）：
      「用中位数直接填，会抹掉"这格本来就缺"这个信号。
        所以建议对有空值的列，额外加一列 0/1 表示它是否缺失。」
      这就是"特征工程"最朴素的一个例子。
"""
)

# ======================================================================
分节(6, "★ groupby + agg —— 本项目的核心，也是唯一真正新的概念")
# ======================================================================
print(
    """
    问题：征信表里一个客户有 3 行，但你要的是"一个客户一行"。
    你得把 3 行压成 1 行。

    这个动作叫 split-apply-combine（分组-计算-合并）：
      ① 按 SK_ID_CURR 分组（split）
      ② 每组算一个汇总值，比如求和 / 平均 / 最大 / 计数（apply）
      ③ 拼回一张"一个客户一行"的表（combine）
"""
)

print("先用手写 NumPy 循环版做一遍（你应该一眼看懂）:")
ids = 征信["SK_ID_CURR"].to_numpy()
amts = 征信["AMT_CREDIT_SUM"].to_numpy()
手写结果 = {}
for 客户, 金额 in zip(ids, amts):
    手写结果.setdefault(客户, []).append(金额)
for 客户 in sorted(手写结果):
    vals = 手写结果[客户]
    print(
        f"   客户 {客户}: 笔数={len(vals)}  合计={sum(vals):.0f}  平均={sum(vals)/len(vals):.0f}  最大={max(vals):.0f}"
    )

print("\n同样的东西，Pandas 一行:")
汇总 = 征信.groupby("SK_ID_CURR")["AMT_CREDIT_SUM"].agg(["count", "sum", "mean", "max"])
print(汇总)

print(
    """
    拆开看这一行：
      征信                       ← 要处理哪张表
      .groupby("SK_ID_CURR")     ← 按哪个列分组（= 你的"客户是谁"）
      ["AMT_CREDIT_SUM"]         ← 对哪一列做计算
      .agg(["count","sum","mean","max"])  ← 算哪几个汇总值

    ★ 这 4 个函数就是全套：count(几次) sum(总共多少) mean(平均水平) max(最极端)
      指导书里还用了 min / std / nunique，用法完全一样。

    ★ 一个客户有两个字段要聚合，就写两行再拼（见下一节）；
      或者用 .agg({"A": ["sum","max"], "B": ["mean"]}) 一次写完。
"""
)

# 分组后改名，避免列名重复
汇总 = 汇总.rename(
    columns={
        "count": "征信_笔数",
        "sum": "征信_总额",
        "mean": "征信_均值",
        "max": "征信_最大",
    }
).reset_index()
print("分组结果要 reset_index() 一下，SK_ID_CURR 才会从「索引」变回「普通的一列」：")
print(汇总)

# ======================================================================
分节(7, "★ merge —— 把聚合结果拼回主表")
# ======================================================================
print(
    """
    merge ≈ SQL 的 JOIN。你现在只需要会用一个形式：

        pd.merge(左表, 右表, on="拼哪一列", how="left")
"""
)
建模表 = pd.merge(申请, 汇总, on="SK_ID_CURR", how="left")
print(建模表)
print(
    """
    how="left" 的意思是：以左表（申请）为准，一行都不能少。
    右表（征信）里没有的客户，就填 NaN。

    ★ 为什么必须用 left？因为你的样本是 307511 笔申请，
      合并完必须还是 307511 行。多一行少一行都是 bug。

    给你一个自己检查的习惯：
        合并前: 申请.shape[0]
        合并后: 建模表.shape[0]     ← 这两个数必须相等
"""
)

# ======================================================================
分节(8, "编码与类型：把文字变成数字")
# ======================================================================
print("模型只认识数字。类别列要么映射成 0/1，要么拆成多列。\n")
print('  pd.get_dummies(申请, columns=["NAME_INCOME_TYPE"])  → 一个类别一列 0/1：')
dummy = pd.get_dummies(申请, columns=["NAME_INCOME_TYPE"])
print(dummy.drop(columns=["SK_ID_CURR", "AMT_CREDIT"]).to_string())

print(
    """
    ★ 指导书里的一个判断（实验任务20说明原文意思）：
      「双值列（只有两个取值）用 get_dummies 会浪费一列，直接映射 0/1；
        多值列才用 get_dummies。
        另外取值特别多的列（高基数）不要 one-hot，会让列数爆炸。」

    .astype(float)    ≈ NumPy 的 .astype(np.float64)，完全一样
"""
)

# ======================================================================
分节(9, "画图：先知道它能画，用的时候抄指导书")
# ======================================================================
print(
    """
    指导书用的是 Plotly（交互式）。原理上就是 pandas 自带的 .plot：

        df["AMT_CREDIT"].plot.hist()        # 直方图：看这一列的分布
        df["TARGET"].value_counts().plot.bar()   # 柱状图：看类别各有多少
        df.plot.scatter(x="A", y="B")       # 散点图：看两个变量关系

    ★ 你现在不用学画图。指导书第五、六章有现成代码，照抄改列名即可。

    画图真正要回答的问题只有一个：这一列能不能区分 TARGET=0 和 TARGET=1。
    指导书实验任务18 就是这么干的（KDE 曲线按 TARGET 分组画）。
    这个东西的本质，就是你在 MNIST 上观察"哪些像素更亮"。
"""
)

# ======================================================================
分节(10, "最后：这些在 CH6_Baseline.py 里长什么样")
# ======================================================================
print(
    """
    你打开 CH6_Baseline.py 会看到这些（都是上面 1-8 节的东西）：

      pd.read_csv(TRAIN_PATH)                     ← 第 1 节
      train_df.shape                               ← 第 2 节
      df[df["DAYS_EMPLOYED"] == 365243]            ← 第 3 节
      df["DAYS_EMPLOYED"].replace(365243, np.nan)  ← 第 5 节
      bureau.groupby("SK_ID_CURR").agg([...])      ← 第 6 节  ★核心
      pd.merge(主表, 征信特征, on="SK_ID_CURR", how="left")  ← 第 7 节 ★核心
      pd.get_dummies(df, columns=cat_cols)         ← 第 8 节
      submission.to_csv(SUBMISSION_PATH, index=False)  ← 第 1 节

    整个文件 24KB，全部由上面这些拼起来。没有别的东西。

    ───────────────────────────────────────────────
    还有两个你以后会用到、现在不用管的：
      df["pred"].rank()        → 把一列数换成"第几名"，模型融合时用
      pd.qcut(df["x"], 5)      → 把连续值切成 5 段，分箱特征用
    ───────────────────────────────────────────────
"""
)

print("=" * 70)
print("跑完了。现在打开 CH6_Baseline.py，从上往下读，")
print("遇到不认识的写法就回到这个文件找对应的一节。")
print("=" * 70)
