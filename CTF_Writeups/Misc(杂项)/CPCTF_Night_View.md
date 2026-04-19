# CPCTF - Night View Writeup

## 题目信息
- **比赛**: CPCTF
- **题目**: Night View
- **类别**: OSINT / Misc
- **难度**: 待补
- **附件/URL**: `chal_55e58f3b2fb358e0733204a6acc7545150a321a5133281f89250094f28be5e82.jpg`
- **附件链接**: [下载附件](https://starnotes-xj.github.io/BIGC_CTF_Writeups/files/Night_View/chal_55e58f3b2fb358e0733204a6acc7545150a321a5133281f89250094f28be5e82.jpg){download} · [仓库位置](https://github.com/starnotes-xj/BIGC_CTF_Writeups/tree/main/CTF_Writeups/files/Night_View){target="_blank"}
- **Flag格式**: `CPCTF{(OpenStreetMapでのway id)}`
- **状态**: 未解

## Flag

```text
TBD
```

## 解题过程

### 1. 初始侦察/文件识别
- 题目给出一张东京夜景照片，要求定位拍摄建筑，并提交该建筑在 OpenStreetMap 上的 `way id`。
- 提示明确指出背景桥梁是彩虹桥，且拍摄点本身位于较高位置。
- 因此本题本质上不是直接读图取字，而是 **地标识别 + 城市天际线比对 + OSM 对象确认**。

### 2. 当前已验证线索
- 背景桥梁应为东京湾的 **彩虹桥（Rainbow Bridge）**。
- 画面视角来自高层室内窗口，候选区域大致落在 **丰洲 / 晴海 / 胜どき** 一带的高层建筑带。
- 已尝试若干丰洲方向候选，但目前都未命中，说明前景单塔与右侧楼群的精确对应关系还需要继续核对。

### 3. 当前卡点
- 左中前景单塔与右侧主楼群尚未完全锁定。
- 仅凭“彩虹桥 + 高层夜景”仍会得到多个相近候选，继续盲猜 `way id` 风险较高。
- 需要进一步确认拍摄点到底是住宅塔楼、酒店高层还是办公楼，并与周边楼群做角度校验。

### 4. 获取 Flag
- 暂未完成。
- 当前不再继续盲猜，先标记为待解，后续补充精确楼体识别与 OSM 验证结果。

## 攻击链/解题流程总结

```text
识别彩虹桥 -> 反推东京湾视角走廊 -> 比对前景单塔与右侧楼群 -> 锁定拍摄建筑 -> 在 OSM 查询正确 way id
```

## 漏洞分析 / 机制分析

### 根因
- 本题并非漏洞利用题，而是利用城市地标、夜景楼群分布和地图对象数据进行交叉定位的 OSINT 题。

### 影响
- 选手需要把“照片中的建筑物”与 OSM 中的具体建筑轮廓对象精确对应，才能拿到最终 flag。

### 修复建议（适用于漏洞类题目）
- 本题不适用。

## 知识点
- 彩虹桥与东京湾典型视角识别
- 东京湾高层楼群方位比对
- OpenStreetMap / Nominatim / Overpass 的 way 查询方法

## 使用的工具
- 图片人工观察 — 识别彩虹桥与楼群布局
- OpenStreetMap / Overpass Turbo — 查询候选建筑 `way id`
- Nominatim — 搜索候选建筑名与地理对象

## 脚本归档
- Go：待补（预期文件名：`CPCTF_Night_View.go`）
- Python：待补（预期文件名：`CPCTF_Night_View.py`）
- 说明：解题代码需包含详细注释
- 备注：当前未解，暂未归档脚本

## 命令行提取关键数据（无 GUI）

```bash
# 示例：锁定候选建筑后，用 Overpass 查询对应 way id
curl -s "https://overpass-api.de/api/interpreter" \
  --data-urlencode 'data=[out:json][timeout:25];way[building][name~"候选建筑名",i](35.62,139.74,35.67,139.80);out ids tags center;'
```

## 推荐工具与优化解题流程

> 参考 `CTF_TOOLS_EXTENSION_PLAN.md` 中的对应类别工具推荐。

### 工具对比总结

| 工具 | 适用阶段 | 本题耗时 | 优点 | 缺点 |
|------|----------|----------|------|------|
| 目视比对 | 初筛地标 | 待补 | 上手快 | 容易被相似楼群误导 |
| Nominatim | 建筑检索 | 待补 | 适合快速搜名称 | 结果可能先落到 POI 而非建筑轮廓 |
| Overpass Turbo | 最终确认 | 待补 | 能直接拿 `way id` | 需要先有较准确候选 |

### 推荐流程

**推荐流程**：先识别彩虹桥与视线方向 → 再锁定前景楼群 → 最后用 Nominatim / Overpass 确认 `way id`。

### 工具 A（推荐首选）
- **安装**：浏览器访问 OpenStreetMap / Overpass Turbo 即可
- **详细步骤**：
  1. 根据照片先缩小到候选区域
  2. 在地图上逐个核对高层楼群排列
  3. 锁定建筑后读取 `way id`
- **优势**：最终结果可直接映射到 flag

### 工具 B（可选）
- **安装**：浏览器访问 Nominatim 或使用 `curl`
- **详细步骤**：
  - 先搜楼名，再回到 OSM 主图点选建筑轮廓
- **优势**：适合从候选名称快速跳转到地图对象

## 未解/进行中说明（仅在未解时保留）
- 当前已验证内容：背景桥梁是彩虹桥；拍摄视角来自东京湾高层建筑；当前若干丰洲方向候选均未命中。
- 待补关键结论：左中前景单塔、右侧楼群的精确对应关系，以及最终拍摄建筑的 `way id`。
- 下一步建议：优先补做晴海 / 胜どき / 丰洲高层建筑的角度验证，再用 Overpass 对最终候选做对象级确认。