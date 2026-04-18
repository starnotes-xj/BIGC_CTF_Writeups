# CPCTF - Sign up for traP Writeup

## 题目信息
- **比赛**: CPCTF
- **题目**: Sign up for traP
- **类别**: PPC
- **难度**: 简单
- **附件/URL**: 无附件，标准输入输出题
- **附件链接**: 无附件
- **Flag格式**: `CPCTF{...}`
- **状态**: 已解

## Flag

```text
CPCTF{s10w1y_bu7_sure1y}
```

## 解题过程

### 1. 初始侦察/文件识别
- 题目要求判断字符串 `S` 是否能作为 traQ ID。
- 合法条件共有三类：
  1. 长度为 `1..32`
  2. 字符只能来自 `A-Z`、`a-z`、`0-9`、`_`、`-`
  3. 首字符和尾字符不能是 `_` 或 `-`
- 约束 `1 <= |S| <= 100`，字符串由 ASCII 33~126 构成，不含空格。

### 2. 关键突破点一
- 这题不需要复杂算法，只需要逐条检查条件。
- 如果用正则表达式，可以把三类条件合并成一个模式：

```regex
^[A-Za-z0-9](?:[A-Za-z0-9_-]{0,30}[A-Za-z0-9])?$
```

- 含义如下：

| 正则片段 | 含义 |
|----------|------|
| `^` | 从字符串开头开始匹配 |
| `[A-Za-z0-9]` | 第一个字符必须是字母或数字 |
| `(?: ... )?` | 后续部分可选，因此可以支持长度为 1 的 ID |
| `[A-Za-z0-9_-]{0,30}` | 中间字符可以是字母、数字、下划线或连字符，最多 30 个 |
| `[A-Za-z0-9]` | 最后一个字符必须是字母或数字 |
| `$` | 匹配到字符串结尾 |

### 3. 关键突破点二
- 为什么长度上限是 32？
  - 如果字符串长度为 1，只匹配开头的 `[A-Za-z0-9]`
  - 如果字符串长度大于等于 2，则结构为：

```text
首字符 1 个 + 中间 0..30 个 + 尾字符 1 个
```

- 因此总长度范围是：

```text
1 或 2..32
```

- 同时，中间字符类 `[A-Za-z0-9_-]` 已经排除了题目不允许的字符。

### 4. 获取 Flag
- Python 版本：

```python
import re
import sys

pattern = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9_-]{0,30}[A-Za-z0-9])?$")
s = sys.stdin.readline().rstrip("\n")
print(200 if pattern.fullmatch(s) else 400)
```

- Go 版本：

```go
package main

import (
    "bufio"
    "fmt"
    "os"
    "regexp"
)

var pattern = regexp.MustCompile(`^[A-Za-z0-9](?:[A-Za-z0-9_-]{0,30}[A-Za-z0-9])?$`)

func main() {
    reader := bufio.NewReader(os.Stdin)
    var s string
    fmt.Fscan(reader, &s)

    if pattern.MatchString(s) {
        fmt.Println(200)
    } else {
        fmt.Println(400)
    }
}
```

- 提交代码通过 AC 后，平台返回最终 flag：

```text
CPCTF{s10w1y_bu7_sure1y}
```

## 攻击链/解题流程总结

```text
读入字符串 S -> 用正则同时检查首尾字符、字符集和长度 -> 合法输出 200，否则输出 400
```

## 漏洞分析 / 机制分析

### 根因
- 这是标准 PPC / 算法题，不涉及漏洞利用。
- 题目核心是把自然语言条件转成可执行的字符串校验逻辑。

### 影响
- 任意不满足 traQ ID 规则的字符串都会输出 `400`。
- 只有满足全部三条规则的字符串输出 `200`。

### 修复建议（适用于漏洞类题目）
- 如果这是实际注册逻辑，应在服务端也做同样校验，不能只依赖前端检查。
- 正则表达式需要使用锚点 `^` / `$` 或语言提供的完整匹配 API，避免只匹配到子串。

## 知识点
- 正则表达式字符类
- 使用可选分组处理长度为 1 的特殊情况
- 字符串完整匹配与子串匹配的区别

## 使用的工具
- Python 3 — 正则表达式解法
- Go — `regexp` 标准库实现同一逻辑

## 脚本归档
- Go：[`CPCTF_Sign_up_for_traP.go` :material-open-in-new:](https://github.com/starnotes-xj/BIGC_CTF_Writeups/blob/main/CTF_Writeups/scripts_go/CPCTF_Sign_up_for_traP.go){target="_blank"}
- Python：[`CPCTF_Sign_up_for_traP.py` :material-open-in-new:](https://github.com/starnotes-xj/BIGC_CTF_Writeups/blob/main/CTF_Writeups/scripts_python/CPCTF_Sign_up_for_traP.py){target="_blank"}
- 说明：两个脚本均使用正则表达式，一次读入 `S` 并输出 `200` 或 `400`

## 命令行提取关键数据（无 GUI）

```bash
echo traQ_ID-123 | python CTF_Writeups/scripts_python/CPCTF_Sign_up_for_traP.py
echo traQ_ID-123 | go run CTF_Writeups/scripts_go/CPCTF_Sign_up_for_traP.go
```

## 推荐工具与优化解题流程

> 本题提示已经说明“只需要逐一检查条件”。正则表达式适合把这些条件压缩成一个完整匹配。

### 工具对比总结

| 工具 | 适用阶段 | 本题耗时 | 优点 | 缺点 |
|------|----------|----------|------|------|
| if + for | 初学者实现 | 1-3 分钟 | 最直观，不容易写错 | 代码略长 |
| 正则表达式 | 简洁实现 | 1 分钟 | 一个模式覆盖全部条件 | 需要注意长度为 1 的特殊情况 |
| 单元测试样例 | 验证 | 秒级 | 快速覆盖边界 | 需要自己补样例 |

### 推荐流程

**推荐流程**：先把条件拆成首字符、尾字符、字符集、长度四件事 -> 写出完整匹配正则 -> 用边界样例验证 -> 提交 AC。

### 工具 A（推荐首选）
- **安装**：Python 3 或 Go
- **详细步骤**：
  1. 读入字符串 `S`
  2. 用正则 `^[A-Za-z0-9](?:[A-Za-z0-9_-]{0,30}[A-Za-z0-9])?$` 做完整匹配
  3. 匹配成功输出 `200`
  4. 匹配失败输出 `400`
- **优势**：代码短，边界清楚，适合这类格式校验题

### 工具 B（可选）
- **安装**：任意支持循环和条件判断的语言
- **详细步骤**：也可以先检查长度，再用 `for` 逐字符检查字符集，最后检查首尾字符。
- **优势**：对不熟悉正则的选手更稳妥
