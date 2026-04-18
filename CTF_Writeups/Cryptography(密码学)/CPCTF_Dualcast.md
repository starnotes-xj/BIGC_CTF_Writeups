# CPCTF - Dualcast Writeup

## 题目信息
- **比赛**: CPCTF
- **题目**: Dualcast
- **类别**: Crypto
- **难度**: 简单
- **附件/URL**: `chal_93a777a5b75dc532378a23c61dd022f7daa6d259ea438c4d353ce5af0514d2e2.py`、`out.txt`
- **附件链接**: [chal_93a777a5b75dc532378a23c61dd022f7daa6d259ea438c4d353ce5af0514d2e2.py](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/Dualcast/chal_93a777a5b75dc532378a23c61dd022f7daa6d259ea438c4d353ce5af0514d2e2.py){download} · [out.txt](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/Dualcast/out.txt){download} · [仓库位置](https://github.com/starnotes-xj/BIGC_CTF_Writeups/tree/main/CTF_Writeups/files/Dualcast){target="_blank"}
- **Flag格式**: `CPCTF{...}`
- **状态**: 已解

## Flag

```text
CPCTF{wh47_7yp3_15_y0ur_477r1bu73?}
```

## 解题过程

### 1. 初始侦察/文件识别
- 入口点只有两个附件：题目脚本和输出文件。
- 先看脚本内容：

```python
from Crypto.Util.number import bytes_to_long
flag = "CPCTF{REDACTED}"
flag_bytes = flag.encode()
print(f"c = {bytes_to_long(flag_bytes)}")
```

- 这段逻辑没有任何真正的加密过程，唯一做的事情只是把 `flag.encode()` 转成一个大整数并打印出来。
- `out.txt` 中给出的就是这个十进制大整数：

```text
c = 510812092313572375684202062709941424740135938555245927502061365582594139087652994941
```

### 2. 关键突破点一
- `bytes_to_long()` 的本质是把字节串按大端序解释成整数。
- 这一步是完全可逆的，对应的逆操作就是 `long_to_bytes()`，或者直接用标准库的 `int.to_bytes(...)`。
- 所以题目表面上给了一个很长的大整数，实际上只是把 flag 的原始字节重新编码了一遍。

### 3. 关键突破点二
- 既然 `c` 只是编码后的整数，解题步骤就非常直接：
  1. 从 `out.txt` 提取整数 `c`
  2. 把 `c` 转回字节串
  3. 按 ASCII / UTF-8 解码
- 用 Python 一行核心逻辑即可恢复：

```python
flag = long_to_bytes(c).decode()
```

### 4. 获取 Flag
- 将 `c` 还原为字节串后，直接得到：

```text
CPCTF{wh47_7yp3_15_y0ur_477r1bu73?}
```

## 攻击链/解题流程总结

```text
阅读题目脚本 -> 识别 bytes_to_long 只是可逆编码 -> 从 out.txt 提取整数 c -> long_to_bytes 还原字节串 -> 解码得到 Flag
```

## 漏洞分析 / 机制分析

### 根因
- 题目没有实现任何加密或混淆，只做了 `bytes_to_long(flag.encode())`。
- `bytes_to_long` 是一种可逆的表示变换，不会损失任何明文信息。
- 因此所谓的“密文”实际上仍然完整保留了原始 flag 的全部内容。

### 影响
- 拿到输出整数的任何人都可以直接恢复原文。
- 不需要爆破、不需要密码分析，也不需要还原额外状态。

### 修复建议（适用于漏洞类题目）
- 如果真实场景需要保护内容，不能把可逆编码当作加密。
- 应使用标准加密方案，例如基于随机密钥的对称加密，或正确使用带填充的公钥加密。
- 设计题目时也要区分“编码”“序列化”“加密”这三类完全不同的操作。

## 知识点
- `bytes_to_long` 与 `long_to_bytes` 的互逆关系
- 大整数与字节串之间的大端序转换
- 代码审计时优先确认“是否真的发生了加密”

## 使用的工具
- Python 3 — 解析输出并恢复字节串
- PowerShell — 快速查看附件内容

## 脚本归档
- Go：[`CPCTF_Dualcast.go` :material-open-in-new:](https://github.com/starnotes-xj/BIGC_CTF_Writeups/blob/main/CTF_Writeups/scripts_go/CPCTF_Dualcast.go){target="_blank"}
- Python：[`CPCTF_Dualcast.py` :material-open-in-new:](https://github.com/starnotes-xj/BIGC_CTF_Writeups/blob/main/CTF_Writeups/scripts_python/CPCTF_Dualcast.py){target="_blank"}
- 说明：两个脚本都会直接读取归档后的 `files/Dualcast/out.txt` 并输出完整 flag

## 命令行提取关键数据（无 GUI）

```bash
python CTF_Writeups/scripts_python/CPCTF_Dualcast.py

go run CTF_Writeups/scripts_go/CPCTF_Dualcast.go
```

## 推荐工具与优化解题流程

> 这题的核心不是密码学算法，而是识别“编码伪装成加密”的最小套路。

### 工具对比总结

| 工具 | 适用阶段 | 本题耗时 | 优点 | 缺点 |
|------|----------|----------|------|------|
| 直接阅读源码 | 初筛 | 秒级 | 立刻发现没有加密 | 需要先有源码 |
| Python 脚本 | 还原 flag | 秒级 | 转换大整数最直接 | 需要手动提取整数 |
| CyberChef / 在线转换工具 | 验证 | 秒级 | 可视化方便 | 不如本地脚本可复现 |

### 推荐流程

**推荐流程**：先看源码确认是否只是 `bytes_to_long` 编码 -> 读取 `out.txt` 提取整数 -> 本地脚本转回字节串 -> 输出 Flag。

### 工具 A（推荐首选）
- **安装**：Python 3
- **详细步骤**：
  1. 读取 `out.txt`
  2. 用正则提取十进制整数 `c`
  3. 调用 `int.to_bytes(...)` 或 `long_to_bytes(...)`
  4. 把结果解码为字符串
- **优势**：完全可复现，适合归档到题库仓库

### 工具 B（可选）
- **安装**：Go 1.20+
- **详细步骤**：
  1. 用 `math/big` 解析十进制整数
  2. 用 `big.Int.Bytes()` 取回原始大端字节
  3. 直接打印字符串结果
- **优势**：无第三方依赖，适合做独立命令行归档
