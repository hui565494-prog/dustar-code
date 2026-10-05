# -*- coding: utf-8 -*-
"""
二维图：把邻域点数 c_i 画回平面上
==================================
给定 r，每个点算出 c_i（圆内点数，含自身），然后**用颜色把 c_i 画在点的位置上**。
直方图告诉你 c 有哪些值、各占多少；这张图告诉你**这些值分布在哪儿**——

  · 整片颜色接近      → 疏密均匀，一个 r 就能切出大小一致的粒
  · 同一片点里深浅差很大 → 疏密悬殊，同一个 r 切出的粒粗细差很多
  · 出现"环状/带状"的色带 → 密度分层（同心环、两个月亮这类非凸结构）

用法（文件名可以只写编号）：
    python 2-tool/plot_count_map.py                    # 8 组并列，r=0.12
    python 2-tool/plot_count_map.py --only 04          # 只画⑤同心环，单张大图
    python 2-tool/plot_count_map.py --r 0.20
    python 2-tool/plot_count_map.py --shared           # 8 组共用一条色阶（比绝对大小）

产出：3-output/count_map_r<r>.png
"""

from __future__ import annotations
import os
import argparse

import numpy as np

from granulate_radius import neighborhood_counts, resolve_npz, OUT_DIR

TITLES = {
    "00": "① 均匀随机",
    "01": "② 高斯混合·等密度",
    "02": "③ 密度悬殊+离群",
    "03": "④ 两个月亮",
    "04": "⑤ 同心环",
    "05": "⑥ 层次嵌套(粗)",
    "06": "⑥b 层次嵌套(细)",
    "07": "⑦ 双螺旋",
}
ORDER = ["00", "01", "02", "03", "04", "05", "06", "07"]

# 与网页算子台同一套色阶：浅青蓝 → 深藏蓝
RAMP = ["#bcd7ee", "#7db2dd", "#4183bd", "#235b91", "#12334f"]


def main():
    ap = argparse.ArgumentParser(description="c_i 的二维分布图（点按邻域点数着色）")
    ap.add_argument("--r", type=float, default=0.12, help="半径 r（默认 0.12）")
    ap.add_argument("--only", default=None, help="只画一个点集：写编号如 04")
    ap.add_argument(
        "--shared",
        action="store_true",
        help="8 组共用同一条色阶（能比绝对大小，但小范围的组会偏淡）",
    )
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
    from matplotlib.colors import LinearSegmentedColormap

    cmap = LinearSegmentedColormap.from_list("granule", RAMP)

    codes = ORDER if args.only is None else [str(args.only).zfill(2)]
    outdir = args.outdir or (OUT_DIR if os.path.isdir(OUT_DIR) else ".")

    items = []
    for code in codes:
        X = np.load(resolve_npz(code))["X"]
        C = neighborhood_counts(X, args.r)
        items.append((code, X, C))
        print(
            f"  {code} {TITLES.get(code,'?'):26s} n={len(X):4d}  "
            f"c 范围 {int(C.min())}~{int(C.max())}  均值 {C.mean():7.3f}  "
            f"变异系数 {C.std()/C.mean():.3f}"
        )

    # 色阶：默认每组按自身范围归一化（看空间结构），--shared 则全图同一把尺子
    vlo = int(min(c.min() for _, _, c in items))
    vhi = int(max(c.max() for _, _, c in items))

    ncol = 4 if len(items) > 1 else 1
    nrow = int(np.ceil(len(items) / ncol))
    # 只画一组时给张大画布，别还是按 1/4 格子的大小出图
    if len(items) == 1:
        figsize = (7.4, 6.9)
    else:
        figsize = (4.35 * ncol, 4.05 * nrow)
    fig, axes = plt.subplots(nrow, ncol, figsize=figsize, squeeze=False)

    for k, (code, X, C) in enumerate(items):
        ax = axes[k // ncol][k % ncol]
        lo, hi = (vlo, vhi) if args.shared else (int(C.min()), int(C.max()))
        if hi == lo:
            hi = lo + 1
        ax.scatter(
            X[:, 0],
            X[:, 1],
            c=C,
            cmap=cmap,
            vmin=lo,
            vmax=hi,
            s=17,
            linewidths=0,
            alpha=0.95,
        )

        # 等比例显示：用 datalim 而不是 box。
        # box 会自动改坐标框的形状，跟 tight_layout 抢位置，横向特别宽的数据
        # （如④两个月亮 x 跨 3.15、y 只有 1.67）会把点画到框外面去。
        # 这里不手动定坐标范围，交给等比例去撑——自己再设范围会触发
        # "Ignoring fixed limits…" 警告，且留白偏大。
        ax.margins(0.07)
        ax.set_aspect("equal", adjustable="datalim")
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color("#cfd8e5")
        ax.set_title(TITLES.get(code, code) + f"　n={len(X)}", fontsize=11.5)
        ax.set_xlabel(
            f"c: {int(C.min())}~{int(C.max())}　均值 {C.mean():.1f}　"
            f"CV={C.std()/C.mean():.2f}",
            fontsize=8.5,
            color="#5b6b80",
        )
        # 细色条，直接用该组的真实 c 值标注 → 每个子图都能自己读懂
        cb = fig.colorbar(
            plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(lo, hi)),
            ax=ax,
            fraction=0.043,
            pad=0.015,
        )
        cb.ax.tick_params(labelsize=8)
        cb.outline.set_edgecolor("#cfd8e5")

    for k in range(len(items), nrow * ncol):
        axes[k // ncol][k % ncol].axis("off")

    scale = "8 组共用同一条色阶" if args.shared else "每组色阶按自身 c 的范围归一化"
    fig.suptitle(
        f"邻域点数 c_i 的二维分布　·　r = {args.r:g}　·　"
        f"颜色 = 该点圆内的点数（含自身）　·　颜色越深 = 粒越粗\n{scale}",
        fontsize=12.5,
        y=0.99,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))

    tag = f"r{args.r:g}" + ("" if args.only is None else "_" + str(args.only).zfill(2))
    os.makedirs(outdir, exist_ok=True)
    dst = os.path.join(outdir, f"count_map_{tag}.png")
    fig.savefig(dst, dpi=150, facecolor="white")
    print(f"\n[saved] {dst}")


if __name__ == "__main__":
    main()
