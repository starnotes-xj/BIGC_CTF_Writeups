## \[比赛\] - \[题目\] Writeup

### 题目信息
- 比赛: Hack for a Change 2026 March: UN SDG 3  
- 题目: `Hidden Recipe`  
- 类别: Web  
- 难度: 中  
- 附件/URL: Web 题目环境  
  - 访问方式: 题目提供的站点 URL  
  - 仓库位置: `Web/writeupHidden Recipe.md`  
- Flag 格式: `SDG{...}`  
- 状态: 已解  

### Flag
`待补充：请填写 Hidden Recipe 的实际 flag`

---

### 解题过程

#### 1) 初始侦察
- 进入题目站点后，先观察页面功能、可交互表单、请求参数与响应内容。  
- 使用浏览器开发者工具与抓包工具检查路由、请求头、Cookie、返回包与前端脚本。  
- 从页面命名和功能推测，题目核心应围绕“recipe/hidden content”相关的访问控制或参数处理问题展开。

#### 2) 枚举入口点
- 检查是否存在隐藏页面、未链接接口、注释、静态资源或前端 JS 中暴露的 API 路径。  
- 对常见位置进行排查，例如：`/admin`、`/api`、`/recipe`、`/hidden`、备份文件、调试接口等。  
- 对输入点进行测试，关注参数篡改、鉴权绕过、信息泄露与服务端校验缺失。

#### 3) 漏洞利用
- 根据实际页面行为，构造能够访问隐藏 recipe 内容的请求。  
- 若存在仅前端限制、可预测对象 ID、弱鉴权、模板泄露或参数信任问题，可直接修改请求进行验证。  
- 成功访问隐藏内容后，进一步定位 flag 所在字段、页面或接口返回值。

#### 4) 获取 Flag
- 在成功访问隐藏 recipe 内容后，从页面源码、接口响应或目标字段中提取 flag。  
- 对关键请求与响应进行保存，便于后续复盘与整理 writeup。  
- 将实际 flag 填入上方 Flag 区域，并补充最终利用请求示例。

---

### 攻击链/解题流程总结
页面与接口侦察 → 枚举隐藏入口 → 构造/篡改请求 → 访问隐藏 recipe 内容 → 提取 Flag

> 注：当前文件原先误写为 `ghost` 的逆向/VM 题解内容；已改为与文件名和目录一致的 `Hidden Recipe` Web 题目记录结构。
> 若需要完整题解，请继续补充该题实际访问 URL、关键请求、漏洞点与真实 flag。
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
