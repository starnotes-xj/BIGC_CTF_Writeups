# CPCTF - omikuji Writeup

## 题目信息

- **比赛**: CPCTF
- **题目**: omikuji
- **类别**: Reverse
- **难度**: 待补
- **附件/URL**: `omikuji`
- **附件链接**: [下载附件](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/omikuji/omikuji){download} · [仓库位置](https://github.com/starnotes-xj/BIGC_CTF_Writeups/tree/main/CTF_Writeups/files/omikuji){target="_blank"}
- **Flag格式**: `CPCTF{...}`
- **状态**: 已解

## 解题过程

先查看文件基础信息：

```bash
file CTF_Writeups/files/omikuji/omikuji
strings -a CTF_Writeups/files/omikuji/omikuji | grep -E "Flag|omikuji"
readelf -sW CTF_Writeups/files/omikuji/omikuji | grep -E "main|omikuji"
```

可以看到二进制中存在 `Flag: %s`，同时符号表没有被完全 strip，保留了 `main` 和 `omikuji` 这两个关键函数：

```text
main
_Z7omikujiNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE
```

继续反汇编 `main`，可以发现程序没有从外部读取输入，而是在 `main` 中构造了一个 `std::string`，随后将该字符串传给 `omikuji`：

```asm
lea     rax, [rbp - 0x60]
mov     esi, 0x43
mov     rdi, rax
call    std::string::operator+=(char)

lea     rax, [rbp - 0x60]
mov     esi, 0x50
mov     rdi, rax
call    std::string::operator+=(char)

...

lea     rdx, [rbp - 0x60]
lea     rax, [rbp - 0x40]
mov     rsi, rdx
mov     rdi, rax
call    std::string::string(std::string const&)

lea     rax, [rbp - 0x40]
mov     rdi, rax
call    omikuji(std::string)
```

其中每次 `mov esi, imm` 都是在向字符串追加一个字符。把这些立即数按 ASCII 转换即可得到完整 flag。

提取到的字符序列如下：

```text
0x43 0x50 0x43 0x54 0x46 0x7b 0x44 0x33
0x72 0x5f 0x34 0x31 0x37 0x33 0x5f 0x77
0x75 0x72 0x66 0x33 0x31 0x37 0x5f 0x6e
0x31 0x63 0x68 0x37 0x7d
```

转换后为：

```text
CPCTF{D3r_4173_wurf317_n1ch7}
```

## `omikuji` 函数逻辑

`omikuji` 会使用 `std::random_device` 初始化 `std::mt19937`，然后生成一个 `[0, 0x7fffffff]` 范围内的随机数。

关键逻辑如下：

```c
r = random();

if (r == 0x7ea) {
    printf("Flag: %s", flag);
} else {
    v = r % 100;

    if (v <= 9) {
        printf("...: %s", flag.substr(0, 10).c_str());
    } else if (v <= 24) {
        printf("...\nFlag: %s", flag.substr(0, 8).c_str());
    } else if (v <= 49) {
        printf("...\nFlag: %s", flag.substr(0, 6).c_str());
    } else if (v <= 84) {
        printf("...\nFlag: %s", flag.substr(0, 4).c_str());
    } else if (v <= 94) {
        printf("...\nFlag: %s", flag.substr(0, 2).c_str());
    } else {
        puts("...\nFlag:");
    }
}
```

也就是说，运行程序时大多数情况下只能看到 flag 的前缀；只有随机数正好等于 `0x7ea`，也就是十进制 `2026` 时，才会直接输出完整 flag。这个概率很低，因此不需要依赖爆破运行，直接静态分析 `main` 中构造的字符串即可。

## 自动提取脚本

也可以用脚本从 `main` 的反汇编中自动提取传给 `std::string::operator+=(char)` 的立即数：

```python
from elftools.elf.elffile import ELFFile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from capstone.x86 import X86_REG_ESI

with open("CTF_Writeups/files/omikuji/omikuji", "rb") as f:
    elf = ELFFile(f)
    text = elf.get_section_by_name(".text")
    symtab = elf.get_section_by_name(".symtab")
    main = next(s for s in symtab.iter_symbols() if s.name == "main")

    start = main["st_value"]
    size = main["st_size"]
    off = start - text["sh_addr"]
    code = text.data()[off:off + size]

md = Cs(CS_ARCH_X86, CS_MODE_64)
md.detail = True

chars = []
last = None

for ins in md.disasm(code, start):
    if (
        ins.mnemonic == "mov"
        and len(ins.operands) == 2
        and ins.operands[0].reg == X86_REG_ESI
        and ins.operands[1].type == 2
    ):
        last = ins.operands[1].imm
    elif ins.mnemonic == "call" and ins.op_str == "0x2210" and last is not None:
        chars.append(last)
        last = None

print("".join(chr(c) for c in chars))
```

输出：

```text
CPCTF{D3r_4173_wurf317_n1ch7}
```

## Flag

```text
CPCTF{D3r_4173_wurf317_n1ch7}
```
