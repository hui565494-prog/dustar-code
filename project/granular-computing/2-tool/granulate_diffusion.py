# -*- coding: utf-8 -*-
"""
扩散粒化（Python 版，与网页算子台完全同构）
=============================================
定义（你给的那条）：

    1) 种子 = 当前未分配点中 c_i 最大的点     （c_i = 半径 r 的圆内点数，含自身）
    2) 粒   = 从种子出发，沿「距离 ≤ r」不断扩散所及的全部未分配点
              —— 一跳、二跳……都算同一粒
    3) 边界 = 始终没被任何粒纳入的点（绝对不被包含）
    4) 回到 1)，直到剩下的点里没有 c_i ≥ 2 的种子

一个必须知道的推论
------------------
把「扩散到不动」写出来就是连通闭包，所以**不限跳数时**：

    粒 = 连通分量（点数 ≥ 2 的那些）
    边界 = 孤立点（单点分量）

也就是说此时边界只可能是孤立点，r 一大就归零。想让「边界」真正有意思，
得给扩散一个停止条件——脚本里的 `max_hop`，对应网页上的「跳数上限」。

用法（文件名可以只写编号）：
    python 2-tool/granulate_diffusion.py                       # 8 组并列，r=0.12
    python 2-tool/granulate_diffusion.py --only 04 --r 0.06
    python 2-tool/granulate_diffusion.py --maxhop 2            # 只扩散 2 跳
    python 2-tool/granulate_diffusion.py --save                # 顺便存 npz

产出：3-output/diffusion_r<r>.png（--only 时是单张大图）
"""

from __future__ import annotations
import os
import argparse

import numpy as np

from granulate_radius import neighborhood_counts, pairwise_dist, resolve_npz, OUT_DIR

TITLES = {
    "00": "① 均匀随机",
    "01": "② 高斯混合",
    "02": "③ 密度悬殊+离群",
    "03": "④ 两个月亮",
    "04": "⑤ 同心环",
    "05": "⑥ 层次嵌套(粗)",
    "06": "⑥b 层次嵌套(细)",
    "07": "⑦ 双螺旋",
}
ORDER = ["00", "01", "02", "03", "04", "05", "06", "07"]
BOUND_C = "#9aa7b6"


# ============================================================
# 一、算子本体
# ============================================================


def diffuse_granules(X, r, max_hop=None, D=None):
    """返回 (lab, hop, parent, granules)。

    lab     : (n,) 粒号；-1 = 落在边界
    hop     : (n,) 第几跳被纳入；边界为 -1
    parent  : (n,) 被哪个点拉进来的；种子与边界为 -1
    granules: [{'seed':, 'members': [按扩散顺序], 'max_hop':}]
    """
    X = np.asarray(X, dtype=float)
    n = len(X)
    if D is None:
        D = pairwise_dist(X)
    c = neighborhood_counts(X, r, D)

    lab = np.full(n, -1, dtype=int)
    hop = np.full(n, -1, dtype=int)
    par = np.full(n, -1, dtype=int)
    granules = []

    K = np.inf if max_hop is None else max_hop
    # 种子顺序：c 降序（并列按点号，保证可复现）
    cand = np.lexsort((np.arange(n), -c))

    for s in cand:
        if lab[s] != -1:
            continue
        if c[s] < 2:  # c 已降序，后面都不会有邻居 → 剩下的全是边界
            break
        g = len(granules)
        lab[s] = g
        hop[s] = 0
        members = [int(s)]
        front = [int(s)]
        while front:
            nxt = []
            for u in front:
                if hop[u] >= K:
                    continue
                for v in np.nonzero((D[u] <= r) & (lab == -1))[0]:
                    v = int(v)
                    lab[v] = g
                    hop[v] = hop[u] + 1
                    par[v] = u
                    members.append(v)
                    nxt.append(v)
            front = nxt
        if len(members) < 2:  # 只剩自己 → 不成立，留给边界
            lab[s] = -1
            hop[s] = -1
            continue
        granules.append(
            {
                "seed": int(s),
                "members": members,
                "max_hop": int(max(hop[m] for m in members)),
            }
        )
    return lab, hop, par, granules


def components(D, r):
    """独立表征用：并查集数连通分量。不限跳数时应有
    粒数 = 点数≥2 的分量数，边界数 = 单点分量数。"""
    n = len(D)
    par = list(range(n))

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a

    iu, ju = np.nonzero(np.triu(D <= r, 1))
    for i, j in zip(iu.tolist(), ju.tolist()):
        a, b = find(i), find(j)
        if a != b:
            par[a] = b
    from collections import Counter

    sizes = Counter(find(i) for i in range(n)).values()
    sizes = list(sizes)
    return len(sizes), sum(1 for v in sizes if v == 1)


# ============================================================
# 二、作图
# ============================================================


def _hsl_to_rgb(h, s, l):
    """与网页同一套配色（HSL 黄金角色相）→ 保证两边的粒颜色对得上。"""
    h = (h % 360) / 360.0
    c = (1 - abs(2 * l - 1)) * s
    hp = h * 6
    x = c * (1 - abs(hp % 2 - 1))
    m = l - c / 2
    rgb = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][
        int(hp) % 6
    ]
    return tuple(np.clip(v + m, 0, 1) for v in rgb)


def gran_color(g):
    """hue = (g*137.508 + 208) % 360 —— 与网页 diffusion_template.html 里的 GRAN_H 一致。"""
    return _hsl_to_rgb(g * 137.508 + 208, 0.58, 0.46)


