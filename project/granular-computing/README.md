# 粒化实验 · 半径 r 下的逐点邻域计数

## 先看这个（不用装任何东西）

双击 **`2-tool/granulation_radius_tool.html`**（半径邻域计数）
或 **`2-tool/diffusion_granulation_tool.html`**（扩散粒化），浏览器打开就是算子台。

- 左栏选点集、拖 **r** 滑块 → 右边立刻重算
- 点 **「▶ 逐点扫描」** → 看 c 是怎么一个一个写进每个点的
- 鼠标悬停任一点 → 看它的圆和邻域名单；单击钉住，再拖 r 看这个点的 c 怎么涨

## 唯一的算子（就这一条，没有别的超参数）

```
N_r(p_i) = { p_j : ‖p_i − p_j‖ ≤ r }      # 圆内（含圆周）
c_i      = |N_r(p_i)|  ≥ 1                # 含自身，所以最小是 1
点 p_i 变成  (x_i, y_i, c_i)               # c 存进点里
```

**r 是唯一的旋钮**，"c 多大算合适"没有先验答案 —— 这正是要观察的东西。
同一个 r=0.12 下，③ 号点集里最密的点装了 **142** 个邻居，① 号最多只有 **12** 个。

## 目录

| 目录 | 里面是什么 | 要不要管 |
|---|---|---|
| `1-data/` | 8 组原始点集 `points_00~07.npz`、总览图、生成它们的 notebook | 换数据时才动 |
| `2-tool/` | 两个算子台（html）＋四个 Python 脚本 | 常用 |
| `3-output/` | 跑出来的结果（带 c 的 npz、四联图、二维图、直方图、点集总览） | 可随时删，能重跑 |
| `4-build/` | 重建算子台的流水线 + 中间缓存 | **平时不用打开** |

## 8 组点集分别是什么

**一张图看全部 8 组**：`3-output/data_gallery.png`（点图，2×4 并列）。
这个仓库里 **8 组点集全程都在**，任何时候你想确认"是不是只剩随机点了"，看这张图即可：

```bash
python 2-tool/make_gallery.py            # 重画总览图（只画点，不做任何粒化）
python 2-tool/make_gallery.py --truth    # 同一批点，换上真值标签着色
```

> **算子台打开时默认停在 ① 均匀随机**，所以初看很像"只有随机点"。
> 点左栏 **1 · 原始素材** 里的 8 个按钮即可切换：
> ① 均匀随机 / ② 高斯混合 / ③ 密度悬殊 / ④ 两个月亮 /
> ⑤ 同心环 / ⑥ 层次嵌套 / ⑥b 层次嵌套细版 / ⑦ 双螺旋。

| 文件 | 结构 | 用来试什么 |
|---|---|---|
| `points_00` | ① 均匀随机 | 对照组：没有结构，任何 r 都同样"对" |
| `points_01` | ② 高斯混合·等密度 | 标准情形，检验基本功 |
| `points_02` | ③ 密度悬殊 + 离群点 | 粗粒该不该吃掉离群点 |
| `points_03` | ④ 两个月亮（非凸缠绕） | 全局距离判据的陷阱 |
| `points_04` | ⑤ 同心环（内外密度不同） | 什么时候该说"我不分了" |
| `points_05` | ⑥ 层次嵌套·粗粒度真值 | 多粒度：同一片点，粗/细两个答案都对 |
| `points_06` | ⑥b 层次嵌套·细粒度真值 | 同上，细的那版 |
| `points_07` | ⑦ 双螺旋 | 两类交替贴近 |

`y` 是生成时留下的真值标签，**图上不据此着色**，只用于事后校准。
（`make_gallery.py` 为了让你一眼看清"有几坨"，才借 `y` 作区分色。）

想重新生成这批点集：跑 `1-data/granulating.ipynb`（纯 numpy，seed 固定，跑出来一模一样）。
它会把 8 个 npz 和总览图写回 `1-data/`——无论你的 Jupyter 是从哪个目录启动的，
运行时会先打印一行 `产出目录：…` 让你确认。

## 用 Python 跑（要 numpy）

```bash
python 2-tool/granulate_radius.py 02 --r 0.12        # 文件名可以只写 02
python 2-tool/granulate_radius.py 1-data/points_03.npz --r 0.10 --i 250
python 2-tool/granulate_radius.py 04 --r 0.08 --no-save   # 只看数值，不写文件
```

产出写进 `3-output/`：`*_granulated_r<r>.npz`（含 X / y / c / r）+ 四联图。

### 只看一张图（二维）

把 c_i **画回平面上**：颜色越深＝该点的粒越粗。看的是"哪儿粗哪儿细"。

