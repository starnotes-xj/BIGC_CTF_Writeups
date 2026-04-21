---
title: yafu 上手使用指南
---

# yafu 上手使用指南

这份文档给出一条可直接落地的流程：安装 `yafu`、分解整数 `N`、提取 `p/q`，再把结果交给 `RsaCtfTool` 完成 RSA 解密。

## 1. 安装

推荐直接使用官方仓库预编译包或自行编译：

- 项目地址：<https://github.com/bbuhrow/yafu>

安装完成后验证：

```bash
yafu "help"
```

## 2. 最小用法：分解一个整数

`yafu` 最常用入口是 `factor(<N>)`：

```bash
yafu "factor(5959)"
```

输出里会给出质因子（例如 `59` 和 `101`）。

## 3. RSA 场景的标准流程

当题目只给了 `n/e/c`，需要先分解 `n`：

### Step 1：用 yafu 分解 `n`

```bash
yafu "factor(<n>)"
```

记录输出中的两个质因子 `p`、`q`。

### Step 2：交给 RsaCtfTool 解密

```bash
RsaCtfTool \
  -p <p> \
  -q <q> \
  -e <e> \
  --decrypt <cipher_int>
```

## 4. 与仓库 writeup 的配合建议

- RSA 题里只要出现“需要分解整数 `n`”的步骤，优先跑 `yafu`
- 得到 `p/q` 后，再交给 `RsaCtfTool` 或自写脚本做私钥恢复与解密
- 若题目存在明显结构（如可直接代数分解），可先用结构法拿到因子，再用 `yafu` 做交叉验证

## 5. 常见命令速查

```bash
# 查看帮助
yafu "help"

# 分解整数 N
yafu "factor(<N>)"

# 示例：把结果写入文件（按终端重定向保存）
yafu "factor(<N>)" > yafu_factor.log
```
