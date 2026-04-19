# CPCTF - jail Writeup

## 题目信息
- **比赛**: CPCTF
- **题目**: jail
- **类别**: Shell / Misc
- **难度**: 简单
- **附件/URL**: `Dockerfile` · `jail.py`
- **附件链接**: [下载 Dockerfile](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/jail/Dockerfile){download} · [下载 jail.py](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/jail/jail.py){download} · [仓库位置](https://github.com/starnotes-xj/BIGC_CTF_Writeups/tree/main/CTF_Writeups/files/jail){target="_blank"}
- **Flag格式**: `CPCTF{...}`
- **状态**: 已解

## Flag

```text
CPCTF{Y0ur3_4_7ru3_CPCTF_l0v3r}
```

## 解题过程

### 1. 初始侦察/文件识别
- 这题一共给了两个关键文件：`Dockerfile` 和 `jail.py`。
- `Dockerfile` 说明服务会创建用户 `cpctf-jail`，登录 shell 实际被替换为 `/usr/local/bin/jailsh`，而这个脚本只会执行：

```bash
exec /usr/bin/python3 /home/cpctf-jail/jail.py
```

- 同时，真正的 flag 放在只读目录 `/flag/flag.txt`：

```dockerfile
RUN mkdir -p /flag && \
    echo "CPCTF{REDACTED}" > /flag/flag.txt && \
    chown -R root:root /flag && \
    chmod 555 /flag && \
    chmod 444 /flag/flag.txt
```

- 所以题目的本质不是普通 SSH 登录，而是**登录后立刻进入一个长度和字符集都被严重限制的 bash jail**。

### 2. 关键突破点一：过滤的是“输入字符”，不是 shell 展开后的结果
- `jail.py` 的逻辑非常短：

```python
ALLOWED = set("cpctf" + string.punctuation)
LEN_LIMIT = 2 + 0 + 2 + 6
data = input("> ").strip()
if set(data) <= ALLOWED and len(data) <= LEN_LIMIT:
    subprocess.run(["/bin/bash", "-c", data], timeout=1)
```

- 这里有两个关键约束：
  - 只允许输入 `c p t f` 这几个字母和各种标点符号
  - 总长度不能超过 `10`

- 但真正危险的地方在于：程序把通过校验的字符串直接交给了

```python
["/bin/bash", "-c", data]
```

- 也就是说，题目过滤的只是**原始输入字符**，并没有阻止 bash 后续进行：
  - 参数展开
  - 通配符展开（globbing）
  - 重定向

- 这就给了我们一条思路：**输入里不直接写出危险命令，而是让 bash 在执行阶段把它展开出来。**

### 3. 关键突破点二：利用 `$_` 和 `/f*/*` 压缩成 8 字符 payload
- Bash 的特殊参数 `_` 在 shell 启动时会被设为当前 shell 的绝对路径。
- 因为本题本来就是 `/bin/bash -c data`，所以 `$_` 会展开成 `/bin/bash`。

- 接下来只差把 `/flag/flag.txt` 喂给这个新启动的 bash。
- 题目长度非常紧，不能老老实实写完整路径，但可以利用通配符把路径压缩成：

```text
/f*/*
```

- 这个模式会唯一匹配到：

```text
/flag/flag.txt
```

- 于是最终 payload 可以写成：

```text
$_</f*/*
```

- 它同时满足本题全部限制：
  - 长度只有 `8`
  - 只使用了 `$`、`_`、`<`、`/`、`*`、`f` 这些允许字符

- 执行效果等价于：

```bash
/bin/bash </flag/flag.txt
```

### 4. 获取 Flag
- 子 `bash` 会把 `/flag/flag.txt` 当作 shell 脚本读取。
- 但 flag 文件第一行通常是：

```text
CPCTF{...}
```

- 这并不是合法命令，因此 bash 会报错并把整行内容原样带到错误信息里，典型形式如下：

```text
/bin/bash: line 1: CPCTF{...}: command not found
```

- 也就是说，**虽然我们没有直接 `cat /flag/flag.txt`，但仍然通过 bash 对脚本行的报错回显把 flag 泄露出来了。**
- 实际得到的 flag 为：

```text
CPCTF{Y0ur3_4_7ru3_CPCTF_l0v3r}
```

## 攻击链/解题流程总结

```text
阅读 jail.py -> 发现输入虽有字符集和长度限制，但仍被送入 /bin/bash -c -> 利用 $_ 展开成 /bin/bash -> 利用 /f*/* 唯一匹配 /flag/flag.txt -> 构造 $_</f*/* -> 子 bash 把 flag 当脚本执行并在报错中回显 flag
```

## 漏洞分析 / 机制分析

### 根因
- 题目把“字符白名单”误当成了“命令白名单”。
- `subprocess.run(["/bin/bash", "-c", data])` 仍然会触发完整的 shell 语义，而不是执行一个受限 DSL。
- 过滤没有考虑：
  - Bash 特殊参数，如 `$_`
  - 通配符路径匹配，如 `/f*/*`
  - 输入重定向，如 `<file`

### 影响
- 攻击者无需输入 `cat`、`bash`、`flag.txt` 这些被禁止的字母。
- 只靠 shell 自带展开机制，就能在 10 字符内构造一个可执行 payload。
- 最终效果是直接读取敏感文件内容，并通过错误回显把 flag 泄露给攻击者。

### 修复建议（适用于漏洞类题目）
- 不要把用户输入交给 `bash -c`。
- 如果确实需要执行固定能力，应该：
  - 明确实现一套自己的命令解析
  - 或者将输入映射到预定义操作，而不是交给 shell
- 如果只是想做单一功能验证，优先直接在 Python 中处理，不要引入 shell 展开语义。
- 即使保留 shell，也必须额外禁用或严格处理：
  - 参数展开
  - glob 展开
  - 重定向

## 知识点
- Bash 特殊参数 `$_`
- Shell glob 路径压缩技巧
- 输入白名单不等于执行结果白名单
- 受限字符集下的命令构造

## 使用的工具
- PowerShell — 阅读附件、整理利用链
- Python 3 — 快速检查 payload 长度与允许字符集合
- Bash 语义分析 — 推导 `$_`、重定向与 glob 的实际展开结果

## 脚本归档
- Python：待补，预期文件名 `CPCTF_jail.py`
- 说明：本题核心利用只需单条 payload；如后续补充远端连接信息，可再归档自动化交互脚本

## 命令行提取关键数据（无 GUI）

```bash
# 检查 payload 是否满足题目限制
python -c "import string; s='$_</f*/*'; print(len(s)); print(set(s) <= set('cpctf' + string.punctuation))"

# 本题最终 payload
$_</f*/*
```

## 推荐工具与优化解题流程

> 这题真正的关键不是爆破，而是尽快识别“白名单输入 + bash -c”这一类典型 shell 逃逸面。

### 工具对比总结

| 工具 | 适用阶段 | 本题耗时 | 优点 | 缺点 |
|------|----------|----------|------|------|
| 直接阅读 `jail.py` | 漏洞定性 | 秒级 | 最快看出 `bash -c` 和长度限制 | 需要有附件 |
| 本地 Docker 复现 | 动态验证 | 分钟级 | 可以完整观察 payload 回显 | 需要本地起容器与 SSH |
| 远端交互验证 | 实战取 flag | 秒级到分钟级 | 能直接拿到真实 flag | 需要题目实例信息 |

### 推荐流程

**推荐流程**：先读 `jail.py` 确认是 `bash -c` -> 再找能在 10 字符内触发 shell 展开的最短 payload -> 锁定 `$_</f*/*` -> 最后到远端或本地容器里输入该 payload 获取 flag。

### 工具 A（推荐首选）
- **安装**：Python 3
- **详细步骤**：
  1. 阅读 `jail.py` 中的字符集和长度限制
  2. 手工验证候选 payload 是否满足 `len <= 10`
  3. 确认 payload 只包含允许字符
  4. 推导实际 bash 展开结果
- **优势**：完全离线，不依赖远端环境即可完成核心分析

### 工具 B（可选）
- **安装**：Docker + OpenSSH 客户端
- **详细步骤**：
  1. 用附件构建容器镜像
  2. 暴露 `22/tcp` 并启动服务
  3. 登录后输入 `$_</f*/*`
  4. 从错误输出中读取 flag
- **优势**：可以对 writeup 做完整动态复现
