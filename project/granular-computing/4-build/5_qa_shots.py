# -*- coding: utf-8 -*-
"""生成若干「预设状态」的临时副本，用于无头截图视觉自查。
两个工具都拍；截图落在本目录（4-build/_qa_*.png），看一眼确认版面没坏，然后删掉。"""
import os, subprocess

BUILD = os.path.dirname(os.path.abspath(__file__))  # 4-build/
ROOT = os.path.dirname(BUILD)  # 项目根
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

TOOLS = [
    (
        "2-tool/granulation_radius_tool.html",
        {
            "A_计数_全部圆": "S.r=0.16; S.circles='all'; loadDS(2);",
            "B_计数_同心环大r": "S.size=true; document.getElementById('ck-size').checked=true; S.r=0.30; loadDS(4);",
            "C_计数_扫描中途": """
          S.r=0.10; S.order='lr'; loadDS(3); buildOrder();
          for(let k=0;k<150;k++) revealed[orderArr[k]]=1;
          S.step=149; S.hover=orderArr[149]; syncTable(0,N); renderAll();
        """,
            "D_计数_延伸闭包": "S.r=0.13; S.comp=true; document.getElementById('ck-comp').checked=true; loadDS(5);",
        },
    ),
    (
        "2-tool/diffusion_granulation_tool.html",
        {
            "E_扩散_默认结果": "loadDS(0);",
            "F_扩散_同心环小r": "S.r=0.06; loadDS(4);",
            "G_扩散_限2跳": "S.r=0.12; loadDS(0); setK(2);",
            "H_扩散_播放中途": """
          S.r=0.12; loadDS(0); S.step=-1;
          for(let k=0;k<60;k++) S.step++;
          renderAll();
        """,
            "I_扩散_按跳数_密度悬殊": """
          S.r=0.12; loadDS(2); S.mode='hop';
          document.getElementById('modeseg').children[1].click();
        """,
        },
    ),
]


def main():
    for rel, cases in TOOLS:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            print("  [skip]", rel)
            continue
        src = open(path, encoding="utf-8").read()
        print("·", rel)
        for name, js in cases.items():
            out = os.path.join(BUILD, "_qa_" + name + ".html")
            open(out, "w", encoding="utf-8").write(
                src.replace("</body>", "<script>" + js + "</script></body>")
            )
            png = os.path.join(BUILD, "_qa_" + name + ".png")
            subprocess.run(
                [
                    EDGE,
                    "--headless=new",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--hide-scrollbars",
                    "--window-size=1680,1000",
                    "--virtual-time-budget=5000",
                    "--screenshot=" + png,
                    "file:///" + out.replace("\\", "/"),
                ],
                capture_output=True,
            )
            print(
                "   ", name, os.path.getsize(png) if os.path.exists(png) else "FAILED"
            )


if __name__ == "__main__":
    main()
