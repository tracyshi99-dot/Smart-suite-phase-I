---
inclusion: auto
---

# 智析 (ZhiXi) — Excel Report Specification

> 本文件定义智析 Excel 报告的固定格式、数据维度、Sheet 结构和生成规则。需求已稳定，不再变化。

---

## 触发条件

当用户说以下任一指令时，生成智析 Excel 报告：
- "生成智析报告"
- "智析"
- "zhixi report"
- "generate zhixi"

---

## 数据输入

**来源：** `{output_path}\metrics\` 目录下的 SSR Funnel Metrics CSV 文件

**必需数据维度（Reg Start + Traffic + T2R%）：**

| 维度 | Channel Rollup | Channel Category | 指标 |
|---|---|---|---|
| CN GEO | GEO | CN Website | Reg Start, Traffic, T2R% |
| NA GEO | GEO | NA Website | Reg Start, Traffic, T2R% |
| EU GEO | GEO | EU Website | Reg Start, Traffic, T2R% |
| JP GEO | GEO | JP Website | Reg Start, Traffic, T2R% |
| NA Direct | Direct | NA Website | Reg Start, Traffic, T2R% |
| EU Direct | Direct | EU Website | Reg Start, Traffic, T2R% |
| JP Direct | Direct | JP Website | Reg Start, Traffic, T2R% |
| CN Direct | Direct | CN Website | Reg Start |
| CN SEO | SEO | CN Website | Reg Start |
| SSR Total | ALL (Organic+Paid) | ALL | Reg Start (sum all rows) |

**时间范围：**
- Weekly: WK1 到当前周（完整，不能缺少任何周）
- Monthly: M1 到当前月 MTD
- YTD: Year-to-Date Actual vs PY

---

## 输出文件

**路径：** `{output_path}\metrics\zhixi_report_WK{XX}.xlsx`
**生成脚本：** `{output_path}\metrics\gen_zhixi_v6.ps1`（模板脚本，每周更新数据后运行）

---

## Excel 固定结构（4 个 Sheet）

---

### Sheet 0: Summary

**名称：** `Summary`

**内容：**

1. **标题行：** `ZhiXi Report WK{XX} - Executive Summary`
2. **判定行：** `Judgment: POSITIVE / MIXED / NEGATIVE` + 一句话总结
3. **EXECUTIVE CALL-OUTS 表格：**

| # | Insight | Supporting Data | Implication |
|---|---|---|---|

**Call-Out 规则：**
- 8 条左右，覆盖：整体表现、稳定信号、异常解读、增长亮点、关键 Gap、站点机会、结构性问题、模型验证
- **必须是叙事性语言**，不是读数。每条要回答"so what"
- Insight = 一句话结论（如"CN GEO has built a self-sustaining weekly base"）
- Supporting Data = 具体数字佐证
- Implication = 对下一步行动的含义

4. **YTD SCORECARD 表格：**

| # | Dimension | YTD Actual | YTD PY | YoY% | vs SSR |
|---|---|---|---|---|---|

包含：GEO Total / WW Direct EST / GEO+WW Direct / Net / SSR Total

**判定规则：**
- 🟢 POSITIVE: GEO+Direct WoW > 0% 且 YoY > SSR benchmark
- 🟡 MIXED: 部分渠道增长部分下降，或 WoW 波动但 YTD 仍正
- 🔴 NEGATIVE: GEO+Direct WoW < -20% 或 YoY < SSR benchmark

---

### Sheet 1: Weekly

**名称：** `Weekly`

**内容：** WK1 到当前周的完整数据，按以下层级结构排列：

| 区块 | 内容 | 展开/折叠 |
|---|---|---|
| 1. GEO Total (CN+WW) | CN GEO / WW GEO (NA+EU+JP) / GEO Total | 展开 |
| 2a. CN GEO 明细 | CN GEO | 折叠 (Excel Row Group) |
| 2b. WW GEO 明细 | NA GEO / EU GEO / JP GEO / WW GEO Total | 折叠 (Excel Row Group) |
| 3. WW Direct EST | NA Direct / EU Direct / JP Direct / WW Direct EST Total | 展开 |
| 4. GEO+Direct Total | GEO Total / WW Direct EST / GEO+Direct Total | 展开 |
| 5. Net vs SSR Benchmark | GEO+Direct / CN Direct (Organic) / CN SEO / Net Total / SSR Total (Org+Paid) | 展开 |
| YTD vs SSR | GEO Total / WW Direct EST / GEO+Direct / CN Direct / CN SEO / Net Total / SSR Total | 展开 |

**列规则：**
- 第 1 列：行号（黑底白字，居中，宽度 3）
- 第 2 列：Channel 名称（宽度 22）
- WK1-WK11：列分组折叠（历史）
- WK12-当前周：展开显示（最近10周主视图）
- 最后一列：WoW%（百分比格式）

**视图规则：**
- 最近 10 周为主视图（列可见）
- WK1-11 历史数据通过 Excel Column Group 折叠
- CN GEO 明细和 WW GEO 明细通过 Excel Row Group 折叠
- 0 值显示为 "-"

**区块间隔：** 每个区块之间空 1 行 + Sub 标题行 + Header 行

---

### Sheet 2: Monthly + YTD

**名称：** `Monthly + YTD`

**内容：** 与 Weekly 保持一致的层级结构，Monthly 粒度：

| 区块 | 内容 | 展开/折叠 |
|---|---|---|
| 1. GEO Total (CN+WW) | CN GEO / WW GEO (NA+EU+JP) / GEO Total + YTD/PY/YoY | 展开 |
| 2a. CN GEO 明细 | CN GEO + YTD | 折叠 (Excel Row Group) |
| 2b. WW GEO 明细 | NA GEO / EU GEO / JP GEO / WW GEO Total + YTD | 折叠 (Excel Row Group) |
| 3. WW Direct EST | NA/EU/JP Direct + WW Direct EST Total + YTD | 展开 |
| 4. GEO+Direct Total | GEO Total / WW Direct EST / GEO+Direct Total + YTD | 展开 |
| 5. Net vs SSR Benchmark | GEO+Direct / CN Direct / CN SEO / Net Total / SSR Total + YTD | 展开 |
| YTD vs SSR | 同 Weekly 的 YTD mini table | 展开 |

**列格式：**
| # | Channel | M1 | M2 | M3 | M4 | M5 MTD | YTD | YTD PY | YoY% |

**M5 MTD 计算：** 当月已完成周的 weekly 数据之和

**视图规则：**
- CN GEO 明细和 WW GEO 明细通过 Excel Row Group 折叠
- 所有月份列均可见（仅 5 列，无需折叠）

---

### Sheet 3: Gaps-Opps

**名称：** `Gaps-Opps`

**内容分三块：**

**GAPS 表格：**
| # | Gap | Impact | Data Point |
|---|---|---|---|

**LEARNINGS 表格：**
| # | Learning | Evidence |
|---|---|---|

**OPPORTUNITIES 表格：**
| # | Opportunity | Expected Impact | Priority |
|---|---|---|---|

**Priority 规则：** High / Medium / Low

---

### Sheet 4: Decision Triggers

**名称：** `Decision Triggers`

**内容：**

| # | Rule | Condition | Status | Action |
|---|---|---|---|---|

**Status 值：** TRIGGERED / NOT Triggered / POSITIVE / CONFIRMED

**底部附：** WK{XX+1} PRIORITY ACTIONS（带行号的行动列表）

---

## 格式规则（全局）

| 规则 | 说明 |
|---|---|
| 行号列 | 每个表格第 1 列为行号，黑底白字，居中，宽度 3 |
| Header 行 | 黑底白字，加粗，9pt |
| 数据单元格 | 9pt，数字用 #,##0 格式 |
| 标题 | 12pt 加粗 |
| 子标题 | 10pt 加粗 |
| Total 行 | Channel 名称加粗 |
| 0 值 | 显示为 "-" 而非 0 |
| WoW% | 百分比格式，如 "+12.8%" 或 "-31.7%" |
| YoY% | 百分比格式，同上 |
| T2R% WoW | 用 bps 格式，如 "+199bps" 或 "-460bps" |
| 列宽 | AutoFit 后行号列强制 3 |
| WK1-6 缺失数据 | Traffic/T2R% 如无数据显示 "-"；Reg Start 必须完整 |

---

## 数据口径

| 指标 | 口径 |
|---|---|
| GEO | Campaign Channel Rollup = "GEO", Organic, EST Total |
| Direct | Campaign Channel Rollup = "Direct", Organic, EST Total |
| CN Direct | Campaign Channel Rollup = "Direct", Channel Category = "CN Website", Organic |
| SEO CN | Campaign Channel Rollup = "SEO", Channel Category = "CN Website", Organic |
| SSR Total | ALL Channel Rollups, ALL Channel Attributes (Organic + Paid), ALL Categories, sum all rows for each week |
| T2R% | Traffic to Reg Start % (from CSV "Traffic to Reg Start%" metric) |
| WoW% | (Current Week - Previous Week) / Previous Week * 100 |
| YoY% | (Actual - PY) / PY * 100 |
| bps | (Current T2R% - Previous T2R%) * 100 |

---

## 与智中枢的关系

智析 Excel 报告是智中枢决策引擎的输入。智中枢读取 Sheet 4 Decision Triggers 来生成 Weekly Plan。

流程：CSV 数据 → 智析 Excel → 智中枢决策 → 执行计划

---

## 生成流程

1. 获取最新 SSR Funnel Metrics CSV
2. 提取所有维度的 Weekly/Monthly/YTD 数据
3. 计算 SSR Total（sum all Reg Start rows per week）
4. 更新 `gen_zhixi_v6.ps1` 中的数据数组
5. 运行脚本生成 Excel
6. 输出到 `{output_path}\metrics\zhixi_report_WK{XX}.xlsx`

---

*Specification locked. Do not modify without explicit user approval.*
