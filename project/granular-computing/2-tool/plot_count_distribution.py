# -*- coding: utf-8 -*-
"""
一个图看懂「邻域点数 c_i 的分布」
================================
给定 r，每个点算出一个 c_i（圆内点数，含自身）。把所有 c_i 摆在一起看，
就得到这个点集的**粒度分布**——它比看散点图更直接：

  · 分布窄 + 单峰    → 这片点的疏密差不多，用这个 r 切出来的粒大小均匀
  · 分布宽 + 长尾    → 疏密悬殊，同一个 r 在稠密处切出大粒、在稀疏处切出小粒
  · 两个峰            → 这片点里存在两种不同的密度层次（比如同心环、两个月亮）
  · 挤在最左边(=1)    → 太多点和谁都不相邻，r 太小了

用法（文件名可以只写编号）：
    python 2-tool/plot_count_distribution.py                    # 8 组点集并列，r=0.12
    python 2-tool/plot_count_distribution.py --r 0.20
    python 2-tool/plot_count_distribution.py --only 03          # 只看①组

产出：3-output/count_distribution_r<r>.png
"""

from __future__ import annotations
import os
import argparse

import numpy as np

from granulate_radius import neighborhood_counts, resolve_npz, DATA_DIR, OUT_DIR

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


def panel_stats(C):
    n = len(C)
    s = {
        "n": n,
        "mean": float(C.mean()),
        "med": float(np.median(C)),
        "sd": float(C.std()),
        "min": int(C.min()),
        "max": int(C.max()),
        "one": int((C == 1).sum()),
    }
    s["cv"] = s["sd"] / s["mean"] if s["mean"] else 0.0
    s["one_pct"] = 100.0 * s["one"] / n
    return s


def main():
    ap = argparse.ArgumentParser(description="邻域点数 c_i 的分布（一张图）")
    ap.add_argument("--r", type=float, default=0.12, help="半径 r（默认 0.12）")
    ap.add_argument(
        "--only", default=None, help="只画一个点集：写编号如 03（不写则 8 组并列）"
    )
    ap.add_argument("--outdir", default=None, help="产出目录，默认 3-output/")
    ap.add_argument("--bins", type=int, default=None, help="直方图柱数，默认按数据自动")
    ap.add_argument(
        "--shared",
        action="store_true",
        help="所有子图共用同一横纵轴（便于比大小，但小范围的组会看不清形状）",
    )
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
    from matplotlib.ticker import MaxNLocator

    codes = ORDER if args.only is None else [str(args.only).zfill(2)]
    outdir = args.outdir or (OUT_DIR if os.path.isdir(OUT_DIR) else ".")

    # ---- 先把所有 c_i 算出来（用的是与网页完全同一个算子）----
    items = []
    for code in codes:
        path = resolve_npz(code)
        X = np.load(path)["X"]
        C = neighborhood_counts(X, args.r)
        items.append((code, C))
        st = panel_stats(C)
        print(
            f"  {code} {TITLES.get(code,'?'):18s} n={st['n']:4d}  "
            f"mean={st['mean']:7.3f}  中位={st['med']:6.1f}  max={st['max']:4d}  "
            f"变异系数={st['cv']:.3f}  c=1 占 {st['one_pct']:5.1f}%"
        )

    # ---- 分箱：整数宽度、横纵轴各自缩放 ----
    # c_i 是整数，柱宽取整数才不会出现 2.5/7.5 这种边界。
    # 统一横轴会让 c 只有 12 的组挤成一条线（形状全丢），而"看形状"才是这张图的目的，
    # 所以默认每组按自身范围缩放；想按同一把尺子比大小，加 --shared。
    def make_edges(lo, hi, target):
        span = hi - lo + 1
        wa = max(1, int(round(span / target)))
        nb = int(np.ceil(span / wa))
        return lo + np.arange(nb + 1) * wa

    if args.shared:
        glo = min(int(c.min()) for _, c in items)
        ghi = max(int(c.max()) for _, c in items)
        shared_edges = make_edges(glo, ghi, args.bins or 18)

    panels = []
    for code, C in items:
        lo, hi = int(C.min()), int(C.max())
        e = shared_edges if args.shared else make_edges(lo, hi, args.bins or 18)
        pct, _ = np.histogram(C, bins=e)
        panels.append((code, C, e, 100.0 * pct / len(C)))

    ncol = 4 if len(items) > 1 else 1
    nrow = int(np.ceil(len(items) / ncol))
    fig, axes = plt.subplots(
        nrow, ncol, figsize=(4.3 * ncol, 3.4 * nrow), squeeze=False
    )

    for k, (code, C, edges, h) in enumerate(panels):
        ax = axes[k // ncol][k % ncol]
        st = panel_stats(C)
        ymax = h.max() * 1.32
        ax.bar(
            edges[:-1],
            h,
            width=np.diff(edges),
            align="edge",
            color="#7db2dd",
            edgecolor="white",
            linewidth=0.6,
        )
        ax.axvline(st["mean"], color="#d9480f", lw=1.5, ls=(0, (4, 3)))
        ax.annotate(
            f"均值 {st['mean']:.1f}",
            xy=(st["mean"], ymax * 0.97),
            xytext=(4, 0),
            textcoords="offset points",
            color="#d9480f",
            fontsize=8.5,
            va="top",
        )
        if abs(st["med"] - st["mean"]) / max(st["mean"], 1) > 0.08:
            ax.axvline(st["med"], color="#1c4e79", lw=1.1, ls=(0, (2, 3)))
            ax.annotate(
                f"中位 {st['med']:.0f}",
                xy=(st["med"], ymax * 0.80),
                xytext=(4, 0),
                textcoords="offset points",
                color="#1c4e79",
                fontsize=8.5,
                va="top",
            )
        ax.set_ylim(0, ymax)
        t = TITLES.get(code, code) + f"　n={st['n']}"
        if code == "06":
            t += "　（与⑥同一片点，只是标签不同）"
        ax.set_title(t, fontsize=11.5)
        ax.tick_params(labelsize=8.5)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins="auto"))
        ax.grid(axis="y", alpha=0.22, lw=0.6)
        ax.set_axisbelow(True)
        ax.set_xlabel(
            f"max={st['max']}　CV={st['cv']:.2f}　" f"孤立点(c=1) {st['one_pct']:.1f}%",
            fontsize=8.5,
            color="#5b6b80",
        )
        if k % ncol == 0:
            ax.set_ylabel("点数占比 %", fontsize=9)

    for k in range(len(items), nrow * ncol):
        axes[k // ncol][k % ncol].axis("off")

    note = "各子图横纵轴按自身范围缩放（加 --shared 可换成同一把尺子）"
    fig.suptitle(
        f"邻域点数 c_i 的分布　·　r = {args.r:g}　·　"
        f"c_i = 以 p_i 为圆心、半径 {args.r:g} 的圆内点数（含自身）\n{note}",
        fontsize=12.5,
        y=0.99,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))

    tag = f"r{args.r:g}" + ("" if args.only is None else "_" + str(args.only).zfill(2))
    os.makedirs(outdir, exist_ok=True)
    dst = os.path.join(outdir, f"count_distribution_{tag}.png")
    fig.savefig(dst, dpi=150, facecolor="white")
    print(f"\n[saved] {dst}")


if __name__ == "__main__":
    main()