```bash
python 2-tool/plot_count_map.py                      # 8 组并列，r=0.12
python 2-tool/plot_count_map.py --only 04            # 只画⑤同心环（单张大图）
python 2-tool/plot_count_map.py --r 0.20             # 换 r
python 2-tool/plot_count_map.py --shared             # 8 组共用一条色阶（比绝对大小）
```

产出 `3-output/count_map_r<r>.png`。
读法：整片深浅接近＝疏密均匀；同一片点里深浅差很大＝疏密悬殊；
出现环状/带状的色带＝密度分层（同心环最典型：内环深、外环浅）。

### 只看一张图（一维分布）

c_i 的直方图，看这个点集的粒度分布形状。

```bash
python 2-tool/plot_count_distribution.py             # 8 组并列
python 2-tool/plot_count_distribution.py --only 04   # 只看⑤同心环
python 2-tool/plot_count_distribution.py --shared    # 用同一把尺子比大小
```

产出 `3-output/count_distribution_r<r>.png`。
读法：分布窄＝疏密均匀；宽/长尾＝疏密悬殊；**两个峰＝两种密度层次**；
堆在最左边（c=1）＝r 太小，太多点和谁都不相邻。

当库用：

```python
from granulate_radius import neighborhood_counts, radius_curve
C = neighborhood_counts(X, 0.12)     # 每个点的 c_i
Xc = np.c_[X, C]                     # c 存进点里
```

## 5 · 扩散粒化（第二个算子）

```
种子 = 当前未分配点中 c_i 最大的点
粒   = 从种子出发，沿「距离 ≤ r」不断扩散所及的全部未分配点（一跳、二跳…都算同一粒）
边界 = 始终没被任何粒纳入的点（绝对不被包含）
回到第一行，直到剩下的点里没有 c_i ≥ 2 的种子
```

- **交互**：双击 `2-tool/diffusion_granulation_tool.html`。
  拖 r 直接看结果；按「播放扩散」看种子一颗颗长出来、一圈圈往外推。
  显示层可切「按粒着色 / 按跳数 / 按 c_i」；点表格会多出 <span class="mono">粒号</span> 与 <span class="mono">跳数</span>。
- **Python**：

```bash
python 2-tool/granulate_diffusion.py                       # 8 组并列，r=0.12
python 2-tool/granulate_diffusion.py --only 04 --r 0.06    # 只画⑤同心环
python 2-tool/granulate_diffusion.py --maxhop 2            # 扩散只走 2 跳
python 2-tool/granulate_diffusion.py --save                # 顺便存 lab/hop 到 npz
```

**一个必须知道的推论**：把"扩散到不动"写出来就是连通闭包，所以**不限跳数时**
`粒 = 连通分量（点数≥2 的）`、`边界 = 孤立点`——边界只可能是孤立点，r 一大就归零。
（脚本和网页自检里都用并查集独立核对了这条等式。）
想让"边界"真正有意思，得给扩散一个停止条件，就是**跳数上限**：
网页上那个滑块，或脚本的 `--maxhop`。限成 1/2/3 跳后，扩散走不了那么远，
剩下的点才会落进边界。



**只有当你要换数据、或改了算子台本身时**：

```bash
cd 4-build
python 1_extract_npz.py      # 1-data/*.npz  ->  cache/_points.json
python 2_compact_points.py   # 精简坐标     ->  cache/_points_compact.json
python 3_build_tool.py       # 注入两个模板 ->  2-tool/*.html
node   4_selftest.js         # 两个算子一起数值自检
python 5_qa_shots.py         # 九种状态无头截图，看版面有没有坏（可选）
```

`tool_template.html`（计数）和 `diffusion_template.html`（扩散）是两个算子台的**源码**
（数据位置写着 `__DATA__` 占位），`2-tool/` 下那两个 html 是注入数据后的**成品** ——
**改功能改模板，改数据不用改任何一个**。

## 两个算子的结果必须一致

两个算子都是「网页版 + Python 版」各一份，**数字必须逐项一致**。改完任一边跑
`node 4-build/4_selftest.js`（两个算子一起测）：

- 计数算子：6656 对计数与独立实现交叉验证；曲线单调性；r→0 / r 极大的退化端点
- 扩散算子：7 组 × 4 个 r = 28 个用例，检查划分完整、种子序 c 降序、跳数-父节点自洽、
  每粒闭包重算一致、**任意两个边界点距离 > r**、以及**粒数/边界数 = 连通分量数（并查集独立算）**

内嵌坐标保留 8 位小数就是为了这件事（4 位会翻转边界点）。
