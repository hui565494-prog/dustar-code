# -*- coding: utf-8 -*-
"""纯标准库读取 .npz（zip 包内是 .npy），导出为 JSON，供前端用。
不依赖 numpy：.npy 的头部是 dict 形式的描述 + 原始二进制数据。
"""
import zipfile, struct, json, os, io

BUILD = os.path.dirname(os.path.abspath(__file__))  # 4-build/
ROOT = os.path.dirname(BUILD)  # 项目根
DATA = os.path.join(ROOT, "1-data")  # 原始点集
CACHE = os.path.join(BUILD, "cache")  # 中间产物
os.makedirs(CACHE, exist_ok=True)

DT = {
    "f8": ("d", 8),
    "f4": ("f", 4),
    "i8": ("q", 8),
    "i4": ("i", 4),
    "u1": ("B", 1),
    "b1": ("b", 1),
}


def read_npy(buf):
    assert buf[:6] == b"\x93NUMPY", "not a npy"
    major = buf[6]
    if major == 1:
        hlen = struct.unpack("<H", buf[8:10])[0]
        start = 10
    else:
        hlen = struct.unpack("<I", buf[8:12])[0]
        start = 12
    header = buf[start : start + hlen].decode("latin1")
    d = eval(header, {"False": False, "True": True})  # 头部是 literals-safe 的 dict
    dt = d["descr"]
    shape = d["shape"]
    order = d.get("fortran_order", False)
    code, size = DT[dt.lstrip("<>=|")]
    body = buf[start + hlen :]
    n = 1
    for s in shape:
        n *= s
    vals = struct.unpack("<" + code * n, body[: n * size])
    if len(shape) == 0:
        return vals[0]
    if len(shape) == 1:
        return list(vals)
    cols = shape[1]
    rows = [list(vals[i * cols : (i + 1) * cols]) for i in range(shape[0])]
    return rows


# 只认原始素材 points_NN.npz；派生文件（*_granulated_*）里是 1 维的 c/r，不该混进来
import re as _re

SRC_FILES = sorted(f for f in os.listdir(DATA) if _re.fullmatch(r"points_\d\d\.npz", f))
assert SRC_FILES, "1-data/ 里没找到 points_NN.npz"

out = {}
for name in SRC_FILES:
    with zipfile.ZipFile(os.path.join(DATA, name)) as z:
        item = {}
        for member in z.namelist():
            arr = read_npy(z.read(member))
            key = os.path.splitext(member)[0]
            item[key] = arr
        out["points_" + name.split("_")[1][:2]] = item
    print(name, {k: (len(v) if isinstance(v, list) else v) for k, v in item.items()})

DST = os.path.join(CACHE, "_points.json")
with open(DST, "w", encoding="utf-8") as f:
    json.dump(out, f, separators=(",", ":"))
print("keys:", list(out.keys()))
print("size:", os.path.getsize(DST), "->", DST)
