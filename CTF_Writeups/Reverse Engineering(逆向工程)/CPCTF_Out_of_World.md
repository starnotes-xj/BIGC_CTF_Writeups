# CPCTF - Out of World Writeup

## 题目信息
- **比赛**: CPCTF
- **题目**: Out of World
- **类别**: Reverse
- **难度**: 简单
- **附件/URL**: `chal-f7199d01c49d56bebaae2d98ff2b597c`
- **附件链接**: [下载附件](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/Out_of_World/chal-f7199d01c49d56bebaae2d98ff2b597c){download} · [仓库位置](https://github.com/starnotes-xj/BIGC_CTF_Writeups/tree/main/CTF_Writeups/files/Out_of_World){target="_blank"}
- **Flag格式**: `CPCTF{...}`
- **状态**: 已解

## Flag

```text
CPCTF{c4n_y0u_f1nd_3nv1r0nm3n7_v4r1abl35}
```

## 解题过程

### 1. 初始侦察/文件识别
- 题目只给了一个没有题意提示的 ELF 附件，先做最基础的文件识别：

```bash
file CTF_Writeups/files/Out_of_World/chal-f7199d01c49d56bebaae2d98ff2b597c
```

- 输出可以确认它是 `ELF 64-bit LSB pie executable, x86-64, stripped`。
- 这说明题目更像是入门二进制逆向：符号被剥离，但体积很小，适合直接进 Ghidra 看伪代码。
- 题目描述“什么事都没发生，对吧……？”和提示“看起来正在调用 `getenv` 函数”也说明关键点大概率在环境变量，而不是传统输入校验。

### 2. 关键突破点一
- 这题**完全可以用 Ghidra 做**，而且很适合用 Ghidra。
- 把附件导入 Ghidra 并执行 Auto Analyze 后，在 `main` 附近很容易看到对 `getenv("CTF_SECRET_KEY")` 的调用。
- 顺着交叉引用往下看，可以定位到一个专门做校验的函数。Ghidra 反编译后逻辑非常直观，大意如下：

```c
int check(char *env) {
    if (env == NULL) return 0;
    if (strlen(env) != 0x18) return 0;

    for (size_t i = 0; i < 0x18; i++) {
        if ((env[i] ^ 0x23) != check_data[i]) {
            return 0;
        }
    }
    return 1;
}
```

- 也就是说，正确环境变量长度必须为 `24`，并且逐字节满足：

```text
env[i] ^ 0x23 == check_data[i]
```

- `.data` 段里对应的校验数组内容是：

```text
wkjp|jp|pvsfq|pf`qfw|hfz
```

- 逐字节异或 `0x23` 后就能直接还原出正确环境变量：

```text
THIS_IS_SUPER_SECRET_KEY
```

### 3. 关键突破点二
- 校验通过后，程序会继续进入另一个解码函数。
- Ghidra 里可以看到它从 `.data` 读取一段密文，然后用刚才的环境变量循环异或，再额外异或常量 `0x45`：

```c
for (size_t i = 0; i < 0x29; i++) {
    out[i] = enc_flag[i] ^ key[i % 0x18] ^ 0x45;
}
out[0x29] = '\0';
puts(out);
```

- 这题的关键不在动态调试，而在于把两个步骤串起来：
  1. 先从校验函数反推出 `getenv` 需要的 key
  2. 再把这个 key 带回解码函数，恢复最终字符串
- `.data` 中的密文如下：

```text
R]OB\wu.xOl0bEp1hs_"tx1n!ca%t;Il"b$auv%5{
```

- 用 `THIS_IS_SUPER_SECRET_KEY` 循环异或，再异或 `0x45` 后，即可解出完整 flag。

### 4. 获取 Flag
- 离线还原结果如下：

```text
CPCTF{c4n_y0u_f1nd_3nv1r0nm3n7_v4r1abl35}
```

## 攻击链/解题流程总结

```text
file 识别 ELF -> Ghidra 定位 getenv("CTF_SECRET_KEY") -> 从校验数组反推出正确环境变量 -> 继续分析解码函数 -> 用 key 循环异或恢复 flag
```

## 漏洞分析 / 机制分析

### 根因
- 程序把环境变量校验逻辑和 flag 解码逻辑都直接编译在二进制里。
- 虽然没有把 flag 明文写进字符串区，但校验数组、密文和异或常量都能通过静态分析直接恢复。
- 由于 `getenv` 的 key 名字也没有隐藏，分析者很容易判断“关键输入来自环境变量”，从而快速缩小搜索范围。

### 影响
- 不需要真正运行程序，也不需要设置环境变量，就可以纯静态还原正确 key 与最终 flag。
- 一旦校验逻辑和解码逻辑同时暴露在本地二进制中，攻击者就能离线复现整个流程。

### 修复建议（适用于漏洞类题目）
- 真实场景下不要把敏感解密逻辑与校验常量一起完整下发到客户端。
- 如果必须依赖环境变量，应避免在本地保存可直接逆推出明文 key 的固定数组。
- 对逆向题设计而言，如果想提升难度，可以增加多层变换、拆分常量或把关键数据生成逻辑放到动态流程中。

## 知识点
- `getenv` 调用在逆向中的定位思路
- 通过异或校验数组反推正确输入
- 使用循环 XOR 还原 `.data` 中的密文

## 使用的工具
- `file` — 判断附件类型与基本属性
- Ghidra — 反编译 `main`、校验函数和解码函数
- Python 3 — 离线复现环境变量恢复与 flag 解码

## 脚本归档
- Python：[`CPCTF_Out_of_World.py` :material-open-in-new:](https://github.com/starnotes-xj/BIGC_CTF_Writeups/blob/main/CTF_Writeups/scripts_python/CPCTF_Out_of_World.py){target="_blank"}
- 说明：脚本会读取归档后的附件，先恢复 `CTF_SECRET_KEY` 对应的正确环境变量，再离线解密输出 flag

## 命令行提取关键数据（无 GUI）

```bash
file CTF_Writeups/files/Out_of_World/chal-f7199d01c49d56bebaae2d98ff2b597c
python CTF_Writeups/scripts_python/CPCTF_Out_of_World.py
```

## 推荐工具与优化解题流程

> 这题的最佳路线就是围绕 `getenv` 展开静态分析，Ghidra 非常适合快速看清校验与解码两个函数之间的关系。

### 工具对比总结

| 工具 | 适用阶段 | 本题耗时 | 优点 | 缺点 |
|------|----------|----------|------|------|
| Ghidra | 主流程逆向 | 分钟级 | 伪代码直观，适合追 `getenv` 交叉引用 | 需要 GUI |
| `file` | 初始识别 | 秒级 | 快速确认是 ELF reverse 题 | 不能直接还原逻辑 |
| Python 脚本 | 自动化验证 | 秒级 | 可复现、适合归档 | 需要先理解算法 |

### 推荐流程

**推荐流程**：`file` 确认 ELF 类型 → Ghidra 搜索 `getenv` 与 `CTF_SECRET_KEY` → 反推出正确环境变量 → 继续看解码循环 → 用 Python 复现输出 flag。

### 工具 A（推荐首选）
- **安装**：下载 [Ghidra](https://ghidra-sre.org/)，需要本地 JDK 17+
- **详细步骤**：
  1. 新建 Project 并导入附件
  2. 选择 Auto Analyze
  3. 在 Strings 或 Decompiler 中定位 `CTF_SECRET_KEY`
  4. 顺着 `getenv` 调用进入校验函数
  5. 记录异或常量、校验数组和解码函数逻辑
- **优势**：这题函数很短，Ghidra 能直接把控制流还原成接近源码的伪代码，阅读成本很低

### 工具 B（可选）
- **安装**：Python 3
- **详细步骤**：
  1. 读取归档后的题目二进制
  2. 从固定偏移提取校验数组和密文数组
  3. 先恢复 `THIS_IS_SUPER_SECRET_KEY`
  4. 再按循环 XOR 规则解出 flag
- **优势**：不依赖 GUI，适合把分析结果固化为可复现脚本
