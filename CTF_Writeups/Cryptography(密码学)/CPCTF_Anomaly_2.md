# CPCTF - Anomaly 2 Writeup

## 题目信息
- **比赛**: CPCTF
- **题目**: Anomaly 2
- **类别**: Crypto
- **难度**: 简单
- **附件/URL**: `chal_11b2c160203be5ff1faff97d47a20145736f862d4f6560638060d42b1131b49f .py`、`output.txt`
- **附件链接**: [chal_11b2c160203be5ff1faff97d47a20145736f862d4f6560638060d42b1131b49f .py](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/Anomaly_2/chal_11b2c160203be5ff1faff97d47a20145736f862d4f6560638060d42b1131b49f%20.py){download} · [output.txt](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/Anomaly_2/output.txt){download} · [仓库位置](https://github.com/starnotes-xj/BIGC_CTF_Writeups/tree/main/CTF_Writeups/files/Anomaly_2){target="_blank"}
- **Flag格式**: `CPCTF{...}`
- **状态**: 已解

## Flag

```text
CPCTF{7h3_n3x7_574710n_15_Kukud0}
```

## 解题过程

### 1. 初始侦察/文件识别
- 题目附件包含源码 `chal_11b2c160203be5ff1faff97d47a20145736f862d4f6560638060d42b1131b49f .py` 和输出文件 `output.txt`。
- 源码的核心逻辑如下：

```python
def rsa_encryption(flag):
    m = bytes_to_long(flag.encode())
    e = 3
    p, q = getPrime(512), getPrime(512)
    n = p * q
    c = pow(n, e, m)
    return (n, e, c)
```

- 这里最异常的地方是 `pow(n, e, m)`：第三个参数 `m` 是模数，而 `m = bytes_to_long(flag.encode())`。
- 也就是说，题目不是常规 RSA 的 `c = m^e mod n`，而是把 flag 对应的大整数当成了模数。
- `output.txt` 给出两组同一 flag 下的输出：

```text
n1 = 87405182736104359780257026883853062930574663561980633775939752446259523158955808889602775147349422181286752422777444540409043705137242444906859982710084376976995577762838755152310969883588687143185855446868518299103284219288298089004723615989669846760852206531362806473299208237879292642911953181354015637739
e1 = 3
c1 = 5947050188011198882167638654472754073461946759644146614025932625290616486683809
n2 = 89984079446277129336031962353513290766726794253576464892005498900113523905864088594103793620450760604852463679010581777863799208215048737093285826288578917592161127386371969728330753862369184707806787782705755694366125100020912792307994059926523686129099696784648345246590104006734129991238410853485925459399
e2 = 3
c2 = 1469764391126334007675223493311131828227376713240295689831327636992622204657369
```

### 2. 关键突破点一
- 因为：

$$
c_i \equiv n_i^{e_i} \pmod m
$$

所以：

$$
n_i^{e_i}-c_i = k_i m
$$

- 两组数据使用同一个 flag，因此使用的是同一个 `m`。
- 于是 `m` 必然同时整除：

$$
n_1^{e_1}-c_1
$$

和：

$$
n_2^{e_2}-c_2
$$

- 直接求 gcd：

```python
from math import gcd

common = gcd(n1**e1 - c1, n2**e2 - c2)
```

### 3. 关键突破点二
- 需要注意，`gcd` 得到的不一定正好等于 `m`，也可能是 `m` 的小倍数：

$$
\gcd(k_1m, k_2m)=m\cdot\gcd(k_1,k_2)
$$

- 本题计算得到的 `common` 是真实明文整数的 `2` 倍。
- 因此尝试小 cofactor，并用 flag 格式和原同余式同时验证：

```python
for cofactor in range(1, 10000):
    if common % cofactor != 0:
        continue
    candidate_m = common // cofactor
    candidate = candidate_m.to_bytes((candidate_m.bit_length() + 7) // 8, "big")
    if candidate.startswith(b"CPCTF{") and candidate.endswith(b"}"):
        assert pow(n1, e1, candidate_m) == c1
        assert pow(n2, e2, candidate_m) == c2
        print(candidate.decode())
```

### 4. 获取 Flag
- 当 `cofactor = 2` 时，得到的整数可以正常还原为 ASCII 字符串，并且能通过两组原始同余式验证。
- 最终 flag 为：

```text
CPCTF{7h3_n3x7_574710n_15_Kukud0}
```

## 攻击链/解题流程总结

```text
阅读源码 -> 发现 flag 被当作模数 m -> 由 c_i = n_i^e_i mod m 推出 m | (n_i^e_i - c_i) -> 对两组差值求 gcd -> 去掉额外小公因子 -> long_to_bytes 还原 flag -> 回代验证
```

## 漏洞分析 / 机制分析

### 根因
- 代码把 `pow(base, exp, mod)` 的第三个参数当成了普通参与加密的值，但它实际代表模数。
- `m = bytes_to_long(flag.encode())` 被放在模数位置后，每个输出都泄露了一个 `m` 的倍数关系：

$$
m \mid (n^e-c)
$$

- 多组同模输出会让攻击者通过 gcd 恢复 `m`。

### 影响
- 不需要分解 `n`，也不需要知道 `p, q`。
- 只要有两组或更多组 `(n, e, c)`，就可以利用共同模数关系恢复 flag 对应的大整数。
- 如果 gcd 带有额外小因子，也能通过 flag 格式和原公式验证去除。

### 修复建议（适用于漏洞类题目）
- 不要把敏感明文或密钥材料作为模数参与公开计算。
- 如果要实现 RSA 加密，应使用 `c = pow(m, e, n)`，并在真实场景中使用标准库提供的带填充方案，例如 RSA-OAEP。
- 代码审计时要特别确认 `pow(base, exp, mod)` 三个参数的语义，避免把“被加密消息”和“模数”混淆。

## 知识点
- Python 三参数 `pow(base, exp, mod)` 的模幂语义
- 由同余式构造整除关系
- 多组倍数取 gcd 恢复隐藏模数
- `bytes_to_long` / `long_to_bytes` 的互逆转换

## 使用的工具
- Python 3 — 解析输出、计算 gcd、还原 flag
- `math.gcd` — 从两组倍数关系中恢复共同因子

## 脚本归档
- Go：待补
- Python：[`CPCTF_Anomaly_2.py` :material-open-in-new:](https://github.com/starnotes-xj/BIGC_CTF_Writeups/blob/main/CTF_Writeups/scripts_python/CPCTF_Anomaly_2.py){target="_blank"}
- 说明：Python 脚本会读取归档后的 `files/Anomaly_2/output.txt`，计算 `gcd(n_i ** e_i - c_i)`，去掉额外小 cofactor 并输出完整 flag。

## 命令行提取关键数据（无 GUI）

```bash
python CTF_Writeups/scripts_python/CPCTF_Anomaly_2.py
```

## 推荐工具与优化解题流程

> 这题的核心不是分解 RSA 模数，而是发现 flag 被错误地放在了模幂运算的模数位置。

### 工具对比总结

| 工具 | 适用阶段 | 本题耗时 | 优点 | 缺点 |
|------|----------|----------|------|------|
| 直接阅读源码 | 建模 | 秒级 | 能立刻发现 `pow(n, e, m)` 参数异常 | 需要理解三参数 `pow` |
| Python `math.gcd` | 恢复明文整数 | 秒级 | 标准库即可完成，结果可复现 | 需要处理 gcd 可能是 `m` 的倍数 |
| 通用 RSA 工具 | 误区 / 备选 | 不适用 | 适合常规 RSA | 本题不需要分解 `n`，方向错误 |

### 推荐流程

**推荐流程**：先读源码确认 `m` 是 flag 整数且处在模数位置 -> 从 `output.txt` 解析两组 `(n, e, c)` -> 计算 `gcd(n1^e1-c1, n2^e2-c2)` -> 尝试小 cofactor -> 转字节并按 `CPCTF{...}` 验证 -> 回代原同余式确认。

### 工具 A（推荐首选）
- **安装**：Python 3
- **详细步骤**：
  1. 读取 `output.txt`
  2. 用正则提取 `n1/e1/c1/n2/e2/c2`
  3. 计算 `common = gcd(n1**e1 - c1, n2**e2 - c2)`
  4. 尝试 `common // cofactor`，把候选整数转换为字节串
  5. 用 flag 格式和 `pow(n_i, e_i, candidate_m) == c_i` 验证候选
- **优势**：完全贴合题目漏洞，依赖少，可直接复现。

### 工具 B（可选）
- **安装**：CyberChef 或任意大整数转字节工具
- **详细步骤**：可在算出候选整数后，把十进制整数按大端序转回字节串辅助验证。
- **优势**：适合手工交叉检查，但最终仍建议使用本地脚本归档。
