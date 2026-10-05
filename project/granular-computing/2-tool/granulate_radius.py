# -*- coding: utf-8 -*-
"""
粒化第一步 · 半径 r 下的逐点邻域计数（Python 版算子，与网页算子台完全同构）
=============================================================================
定义（本次算子，只有这一条）：

    N_r(p_i) = { p_j ∈ P : ‖p_i − p_j‖₂ ≤ r }        # 闭球，含自身
    c_i      = |N_r(p_i)|  ≥ 1

把 c_i 作为第 3 个字段写回点：  p_i = (x_i, y_i, c_i)

为什么先做这一步：
  · c_i 是「这个点所在的那颗粒有多粗」最原始的一个度量——它不依赖任何聚类算法，
    没有迭代、没有初值、没有超参数（除了 r 本身），所以它把「多粗才够(Q3)」
    这个问题赤裸地摊在你面前：你唯一能调的就是 r。
  · 它同时是后面所有粒化模型（邻域粒 / 粒球 / GBC / 模糊粒）的共同地基。

用法
----
命令行（在项目根目录或 2-tool/ 下都能跑）：
    python 2-tool/granulate_radius.py                        # 默认 points_00，r=0.12
    python 2-tool/granulate_radius.py 1-data/points_02.npz --r 0.12
    python 2-tool/granulate_radius.py points_03 --r 0.10 --i 250 --order lr

当库用：
    from granulate_radius import neighborhood_counts, granulate_one, radius_curve
    C = neighborhood_counts(X, 0.12)          # (n,) 每个点的 c_i
    Xc = np.c_[X, C]                          # c 存进点里

产出（写进 3-output/）：
    <name>_granulated_r<r>.npz    含 X / y / c / r
    <name>_granulated_r<r>.png    四联图：原始 · 过程 · 结果 · 粒度曲线
"""

from __future__ import annotations
import os
import glob
import argparse

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))  # 2-tool/
ROOT = os.path.dirname(HERE)  # 项目根
DATA_DIR = os.path.join(ROOT, "1-data")
OUT_DIR = os.path.join(ROOT, "3-output")


def resolve_npz(arg: str | None) -> str:
    """把 '02' / 'points_02' / 'points_02.npz' / 完整路径 都解析成存在的文件路径。"""
    if arg is None:
        hits = sorted(glob.glob(os.path.join(DATA_DIR, "points_*.npz")))
        if not hits:
            raise SystemExit(f"没给文件名，且 {DATA_DIR} 里没有 points_*.npz")
        return hits[0]
    if os.path.isfile(arg):
        return arg
    name = os.path.basename(arg)
    if name.isdigit():
        name = "points_" + name.zfill(2)
    if not name.endswith(".npz"):
        name += ".npz"
    for cand in (os.path.join(DATA_DIR, name), name):
        if os.path.isfile(cand):
            return cand
    raise SystemExit(f"找不到 {name}（{DATA_DIR} 里也没有）")


# ============================================================
# 一、算子本体
# ============================================================


def pairwise_dist(X: np.ndarray) -> np.ndarray:
    """(n,2) → (n,n) 欧氏距离矩阵。纯 NumPy 广播，n≤几千时足够快。"""
    X = np.asarray(X, dtype=float)
    d = X[:, None, :] - X[None, :, :]
    return np.sqrt((d * d).sum(axis=-1))


def neighborhood_counts(
    X: np.ndarray, r: float, D: np.ndarray | None = None
) -> np.ndarray:
    """c_i = |{ j : ‖p_i − p_j‖ ≤ r }|（含 j = i，故 c_i ≥ 1）。返回 int 数组 (n,)。

    注意是「≤」不是「<」：闭球。r 恰好等于某个距离时该点计入——
    这个约定在边界情形（等距格阵）下会直接改变结果，所以写死在这里、不留给默认值。
    """
    if D is None:
        D = pairwise_dist(X)
    return (D <= r).sum(axis=1).astype(int)


def radius_curve(
    X: np.ndarray, r_max: float = 0.8, steps: int = 64, D: np.ndarray | None = None
):
    """扫 r，返回 (rs, mean_c, n_granule)。

    mean_c    —— 本次算子的平均粒度
    n_granule —— 「距离 ≤ r」做传递闭包后的粒个数（延伸量，网页里那条虚线）
                 r=0 时 = n（每个点是自己的粒）；r 足够大时 = 1（全并成一粒）。
    两条线一起看才是 Q3：粒度什么时候就不再变细了？
    """
    if D is None:
        D = pairwise_dist(X)
    n = len(D)
    rs = np.linspace(0.0, r_max, steps + 1)
    mean_c = np.empty_like(rs)
    n_gran = np.empty(len(rs), dtype=int)
    for k, r in enumerate(rs):
        A = D <= r
        mean_c[k] = A.sum() / n
        n_gran[k] = _connected_components(A)
    return rs, mean_c, n_gran


