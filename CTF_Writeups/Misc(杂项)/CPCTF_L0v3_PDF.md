# CPCTF - L0v3 PDF Writeup

## 题目信息
- **比赛**: CPCTF
- **题目**: L0v3 PDF
- **类别**: Misc
- **难度**: 简单
- **附件/URL**: `il0v3pdfs.pdf`
- **附件链接**: [下载附件](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/L0v3_PDF/il0v3pdfs.pdf){download} · [仓库位置](https://github.com/starnotes-xj/BIGC_CTF_Writeups/tree/main/CTF_Writeups/files/L0v3_PDF){target="_blank"}
- **Flag格式**: `CPCTF{...}`
- **状态**: 已解

## Flag

```text
CPCTF{Lets_P1ey_W1th_PdFs}
```

## 解题过程

### 1. 初始侦察/文件识别
- 题目给了一个 PDF 附件 `il0v3pdfs.pdf`，题面提示：
  - “本文档包含除可见文本以外的数据。”
  - “PDF 不仅仅是图像或文档，而是一组供计算机读取的复杂指令。”
- 这说明不能只用 PDF 阅读器看页面，还要检查 PDF 的**原始字节流**、对象和内容流。
- 最直接的做法是先跑 `strings` 看有没有可疑文本：

```bash
strings il0v3pdfs.pdf | grep -A 10 CPCTF
```

### 2. 关键突破点一
- 提取结果里出现了两段像 flag 的内容：

```text
/F42 24.7871 Tf 148.712 699.875 Td [(CPCTF{dummy!})]TJ
```

和

```text
% CPCTF{Lets_P1ey_W1th_PdFs}
```

- 第一段里的 `TJ` 是 PDF 内容流中的**文本绘制操作符**，表示把 `CPCTF{dummy!}` 作为页面上显示的文字画出来。
- 这更像是题目故意放在可见区域里的**假 flag**。

### 3. 关键突破点二
- 第二段前面的 `%` 是 PDF 的**注释标记**。
- 注释不会被 PDF 阅读器正常渲染显示，但依然真实存在于文件字节流中。
- 这正好对应题目提示的“包含除可见文本以外的数据”——真正的信息不在页面渲染层，而在 PDF 的原始结构里。
- 所以：
  - `CPCTF{dummy!}` 是可见文本诱饵
  - `CPCTF{Lets_P1ey_W1th_PdFs}` 是隐藏在 PDF 注释中的真 flag

### 4. 获取 Flag
- 用 `strings` / 原始字节扫描后即可确认真实 flag 为：

```text
CPCTF{Lets_P1ey_W1th_PdFs}
```

- 我另外补了一个很小的 Python 脚本，直接扫描 PDF 原始字节流中的 `CPCTF{...}` 候选，并自动跳过 `dummy`。

## 攻击链/解题流程总结

```text
不要只看 PDF 页面内容 -> 检查 PDF 原始字节流 -> 发现可见文本中的 dummy flag 和注释中的隐藏 flag -> 识别 % 注释不会被渲染 -> 提取真实 flag
```

## 漏洞分析 / 机制分析

### 根因
- PDF 是一种包含对象、流、操作符和注释的结构化格式，不只是“显示出来的页面”。
- 题目把假 flag 放在了可见文本绘制指令里，又把真 flag 藏在 PDF 注释里。
- 如果只依赖 PDF 阅读器看到的内容，就会被可见文本误导。

### 影响
- 能够检查 PDF 原始数据的人可以轻松恢复隐藏信息。
- 不需要破解密码、不需要 OCR，也不需要复杂的文件格式利用。

### 修复建议（适用于漏洞类题目）
- 真实场景里，如果 PDF 要公开分发，不应把敏感数据直接写入注释、未显示对象或其他隐藏元数据。
- 对外发布前应使用 PDF 清洗/重写工具移除注释、隐藏对象和冗余元数据。

## 知识点
- PDF 内容流中的文本绘制指令（如 `TJ`）
- PDF 注释 `% ...` 不会被正常渲染
- 文件取证时区分“可见内容”和“原始字节流”

## 使用的工具
- `strings` — 提取 PDF 字节流中的可打印字符串
- `grep` — 快速定位 `CPCTF{...}` 候选
- Python 3 — 编写自动提取脚本

## 脚本归档
- Go：待补
- Python：[`CPCTF_L0v3_PDF.py` :material-open-in-new:](https://github.com/starnotes-xj/BIGC_CTF_Writeups/blob/main/CTF_Writeups/scripts_python/CPCTF_L0v3_PDF.py){target="_blank"}
- 说明：Python 脚本会扫描附件原始字节流中的 `CPCTF{...}` 候选，并优先输出非 dummy 的真实 flag

## 命令行提取关键数据（无 GUI）

```bash
strings il0v3pdfs.pdf | grep -A 10 CPCTF

python CTF_Writeups/scripts_python/CPCTF_L0v3_PDF.py
```

## 推荐工具与优化解题流程

> 这题的重点不是“看 PDF 页面”，而是把 PDF 当作结构化文本格式来检查。

### 工具对比总结

| 工具 | 适用阶段 | 本题耗时 | 优点 | 缺点 |
|------|----------|----------|------|------|
| `strings` | 初筛 | 秒级 | 极快，适合抓明文残留 | 只能看到可打印字符串，结构信息有限 |
| `grep` | 定位 flag | 秒级 | 结合关键字过滤很高效 | 依赖已知 flag 格式 |
| Python 原始字节扫描 | 复现归档 | 秒级 | 可自动化，可归档到仓库 | 仍然是轻量提取，不是完整 PDF 解析 |

### 推荐流程

**推荐流程**：先用 `strings` 对 PDF 做原始文本初筛 -> 用 `grep` 搜索 flag 格式 -> 发现 dummy / 注释中的真 flag -> 再用小脚本把提取流程固化下来。

### 工具 A（推荐首选）
- **安装**：`strings`（binutils / 系统自带工具）
- **详细步骤**：
  1. 对附件运行 `strings il0v3pdfs.pdf`
  2. 结合 `grep CPCTF` 过滤可疑内容
  3. 对比可见文本指令和注释中的候选
- **优势**：最快速，比赛里几乎是秒解

### 工具 B（可选）
- **安装**：Python 3
- **详细步骤**：
  1. 读取 PDF 原始字节
  2. 用正则提取 `CPCTF{...}` 样式候选
  3. 排除 `dummy` 干扰项
- **优势**：适合归档、复现和批量处理
