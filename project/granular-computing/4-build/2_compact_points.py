# -*- coding: utf-8 -*-
"""把 cache/_points.json 精简（坐标保留 8 位小数）并输出统计，供 HTML 内嵌。"""
import json, os

BUILD = os.path.dirname(os.path.abspath(__file__))  # 4-build/
CACHE = os.path.join(BUILD, "cache")
with open(os.path.join(CACHE, "_points.json"), encoding="utf-8") as f:
    raw = json.load(f)

META = {
    "00": ("① 均匀随机（无结构）", "没有任何结构，任何 r 都同样“对”——对照组"),
    "01": ("② 高斯混合·等密度", "四团等密度，标准情形"),
    "02": ("③ 密度悬殊 + 离群点", "三团密度差 4 倍，另有 14 个离群点"),
    "03": ("④ 两个月亮（非凸缠绕）", "非凸、互相缠绕，全局判据的陷阱"),
    "04": ("⑤ 同心环（内外密度不同）", "内环细密、外环松散"),
    "05": ("⑥ 层次嵌套·粗粒度真值", "3 个大簇，每簇含 3 个小簇"),
    "06": ("⑥b 层次嵌套·细粒度真值", "同一片点的另一种“对”"),
    "07": ("⑦ 双螺旋", "两类互为 180° 旋转，交替贴近"),
}

out = []
for k in sorted(raw.keys()):
    code = k.split("_")[1]
    # 保留 8 位小数：扰动 ~1e-8，远小于任何真实距离间隔，
    # 保证网页里的判定与 npz 原始数据一致（4 位小数会偶尔翻转边界点）
    X = [[round(float(v), 8) for v in p] for p in raw[k]["X"]]
    y = [int(v) for v in raw[k]["y"]]
    xs = [p[0] for p in X]
    ys = [p[1] for p in X]
    title, note = META[code]
    out.append(
        {
            "id": code,
            "title": title,
            "note": note,
            "X": X,
            "y": y,
            "box": [
                round(min(xs), 3),
                round(max(xs), 3),
                round(min(ys), 3),
                round(max(ys), 3),
            ],
        }
    )
    print(
        code,
        title,
        "n=%d" % len(X),
        "x[%.2f,%.2f] y[%.2f,%.2f]" % (min(xs), max(xs), min(ys), max(ys)),
    )

DST = os.path.join(CACHE, "_points_compact.json")
with open(DST, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
print("compact size:", os.path.getsize(DST), "->", DST)