def _connected_components(adj: np.ndarray) -> int:
    """邻接矩阵的连通分量数（并查集，纯 NumPy 循环，不依赖 scipy）。"""
    n = adj.shape[0]
    par = np.arange(n)

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a

    iu, ju = np.nonzero(np.triu(adj, 1))
    for i, j in zip(iu.tolist(), ju.tolist()):
        a, b = find(i), find(j)
        if a != b:
            par[a] = b
    return len({find(i) for i in range(n)})


def granulate_one(X, y, r, order="index", i=None, seed=0):
    """一次完整调用：返回 dict，含 c、遍历序、被考察的点 i、以及 D。"""
    X = np.asarray(X, dtype=float)
    D = pairwise_dist(X)
    c = neighborhood_counts(X, r, D)
    n = len(X)

    if order == "lr":
        idx = np.argsort(X[:, 0], kind="stable")
    elif order == "out":
        ctr = X.mean(axis=0)
        idx = np.argsort(((X - ctr) ** 2).sum(axis=1), kind="stable")
    elif order == "rand":
        rng = np.random.default_rng(seed)
        idx = rng.permutation(n)
    else:
        idx = np.arange(n)

    if i is None:
        # 默认挑一个「有代表性」的点：c 最接近中位数
        i = int(np.argsort(np.abs(c - np.median(c)))[0])
    return dict(
        X=X, y=np.asarray(y), r=float(r), c=c, D=D, order=order, order_idx=idx, i=int(i)
    )


# ============================================================
# 二、把过程画出来
# ============================================================


def _cn_font():
    import matplotlib

    matplotlib.rcParams["font.sans-serif"] = [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "DejaVu Sans",
    ]
    matplotlib.rcParams["axes.unicode_minus"] = False


def _color_by_c(c):
    """按 c 上色：浅青蓝 → 深藏蓝，与网页同一套色阶。"""
    import matplotlib
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list(
        "granule", ["#bcd7ee", "#4183bd", "#12334f"]
    )


def plot_process(res, out_png=None, figsize=(17.0, 7.0)):
    """四联图：① 原始 ② 计数过程 ③ 结果(c 写回点里) ④ r→粒度曲线"""
    import matplotlib

    matplotlib.use("Agg")
    _cn_font()
    import matplotlib.pyplot as plt

    X, y, r, c, D, i = res["X"], res["y"], res["r"], res["c"], res["D"], res["i"]
    n = len(X)
    nb = np.nonzero(D[i] <= r)[0]
    cm = _color_by_c(c)

    fig, axes = plt.subplots(1, 4, figsize=figsize)
    box = (
        X[:, 0].min() - 0.1,
        X[:, 0].max() + 0.1,
        X[:, 1].min() - 0.1,
        X[:, 1].max() + 0.1,
    )

    def frame(ax, title, sub=None):
        ax.set_title(title, fontsize=11.5)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlim(box[0], box[1])
        ax.set_ylim(box[2], box[3])
        if sub:
            ax.set_xlabel(sub, fontsize=8.5, color="#666")

    # ① 原始素材：不起眼，但它才是被施加算子的东西
    ax = axes[0]
    ax.scatter(X[:, 0], X[:, 1], s=11, c="#5b6b80", linewidths=0)
    frame(ax, "① 原始点云（未加工）", f"n = {n}")

    # ② 过程：以 p_i 为圆心、r 为半径，圆内的点全部连到圆心
    ax = axes[1]
    ax.scatter(X[:, 0], X[:, 1], s=11, c="#cdd6e2", linewidths=0)
    ax.scatter(
        X[nb, 0],
        X[nb, 1],
        s=22,
        facecolors="none",
        edgecolors="#d9480f",
        linewidths=1.3,
    )
    for j in nb:
        if j != i:
            ax.plot(
                [X[i, 0], X[j, 0]],
                [X[i, 1], X[j, 1]],
                color="#d9480f",
                lw=0.7,
                alpha=0.35,
                zorder=1,
            )
    ax.add_patch(
        plt.Circle(
            X[i], r, facecolor="#d9480f", alpha=0.09, edgecolor="#d9480f", lw=1.5
        )
    )
    ax.plot(
        [X[i, 0], X[i, 0] + r],
        [X[i, 1], X[i, 1]],
        color="#d9480f",
        lw=1,
        ls=(0, (4, 3)),
    )
    ax.scatter(
        [X[i, 0]],
        [X[i, 1]],
        s=52,
        facecolors="none",
        edgecolors="#1c4e79",
        linewidths=1.8,
        zorder=5,
    )
    frame(
        ax,
        "② 计数过程：圆内点数（含自身）",
        f"p[{i}] 的邻域 N_r = {len(nb)} 个点　→　c[{i}] = {c[i]}",
    )

    # ③ 结果：c 已经写进每个点，颜色/大小直接读出粒度
    ax = axes[2]
    sizes = 14 + 90 * np.sqrt((c - c.min()) / max(1, c.max() - c.min()))
    ax.scatter(X[:, 0], X[:, 1], s=sizes, c=c, cmap=cm, linewidths=0)
    ax.scatter(
        [X[i, 0]],
        [X[i, 1]],
        s=110,
        facecolors="none",
        edgecolors="#d9480f",
        linewidths=1.8,
    )
    frame(ax, "③ 结果：c 存进每个点", "点面积 ∝ c　→　一眼看出哪儿粗哪儿细")
    cb = fig.colorbar(
        plt.cm.ScalarMappable(cmap=cm, norm=plt.Normalize(c.min(), c.max())),
        ax=ax,
        fraction=0.045,
        pad=0.02,
    )
    cb.set_label("c_i", fontsize=9)

    # ④ r → 粒度：调 r 是唯一的旋钮，这条线告诉你它有多敏感
    ax = axes[3]
    rs, mean_c, n_gran = radius_curve(X, r_max=max(0.8, r * 3), D=D)
    ax.plot(rs, mean_c, color="#2b6ca3", lw=2, label="平均 c（左轴）")
    ax.set_xlabel("半径 r", fontsize=9.5)
    ax.set_ylabel("平均 c", color="#2b6ca3", fontsize=9.5)
    ax.tick_params(axis="y", labelcolor="#2b6ca3", labelsize=8.5)
    ax.tick_params(axis="x", labelsize=8.5)
    ax.axvline(r, color="#d9480f", ls=(0, (3, 3)), lw=1.4)
    ax.plot([r], [mean_c[np.argmin(np.abs(rs - r))]], "o", color="#d9480f", ms=5)
    ax2 = ax.twinx()
    ax2.plot(rs, n_gran, color="#c78a4e", lw=1.4, ls=(0, (4, 3)), label="粒数（右轴）")
    ax2.set_ylabel("粒数（连通闭包）", color="#c78a4e", fontsize=9.5)
    ax2.tick_params(axis="y", labelcolor="#c78a4e", labelsize=8.5)
    ax.set_title("④ 调 r 的代价", fontsize=11.5)
    ax.grid(alpha=0.25)

    k = np.argmin(np.abs(rs - r))
    fig.suptitle(
        f"半径粒化 · r = {r:g}　|　n = {n}，平均 c = {c.mean():.2f}，"
        f"min = {c.min()}，max = {c.max()}，孤立点(c=1) = {int((c == 1).sum())} 个"
        f"　|　此时若把邻域闭包成粒，是 {n_gran[k]} 粒",
        fontsize=12,
        y=0.985,
    )
    fig.tight_layout(rect=(0, 0, 0.995, 0.95), w_pad=1.6)

    if out_png:
        fig.savefig(out_png, dpi=150, facecolor="white")
        print(f"[saved] {out_png}")
    return fig


