# 历史参赛记录

> 用于记录参加过的比赛时间、比赛情况与遇到的问题。

## 模板文件
- [参赛记录模板](competitions.template.md)

## 比赛列表
| 比赛名称 | 时间 | 平台/主办 | 参赛形式 | 队伍/成员 | 名次/成绩 | 题目/问题 | 复盘要点 | 相关附件/链接 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NovruzCTF 2026 | 2026-03-28 13:00 ～ 2026-03-29 13:00 | https://canyouhack.org/（QarabagTeam） | 团队；Jeopardy（Pwn/Web/逆向/密码学/取证等） | 幻方队（星记、yuyingqi、youfeng）；我也没有key（WANGliulan） | 队伍24名；个人18名 | 延迟导致flag无法获取 | 需准备欧洲低延迟VPS；公共费用313.80 | — |
| Hack For A Change 2026 March | 2026-03 | 待补 | 待补 | 待补 | 待补 | Patient Zero / Encrypted Audit Logs / GenomeRand | 裸 RSA、日志编码、LCG 状态恢复 | — |
| kashiCTF 2026 | 2026-04-03 12:00 ～ 2026-04-04 12:00 (UTC) | [kashictf.iitbhucybersec.in](https://kashictf.iitbhucybersec.in/)（IIT(BHU)CyberSec / Codefest） | 团队；Jeopardy | 待补 | 待补 | — | — | [CTFtime](https://ctftime.org/event/3150/) |
| CPCTF | 2026-04-17 11:00 UTC ～ 2026-04-19 11:00 UTC | [cpctf.space](https://cpctf.space/)（traP） | 个人；Jeopardy（Online） | 待补 | 待补 | Bitwise Scrumble / Dualcast / Anomaly 2 / Ultra Janken Tournament / Very Exciting / Janken Master / hidden / L0v3 PDF / killionaire / Sign up for traP | 入门字符串检索题、常规密码题、PRNG 初始化题、PDF 杂项题、PPC 与业务逻辑型 Pwn 并存，先按题型分流更高效 | [CTFtime](https://ctftime.org/event/3077/) |
| MetaCTF | 待补 | 待补 | 待补 | 待补 | 待补 | Physics Notes（Crypto / 文本隐写） / pwnMe（Pwn / 格式化字符串） / Teaching Bricks（Pwn / Ret2win） | 文本首尾字符提取；格式化字符串任意读写；识别 win 地址泄露并完成 ret2win | — |
| UMassCTF 2026 | 待补 | 待补 | 待补 | 待补 | 待补 | The Accursed Lego Bin（Crypto / RSA） | 裸 RSA + 可逆随机置换 | — |
| VishwaCTF 2026 | 待补 | 待补 | 待补 | 待补 | 待补 | — | — | — |
| putcCTF | 待补 | [ctf.putcyberdays.pl/challenges](https://ctf.putcyberdays.pl/challenges) | 待补 | 待补 | 待补 | Exercise（Crypto / RSA） / 文件里面有什么（Crypto / Stego） | 低指数提升法复现；多层隐写链路还原 | [CTFtime](https://ctftime.org/event/3202/) |

## 比赛详情
### NovruzCTF 2026
- **时间**：2026-03-28 13:00 ～ 2026-03-29 13:00
- **平台/主办**：https://canyouhack.org/（QarabagTeam）
- **参赛形式**：团队；Jeopardy（Pwn/Web/逆向/密码学/取证等）
- **队伍/成员**：幻方队（星记、yuyingqi、youfeng）；我也没有key（WANGliulan）
#### 名次/成绩
| 类型 | 名次 | 备注 |
| --- | --- | --- |
| 队伍（幻方队） | 24 | — |
| 个人（星记） | 18 | — |
| 个人（WANGliulan） | 183 | — |
| 队伍（我也没有key） | 148 | — |

- **题目/问题**：
  - 有题目因延迟无法获得flag（脚本正确但物理距离过远）
- **复盘要点**：
  - 需要准备欧洲低延迟VPS
- **公共费用**：
  - 313.80
- **相关附件/链接**：
  - —

### kashiCTF 2026
- **时间**：2026-04-03 12:00 ～ 2026-04-04 12:00 (UTC)
- **平台/主办**：[kashictf.iitbhucybersec.in](https://kashictf.iitbhucybersec.in/)（IIT(BHU)CyberSec / Codefest）
- **参赛形式**：团队；Jeopardy（Open）
- **队伍/成员**：待补
#### 名次/成绩
| 类型 | 名次 | 备注 |
| --- | --- | --- |
| 待补 | 待补 | — |

- **题目/问题**：
  - 待补
- **复盘要点**：
  - 待补
- **相关附件/链接**：
  - [CTFtime Event #3150](https://ctftime.org/event/3150/)

### CPCTF
- **时间**：2026-04-17 11:00 UTC ～ 2026-04-19 11:00 UTC
- **平台/主办**：[cpctf.space](https://cpctf.space/)（traP）
- **参赛形式**：个人；Jeopardy（Online）
- **队伍/成员**：待补
#### 名次/成绩
| 类型 | 名次 | 备注 |
| --- | --- | --- |
| 待补 | 待补 | — |

- **题目/问题**：
  - Bitwise Scrumble（Crypto / bitwise 真值表）
  - Dualcast（Crypto / 编码还原）
  - Anomaly 2（Crypto / 特殊 RSA 模数分解）
  - Ultra Janken Tournament（Crypto / 伪随机与博弈）
  - Very Exciting（Crypto / 数学恢复）
  - Janken Master（Crypto / xoroshiro128+ 全零状态）
  - hidden（Reverse / strings）
  - L0v3 PDF（Misc / PDF 隐写）
  - killionaire（Pwn / 负数下注逻辑漏洞）
  - Sign up for traP（PPC / 正则校验）
- **复盘要点**：
  - CPCTF 当前已归档题目横跨 Crypto、Reverse、Misc、Pwn 与 PPC，先按题型做工具分流更高效
  - Reverse 入门题应优先执行 `file` / `strings` 等低成本静态侦察，再决定是否进入反编译阶段
  - 面对 PDF 附件时应优先检查元数据、文本层与隐藏对象，而不是只盯图片页内容
  - 业务逻辑型 Pwn 题要先检查金额、次数、边界值等基础不变量是否被破坏
  - 看到 PRNG 提示时，也要先确认初始化是否满足算法前置条件，而不是直接进入状态恢复
- **相关附件/链接**：
  - [CTFtime Event #3077](https://ctftime.org/event/3077/)
  - [Official Platform](https://cpctf.space/)

### MetaCTF
- **时间**：待补
- **平台/主办**：待补
- **参赛形式**：待补
- **队伍/成员**：待补
#### 名次/成绩
| 类型 | 名次 | 备注 |
| --- | --- | --- |
| 待补 | 待补 | — |

- **题目/问题**：
  - Physics Notes（Crypto / Text Stego）
  - pwnMe（Pwn / Format String）
  - Teaching Bricks（Pwn / Ret2win）
- **复盘要点**：
  - 常规密码学自动识别失败时，应及时切换到文本结构分析
  - 对每一行的首字符、尾字符、固定列字符做快速检查
  - 格式化字符串题可优先检查 %p / %s / %n 三类能力：泄露、读、写
  - 面对无 banner 的服务题时，应主动发送最小输入探测交互逻辑
  - 已知 win 地址时，优先枚举偏移完成 ret2win，而不是过早构造复杂 ROP
- **相关附件/链接**：
  - —

### Hack For A Change 2026 March
- **时间**：2026-03（待补具体日期）
- **平台/主办**：待补
- **参赛形式**：待补
- **队伍/成员**：待补
#### 名次/成绩
| 类型 | 名次 | 备注 |
| --- | --- | --- |
| 待补 | 待补 | — |

- **题目/问题**：
  - Patient Zero（Crypto / RSA）
  - Encrypted Audit Logs（Crypto / 编码恢复）
  - GenomeRand Clinical Randomization System（Crypto / LCG）
- **复盘要点**：
  - 同一比赛的 Crypto 题较集中，适合按“题型族”沉淀脚本
  - 需要统一比赛命名，避免 `Hack For A Change` / `Hack for a Change` 混写
- **相关附件/链接**：
  - —

### UMassCTF 2026
- **时间**：待补
- **平台/主办**：待补
- **参赛形式**：待补
- **队伍/成员**：待补
#### 名次/成绩
| 类型 | 名次 | 备注 |
| --- | --- | --- |
| 待补 | 待补 | — |

- **题目/问题**：
  - The Accursed Lego Bin（Crypto / RSA）
- **复盘要点**：
  - 识别“小明文 + 小指数 + 裸 RSA”导致整数幂泄露
  - 随机置乱如果种子可恢复，本质上仍然是可逆的
- **相关附件/链接**：
  - —

### VishwaCTF 2026
- **时间**：待补
- **平台/主办**：待补
- **参赛形式**：待补
- **队伍/成员**：待补
#### 名次/成绩
| 类型 | 名次 | 备注 |
| --- | --- | --- |
| 待补 | 待补 | — |

- **题目/问题**：
  - 待补
- **复盘要点**：
  - 待补
- **相关附件/链接**：
  - —

### putcCTF
- **时间**：待补
- **平台/主办**：[ctf.putcyberdays.pl/challenges](https://ctf.putcyberdays.pl/challenges)
- **参赛形式**：待补
- **队伍/成员**：待补
#### 名次/成绩
| 类型 | 名次 | 备注 |
| --- | --- | --- |
| 待补 | 待补 | — |

- **题目/问题**：
  - Exercise（Crypto / RSA）
  - 文件里面有什么（Crypto / Stego）
- **复盘要点**：
  - 通过 `m^e = c + k*n` 的低指数提升法恢复明文
  - 面对多层隐写链路时，按“容器结构 → 元数据 → 位平面 → 频域”顺序拆解更稳定
- **相关附件/链接**：
  - [CTFtime Event #3202](https://ctftime.org/event/3202/)
