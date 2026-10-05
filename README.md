# dustar-code

个人学习与项目代码库 —— C / C++ / Python 学习，以及若干从零实现的项目。

## 目录

```
├── c/          C 语言学习（01-basics / 02-function / 03-array / 04-practice）
├── cpp/        C++ 学习（01-io）
├── python/     Python 学习（basics / numpy / pandas / module / p1）
└── project/    项目
    ├── neural-network/        从零实现神经网络（纯 NumPy）
    ├── cellular-automata/     元胞自动机
    ├── cellular-complexity/   元胞自动机复杂度研究
    ├── granular-computing/    粒计算实验
    └── homecredit/            Home Credit 数据工程实践
```

<details>
<summary>命名与代码风格</summary>

- **目录**：`NN-主题`（小写连字符），如 `01-io`、`03-array`。
- **C/C++ 文件**：小写连字符，前缀用「题号」或「层级」，如 `04-selection-sort.cpp`、`l2-bmi.cpp`。
- **Python 文件**：下划线（PEP 8），如 `granulate_radius.py`。
- **格式**：C/C++ 用 clang-format（见 `.clang-format`，Microsoft 风格）；Python / notebook 用 black。

</details>
