import numpy as np

rng = np.random.default_rng()


def lc_sum(now):
    """计算邻位数据和,返回一个与输入数组形状相同的数组"""
    x = np.roll(now, 1, axis=0)
    w = np.roll(now, -1, axis=0)
    d = np.roll(now, 1, axis=1)
    a = np.roll(now, -1, axis=1)
    q = np.roll(w, -1, axis=1)
    e = np.roll(w, 1, axis=1)
    z = np.roll(x, -1, axis=1)
    c = np.roll(x, 1, axis=1)
    total = q + w + e + a + d + z + x + c
    return total


size = (100, 100)
s = rng.integers(0, 2, size)
B_kw = [3]
S_kw = [2, 3]
times = 10

now = s.copy()
for i in range(times):
    lc = lc_sum(now)
    d_value = (now == 0) & np.isin(lc, B_kw)
    b_value = (now == 1) & ~np.isin(lc, S_kw)
    now[d_value] = 1
    now[b_value] = 0
