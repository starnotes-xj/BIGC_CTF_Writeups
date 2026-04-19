# CPCTF - QRRRRRRRRRR Writeup

## 题目信息
- **比赛**: CPCTF
- **题目**: QRRRRRRRRRR
- **类别**: Misc
- **难度**: 简单
- **附件/URL**: `qr-2d27682362537184a1db08f100d60c5735ef7a84cfa837a27226c2604ae92b56.png`
- **附件链接**: [下载附件](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/QR_Generator/qr-2d27682362537184a1db08f100d60c5735ef7a84cfa837a27226c2604ae92b56.png){download} · [仓库位置](https://github.com/starnotes-xj/BIGC_CTF_Writeups/tree/main/CTF_Writeups/files/QR_Generator){target="_blank"}
- **Flag格式**: `CPCTF{...}`
- **状态**: 已解

## Flag

```text
CPCTF{z3r0_l3ngth_h1dd3n_d4t4}
```

## 解题过程

### 1. 初始侦察/文件识别
- 题目给出一张二维码图片，题面提示：
  - “我实现了一个二维码生成器！”
  - “我尝试把一面旗帜转换成二维码！”
  - 建议使用 `strong-qr-decoder` 或 `QRazybox` 等二维码解码工具。
- 直接用普通二维码扫描器尝试解码时，会出现失败或无有效结果。
- 这说明二维码图像本身大概率不是简单损坏，而是**二维码数据结构中存在会干扰标准解码器的构造**。

### 2. 关键突破点一：标准解码器被 zero-length 段干扰
- 这张图是标准 29×29 module 的 QR Code，对应 Version 3。
- 读取格式信息可以得到：
  - Error correction level：`Q`
  - Mask pattern：`3`
- 按 QR 规范提取码字，并对 Version 3-Q 的两个 Reed-Solomon block 进行 deinterleave 后，可以看到数据区并不是普通解码器期望的正常 payload。
- 原始数据比特开头是一个 byte mode 段：

```text
0100 00000000
```

- 其中：
  - `0100` 表示 byte mode
  - `00000000` 表示长度为 0
- 也就是说，二维码开头伪造了一个**长度为 0 的 byte segment**。
- 普通解码器会先解析这个空段，随后继续尝试把后面的隐藏数据当成新的 QR segment 结构，从而解码失败。

### 3. 关键突破点二：直接查看 RS 修正后的原始数据
- 这题不能只依赖普通扫码结果，而要使用能展示 QR 原始 bitstream / codeword 的工具，例如：
  - `strong-qr-decoder`
  - `QRazybox`
- 对 RS block 进行正确还原后，不按标准 segment 长度解释，而是从第一个 zero-length byte segment 后继续按字节查看原始数据。
- 在 bit offset 12 之后，可以直接读到：

```text
CPCTF{z3r0_l3ngth_h1dd3n_d4t4}
```

- 这也解释了 flag 文本中的 `z3r0_l3ngth_h1dd3n_d4t4`：隐藏点正是 **zero-length segment 后面的数据**。

### 4. 获取 Flag
- 最终恢复出的 flag 为：

```text
CPCTF{z3r0_l3ngth_h1dd3n_d4t4}
```

## 攻击链/解题流程总结

```text
普通二维码扫描失败 -> 使用 strong-qr-decoder / QRazybox 查看原始 QR 结构 -> 识别 Version 3-Q、mask 3 -> deinterleave Reed-Solomon blocks -> 发现开头 byte mode 长度为 0 -> 跳过 zero-length 段后按原始字节读取隐藏数据 -> 得到 flag
```

## 漏洞分析 / 机制分析

### 根因
- QR Code 的 payload 由一个或多个 segment 组成，每个 segment 都有 mode 和长度字段。
- 本题构造了一个 byte mode、长度为 0 的 segment，把真正的数据放在后续原始 bitstream 中。
- 普通解码器严格按 segment 结构解析，因此不会直接把后面的隐藏字节当作有效消息输出。

### 影响
- 标准扫码器可能无法给出 flag，甚至只表现为“解码失败”。
- 但只要能查看 QR 的底层 codeword / bitstream，就可以绕过高层 segment 解析，直接恢复隐藏数据。

### 修复建议（适用于漏洞类题目）
- N/A。本题是利用 QR 编码结构做隐藏数据的 CTF 题。
- 如果真实场景中要验证 QR 内容，不能只依赖“普通扫码器可读内容”，还应检查底层结构中是否存在异常 segment 或冗余数据。

## 知识点
- QR Code mode 与长度字段
- QR Version 3-Q 的 Reed-Solomon block deinterleave
- zero-length segment 隐藏数据技巧
- 使用强二维码解码器查看原始 bitstream

## 使用的工具
- `strong-qr-decoder` / `QRazybox` — 查看二维码底层结构和原始数据
- Python 3 — 辅助验证 module matrix、format info 和 bit offset
- Reed-Solomon 解码 — 还原 Version 3-Q 的数据 block

## 脚本归档
- Go：待补
- Python：待补
- 说明：本题主要依赖二维码结构分析工具；如需后续自动化复现，可补充 `CPCTF_QR_Generator.py` 用于提取 QR codeword 并展示 bit offset 12 后的数据

## 命令行提取关键数据（无 GUI）

```bash
# 普通 QR 解码器可能失败，因为 payload 开头包含 zero-length byte segment
# 推荐使用 strong-qr-decoder / QRazybox 查看 RS 修正后的原始数据区
# 关键观察结果：bit offset 12 后的字节流为 CPCTF{z3r0_l3ngth_h1dd3n_d4t4}
```

## 推荐工具与优化解题流程

> 这题不是“扫不出来就修图”，而是要把二维码当作一种结构化编码格式来分析。

### 工具对比总结

| 工具 | 适用阶段 | 本题耗时 | 优点 | 缺点 |
|------|----------|----------|------|------|
| 普通二维码扫描器 | 初筛 | 秒级 | 快速验证是否是普通 QR | 会被 zero-length segment 干扰 |
| `strong-qr-decoder` | 深入分析 | 分钟级 | 能查看更底层的 QR 解码过程 | 需要理解 QR segment 结构 |
| `QRazybox` | 手动修复/观察 | 分钟级 | 适合观察 module、mask、codeword | 手工操作步骤更多 |

### 推荐流程

**推荐流程**：先用普通扫码器确认失败 -> 换 `strong-qr-decoder` / `QRazybox` 查看 QR 底层数据 -> 确认 zero-length byte segment -> 从后续 raw bytes 中提取 flag。

### 工具 A（推荐首选）
- **安装**：使用 `strong-qr-decoder` 或其在线/本地版本
- **详细步骤**：
  1. 导入二维码图片
  2. 查看格式信息和原始数据区
  3. 注意开头 byte mode 的长度字段为 `0`
  4. 继续查看该空段后面的原始字节
- **优势**：比普通扫码器更适合处理结构异常的 QR

### 工具 B（可选）
- **安装**：使用 `QRazybox`
- **详细步骤**：
  1. 导入 QR 图片并确认 module matrix
  2. 应用正确 mask 和纠错等级
  3. 查看 codeword / bitstream
  4. 从 bit offset 12 后读取隐藏文本
- **优势**：适合手工验证每一步 QR 结构
