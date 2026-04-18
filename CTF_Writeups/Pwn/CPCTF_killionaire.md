# CPCTF - killionaire Writeup

## 题目信息
- **比赛**: CPCTF
- **题目**: killionaire
- **类别**: Pwn
- **难度**: 简单
- **附件/URL**: `chal`、`chal.c`、`nc 133.88.122.244 32457`
- **附件链接**: [chal](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/killionaire/chal){download} · [chal.c](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/killionaire/chal.c){download} · [仓库位置](https://github.com/starnotes-xj/BIGC_CTF_Writeups/tree/main/CTF_Writeups/files/killionaire){target="_blank"}
- **Flag格式**: `CPCTF{...}`
- **状态**: 已解

## Flag

```text
CPCTF{n3g4t1v3_v41u3_1s_m0re_p0w3rfu1_th4n_p0s1tiv3_va1u3}
```

## 解题过程

### 1. 初始侦察/文件识别
- 附件同时给了二进制 `chal` 和源码 `chal.c`，这类题最省时间的做法就是先读源码。
- 核心逻辑非常短，本质上是一个 10 回合赌博小游戏：
  - 初始金币 `coins = 1`
  - 每轮输入下注金额 `bet`
  - 如果 `rand() % 2 == 0`，则“成功”并增加 `gain = (bet * (rand() % 301)) / 100`
  - 否则“失败”并执行 `coins -= bet`
  - 只要 `coins >= 1000` 就直接调用 `print_flag()`

- 题目的关键代码如下：

```c
if (bet > coins) {
  printf("Invalid bet.\n");
  continue;
}

if (rand() % 2 == 0) {
  int gain = (bet * (rand() % 301)) / 100;
  coins += gain;
  printf("Result: SUCCESS (Gain: %d)\n", gain);
} else {
  coins -= bet;
  printf("Result: FAILURE (Lost: %d)\n", bet);
}
```

- 这里立刻能看到一个非常危险的点：**程序只检查了 `bet > coins`，却完全没有限制 `bet >= 0`**。

### 2. 关键突破点一：负数下注会反转输赢语义
- 正常业务语义下，下注额应该是非负整数；但这里可以直接输入负数。
- 一旦 `bet` 为负数，失败分支：

```c
coins -= bet;
```

- 就会变成：

```text
coins = coins + abs(bet)
```

- 也就是说，本来应该“输钱”的分支，反而会给你加钱。
- 最直接的利用是首轮输入 `-999`：
  - 初始 `coins = 1`
  - 如果第一轮走到失败分支，则：

```text
coins = 1 - (-999) = 1000
```

  - 立刻满足 `coins >= 1000`，直接打印 flag。

- 这已经足够拿到 flag，但它还有 50% 概率首轮走到“成功”分支，所以还可以继续优化。

### 3. 关键突破点二：余额状态本身也坏掉了
- 题目提示说“实际上，你可以输入负数作为投注金额。此外，查询余额也存在一些问题。”  
  这句话对应的不是额外菜单，而是**`coins` 这个余额状态一旦进入负数，整个校验逻辑都会继续失真**。

- 注意程序唯一的下注校验是：

```c
if (bet > coins) invalid;
```

- 这意味着：
  - 当 `coins` 为正时，任何负数下注都合法
  - 当 `coins` 变成负数时，只要你下注一个**更负**的数，它依然合法

- 更离谱的是，成功分支里的“收益”公式：

```c
gain = (bet * k) / 100
```

  在 `bet < 0` 时通常也是负数，所以程序会出现：
  - 显示 `SUCCESS`
  - 但你的余额实际上更少了

- 这说明题目的“余额系统”已经完全不再维护正常业务不变量：  
  **负数下注不仅能合法进入逻辑，甚至会把成功/失败的经济含义彻底反过来。**

### 4. 单局高概率稳定打法
- 如果只在第一轮发 `-999`，理论上要看脸。
- 更稳的做法是：**每一轮看到当前金币 `coins` 后，都下注**

```text
bet = coins - 1000
```

- 为什么这个式子好用？
  - 它一定满足 `bet <= coins`，因此总能通过校验
  - 一旦本轮走到失败分支：

```text
new_coins = coins - bet
          = coins - (coins - 1000)
          = 1000
```

  - 也就是只要当前这一轮失败，就会被精确送到 1000 金币并直接出 flag

- 如果本轮反而进入成功分支，由于 `bet` 是负数，`gain` 大概率也是负数，金币会进一步下降；但这没有关系：
  - 下一轮仍然读取新的 `coins`
  - 再次发送 `bet = coins - 1000`
  - 继续等待一次失败即可

- 因此，这题其实不需要预测随机数。  
  **只要按这个策略打满 10 轮，拿不到 flag 的概率仅为 `1/2^10 = 1/1024`。**

### 5. 获取 Flag
- 我最开始用的是最小利用版本：首轮直接发 `-999`，然后多次重连，直到命中失败分支。
- 远端在一次命中时返回：

```text
Result: FAILURE (Lost: -999)
Flag: CPCTF{n3g4t1v3_v41u3_1s_m0re_p0w3rfu1_th4n_p0s1tiv3_va1u3}
```

- 后续整理脚本时，把策略升级成“每轮都发送 `coins - 1000`”的稳定版，写入了归档脚本，单次会话就有极高概率拿到 flag。

## 攻击链/解题流程总结

```text
阅读源码 -> 发现下注金额只做上界检查、未限制非负 -> 构造负数下注使失败分支变成加钱 -> 进一步利用余额状态失真，按每轮 bet = coins - 1000 的策略下注 -> 任意一轮失败即把 coins 精确推到 1000 -> 程序调用 print_flag 输出 flag
```

## 漏洞分析 / 机制分析

### 根因
- 业务输入校验不完整：只限制了 `bet <= coins`，没有限制下注必须是非负数。
- 余额更新逻辑直接对带符号整数做运算，没有维护“余额应始终为非负”的业务不变量。
- 因为 `bet` 可以是负数，导致：
  - 失败分支 `coins -= bet` 会变成加钱
  - 成功分支 `gain = (bet * k) / 100` 可能变成负收益

### 影响
- 攻击者可以在不控制随机数的前提下，利用负数下注把金币推高到出 flag 阈值。
- 由于余额进入负数后校验依旧允许“更负的下注”，攻击者可以在 10 回合内以极高概率稳定通关。
- 从真实业务系统角度看，这类问题本质上属于**金额/余额逻辑校验失效**，可能进一步演化为刷钱、绕过风控或状态污染。

### 修复建议（适用于漏洞类题目）
- 明确限制下注金额必须满足：

```c
if (bet < 0 || bet > coins) {
    printf("Invalid bet.\n");
    continue;
}
```

- 对余额状态增加业务约束，避免出现负数余额继续参与后续计算。
- 对“成功/失败”的金额更新逻辑做一致性设计与单元测试，至少覆盖：
  - `bet = 0`
  - `bet < 0`
  - `coins = 0`
  - 接近阈值 `coins = 999`

## 知识点
- 负数输入绕过业务校验
- 有符号整数参与金额运算时的逻辑漏洞
- 不依赖随机数预测的高概率策略构造

## 使用的工具
- PowerShell — 查看附件与整理源码
- Python 3 + pwntools — 编写自动化利用脚本并连接远端服务

## 脚本归档
- Python：[`CPCTF_killionaire.py` :material-open-in-new:](https://github.com/starnotes-xj/BIGC_CTF_Writeups/blob/main/CTF_Writeups/scripts_python/CPCTF_killionaire.py){target="_blank"}
- 说明：脚本会解析每轮显示的 `Coins`，自动发送 `bet = coins - 1000`，并在单次会话失败时自动重连重试

## 命令行提取关键数据（无 GUI）

```bash
# 直接运行自动化利用脚本
python CTF_Writeups/scripts_python/CPCTF_killionaire.py

# 或者手工验证最小利用思路（首轮赌一次失败）
python -c "from pwn import *; io=remote('133.88.122.244',32457); io.recvuntil(b'Bet: '); io.sendline(b'-999'); print(io.recvall(timeout=2).decode('latin-1', errors='ignore'))"
```

## 推荐工具与优化解题流程

> 这题虽然在分类上是 Pwn，但真正的关键不是内存破坏，而是先把源码中的业务逻辑漏洞看明白。

### 工具对比总结

| 工具 | 适用阶段 | 本题耗时 | 优点 | 缺点 |
|------|----------|----------|------|------|
| 直接阅读源码 | 漏洞定性 | 秒级 | 一眼看到负数下注漏洞 | 需要题目提供源码 |
| pwntools 自动化脚本 | 远端利用 | 秒级到分钟级 | 可自动读取余额并稳定重试 | 需要本地 Python 环境 |
| netcat | 手工验证 | 秒级 | 最轻量，适合快速试 `-999` | 不适合做稳定多轮策略 |

### 推荐流程

**推荐流程**：先读 `chal.c` 确认下注校验缺失 -> 手工试一次 `-999` 理解失败分支会加钱 -> 改成自动化脚本，每轮按 `bet = coins - 1000` 下注 -> 任意一轮失败即拿到 flag。

### 工具 A（推荐首选）
- **安装**：`pip install pwntools`
- **详细步骤**：
  1. 连接远端服务
  2. 读取每轮提示中的 `Coins: <value>`
  3. 计算 `bet = coins - 1000`
  4. 发送下注并检查是否出现 `Flag:`
  5. 如果单局 10 轮全都没失败，则自动重连
- **优势**：不需要预测随机数，只利用业务逻辑本身就能非常稳定地出 flag

### 工具 B（可选）
- **安装**：系统自带 `nc`
- **详细步骤**：
  1. `nc 133.88.122.244 32457`
  2. 第一轮手工输入 `-999`
  3. 若第一轮失败直接拿 flag；若没中则重连
- **优势**：几乎零准备成本，适合先快速确认漏洞方向