# ============================================================
# 三、主流程
# ============================================================


def main():
    ap = argparse.ArgumentParser(description="半径 r 下的逐点邻域计数")
    ap.add_argument(
        "npz",
        nargs="?",
        default=None,
        help="点集文件；可写 02 / points_02 / points_02.npz / 完整路径。不给则用 1-data/ 里第一个",
    )
    ap.add_argument(
        "--r", type=float, default=0.12, help="半径 r（数据坐标，默认 0.12）"
    )
    ap.add_argument("--i", type=int, default=None, help="要画成「过程」的那个点的下标")
    ap.add_argument(
        "--order",
        default="index",
        choices=["index", "lr", "out", "rand"],
        help="遍历序（只影响过程图的取点口吻）",
    )
    ap.add_argument(
        "--outdir",
        default=None,
        help="产出目录，默认 3-output/（不存在时与输入同目录）",
    )
    ap.add_argument(
        "--no-save",
        action="store_true",
        help="只打印数值，不写 npz / 不画图（试参数时用）",
    )
    args = ap.parse_args()

    path = resolve_npz(args.npz)
    P = np.load(path)
    X = P["X"]
    y = P["y"] if "y" in P else np.zeros(len(X), dtype=int)
    name = os.path.splitext(os.path.basename(path))[0]

    if args.outdir:
        outdir = args.outdir
    elif os.path.isdir(OUT_DIR):
        outdir = OUT_DIR
    else:
        outdir = os.path.dirname(os.path.abspath(path))
    os.makedirs(outdir, exist_ok=True)

    res = granulate_one(X, y, args.r, order=args.order, i=args.i)
    c = res["c"]

    print(f"点集 {name}（{path}）")
    print(f"  n={len(X)}  r={args.r:g}")
    print(
        f"  c_i ：min={c.min()}  mean={c.mean():.3f}  max={c.max()}  "
        f"孤立点(c=1)={int((c == 1).sum())}"
    )
    print(
        f"  被考察的点 p[{res['i']}]：c = {c[res['i']]}，"
        f"邻域内点号 = {np.nonzero(res['D'][res['i']] <= args.r)[0][:20].tolist()}"
        f"{' …' if c[res['i']] > 20 else ''}"
    )

    tag = f"r{args.r:g}"
    if args.no_save:
        return
    out_npz = os.path.join(outdir, f"{name}_granulated_{tag}.npz")
    np.savez(out_npz, X=X, y=y, c=c, r=args.r, order_idx=res["order_idx"])
    print(f"[saved] {out_npz}")
    plot_process(res, out_png=os.path.join(outdir, f"{name}_granulated_{tag}.png"))


if __name__ == "__main__":
    main()
