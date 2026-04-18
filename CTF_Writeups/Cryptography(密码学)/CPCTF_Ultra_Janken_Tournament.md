# CPCTF - Ultra Janken Tournament Writeup

> 原题名没有和附件一起单独保存，本文按服务横幅暂记为 `Ultra Janken Tournament`。

## 题目信息
- **比赛**: CPCTF
- **题目**: Ultra Janken Tournament
- **类别**: Crypto
- **难度**: 中等
- **附件/URL**: `server.py`、`nc 133.88.122.244 32035`
- **附件链接**: [下载附件](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/Ultra_Janken_Tournament/server.py){download} · [仓库位置](https://github.com/starnotes-xj/BIGC_CTF_Writeups/tree/main/CTF_Writeups/files/Ultra_Janken_Tournament){target="_blank"}
- **Flag格式**: `CPCTF{...}`
- **状态**: 已解

## Flag

```text
CPCTF{Tie_15_A_T1Me_ThiEf}
```

## 解题过程

### 1. 初始侦察/文件识别
- 服务端脚本入口就是根目录下的 `server.py`，逻辑核心如下：

```python
def nextrand(n):
    n ^= n << 13
    n ^= n >> 7
    n ^= n << 17
    return n & ((1 << 64) - 1)
```

- 题目先生成 100 个隐藏选手。每个选手只有一个随机种子，后续 119 项都由 `nextrand()` 迭代出来。
- 我们可以提交自己的 120 个 64-bit 整数作为第 101 位选手。
- 每一轮服务器会打印：
  1. `player_no`
  2. 当前的 120 bit `luck_pattern`
  3. 允许我们翻转若干个位置，然后再结算 winner

- 结算代码是：

```python
clash_power = 0
for i in range(PARTICIPANTS):
    for j in range(STRATEGY_LEN):
        clash_power ^= janken_powers[i][j] * luck_pattern[j]

winner = clash_power % PARTICIPANTS
```

- 因为 `luck_pattern[j] ∈ {0,1}`，所以上面其实就是“选中列的 64-bit 数按位异或”。

### 2. 关键突破点一：把 100 个隐藏选手整体消掉
- 设 `T` 表示 `nextrand()` 诱导出的 GF(2) 线性变换。
- 每个隐藏选手第 `j` 列的数都可以写成 `T^j(seed_i)`。
- 如果我们把某个 120 bit 向量 `l = (l_0, ..., l_119)` 当成 luck pattern，那么 100 个隐藏选手的总贡献可以写成：

\[
\bigoplus_{i=1}^{100} \bigoplus_{j=0}^{119} l_j T^j(seed_i)
= \left(\sum_{j=0}^{119} l_j T^j \right)\left(\bigoplus_{i=1}^{100} seed_i\right)
\]

- 所以只要满足

\[
\sum_{j=0}^{119} l_j T^j = 0
\]

就能让这 100 个人的贡献整体变成 0，不需要知道任何隐藏种子。

- 对精确版 `nextrand()` 做线性化后，可以求出一个 64 次消去多项式：

\[
\begin{aligned}
m(x)=&x^{64}+x^{51}+x^{49}+x^{48}+x^{46}+x^{45}+x^{43}+x^{42}+x^{41}+x^{39}+x^{38}\\
&+x^{35}+x^{34}+x^{33}+x^{32}+x^{31}+x^{30}+x^{23}+x^{21}+x^{20}+x^{17}+x^{16}\\
&+x^{14}+x^{13}+x^{10}+x^8+x^4+x^3+x^2+1
\end{aligned}
\]

- 因此，只要把 luck pattern 的系数向量限制在所有 `g(x) * m(x)`（`deg g < 56`）组成的线性码里，隐藏 100 人的贡献就会被完全消掉。

### 3. 关键突破点二：让自己的 strategy 直接编码 winner
- 上一步已经把隐藏选手全部消掉了，剩下只需要让**自己的贡献**在 `% 101` 之后等于当前轮的 `player_no`。
- 如果把合法 codeword 写成 `c(x)=g(x)m(x)`，那么 `g(x)` 的低 8 bit 可以拿来编码一个 `0..255` 的数。
- 问题在于，由于 `m(x)` 低位还有 `x^2+x^3+x^4`，codeword 的前 8 位并不直接等于 `g_0..g_7`。递推展开后有：

\[
\begin{aligned}
g_0 &= c_0 \\
g_1 &= c_1 \\
g_2 &= c_2 \oplus c_0 \\
g_3 &= c_3 \oplus c_1 \oplus c_0 \\
g_4 &= c_4 \oplus c_2 \oplus c_1 \\
g_5 &= c_5 \oplus c_3 \oplus c_2 \\
g_6 &= c_6 \oplus c_4 \oplus c_3 \\
g_7 &= c_7 \oplus c_5 \oplus c_4 \oplus c_0
\end{aligned}
\]

- 所以只要把自己的前 8 个 strategy 值设成这些线性组合对应的系数即可：

```python
[141, 26, 52, 104, 208, 160, 64, 128]
```

- 其余位置全部填 0。这样对任意合法 codeword，都有：

\[
\text{my\_contribution} = g_0 + 2g_1 + 4g_2 + \cdots + 128g_7
\]

- 在线时我们只需要在 `0..255` 中挑一个满足

\[
value \bmod 101 = player\_no
\]

的值即可。候选最多只有三个：`player_no`、`player_no+101`、`player_no+202`。

### 4. 获取 Flag：最近码字搜索 + 自动交互
- 现在在线问题变成：
  1. 当前随机 `luck_pattern` 已知
  2. 目标 residue（即 `player_no`）已知
  3. 需要找一个离它最近的合法 codeword，并让该 codeword 对应的 `value % 101 == player_no`

- 我把 `g_8..g_55` 这 48 个自由变量按高位到低位展开做 beam search：
  - 每一步只决定一个 message bit 是否置 1
  - 对应 codeword 掩码通过异或 `x^i m(x)` 的 bitmask 更新
  - 评分函数不是完整距离，而是“已经被冻结、未来变量再也不会影响的那些输出位”的实际汉明距离

- 这个剪枝很关键：它让搜索宽度只用 `1000` 就足够稳定。
- 本地模拟 20 轮的总翻转数通常在 `430~450` 左右，远低于题目限制的 `600`。

- 最后用脚本连到远端：

```bash
python CTF_Writeups/scripts_python/CPCTF_Ultra_Janken_Tournament.py --host 133.88.122.244 --port 32035
```

- 脚本跑完 20 轮后得到：

```text
CPCTF{Tie_15_A_T1Me_ThiEf}
```

## 攻击链/解题流程总结

```text
线性化 nextrand -> 求 64 次消去多项式 m(x) -> 把 luck pattern 强制改成 g(x)m(x) 形式以消掉 100 个隐藏选手 -> 用自定义 strategy 读取 g 的低 8 bit 作为 winner 编码 -> 对每轮随机 pattern 做最近码字 beam search -> 自动交互拿到 Flag
```

## 漏洞分析 / 机制分析

### 根因
- `nextrand()` 虽然写成了 Python 的大整数异或移位，但从 GF(2) 角度看它仍然是一个 64 维线性变换。
- 题目把 100 个隐藏选手全部建立在同一个线性变换的幂序列上，因此整个系统天然存在一个低维线性关系空间。
- 又因为我们可以：
  1. 自由提交自己的 120 个 64-bit strategy
  2. 在看到每轮 `luck_pattern` 后再做在线修改

  所以可以把“消除别人贡献”和“编码自己想要的 winner”这两个目标合并到同一个线性码里完成。

### 影响
- 不需要恢复任何隐藏种子，也不需要预测 Python `random`。
- 只要预先求出 `nextrand` 的消去多项式，就能把 100 个隐藏参赛者的影响整体归零。
- 然后再利用自定义 strategy，把剩余 winner 完全变成一个我们可控的 residue 类问题。

### 修复建议（适用于漏洞类题目）
- 不要把所有参赛者都放在同一个线性递推族上，更不要允许选手在公开看到挑战向量后继续在线修改。
- 如果必须提供“修改位”的交互能力，应把结算函数换成不可线性分解的结构，避免被 GF(2) 线性代数整体消元。
- 不要让用户自定义的 strategy 直接参与最终的线性异或聚合，否则很容易被拿来编码目标 residue。

## 知识点
- GF(2) 线性变换与 xorshift / 线性递推
- 消去多项式 / 最小多项式思想
- 线性码中的最近码字搜索
- 利用自定义线性映射控制最终模 101 结果

## 使用的工具
- Python 3 / Go — 线性关系构造、beam search、远程自动交互
- PowerShell — 快速查看附件和验证仓库路径

## 脚本归档
- Go：[`CPCTF_Ultra_Janken_Tournament.go` :material-open-in-new:](https://github.com/starnotes-xj/BIGC_CTF_Writeups/blob/main/CTF_Writeups/scripts_go/CPCTF_Ultra_Janken_Tournament.go){target="_blank"}
- Python：[`CPCTF_Ultra_Janken_Tournament.py` :material-open-in-new:](https://github.com/starnotes-xj/BIGC_CTF_Writeups/blob/main/CTF_Writeups/scripts_python/CPCTF_Ultra_Janken_Tournament.py){target="_blank"}
- 说明：Go / Python 两个脚本都会自动完成 20 轮交互并输出真实 flag

## 命令行提取关键数据（无 GUI）

```bash
go run CTF_Writeups/scripts_go/CPCTF_Ultra_Janken_Tournament.go --host 133.88.122.244 --port 32035

python CTF_Writeups/scripts_python/CPCTF_Ultra_Janken_Tournament.py --host 133.88.122.244 --port 32035
```

## 推荐工具与优化解题流程

> 这题不是随机数预测题，而是“线性变换 + 线性码 + 在线最近码字搜索”的组合题。

### 工具对比总结

| 工具 | 适用阶段 | 本题耗时 | 优点 | 缺点 |
|------|----------|----------|------|------|
| 直接读 `server.py` | 建模 | 5-10 分钟 | 能立刻看出 `clash_power` 是 GF(2) 异或聚合 | 需要继续把 `nextrand` 形式化 |
| Python 线性代数 / 预计算脚本 | 求消去多项式 | 10-20 分钟 | 能把 100 个隐藏选手整体消掉 | 需要自己处理位级线性化 |
| Beam search 自动交互 | 在线利用 | 秒级 | 足够稳定，20 轮总翻转数明显小于 600 | 需要先把合法 codeword 参数化好 |

### 推荐流程

**推荐流程**：先把 `nextrand` 线性化并求出消去多项式 -> 构造合法 luck pattern 线性码 -> 设计自己的 strategy 把低 8 个 message bit 映射成 `0..255` -> 在线对每轮随机 pattern 做最近码字 beam search -> 自动交互拿 flag。

### 工具 A（推荐首选）
- **安装**：Python 3
- **详细步骤**：
  1. 预计算 `nextrand` 的 64 维线性关系
  2. 构造 `g(x)m(x)` 对应的 codeword 掩码
  3. 预计算 beam search 的冻结位剪枝掩码
  4. 连接远端并按轮次自动发送所有 `C / index / G`
- **优势**：从数学建模到远端利用完全一体化，最适合归档复现

### 工具 B（可选）
- **安装**：SageMath
- **详细步骤**：可用矩阵和多项式工具更快求出线性关系，再把最终交互逻辑交给 Python 脚本
- **优势**：适合比赛时快速验证消去多项式与码空间维数
