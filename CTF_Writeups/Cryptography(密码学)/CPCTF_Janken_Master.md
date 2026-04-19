# CPCTF - Janken Master Writeup

## 题目信息
- **比赛**: CPCTF
- **题目**: Janken Master
- **类别**: Crypto
- **难度**: 简单
- **附件/URL**: `server_6ab09e380fef5d661f0e6a88f955dfb31db646c0cb1faec8e8908629e1c04182.py`、`nc 133.88.122.244 32212`
- **附件链接**: [下载附件](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/Janken%20Master/server_6ab09e380fef5d661f0e6a88f955dfb31db646c0cb1faec8e8908629e1c04182.py){download} · [仓库位置](https://github.com/starnotes-xj/BIGC_CTF_Writeups/tree/main/CTF_Writeups/files/Janken%20Master){target="_blank"}
- **Flag格式**: `CPCTF{...}`
- **状态**: 已解

## Flag

```text
CPCTF{M45TER_of_riGGed_d1Ce}
```

## 解题过程

### 1. 初始侦察/文件识别
- 题目给了一个 Python 服务端脚本，题面是“咱们一起玩石头剪刀布吧！”，并额外提示使用了 `xoroshiro128+` 随机数生成算法。
- 脚本核心逻辑如下：

```python
seed = int(seed_input)
seed ^= 0x1234567890abcdef1234567890abcdef
rng = Xoroshiro128Plus(seed)

for _ in range(99):
    npc_hands.append(rng.next() % 3)
```

- 也就是说：
  1. 我们先输入一个整数种子
  2. 服务端把它和固定 128 bit 常量异或
  3. 再把结果直接当作 `xoroshiro128+` 的内部状态来源
  4. 连续生成 99 个 NPC 的出拳
- 玩家自己只能选择一次手势，目标是成为 **唯一赢家**。

### 2. 关键突破点一：题目没有禁止 xoroshiro128+ 的全零状态
- `xoroshiro128+` 这类生成器有一个非常经典的前提：**内部状态不能是全零**。
- 但题目这里没有做任何状态合法性检查，而是直接把：

$$
\mathrm{seed} \oplus \mathtt{0x1234567890abcdef1234567890abcdef}
$$

- 的结果拆成两个 64 bit 状态字。
- 如果我们让异或后的内部状态恰好变成 $0$，那么：

$$
s_0 = 0,\qquad s_1 = 0
$$

- 之后每一次 `next()` 都只会在 0 上做旋转、异或和加法，结果仍然永远是 0。

### 3. 关键突破点二：构造让内部状态归零的幸运数字
- 要让内部状态为 $0$，只需要输入与掩码完全相同的十进制整数：

```text
24197857200151252728969465429440056815
```

- 因为服务端会先执行：

$$
\mathrm{input\_seed} \oplus \mathtt{0x1234567890abcdef1234567890abcdef}
$$

- 所以内部真正进入 RNG 的值就是：

$$
0
$$

- 这意味着 99 个 NPC 的手势全部满足：

```python
rng.next() % 3 == 0
```

- 也就是全部出 `Rock`。
- 既然所有 NPC 都固定为 `Rock`，我们只要选择 `Paper (2)` 即可。

### 4. 获取 Flag
- 最终利用步骤非常短：
  1. 输入幸运数字 `24197857200151252728969465429440056815`
  2. 选择手势 `2`（Paper）
  3. 因为 99 个 NPC 全是 Rock，我们成为唯一赢家
- 远端返回：

```text
CPCTF{M45TER_of_riGGed_d1Ce}
```

## 攻击链/解题流程总结

```text
阅读 server.py -> 发现用户可控 seed 会先与固定常量异或 -> 注意到题目未禁止 xoroshiro128+ 全零状态 -> 输入与掩码相同的十进制数使内部状态归零 -> 99 个 NPC 全部出 Rock -> 玩家出 `Paper (2)` 成为唯一赢家 -> 获得 Flag
```

## 漏洞分析 / 机制分析

### 根因
- 题目直接把用户输入经过一次固定异或后作为 `xoroshiro128+` 的内部状态。
- 但 `xoroshiro128+` 的状态空间里，全零状态是退化点，生成器会永久卡死在 $0$。
- 服务端没有对这个非法状态做过滤或重新播种，导致我们可以把“随机局”退化成完全确定的局面。

### 影响
- NPC 的 99 次出拳全部变成可预测常量。
- 攻击者不需要恢复种子，也不需要做状态回溯，只要构造一次特殊输入即可稳定获胜。
- 题面提示看起来像“PRNG 分析题”，但实际利用点是“不合法状态注入”。

### 修复建议（适用于漏洞类题目）
- 初始化 `xoroshiro128+` 时必须拒绝 `(0, 0)` 全零状态。
- 不要直接把用户输入映射为内部状态，至少应通过安全播种过程生成状态，例如使用经过验证的 seed expander。
- 如果业务依赖随机性判定输赢，必须确保状态初始化满足算法前置条件。

## 知识点
- `xoroshiro128+` 的状态约束
- 全零状态导致 PRNG 退化为常量输出
- 区分“预测随机数”与“构造非法初始状态”

## 使用的工具
- Python 3 — 本地验证全零状态与自动交互远端服务
- `nc` / socket — 与题目远程服务交互
- 代码审计 — 识别种子异或与状态初始化缺陷

## 脚本归档
- Python：[`CPCTF_Janken_Master.py` :material-open-in-new:](https://github.com/starnotes-xj/BIGC_CTF_Writeups/blob/main/CTF_Writeups/scripts_python/CPCTF_Janken_Master.py){target="_blank"}
- 说明：脚本默认本地验证 exploit 条件，使用 `--remote` 可直接连接题目服务拿 flag

## 命令行提取关键数据（无 GUI）

```bash
python CTF_Writeups/scripts_python/CPCTF_Janken_Master.py

python CTF_Writeups/scripts_python/CPCTF_Janken_Master.py --remote --host 133.88.122.244 --port 32212
```

## 推荐工具与优化解题流程

> 这题的重点不是做复杂 PRNG 预测，而是先确认题目是否满足所声称算法的初始化前提。

### 工具对比总结

| 工具 | 适用阶段 | 本题耗时 | 优点 | 缺点 |
|------|----------|----------|------|------|
| 直接阅读 `server.py` | 建模 | 分钟级 | 立刻看出 seed 异或与状态初始化方式 | 需要手动理解算法前提 |
| Python 本地验证 | 验证 exploit | 秒级 | 能快速确认全零状态导致全 0 输出 | 需要自己补一段验证代码 |
| 远端自动交互脚本 | 获取 flag | 秒级 | 可复现、便于归档 | 依赖远端服务在线 |

### 推荐流程

**推荐流程**：先读源码确认 `xoroshiro128+` 的内部状态来源 -> 检查是否允许非法全零状态 -> 构造能让异或后状态归零的输入 -> 本地验证 NPC 全部出 Rock -> 远端选择 Paper 拿 flag。

### 工具 A（推荐首选）
- **安装**：Python 3
- **详细步骤**：
  1. 读取附件中的固定异或常量
  2. 直接把该常量转换成十进制输入值
  3. 本地模拟 `xoroshiro128+` 并验证输出恒为 0
  4. 连接远端发送种子和手势 `2`
- **优势**：最直接、最稳定，不依赖复杂数学恢复

### 工具 B（可选）
- **安装**：`nc` 或任意 TCP 客户端
- **详细步骤**：
  1. 手动连接 `nc 133.88.122.244 32212`
  2. 输入十进制种子 `24197857200151252728969465429440056815`
  3. 输入手势 `2`
  4. 读取服务端返回 flag
- **优势**：最贴近题目原始交互，适合快速手动复现
