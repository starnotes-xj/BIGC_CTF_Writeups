# BIGC CTF Writeups - Claude Code 工作指南

## 项目概览

MkDocs Material 驱动的 CTF 解题记录站点。文档根目录为 `CTF_Writeups/`。

## Writeup 发布流程

解完题目 / 写完 writeup 后，**必须按顺序执行以下全部步骤**：

### 1. 放置 writeup 文件

根据题目类别放入对应目录，文件命名格式 `{比赛名}_{题目名}.md`（空格用下划线替代）：

| 类别 | 目录 |
|------|------|
| Web | `CTF_Writeups/Web/` |
| Crypto | `CTF_Writeups/Cryptography(密码学)/` |
| Reverse | `CTF_Writeups/Reverse Engineering(逆向工程)/` |
| Misc | `CTF_Writeups/Misc(杂项)/` |
| PPC | `CTF_Writeups/PPC/` |
| Pwn | `CTF_Writeups/Pwn/`（新类别则新建目录） |
| Forensics | `CTF_Writeups/Forensics(取证)/`（新类别则新建目录） |

### 2. 使用模板

所有 writeup **必须基于** `CTF_Writeups/WRITEUP_TEMPLATE.md` 模板生成。关键要求：
- 题目信息区域全部填写
- 附件链接格式：`[下载附件](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/{题目目录}/{附件名}){download} · [仓库位置](https://github.com/starnotes-xj/BIGC_CTF_Writeups/tree/main/CTF_Writeups/files/{题目目录}){target="_blank"}`
- 脚本归档链接指向 `scripts_go/` 或 `scripts_python/` 下的实际文件
- 已解题目必须填写完整 Flag

### 3. 维护导航入口

`mkdocs.yml` 的 `nav` 只保留顶层栏目入口，不再逐篇追加 writeup 或逐个追加比赛页。注意：
- 新增普通 writeup 时，**不要**修改 `mkdocs.yml`
- 新增全新类别时，先创建该类别 `index.md`，再只在 `mkdocs.yml` 中新增该类别入口（放在“比赛”之前）
- 新增全新比赛时，创建 `CTF_Writeups/events/{比赛名}/index.md`，并更新 `CTF_Writeups/events/index.md` 的比赛卡片列表
- 路径相对于 `docs_dir`（即 `CTF_Writeups/`）
- 含中文括号的目录名需用引号包裹并使用 Unicode 转义，参照已有顶层入口格式

### 4. 放置附件

题目附件放入 `CTF_Writeups/files/{题目名}/` 目录（题目名与附件目录名保持可识别对应即可，参照已有目录命名风格）。

### 5. 放置解题脚本

- Go 脚本 → `CTF_Writeups/scripts_go/{比赛名}_{题目名}.go`
- Python 脚本 → `CTF_Writeups/scripts_python/{比赛名}_{题目名}.py`
- 脚本必须包含详细注释
- 如果解题过程中产生了多个变体脚本（如 ghidra 版、r2 版），使用后缀区分：`{名称}_ghidra.go`

### 6. 更新比赛索引页

如果该比赛已有索引页（`CTF_Writeups/events/{比赛名}/index.md`），在对应类别表格中追加该题目行，格式参照已有条目：
```markdown
| [题目显示名](../../{类别目录}/{文件名}.md) | 难度 | :material-check-circle: 已解 |
```

如果是新比赛的第一道题，创建 `CTF_Writeups/events/{比赛名}/index.md` 索引页，参照 `NovruzCTF_2026/index.md` 格式。同时在 `CTF_Writeups/events/index.md` 中添加该比赛卡片。

### 7. 更新历史参赛记录（新比赛时）

新比赛首次出现时，在 `CTF_Writeups/history/competitions.md` 中：
- 比赛列表表格追加一行
- 比赛详情区追加详情块
- 时间、平台等信息从题目或用户提供的上下文中提取；未知字段标注"待补"

## 发布前校验清单

完成上述步骤后，逐项自检：

- [ ] writeup 文件在正确的类别目录中
- [ ] 分类索引页与比赛索引页已更新；如新增类别，`mkdocs.yml` 顶层 nav 已更新
- [ ] 附件已放入 `files/` 对应目录
- [ ] writeup 中的附件下载链接和仓库链接指向正确路径
- [ ] 解题脚本已放入 `scripts_go/` 和/或 `scripts_python/`
- [ ] writeup 中的脚本归档链接指向正确的 GitHub 路径
- [ ] 无死链（附件引用 vs 实际文件一致）

## 附件完整性校验

writeup 中引用的所有附件路径，必须在 `CTF_Writeups/files/` 下存在对应文件。如果附件由用户提供但尚未放入仓库，在 writeup 中标注"附件待上传"并提醒用户。

## Tags 一致性

writeup 中使用的 tags 应与项目已有标签体系一致。添加新 tag 前检查 `CTF_Writeups/tags.md` 和已有 writeup 中的 tag 使用情况，避免同义重复（如 `crypto` vs `cryptography`）。

## 注意事项

- 目录名中的中文括号是目录名的一部分（如 `Cryptography(密码学)`），不要擅自修改
- 比赛名中的特殊字符在文件名中保留原样（如 `HackForAChange2026March`）
- 未解/进行中的题目也要走完整流程，writeup 中保留"未解/进行中说明"部分
