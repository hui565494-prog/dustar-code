# -*- coding: utf-8 -*-
"""
把 1-data/ 里 8 组原始点集画成一张总览图（点图，按簇着色便于区分结构）。

用法（在 2-tool/ 下）：
    python make_gallery.py                 # 8 组 2x4，r 无关
    python make_gallery.py --truth         # 用 npz 里的真值 y 着色
    python make_gallery.py --out xxx.png   # 指定输出
产出默认写 3-output/data_gallery.png
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from granulate_radius import resolve_npz  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "3-output")

IDS = ["00", "01", "02", "03", "04", "05", "06", "07"]
HINT = {
    "00": "对照组：任何 r 都同样「对」",
    "01": "标准情形：检验基本功",
    "02": "粗粒该不该吃掉离群点",
    "03": "局部判据 vs 全局距离",
    "04": "什么时候该说「我不分了」",
    "05": "多粒度：粗的那版答案",
    "06": "多粒度：细的那版答案",
    "07": "两类互为 180° 交替贴近",
}
TITLE = {
    "00": "① 均匀随机（无结构）",
    "01": "② 高斯混合·等密度",
    "02": "③ 密度悬殊 + 离群点",
    "03": "④ 两个月亮（非凸缠绕）",
    "04": "⑤ 同心环（内外密度不同）",
    "05": "⑥ 层次嵌套·粗粒度真值",
    "06": "⑥b 层次嵌套·细粒度真值",
    "07": "⑦ 双螺旋",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--truth", action="store_true", help="用 npz 里的真值标签 y 着色")
    ap.add_argument("--out", default=None)
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from matplotlib.ticker import MaxNLocator

    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, axes = plt.subplots(2, 4, figsize=(19.2, 9.6))
    axes = axes.ravel()
    cmap = ListedColormap(plt.get_cmap("tab20")(np.linspace(0, 1, 20)))

    for k, sid in enumerate(IDS):
        path = resolve_npz(sid)
        z = np.load(path)
        X, y = z["X"], z["y"].astype(int)
        ax = axes[k]
        if args.truth:
            ax.scatter(X[:, 0], X[:, 1], c=y, cmap=cmap, s=13, linewidths=0)
        else:
            # 不做任何粒化：按真值分块粗着色，只为看清"有几坨"
            ax.scatter(
                X[:, 0], X[:, 1], c=y, cmap="tab10", s=13, linewidths=0, alpha=0.9
            )
        title = TITLE.get(sid, "数据集" + sid)
        ax.set_title(f"{title}   n={len(X)}", fontsize=12)
        ax.text(
            0.5,
            -0.09,
            HINT[sid],
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=9,
            color="#666",
        )
        ax.set_aspect("equal", adjustable="datalim")
        ax.margins(0.07)
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color("#bbb")

    fig.suptitle("8 组原始点集总览（未加工：只画点，不做任何粒化）", fontsize=14)
    out = args.out or os.path.join(OUTDIR, "data_gallery.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out, dpi=args.dpi, facecolor="white")
    print("已写出：", out)


if __name__ == "__main__":
    main()
