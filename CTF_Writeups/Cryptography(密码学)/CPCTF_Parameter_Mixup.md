# CPCTF - Parameter Mixup Writeup

> 原题名未随附件一起保存。本文按题目机制暂记为 `Parameter Mixup`，核心问题是把 `pow(m, e, n)` 写成了 `pow(n, e, m)`。

## 题目信息
- **比赛**: CPCTF
- **题目**: Parameter Mixup
- **类别**: Crypto
- **难度**: 简单
- **附件/URL**: `challenge.py`、`output.txt`
- **附件链接**: [challenge.py](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/Parameter%20Mixup/challenge.py){download} · [output.txt](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/Parameter%20Mixup/output.txt){download} · [仓库位置](https://github.com/starnotes-xj/BIGC_CTF_Writeups/tree/main/CTF_Writeups/files/Parameter%20Mixup){target="_blank"}
- **Flag格式**: `CPCTF{...}`
- **状态**: 已解

## Flag

```text
CPCTF{7h3_n3x7_574710n_15_Kukud0}
```

## 解题过程

### 1. 初始侦察/文件识别
- 题目给了两组看起来像 RSA 的 `(n, e, c)`，而且 `e = 3`：

```text
n1 = ...
e1 = 3
c1 = ...
n2 = ...
e2 = 3
c2 = ...
```

- 一开始很容易把它误判成低指数广播攻击，但源码一看就发现真正的关键不在 `e = 3`，而在参数顺序：

```python
def rsa_encryption(flag):
    m = bytes_to_long(flag.encode())
    e = 3
    p, q = getPrime(512), getPrime(512)
    n = p * q
    c = pow(n, e, m)
    return (n, e, c)
```

- 正常 RSA 应该是 `pow(m, e, n)`，题目却写成了 `pow(n, e, m)`。这意味着它根本没有在模 `n` 下加密明文，而是在模 `m` 下计算 `n^3 mod m`。

### 2. 关键突破点一
- 令 `m = bytes_to_long(flag.encode())`，那么两次输出满足：

```text
c1 = n1^3 mod m
c2 = n2^3 mod m
```

- 根据模运算定义：

```text
n1^3 = k1 * m + c1
n2^3 = k2 * m + c2
```

- 移项后可得：

```text
n1^3 - c1 = k1 * m
n2^3 - c2 = k2 * m
```

- 这说明 `m` 同时整除 `n1^3 - c1` 与 `n2^3 - c2`，因此它必然也是这两个数最大公约数的因子：

```python
g = gcd(n1**3 - c1, n2**3 - c2)
```

### 3. 关键突破点二
- 实际算出来的 `g` 不是恰好等于 `m`，而是 `m` 的一个倍数：

```text
g = 15588747934374104316628062759697384558095701884059069641547471556182750754529530
```

- 直接把 `g` 转回字节串会得到不可读结果，因此还需要继续处理。
- 对 `g` 做因式分解后，可以得到：

```text
g = 2 * 5 * 893772566384902460933 * 669676863714040039901 * 2604467362279384028363243660995220041
```

- 然后枚举这些素因子的组合，筛选可打印 ASCII 且以 `CPCTF{` 开头的候选，即可恢复真正的 `m`。

### 4. 获取 Flag
- 在全部因子组合中，唯一符合格式的结果是：

```text
CPCTF{7h3_n3x7_574710n_15_Kukud0}
```

- 到这里可以确认：题目并不是考低指数 RSA，而是考“源码审计 + 模运算含义 + gcd 提取公共模数因子”。

## 攻击链/解题流程总结

```text
阅读源码发现 pow 参数写反 -> 建立 c = n^3 mod m 的关系 -> 推出 m | (n1^3 - c1) 且 m | (n2^3 - c2) -> 计算 gcd 提取公共因子 -> 分解 gcd 并筛选出符合 CPCTF{...} 格式的字节串 -> 得到 Flag
```

## 漏洞分析 / 机制分析

### 根因
- 题目把快速幂函数 `pow(base, exp, mod)` 的三个参数顺序写错了。
- 正常 RSA 加密流程应当把明文作为底数、模数 `n` 作为第三个参数；题目却把随机生成的 `n` 当成底数，把明文整数 `m` 当成模数。
- 一旦 `m` 被拿来做模数，输出 `c` 就不再是“明文在模 `n` 下的幂”，而是“随机 `n` 在模 `m` 下的余数”，从而暴露出关于 `m` 的整除关系。

### 影响
- 不需要分解 RSA 模数，也不需要做 Hastad broadcast attack。
- 仅凭两组输出就能构造出两个 `m` 的倍数，再用 `gcd` 把公共因子提取出来。
- 如果 `gcd` 直接等于 `m`，题目会被一行 `long_to_bytes(g)` 秒杀；即便不是，也通常只剩一层较弱的因子筛选。

### 修复建议（适用于漏洞类题目）
- 使用 `pow` 时必须明确参数语义：`pow(message, exponent, modulus)`。
- 对加密实现写单元测试，至少校验“加密后结果小于模数 `n`”以及“解密能回到原文”。
- 对密码代码做最小限度的自检，避免因为参数顺序错误把数学对象彻底换掉。

## 知识点
- Python 三参数 `pow(base, exp, mod)` 的语义
- 模运算与整除关系：`a mod m = r` 等价于 `a - r` 可被 `m` 整除
- 用 `gcd` 从多个倍数中提取公共因子
- 结合 flag 格式对候选明文进行筛选

## 使用的工具
- Python 3 — 计算 `gcd`、因式分解倍数并枚举候选
- PowerShell — 查看题目附件与归档文件

## 脚本归档
- Python：[`CPCTF_Parameter_Mixup.py` :material-open-in-new:](https://github.com/starnotes-xj/BIGC_CTF_Writeups/blob/main/CTF_Writeups/scripts_python/CPCTF_Parameter_Mixup.py){target="_blank"}
- 说明：Python 脚本使用标准库实现 Miller-Rabin 与 Pollard Rho，自动恢复 flag

## 命令行提取关键数据（无 GUI）

```bash
python CTF_Writeups/scripts_python/CPCTF_Parameter_Mixup.py
```

## 推荐工具与优化解题流程

> 这题的关键是先读源码纠正问题模型，而不是先在错误的 RSA 假设上堆公式。

### 工具对比总结

| 工具 | 适用阶段 | 本题耗时 | 优点 | 缺点 |
|------|----------|----------|------|------|
| 直接阅读源码 | 建模纠错 | 1-2 分钟 | 能立刻发现 `pow` 参数写反 | 需要题目给出源码 |
| Python 脚本 | 计算与筛选 | 秒级 | 很适合实现 `gcd`、分解和枚举 | 需要写少量辅助代码 |
| 盲目套广播攻击 | 误入歧途 | 不定 | 无 | 会在错误模型上浪费时间 |

### 推荐流程

**推荐流程**：先确认 `pow` 参数语义 -> 识别真实关系是 `c = n^3 mod m` -> 计算 `gcd(n1^3 - c1, n2^3 - c2)` -> 若结果不是明文则继续分解并筛选符合 flag 格式的因子组合。

### 工具 A（推荐首选）
- **安装**：Python 3
- **详细步骤**：
  1. 读取两组 `n, c`
  2. 计算 `g = gcd(n1**3 - c1, n2**3 - c2)`
  3. 对 `g` 做因式分解
  4. 枚举因子组合并筛选以 `CPCTF{` 开头的结果
- **优势**：推导和利用完全一致，最利于归档与复现

### 工具 B（可选）
- **安装**：SageMath / SymPy
- **详细步骤**：直接调用现成因式分解能力，加速定位 `g` 中的真实明文因子
- **优势**：比赛现场更省时间，适合快速验证思路