def main():
    ap = argparse.ArgumentParser(description="扩散粒化")
    ap.add_argument("--r", type=float, default=0.12, help="半径 r（默认 0.12）")
    ap.add_argument(
        "--maxhop",
        type=int,
        default=None,
        help="扩散跳数上限；不给＝不限（此时边界＝孤立点）",
    )
    ap.add_argument("--only", default=None, help="只画一组，写编号如 04")
    ap.add_argument("--save", action="store_true", help="顺便把 lab/hop 存成 npz")
    ap.add_argument("--outdir", default=None, help="产出目录，默认 3-output/")
    args = ap.parse_args()

    import matplotlib

    matplotlib.use("Agg")
    matplotlib.rcParams["font.sans-serif"] = [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "DejaVu Sans",
    ]
    matplotlib.rcParams["axes.unicode_minus"] = False
    import matplotlib.pyplot as plt

    codes = ORDER if args.only is None else [str(args.only).zfill(2)]
    outdir = args.outdir or (OUT_DIR if os.path.isdir(OUT_DIR) else ".")
    K = args.maxhop

    items = []
    hdr = "%-10s %5s %6s %6s %6s %6s %7s %7s" % (
        "点集",
        "r",
        "n",
        "粒数",
        "边界",
        "边界%",
        "最大粒",
        "最深跳",
    )
    print(hdr)
    for code in codes:
        X = np.load(resolve_npz(code))["X"]
        D = pairwise_dist(X)
        lab, hop, par, grans = diffuse_granules(X, args.r, K, D)
        nbd = int((lab == -1).sum())
        sizes = [len(g["members"]) for g in grans]
        items.append(dict(code=code, X=X, lab=lab, hop=hop, grans=grans))
        print(
            "%-10s %5.2f %6d %6d %6d %5.1f%% %7d %7d"
            % (
                "points_" + code,
                args.r,
                len(X),
                len(grans),
                nbd,
                100 * nbd / len(X),
                max(sizes) if sizes else 0,
                max([g["max_hop"] for g in grans]) if grans else 0,
            )
        )
        if K is None:  # 不限跳数时，用连通分量独立核对一遍
            nc, ns = components(D, args.r)
            assert (
                len(grans) == nc - ns
            ), f"{code}: 粒数 {len(grans)} ≠ 多点多分量 {nc-ns}"
            assert nbd == ns, f"{code}: 边界 {nbd} ≠ 单点分量 {ns}"
        if args.save:
            os.makedirs(outdir, exist_ok=True)
            dst = os.path.join(
                outdir,
                f"points_{code}_diffusion_r{args.r:g}"
                + (f"_k{K}" if K else "")
                + ".npz",
            )
            np.savez(
                dst,
                X=X,
                lab=lab,
                hop=hop,
                parent=par,
                seeds=np.array([g["seed"] for g in grans]),
                r=args.r,
            )
            print("   [saved]", dst)
    print("（不限跳数时已用连通分量独立核对通过）" if K is None else "")

    # ---------- 画 ----------
    ncol = 4 if len(items) > 1 else 1
    nrow = int(np.ceil(len(items) / ncol))
    figsize = (7.6, 7.0) if len(items) == 1 else (4.35 * ncol, 4.05 * nrow)
    fig, axes = plt.subplots(nrow, ncol, figsize=figsize, squeeze=False)

    for k, it in enumerate(items):
        ax = axes[k // ncol][k % ncol]
        X, lab, grans = it["X"], it["lab"], it["grans"]
        bd = lab == -1
        # 边界：空心灰圈，单独一层
        if bd.any():
            ax.scatter(
                X[bd, 0],
                X[bd, 1],
                s=22,
                facecolors="none",
                edgecolors=BOUND_C,
                linewidths=1.3,
                zorder=1,
            )
        for g, gr in enumerate(grans):
            m = np.array(gr["members"])
            ax.scatter(
                X[m, 0], X[m, 1], s=15, c=[gran_color(g)], linewidths=0, zorder=2
            )
            ax.scatter(
                [X[gr["seed"], 0]],
                [X[gr["seed"], 1]],
                s=52,
                facecolors="none",
                edgecolors="#16202f",
                linewidths=1.7,
                zorder=4,
            )
        ax.margins(0.07)
        ax.set_aspect("equal", adjustable="datalim")
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color("#cfd8e5")
        nbd = int(bd.sum())
        ax.set_title(
            TITLES.get(it["code"], it["code"]) + f"　n={len(X)}", fontsize=11.5
        )
        ax.set_xlabel(
            f"粒 {len(grans)}　边界 {nbd} ({100*nbd/len(X):.1f}%)　"
            f"最大粒 {max([len(g['members']) for g in grans]) if grans else 0}",
            fontsize=8.5,
            color="#5b6b80",
        )

    for k in range(len(items), nrow * ncol):
        axes[k // ncol][k % ncol].axis("off")

    ktext = "不限跳数（扩散到不动）" if K is None else f"跳数上限 {K}"
    fig.suptitle(
        f"扩散粒化　·　r = {args.r:g}　·　{ktext}\n"
        f"种子＝未分配点中 c_i 最大者（黑圈）；粒＝从种子沿「距离 ≤ r」扩散所及的全部点（同色）；"
        f"边界＝始终没被纳入的点（空心灰圈）",
        fontsize=12,
        y=0.99,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))

    tag = (
        f"r{args.r:g}"
        + (f"_k{K}" if K else "")
        + ("" if args.only is None else "_" + str(args.only).zfill(2))
    )
    os.makedirs(outdir, exist_ok=True)
    dst = os.path.join(outdir, f"diffusion_{tag}.png")
    fig.savefig(dst, dpi=150, facecolor="white")
    print("[saved]", dst)


if __name__ == "__main__":
    main()
