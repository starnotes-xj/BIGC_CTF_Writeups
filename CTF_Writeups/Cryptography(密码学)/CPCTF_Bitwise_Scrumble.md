# CPCTF - Bitwise Scrumble Writeup

## 题目信息
- **比赛**: CPCTF
- **题目**: Bitwise Scrumble
- **类别**: Crypto
- **难度**: 简单
- **附件/URL**: `letsbitwise_04aed83f977321dd26f1e7d4d033e271d28a8490f406e37efb45f0606d6f1ae3.py`
- **附件链接**: [下载附件](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/Bitwise_Scrumble/letsbitwise_04aed83f977321dd26f1e7d4d033e271d28a8490f406e37efb45f0606d6f1ae3.py){download} · [仓库位置](https://github.com/starnotes-xj/BIGC_CTF_Writeups/tree/main/CTF_Writeups/files/Bitwise_Scrumble){target="_blank"}
- **Flag格式**: `CPCTF{...}`
- **状态**: 已解

## Flag

```text
CPCTF{B1twis3_r0t4t10n!_3tim3s}
```

## 解题过程

### 1. 初始侦察/文件识别
- 题目给了一个 Python 加密脚本和密文：

```text
encrypted_flag : 10aa77170b38758c146245779086332e5e8237430f362d317310124333b999b890043152135
```

- 附件核心逻辑如下：

```python
key = "0123456789012109876543210"

textnum = str(bytes_to_long(text.encode()))
first_part = textnum[:25]
second_part = textnum[25:50]
third_part = textnum[50:75]

encrypted_f = format(((f | k) & (f ^ k)), 'x')
encrypted_s = format(((s & k) ^ (s | k)), 'x')
encrypted_t = format((t ^ ((t | k) & k)), 'x')
```

- 明文会先被转成一个 75 位十进制整数串，再切成三个 25 位块。
- 每个块的同一位置都和 `key[i]` 做一个 bitwise 表达式，输出为一位十六进制字符。

### 2. 关键突破点一
- 题目提示说“每个比特执行的操作都是独立的”，因此不需要把 `0..9` 的十进制数字整体看成复杂对象。
- 对单个 bit 设明文 bit 为 $x$，key bit 为 $y$，逐个写真值表。

#### 第一段

$$
(x \lor y) \land (x \oplus y)
$$

| x | y | x OR y | x XOR y | result |
|---|---|--------|---------|--------|
| 0 | 0 | 0 | 0 | 0 |
| 0 | 1 | 1 | 1 | 1 |
| 1 | 0 | 1 | 1 | 1 |
| 1 | 1 | 1 | 0 | 0 |

- 结果等价于：

$$
x \oplus y
$$

#### 第二段

$$
(x \land y) \oplus (x \lor y)
$$

| x | y | x AND y | x OR y | result |
|---|---|---------|--------|--------|
| 0 | 0 | 0 | 0 | 0 |
| 0 | 1 | 0 | 1 | 1 |
| 1 | 0 | 0 | 1 | 1 |
| 1 | 1 | 1 | 1 | 0 |

- 结果同样等价于：

$$
x \oplus y
$$

#### 第三段

$$
x \oplus ((x \lor y) \land y)
$$

- 其中：

$$
(x \lor y) \land y = y
$$

- 因此第三段直接化简为：

$$
x \oplus y
$$

### 3. 关键突破点二
- 三个加密表达式虽然长得不同，但对每个 bit 来说都等价于：

$$
\mathrm{encrypted\_digit} = \mathrm{original\_digit} \oplus \mathrm{key\_digit}
$$

- XOR 自反，所以解密时再异或同一个 `key_digit`：

$$
\mathrm{original\_digit} = \mathrm{encrypted\_digit} \oplus \mathrm{key\_digit}
$$

- 由于加密输出是十六进制字符，解密时要先把每个字符按 hex nibble 解析：

```python
digit = int(encrypted_nibble, 16) ^ int(key_digit)
```

- 对三个 25 位分块分别恢复后拼接，得到原始 75 位十进制整数串。

### 4. 获取 Flag
- 恢复出的十进制串是：

```text
118932708239548593070656909407782612255397407903631131065430989999835411325
```

- 将这个大整数转回字节串即可得到：

```text
CPCTF{B1twis3_r0t4t10n!_3tim3s}
```

## 攻击链/解题流程总结

```text
阅读附件 -> 发现 flag 被转成 75 位十进制串并三等分 -> 对三个 bitwise 表达式写单 bit 真值表 -> 三者都化简为 digit ^ key_digit -> 密文逐位再异或 key -> 拼回十进制整数 -> long_to_bytes 得到 Flag
```

## 漏洞分析 / 机制分析

### 根因
- 附件中的三个 bitwise 表达式看起来不同，但每个 bit 的真值表完全等价于 XOR。
- 由于每个十进制数字位置都独立处理，没有跨位扩散、没有随机 IV，也没有不可逆步骤。
- 因此只要识别等价表达式，就能逐位恢复原始数字。

### 影响
- 密文中的每个 hex nibble 都可以独立解密。
- 不需要爆破 flag，也不需要求解复杂方程。
- 题目实际退化成了“真值表化简 + XOR 自反”。

### 修复建议（适用于漏洞类题目）
- 不要把可逆的简单 bitwise 表达式当作加密方案。
- 如果要隐藏明文，应使用标准对称加密，并引入密钥、随机 IV / nonce 与认证机制。
- 自定义混淆至少应避免每个位置完全独立，否则极易被真值表逐位还原。

## 知识点
- bitwise 运算的单 bit 真值表
- XOR 的自反性质：$a \oplus b \oplus b = a$
- 大整数与字节串转换：`bytes_to_long` / `long_to_bytes`

## 使用的工具
- Go — 按题解思路还原十进制数字并转回字节
- Python 3 — 编写等价复现脚本

## 脚本归档
- Go：[`CPCTF_Bitwise_Scrumble.go` :material-open-in-new:](https://github.com/starnotes-xj/BIGC_CTF_Writeups/blob/main/CTF_Writeups/scripts_go/CPCTF_Bitwise_Scrumble.go){target="_blank"}
- Python：[`CPCTF_Bitwise_Scrumble.py` :material-open-in-new:](https://github.com/starnotes-xj/BIGC_CTF_Writeups/blob/main/CTF_Writeups/scripts_python/CPCTF_Bitwise_Scrumble.py){target="_blank"}
- 说明：两个脚本都会输出完整 flag

## 命令行提取关键数据（无 GUI）

```bash
go run CTF_Writeups/scripts_go/CPCTF_Bitwise_Scrumble.go

python CTF_Writeups/scripts_python/CPCTF_Bitwise_Scrumble.py
```

## 推荐工具与优化解题流程

> 本题提示已经点明“每个比特独立”，最有效的方法就是写真值表并做布尔表达式化简。

### 工具对比总结

| 工具 | 适用阶段 | 本题耗时 | 优点 | 缺点 |
|------|----------|----------|------|------|
| 真值表 | 建模 | 1-3 分钟 | 直接看出三个表达式都等价于 XOR | 需要逐个表达式验证 |
| Go / Python 脚本 | 解密 | 秒级 | 适合逐位处理与大整数转字节 | 需要注意 hex nibble 解析 |
| 盲目爆破 | 误区 | 不定 | 无 | 完全没必要，题目是可逆逐位变换 |

### 推荐流程

**推荐流程**：先把三个 bitwise 表达式降到单 bit 真值表 -> 发现都等价于 XOR -> 对密文每个 hex 字符异或对应 key 数字 -> 拼接十进制串 -> 转回字节得到 flag。

### 工具 A（推荐首选）
- **安装**：Go 或 Python 3
- **详细步骤**：
  1. 把密文按 `25/25/25` 切成三段
  2. 遍历每段每个位置
  3. `int(hex_char, 16) ^ int(key[i])` 还原原始十进制数字
  4. 拼接 75 位十进制数
  5. 转为大整数，再转回 bytes
- **优势**：完全复现加密逆过程，代码短且稳定

### 工具 B（可选）
- **安装**：任意布尔代数 / 真值表工具
- **详细步骤**：验证三个表达式的真值表均为 XOR。
- **优势**：适合快速确认化简是否正确
