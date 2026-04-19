## \[比赛\] - \[题目\] Writeup

### 题目信息
- 比赛: Hack for a Change 2026 March: UN SDG 3  
- 题目: `ghost`（自定义 VM 逆向）  
- 类别: Reverse / Pwn（Binary + VM）  
- 难度: 中  
- 附件/URL: `D:\BIGC_CTF_Writeups\CTF_Writeups\files\Prescription_Pad.zip`（内含 ELF x86_64 `ghost`）  
  - 附件链接: `D:\BIGC_CTF_Writeups\CTF_Writeups\files\Prescription_Pad.zip`  
  - 仓库位置: `D:\BIGC_CTF_Writeups\CTF_Writeups\files\Prescription_Pad.zip`  
- Flag 格式: `SDG{...}`  
- 状态: 已解  

### Flag
`SDG{c79f529e74a36bef787a15c2ec53fb6d}`

---

### 解题过程

#### 1) 初始侦察/文件识别
- 入口: 本地 `./ghost`  
- 命令: `file ghost`、`strings ghost`  
- 现象: 仅有 “Correct!” / “Wrong.”，无业务逻辑，怀疑自定义 VM。

#### 2) 关键突破点一
- `.text` 中发现按字节取 opcode → 跳表 `notrack jmp` 的分发器，确认栈式 VM。  
- 用 `pyelftools` 计算 vaddr→offset，dump 跳表与字节码（起始约 `0x4040`）。

#### 3) 关键突破点二
- 逆 handler 语义，得到指令集：  
  - 栈：`push` / `pop` / `dup`  
  - 算术/位：`add` / `sub` / `xor` / `mul` / `rol` / `and`  
  - 内存：`load idx` / `store idx`（单字节槽，初值 0x5a，参与链式校验）  
  - 输入：`push_input i`（取明文第 i 字节）  
  - 控制：`cmp` + `jeq` / `jne` / `jmp`  
  - 输出/结束：`print_correct` / `print_wrong` / `exit`
- 解码字节码：长度必须 37；每字符做位运算、乘法 mod 256、位旋转、nibble 拆分，并与状态槽累加耦合。

#### 4) 获取 Flag
- Python 求解脚本思路：  
  - 乘法 mod 256 直接暴力 0..255 反推  
  - `rol` 的逆为 `ror`  
  - 高/低 nibble 拆分后异或/与常量再合并  
  - 同步状态槽的累加/异或  
- 唯一解：`SDG{c79f529e74a36bef787a15c2ec53fb6d}`，输入即得 “Correct!”。

---

### 攻击链/解题流程总结
识别 VM 分发器 → dump 跳表与字节码 → 还原指令集 → 线性解码字节码 → 逆运算脚本求解 → Flag

---

### 漏洞分析 / 机制分析
- 根因: 核心校验在本地明文字节码 + 自定义 VM；反编译无效但可直接提取逆向。  
- 影响: 攻击者可复原指令语义，线性求解合法凭据，绕过表层混淆。

### 修复建议
- 将关键校验迁移到服务器端；或对本地逻辑做加密/自校验/反调试，避免明文字节码直读。

---

### 知识点
- 自定义栈式 VM 识别与指令集还原  
- ELF 段/节偏移（vaddr→file offset）  
- 字节码算术/位运算逆向（rol / 乘法 mod 256 / nibble 拆分）

### 使用的工具
- `pyelftools` — 段/节解析、offset 计算  
- `capstone` — 辅助反汇编 handler  
- Python — dump、解码、求解脚本

### 脚本归档
- `disasm_vm.py`（反汇编 VM 字节码）  
- `solve_flag.py`（逆向求解，含注释）  
- 若需 Go 版本，可命名 `ghost_vm_solver.go`（待补）

### 命令行提取关键数据（无 GUI）
```bash
python dump_vm.py      # dump 跳表/字节码
python disasm_vm.py    # 反汇编 VM 字节码
python solve_flag.py   # 求解 flag
```

### 推荐流程
Python + pyelftools → capstone 标注 handler → 自写字节码解码 → 逆运算求解 → Flag（约 30–60 分钟）

---

*状态: 已解；Flag 如上。*
