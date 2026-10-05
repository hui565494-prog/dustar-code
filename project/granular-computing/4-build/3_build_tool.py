# -*- coding: utf-8 -*-
"""把 1-data/ 的点集分别注入两个 HTML 模板，产出 2-tool/ 下的两个交互工具。

  tool_template.html        →  2-tool/granulation_radius_tool.html   （半径邻域计数）
  diffusion_template.html   →  2-tool/diffusion_granulation_tool.html（扩散粒化）

完整重建（在 4-build/ 目录下按顺序跑）：
    python 1_extract_npz.py     # 1-data/*.npz            -> cache/_points.json
    python 2_compact_points.py  # cache/_points.json      -> cache/_points_compact.json
    python 3_build_tool.py      # 注入两个模板             -> 2-tool/*.html
    node   4_selftest.js        # 两个算子一起数值自检
"""
import os, json, re

BUILD = os.path.dirname(os.path.abspath(__file__))  # 4-build/
ROOT = os.path.dirname(BUILD)  # 项目根
CACHE = os.path.join(BUILD, "cache")
OUT_DIR = os.path.join(ROOT, "2-tool")

PAIRS = [
    ("tool_template.html", "granulation_radius_tool.html", "count"),
    ("diffusion_template.html", "diffusion_granulation_tool.html", "diffusion"),
]


def main():
    data = open(os.path.join(CACHE, "_points_compact.json"), encoding="utf-8").read()
    os.makedirs(OUT_DIR, exist_ok=True)
    for tpl_name, out_name, tag in PAIRS:
        tpl_path = os.path.join(BUILD, tpl_name)
        if not os.path.exists(tpl_path):
            print(f"[skip] {tpl_name} 不存在")
            continue
        tpl = open(tpl_path, encoding="utf-8").read()
        assert tpl.count("__DATA__") == 1, (tpl_name, tpl.count("__DATA__"))
        out = tpl.replace("__DATA__", data)
        dst = os.path.join(OUT_DIR, out_name)
        open(dst, "w", encoding="utf-8").write(out)
        # 把 <script> 里的 JS 单独落盘，便于 node --check 与自检
        js = re.findall(r"<script>(.*?)</script>", out, re.S)
        open(os.path.join(CACHE, f"_check_{tag}.js"), "w", encoding="utf-8").write(
            js[-1]
        )
        print(f"written {dst}  {os.path.getsize(dst)} bytes  (js {len(js[-1])} chars)")


if __name__ == "__main__":
    main()
