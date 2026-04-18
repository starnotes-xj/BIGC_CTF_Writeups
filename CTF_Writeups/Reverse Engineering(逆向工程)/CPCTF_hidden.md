# CPCTF - hidden Writeup

## 题目信息
- **比赛**: CPCTF
- **题目**: hidden
- **类别**: Reverse
- **难度**: 简单
- **附件/URL**: `hidden`
- **附件链接**: [下载附件](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/hidden/hidden){download} · [仓库位置](https://github.com/starnotes-xj/BIGC_CTF_Writeups/tree/main/CTF_Writeups/files/hidden){target="_blank"}
- **Flag格式**: `CPCTF{...}`
- **状态**: 已解

## Flag

```text
CPCTF{H1dd3n_1n_5tr1ngs}
```

## 解题过程

### 1. 初始侦察/文件识别
- 题目只给了一个名为 `hidden` 的附件，先做最基础的文件识别：

```bash
file CTF_Writeups/files/hidden/hidden
```

- 可以确认它是 `ELF 64-bit` 可执行文件，属于典型的入门 Reverse 附件。
- 这类题第一步通常不急着进 GUI 反编译器，而是先看字符串、段信息和保护，判断题目到底是“逻辑逆向”还是“把 flag 直接埋在文件里”。

### 2. 关键突破点一
- 继续做字符串检查：

```bash
strings CTF_Writeups/files/hidden/hidden
```

- 结果里可以直接看到提示语：

```text
The flag is hidden in this file. Can you find it?
```

- 同时还能直接看到一条符合题目格式的字符串：

```text
CPCTF{H1dd3n_1n_5tr1ngs}
```

- 到这里基本已经可以判断：题目没有把 flag 做复杂加密，也没有要求动态调试，核心考点就是先建立“做二进制基础侦察”的习惯。

### 3. 关键突破点二
- 为了避免把别的提示串误认成 flag，仍然要做一次最小验证：
  1. 确认该字符串完整符合 `CPCTF{...}` 格式
  2. 确认文件中没有第二条同格式候选
  3. 结合提示语 `The flag is hidden in this file`，可以说明这不是运行时拼接，而是静态埋在文件内部
- 如果习惯用逆向工具，也可以在 `.rodata` 区域看到这条字符串，因此这题本质上是“字符串检索”而不是“控制流恢复”。

### 4. 获取 Flag
- 直接提取字符串后即可得到最终答案：

```text
CPCTF{H1dd3n_1n_5tr1ngs}
```

## 攻击链/解题流程总结

```text
file 判断 ELF 类型 -> strings 枚举可打印字符串 -> 发现提示语与 CPCTF flag -> 验证唯一性 -> 提交 Flag
```

## 漏洞分析 / 机制分析

### 根因
- 题目把 flag 以明文形式直接保存在二进制的可打印字符串区域中。
- 只要进行最基础的静态侦察，就能在不执行程序的情况下把 flag 找出来。
- 这说明题目设计重点不在复杂逆向逻辑，而在于让选手建立正确的二进制初筛顺序。

### 影响
- 拿到附件的任何人都可以通过 `strings` 或等价方法直接恢复 flag。
- 不需要 patch、调试、符号执行，也不需要分析复杂控制流。

### 修复建议（适用于漏洞类题目）
- 如果真实场景不希望敏感数据被直接提取，就不能把密钥、口令或 flag 明文放进 `.rodata`。
- 至少应当进行运行时生成、拆分存储或混淆处理，而不是把完整敏感字符串直接编译进程序。
- 对逆向题设计而言，如果想提高区分度，可以把字符串检索变成入口线索，而不是直接给出完整 flag。

## 知识点
- ELF 可执行文件的基础识别
- `strings` 在逆向初筛中的作用
- 区分“字符串隐藏题”和“真实逻辑逆向题”

## 使用的工具
- `file` — 判断附件类型与基本属性
- `strings` — 快速提取可打印字符串
- Python 3 — 自动提取符合 `CPCTF{...}` 格式的 flag

## 脚本归档
- Python：[`CPCTF_hidden.py` :material-open-in-new:](https://github.com/starnotes-xj/BIGC_CTF_Writeups/blob/main/CTF_Writeups/scripts_python/CPCTF_hidden.py){target="_blank"}
- 说明：脚本会读取归档后的 `CTF_Writeups/files/hidden/hidden`，并匹配输出完整 flag

## 命令行提取关键数据（无 GUI）

```bash
file CTF_Writeups/files/hidden/hidden
strings CTF_Writeups/files/hidden/hidden | grep CPCTF
python CTF_Writeups/scripts_python/CPCTF_hidden.py
```

## 推荐工具与优化解题流程

> 这题的关键不是反编译，而是先做低成本静态侦察，避免一上来就陷入过度分析。

### 工具对比总结

| 工具 | 适用阶段 | 本题耗时 | 优点 | 缺点 |
|------|----------|----------|------|------|
| `file` | 初始识别 | 秒级 | 立刻知道是不是 ELF | 不能直接给出 flag |
| `strings` | 字符串初筛 | 秒级 | 对这题可直接命中 flag | 遇到混淆题时信息有限 |
| Ghidra / IDA | 深入逆向 | 分钟级 | 适合分析真实逻辑 | 对本题属于过度投入 |
| Python 脚本 | 自动化验证 | 秒级 | 可复现、便于归档 | 仍依赖已知 flag 格式 |

### 推荐流程

**推荐流程**：先用 `file` 确认二进制类型 -> 用 `strings` 搜索可打印内容 -> 若直接命中 `CPCTF{...}` 则验证唯一性 -> 再决定是否需要进入反编译工具。

### 工具 A（推荐首选）
- **安装**：大多数 Linux 环境自带 `file` 与 `strings`（Windows 可在 WSL / Git Bash 中使用）
- **详细步骤**：
  1. 用 `file` 判断附件类型
  2. 用 `strings` 枚举可打印字符串
  3. 搜索 flag 前缀 `CPCTF{`
  4. 命中后再做唯一性确认
- **优势**：成本最低，最适合处理“明文埋字符串”的入门 Reverse 题

### 工具 B（可选）
- **安装**：Python 3
- **详细步骤**：
  1. 读取二进制原始字节
  2. 用正则匹配 `CPCTF\{[^}]+\}`
  3. 输出唯一命中的 flag
- **优势**：方便脚本化归档，后续批量扫描同类题也能复用
