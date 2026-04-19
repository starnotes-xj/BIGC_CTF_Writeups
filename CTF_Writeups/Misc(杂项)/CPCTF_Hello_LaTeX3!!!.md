# CPCTF - Hello LaTeX3!!! Writeup

## 题目信息
- **比赛**: CPCTF
- **题目**: Hello LaTeX3!!!
- **类别**: Misc
- **难度**: 简单
- **附件/URL**: `h3110_1473x3.tex`
- **附件链接**: [下载附件](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/Hello_LaTeX3!!!/h3110_1473x3.tex){download} · [仓库位置](https://github.com/starnotes-xj/BIGC_CTF_Writeups/tree/main/CTF_Writeups/files/Hello_LaTeX3!!!){target="_blank"}
- **Flag格式**: `CPCTF{...}`
- **状态**: 已解

## Flag

```text
CPCTF{seq_set_from_clist}
```

## 解题过程

### 1. 初始侦察/文件识别
- 附件只有一个 `h3110_1473x3.tex`，显然不是常规的二进制附件，而是一份 LaTeX 源码。
- 题面同时提示了两个非常关键的点：
  - LaTeX 的下一代项目叫 **LaTeX3**
  - 其中编程层 **expl3** 遵循非常严格的命名规则
- 这意味着解题重点不在“编译 PDF 看效果”，而在**直接阅读 expl3 源码并根据命名规则补全缺失命令**。
- 打开附件后，很快就能看到核心代码：

```tex
\seq_new:N \l_my_char_code_seq
\tl_new:N  \l_my_result_tl

\cs_new_protected:Npn \my_convert_clist_to_string:n #1
  {
    \???:Nn \l_my_char_code_seq { #1 }
    \tl_clear:N \l_my_result_tl
    \seq_map_inline:Nn \l_my_char_code_seq
      {
        \tl_put_right:Nx \l_my_result_tl { \char_generate:nn { ##1 } { 12 } }
      }
    \tl_use:N \l_my_result_tl
  }
```

- 从变量名就能看出：
  - `\l_my_char_code_seq` 是一个 `seq`
  - `#1` 传入的参数名写成了 `clist`
  - 后面又对 `seq` 做 `\seq_map_inline:Nn` 遍历，并把每个数字转成字符
- 所以 `???` 这一行的职责，显然是**把 clist 转成 seq**。

### 2. 关键突破点一：根据 expl3 命名规则缩小范围
- expl3 的命名风格高度结构化，通常可以从“数据类型 + 动作 + 参数签名”反推出命令用途。
- 这里缺失命令的形态是：

```tex
\???:Nn \l_my_char_code_seq { #1 }
```

- 结合上下文，这个命令应该满足三个条件：
  1. 作用对象是 `seq`
  2. 输入来源是 `clist`
  3. 参数签名是 `:Nn`
- 因此最合理的候选就是：

```tex
\seq_set_from_clist:Nn
```

- 这个名字完全符合 expl3 的严格命名模式：
  - `seq`：目标数据结构
  - `set_from_clist`：把逗号列表内容装入 seq
  - `:Nn`：第一个参数是变量名，第二个参数是普通参数

### 3. 关键突破点二：验证整段代码的语义闭环
- 把 `???` 补成 `\seq_set_from_clist:Nn` 后，整段逻辑就完全自洽了：
  1. 先把逗号分隔的字符编码列表放进 `\l_my_char_code_seq`
  2. 清空结果 token list `\l_my_result_tl`
  3. 用 `\seq_map_inline:Nn` 逐个取出编码值
  4. 通过 `\char_generate:nn { ##1 } { 12 }` 把数字变成字符
  5. 最后输出拼好的字符串
- 也就是说，这题真正考的是：**能不能从 expl3 的变量类型和命令命名规则中，正确补出缺失 API 名称。**
- 由于题目要求直接提交 `???` 对应的命令名称，因此不需要把前导反斜杠一起写进 flag。

### 4. 获取 Flag
- 最终补全出的命令是：

```text
seq_set_from_clist
```

- 按题目要求包装后得到 flag：

```text
CPCTF{seq_set_from_clist}
```

## 攻击链/解题流程总结

```text
识别附件是 LaTeX 源码 -> 根据题面锁定 expl3 命名规则 -> 从 clist/seq 类型和 :Nn 参数签名反推缺失命令 -> 确认答案为 seq_set_from_clist -> 提交 CPCTF{seq_set_from_clist}
```

## 漏洞分析 / 机制分析

### 根因
- 这题本质上不是漏洞利用题，而是一道 **源码阅读 + 语言规则识别** 题。
- 关键在于 expl3 的命令命名并不是随意命名，而是高度结构化的“自描述接口”。
- 只要理解 `seq`、`clist` 和 `:Nn` 的含义，就能从上下文反推出缺失命令。

### 影响
- 熟悉 expl3 命名约定的人，可以不运行 LaTeX，直接通过静态阅读源码拿到答案。
- 不熟悉 expl3 的人则容易把它看成“陌生语法”，从而卡在 `???` 的补全上。

### 修复建议（适用于漏洞类题目）
- N/A。本题不是现实漏洞场景。
- 如果在真实文档项目中不希望内部逻辑被轻易猜出，避免把关键信息直接暴露在可读性极强的 API 命名和源码结构里。

## 知识点
- LaTeX3 / expl3 的命名规则
- `seq` 与 `clist` 两种数据结构的角色区别
- 通过参数签名 `:Nn` 反推命令用途
- 静态阅读源码而非依赖运行结果

## 使用的工具
- 文本编辑器 — 直接阅读 `.tex` 源码
- `grep` — 快速定位 `seq`、`clist` 和 `???` 的上下文
- expl3 文档 / `interface3` — 辅助确认命令命名规则

## 脚本归档
- Go：待补
- Python：待补
- 说明：本题无需单独脚本，直接阅读附件源码并结合 expl3 命名规则即可复现

## 命令行提取关键数据（无 GUI）

```bash
grep -n "???\|seq_\|clist\|char_generate" h3110_1473x3.tex
```

## 推荐工具与优化解题流程

> 这题的重点不是跑环境，而是尽快识别 expl3 是“强命名约束”的接口层，然后利用命名规则反推缺失命令。

### 工具对比总结

| 工具 | 适用阶段 | 本题耗时 | 优点 | 缺点 |
|------|----------|----------|------|------|
| 直接阅读源码 | 初始分析 | 秒级 | 信息最完整，马上看到变量类型与上下文 | 需要对 expl3 命名有基本感觉 |
| `grep` | 线索定位 | 秒级 | 适合快速抓取 `seq` / `clist` / `char_generate` 关键字 | 只能定位文本，不能自动解释语义 |
| `interface3` 文档 | 规则确认 | 分钟级 | 可以快速验证猜到的命令名是否真实存在 | 需要额外查阅文档 |

### 推荐流程

**推荐流程**：先直接阅读 `.tex` 附件 -> 从变量类型和参数签名推断命令作用 -> 再用 `interface3` 文档确认 `seq_set_from_clist:Nn` 的存在与语义 -> 最后提交 flag。

### 工具 A（推荐首选）
- **安装**：任意文本编辑器即可
- **详细步骤**：
  1. 打开 `h3110_1473x3.tex`
  2. 定位 `\???:Nn` 所在函数
  3. 结合 `\l_my_char_code_seq`、`clist`、`\seq_map_inline:Nn` 推断缺失命令
- **优势**：最快，不需要搭建任何 TeX 环境

### 工具 B（可选）
- **安装**：TeX Live `texdoc` 或在线 CTAN 文档
- **详细步骤**：
  1. 查阅 `interface3` 文档
  2. 搜索 `seq_set_from_clist`
  3. 确认其参数形式与当前代码一致
- **优势**：能把“推断”进一步变成“文档验证”
