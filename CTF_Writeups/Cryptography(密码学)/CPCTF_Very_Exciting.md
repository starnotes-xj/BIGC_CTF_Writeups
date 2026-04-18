# CPCTF - Very Exciting Writeup

## 题目信息
- **比赛**: CPCTF
- **题目**: Very Exciting
- **类别**: Crypto
- **难度**: 简单
- **附件/URL**: `server_5dd79bdc6f546c5f0a01a3568e6fe0bbd190887ff16eaf8c34613559c2c574e7.py`、`nc 133.88.122.244 32007`
- **附件链接**: [server_5dd79bdc6f546c5f0a01a3568e6fe0bbd190887ff16eaf8c34613559c2c574e7.py](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/Very%20Exciting/server_5dd79bdc6f546c5f0a01a3568e6fe0bbd190887ff16eaf8c34613559c2c574e7.py){download} · [仓库位置](https://github.com/starnotes-xj/BIGC_CTF_Writeups/tree/main/CTF_Writeups/files/Very%20Exciting){target="_blank"}
- **Flag格式**: `CPCTF{...}`
- **状态**: 已解

## Flag

```text
CPCTF{SAMe_01d_STReam_1s_A1WaYs_b0r1ng}
```

## 解题过程

### 1. 初始侦察/文件识别
- 服务先随机生成 `secret_key` 与 `exciting_iv`，随后用 `BoringRandom` 作为密钥流生成器加密 flag：

```python
myPKSG = BoringRandom(secret_key, exciting_iv)
exciting_flag = stream_excite(myPKSG, secret_flag_plaintext)
print(f"... exciting_iv ... {exciting_iv.hex()}")
print(f"... exciting_flag ... {exciting_flag.hex()}")
```

- 接着它又允许我们提交任意明文，并且**自己指定一个 16 字节 IV**，仍然使用同一个 `secret_key` 重新实例化生成器：

```python
yourPKSG = BoringRandom(secret_key, very_exciting_iv)
enc_your_favorite = stream_excite(yourPKSG, your_favorite)
```

- 这说明题目的核心不是去逆向 `BoringRandom` 内部结构，而是观察“同一把 key + 可控 IV + 可选明文加密 oracle”这件事本身。
- 远端服务实际提示文字是英文版，但逻辑与附件完全一致。

### 2. 关键突破点一
- `stream_excite()` 的本质就是典型流密码异或：

```python
return bytes([a ^ b for a, b in zip(data, keystream)])
```

- 因此可以写成：

```text
C_flag = P_flag XOR KS(secret_key, exciting_iv)
C_user = P_user XOR KS(secret_key, very_exciting_iv)
```

- 只要我们把 `very_exciting_iv` 设成打印出来的 `exciting_iv`，就有：

```text
KS(secret_key, very_exciting_iv) = KS(secret_key, exciting_iv)
```

- 也就是说，服务把“加密 flag 时用到的同一段密钥流”重新开放给了攻击者调用。

### 3. 关键突破点二
- 既然能重用同一段密钥流，最直接的做法就是提交**与 flag 密文等长的全 0 明文**。
- 对全 0 明文而言：

```text
C_zero = 00...00 XOR KS = KS
```

- 服务返回的密文就不再是“密文”，而是裸露的 keystream。
- 最后再异或回去即可恢复 flag：

```text
P_flag = C_flag XOR KS
```

- 题目后面那个“茶神签”会再调用一次 `nextrand()`，但这发生在我们拿到密钥流之后，对解题没有任何影响。

### 4. 获取 Flag
- 攻击流程如下：
  1. 连接 `nc 133.88.122.244 32007`
  2. 读取服务打印的 `exciting_iv` 和 `exciting_flag`
  3. 发送与 `exciting_flag` 等长的全 0 十六进制串
  4. 把自己的 `very_exciting_iv` 设为同一个 `exciting_iv`
  5. 取得返回的 keystream，并与 `exciting_flag` 异或
- 实际恢复结果：

```text
CPCTF{SAMe_01d_STReam_1s_A1WaYs_b0r1ng}
```

## 攻击链/解题流程总结

```text
审计源码确认是流密码 XOR -> 发现 flag 加密与用户加密共用同一 secret_key 且 IV 可控 -> 复用打印出来的 exciting_iv -> 用等长全 0 明文取回 keystream -> 与 exciting_flag 异或恢复 Flag
```

## 漏洞分析 / 机制分析

### 根因
- 服务把同一个 `secret_key` 同时用于“保护 flag”和“给用户提供加密 oracle”。
- 用户还能自由指定 `very_exciting_iv`，因此可以主动制造与 flag 完全相同的 keystream。
- 流密码/同步密钥流方案一旦发生 keystream reuse，就会退化为简单异或问题，不需要恢复密钥本身。

### 影响
- 攻击者无需破解 `BoringRandom`，也无需预测随机数内部状态，就能直接恢复 flag。
- 如果同一会话中还有其他使用同样 `(key, IV)` 组合的敏感数据，也会被同样方式解出。
- 这是典型的“nonce/IV 重用 + chosen-plaintext oracle”组合失误。

### 修复建议（适用于漏洞类题目）
- 流密码或任何基于 keystream 的方案都必须保证 **同一 key 下 nonce/IV 唯一**。
- 不要让攻击者选择可能与敏感数据复用的 nonce/IV；更安全的做法是服务端自行生成并强制唯一性。
- 保护敏感数据与对外提供加密服务时，应使用不同密钥，或直接改用带认证的标准 AEAD（如 ChaCha20-Poly1305、AES-GCM）。

## 知识点
- 流密码 / keystream XOR 模型
- nonce / IV 重用导致的 two-time pad 问题
- chosen-plaintext oracle 的利用方式

## 使用的工具
- Python 3 — 编写远程利用脚本并自动恢复 flag
- Go — 编写无第三方依赖的归档版解题脚本
- PowerShell — 查看附件与快速验证本地文件路径

## 脚本归档
- Go：[`CPCTF_Very_Exciting.go` :material-open-in-new:](https://github.com/starnotes-xj/BIGC_CTF_Writeups/blob/main/CTF_Writeups/scripts_go/CPCTF_Very_Exciting.go){target="_blank"}
- Python：[`CPCTF_Very_Exciting.py` :material-open-in-new:](https://github.com/starnotes-xj/BIGC_CTF_Writeups/blob/main/CTF_Writeups/scripts_python/CPCTF_Very_Exciting.py){target="_blank"}
- 说明：两个脚本都会连接远端服务，自动复用 `exciting_iv` 并恢复完整 flag

## 命令行提取关键数据（无 GUI）

```bash
python CTF_Writeups/scripts_python/CPCTF_Very_Exciting.py

go run CTF_Writeups/scripts_go/CPCTF_Very_Exciting.go
```

## 推荐工具与优化解题流程

> 这题最重要的是尽快识别“不要被自定义 PRNG 吓住，真正漏洞是 keystream reuse”。

### 工具对比总结

| 工具 | 适用阶段 | 本题耗时 | 优点 | 缺点 |
|------|----------|----------|------|------|
| 直接阅读源码 | 漏洞定位 | 1-3 分钟 | 能立刻看出同 key + 可控 IV 的设计失误 | 需要先拿到附件 |
| Python socket 脚本 | 远程利用 | 秒级 | 编写最快，适合一次性验证与归档 | 依赖远端服务在线 |
| Go 标准库脚本 | 长期归档 | 秒级 | 无第三方依赖，便于跨平台复现 | 开发速度略慢于 Python |

### 推荐流程

**推荐流程**：先审计源码确认流密码和 keystream 复用点 -> 直接写脚本复用 `exciting_iv` -> 发送等长全 0 明文取回 keystream -> 异或得到 Flag（通常分钟级完成）。

### 工具 A（推荐首选）
- **安装**：Python 3
- **详细步骤**：
  1. 建立到题目服务的 TCP 连接
  2. 解析横幅中的 `exciting_iv` 与 `exciting_flag`
  3. 发送等长全 0 明文并复用同一个 IV
  4. 把返回结果当作 keystream，与 flag 密文异或
- **优势**：脚本最短，调试最方便，适合比赛现场快速拿分

### 工具 B（可选）
- **安装**：Go 1.20+
- **详细步骤**：
  1. 用 `net.Dial` 连接服务
  2. 读到提示后发送十六进制输入
  3. 使用正则提取密文并异或恢复 flag
- **优势**：仅用标准库即可复现，适合长期归档到题库仓库
