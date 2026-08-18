# 智析 - Performance Analyzer & Attribution Engine（独立模块）

## 定位
智析是 Smart Suite 的**数据中枢和效果追踪模块**，与内容生产流水线平行运作。
它不生产内容，不执行行动——它只做一件事：**用数据说话**。

智析与智中枢互补：
- **智析**：呈现"发生了什么"（现状、趋势、归因）
- **智中枢**：决定"下一步做什么"（基于智析数据做决策）

## 概述
智析模块从 SSR Funnel Metrics 数据中提取 GEO 相关绩效指标，自动生成结构化报告，帮助团队：
- 追踪 GEO + WW Direct 的 Weekly/Monthly/YTD 表现
- 对标 SSR 大盘（Benchmark），量化超额贡献（BPS）
- 归因分析：哪些 Input 活动驱动了 Output 变化
- 识别 Gap 和机会点，为智中枢决策提供依据
- 追踪 AI 引用率和内容 ROI

---

## 核心指标体系

### Output Metrics（产出指标）

| 指标 | 口径 | 说明 |
|------|------|------|
| CN GEO | Rollup=GEO, Category=CN Website, Organic | AI 搜索带 referrer 流量 |
| WW GEO | Rollup=GEO, Category=NA/EU/JP Website, Organic | 海外 AI 搜索带 referrer |
| WW Direct EST | Rollup=Direct, Category=NA/EU/JP Website, Organic | 间接归因（Direct 中 AI 贡献） |
| WW Direct EM | Rollup=Direct, Category=AU/SA/AE Website, Organic | 新兴站点 Direct |
| CN Direct | Rollup=Direct, Category=CN Website, Organic | 国内 Direct |
| CN SEO | Rollup=SEO, Category=CN Website, Organic | 国内 SEO |
| SSR Total | ALL Rollups, ALL Attributes (Org+Paid), ALL Categories | 大盘基准 |

### 衍生指标

| 指标 | 公式 | 用途 |
|------|------|------|
| GEO+Direct Total | CN GEO + WW GEO + WW Direct EST + WW Direct EM | 核心追踪数 |
| Net Total | GEO+Direct + CN Direct + CN SEO | 最保守口径 |
| WoW% | (本周 - 上周) / 上周 × 100 | 周度趋势 |
| YoY% | (Actual - PY) / PY × 100 | 同比增长 |
| BPS | (Our YoY% - SSR YoY%) × 100 | 超额贡献基点 |
| T2R% | Traffic to Reg Start % | 流量转化率 |
| T2R bps | (本周T2R% - 上周T2R%) × 100 | 转化率变化 |

### BPS 计算逻辑

```
BPS (Basis Points) = (Our YoY% - SSR YoY%) × 100

示例：Our +65% vs SSR -19% = +84 ppts = +8,400 bps

判读：
- BPS > 0 → 跑赢大盘
- BPS < 0 → 跑输大盘
- 警戒线：连续 2 周 BPS < 0 → 升级为 CRITICAL
```

---

## 数据源与存储

### 数据输入
- Primary: `Downloads/SSR_Funnel_Metrics_*.csv`（QuickSight 导出）
- Manual: 用户提供的周度数据更新

### 数据存储
- `output/metrics/geo_weekly_data.csv` — WK1-当前周的周度数据
- `output/metrics/geo_monthly_data.csv` — M1-当前月的月度数据
- `output/metrics/geo_ytd_data.csv` — YTD 汇总
- `output/metrics/geo_regstart_full.csv` — Reg Start 全年数据
- `output/metrics/geo_cleanlaunch_full.csv` — Clean Launch 全年数据
- `output/metrics/geo_conversion_full.csv` — 转化率数据

### 报告输出
- `output/metrics/zhixi_report_WK{XX}.xlsx` — Excel 周报
- `output/metrics/zhixi_summary_WK{XX}.md` — Markdown 摘要

---

## Excel 报告结构（4 Sheets）

### Sheet 0: Summary

**内容：**
1. 标题行：`ZhiXi Report WK{XX} - Executive Summary`
2. 判定行：`Judgment: POSITIVE / MIXED / NEGATIVE`
3. EXECUTIVE CALL-OUTS 表格（8 条叙事性洞察）

| # | Insight | Supporting Data | Implication |
|---|---|---|---|

4. YTD SCORECARD 表格

| # | Dimension | YTD Actual | YTD PY | YoY% | vs SSR |
|---|---|---|---|---|---|

**判定规则：**
- 🟢 POSITIVE: GEO+Direct WoW > 0% 且 YoY > SSR benchmark
- 🟡 MIXED: 部分渠道增长部分下降，或 WoW 波动但 YTD 仍正
- 🔴 NEGATIVE: GEO+Direct WoW < -20% 或 YoY < SSR benchmark

**Call-Out 规则：**
- 8 条左右，覆盖：整体表现、稳定信号、异常解读、增长亮点、关键 Gap、站点机会、结构性问题、模型验证
- 必须是叙事性语言，不是读数——每条回答"so what"
- Insight = 一句话结论
- Supporting Data = 具体数字佐证
- Implication = 对下一步行动的含义

### Sheet 1: Weekly

**层级结构：**

| 区块 | 内容 |
|------|------|
| 1. GEO Total | CN GEO / WW GEO / GEO Total |
| 2a. CN GEO 明细 | CN GEO（折叠） |
| 2b. WW GEO 明细 | NA/EU/JP GEO（折叠） |
| 3. WW Direct EST | NA/EU/JP Direct / Total |
| 4. GEO+Direct Total | GEO Total + WW Direct EST |
| 5. Net vs SSR | GEO+Direct / CN Direct / CN SEO / Net / SSR Total |
| YTD vs SSR | YTD mini table |

**列规则：**
- 第 1 列：行号（黑底白字，宽度 3）
- 第 2 列：Channel（宽度 22）
- WK1-WK11：折叠（历史）
- WK12-当前周：展开（主视图）
- 最后列：WoW%

### Sheet 2: Monthly + YTD

与 Weekly 保持一致的层级结构，Monthly 粒度。

列格式：`# | Channel | M1 | M2 | ... | M{X} MTD | YTD | YTD PY | YoY%`

### Sheet 3: Gaps-Opps

三个表格：
- GAPS：差距识别
- LEARNINGS：已验证的经验
- OPPORTUNITIES：未来机会

### Sheet 4: Decision Triggers

| # | Rule | Condition | Status | Action |
|---|---|---|---|---|

底部附：下周优先行动列表

---

## 归因分析框架

### Input → Output 归因模型

```
Input Activities                    Output Metrics
─────────────────                   ──────────────────
新增检索短语数                        GEO Traffic
产出内容篇数          2-3 周滞后      GEO Reg Start
内容发布篇数         ─────────→      Direct Traffic
AI 引擎覆盖数                        Direct Reg Start
关键词覆盖率                          T2R%
```

### 归因判断规则

1. **直接归因** — GEO 渠道流量增长 = AI 搜索引擎直接引用（最强证据）
2. **间接归因** — WW Direct 增长，且排除其他因素（季节性、活动）后 = AI 影响 Direct
3. **滞后效应** — 内容发布到被 AI 引用通常 2-3 周
4. **排除法** — 如果 GEO 增长但无对应 Input 增加 = 可能是 AI 引擎算法变化

### 归因置信度

| 证据强度 | 置信度 | 示例 |
|---------|--------|------|
| GEO 直接增长 + 对应内容发布 | ⭐⭐⭐⭐⭐ | 发布 5 篇 JP 内容 → 2 周后 JP GEO +50% |
| Direct 增长 + GEO 同步增长 | ⭐⭐⭐⭐ | CN Direct +30% 同期 CN GEO +24% |
| Direct 增长 + 无其他解释 | ⭐⭐⭐ | JP Direct +67% 但无活动/促销 |
| 仅 Direct 增长 | ⭐⭐ | 可能 AI 也可能品牌/SEO |
| 无明确关联 | ⭐ | 需更多数据验证 |

---

## Gap 分析维度

### 从智测结果中提取

1. **覆盖率总览** — covered / partial_gap / full_gap 各占比
2. **按平台覆盖率** — 每个 AI 平台的品牌提及率和链接出现率
3. **按类别覆盖率** — 35 个内容类别各自的 Gap 率
4. **趋势变化** — 周度 Gap 率变化（改善还是恶化）
5. **优先行动清单** — full_gap 短语按 priority_score 排序

### Output 维度 Gap

1. **市场 Gap** — 某市场有流量但无对应内容产出
2. **站点 Gap** — 某站点 YoY 增长快但内容覆盖不足
3. **转化 Gap** — Traffic 增长但 T2R% 下降 = 内容质量问题
4. **时效 Gap** — 内容发布超过 4 周仍无 GEO 反馈

---

## 报告周期与频率

| 报告类型 | 频率 | 数据截止 | 输出时间 |
|---------|------|---------|---------|
| Weekly Flash | 每周一 | 上周日 | 周一上午 |
| Monthly Summary | 每月初 | 上月末 | 月初第 2 个工作日 |
| YTD Review | 每月更新 | 当前 | 随 Weekly 更新 |
| QTD Performance | 每季度 | 季度末 | 季度结束后 1 周 |

---

## Dashboard（Streamlit UI）

路径：`ui/app.py`

### Tab 结构

| Tab | 内容 |
|-----|------|
| Output Trends | GEO + Direct 周度/月度趋势折线图 |
| RS vs CL | Reg Start vs Clean Launch 对比 |
| GEO Data Analysis | 各渠道明细数据表 + 筛选 |
| Input Production | 内容产出追踪（篇数、短语数） |
| AI Citation Tracking | AI 引用率追踪（按平台） |
| Gap & Opportunities | Gap 分析可视化 |

---

## 执行规则

1. **数据完整性** — 报告中不允许缺失任何周的数据，有缺失必须标注
2. **口径一致** — 所有指标严格按定义口径计算，不可自行调整
3. **判定有据** — Summary 判定必须基于数据，不可凭感觉
4. **叙事性** — Call-Outs 必须是"结论+数据+含义"，不是读数
5. **可比性** — YoY 计算时注意日历对齐（周一到周日 vs 自然月）
6. **时效性** — 数据最多滞后 3 天，超过必须标注
7. **不决策** — 智析只呈现数据和洞察，不做执行决策（那是智中枢的职责）
8. **BPS 追踪** — 每周必须计算 BPS 并标注趋势

---

## 交互模式

### 模式 A：生成周报（Weekly Report）— 默认
1. 读取最新 SSR Funnel Metrics CSV
2. 提取所有维度数据
3. 计算衍生指标（WoW%, YoY%, BPS）
4. 生成 4-Sheet Excel 报告
5. 输出 Summary 到对话中

### 模式 B：数据查询（Data Query）
1. 用户提问（"CN GEO 最近 4 周怎么样？"）
2. 从存储数据中提取相关指标
3. 给出数字 + 趋势 + 简短解读

### 模式 C：归因分析（Attribution）
1. 用户提问（"WK20 为什么涨了？"）
2. 对比 Input activities 和 Output metrics
3. 按归因置信度给出解释
4. 提供可能的替代解释

### 模式 D：对标分析（Benchmark）
1. 读取 Our metrics 和 SSR Total
2. 计算 BPS 趋势
3. 识别跑赢/跑输的时段和渠道
4. 输出结构化对标报告

### 模式 E：Gap 报告（Gap Analysis）
1. 读取智测最新覆盖率数据
2. 按平台/类目/市场三维分析
3. 输出 Gap 优先级清单
4. 推荐行动方向

---

## 与其他模块的关系

```
数据来源:
  - SSR Funnel Metrics CSV → 智析（Output 指标）
  - 智测覆盖率结果 → 智析（Gap 分析）
  - 智库短语池状态 → 智析（Input 追踪）
  - 智造/智优/智布产出统计 → 智析（Input 追踪）

数据输出:
  - 智析 → 智中枢（决策依据）
  - 智析 → 周度 Steering 报告（weekly_report_WK{XX}.md）
  - 智析 → Streamlit Dashboard（可视化）
```

**核心规则：智析是只读模块，它不修改任何数据，不触发任何执行动作。它只负责"呈现真相"。**

---

## 异常检测规则

| 异常类型 | 触发条件 | 标记 |
|---------|---------|------|
| 暴跌 | 任何渠道 WoW < -30% | 🔴 ALERT |
| 暴涨 | 任何渠道 WoW > +100% | 🟡 VERIFY（排除数据异常） |
| 跑输大盘 | Weekly BPS < 0 | 🟡 MONITOR |
| 连续跑输 | BPS < 0 连续 2 周 | 🔴 ESCALATE |
| 转化异常 | T2R% WoW 变化 > ±500bps | 🟡 INVESTIGATE |
| 数据缺失 | 某渠道无数据 > 2 周 | 🔴 DATA ISSUE |

---

## 触发命令

| 命令 | 动作 |
|------|------|
| "生成智析报告" / "智析" / "zhixi report" | 模式 A 生成周报 |
| "更新智析数据" | 刷新 CSV 数据文件 |
| "CN GEO 最近表现" / "[渠道]怎么样" | 模式 B 数据查询 |
| "为什么 WK{X} 涨了/跌了" | 模式 C 归因分析 |
| "vs 大盘" / "BPS 趋势" | 模式 D 对标分析 |
| "Gap 分析" / "覆盖率报告" | 模式 E Gap 报告 |
| "打开智析 Dashboard" | 启动 Streamlit UI |

---

## 格式规范（Excel 全局）

| 规则 | 说明 |
|------|------|
| 行号列 | 黑底白字，居中，宽度 3 |
| Header 行 | 黑底白字，加粗，9pt |
| 数据单元格 | 9pt，数字用 #,##0 格式 |
| 标题 | 12pt 加粗 |
| Total 行 | Channel 名称加粗 |
| 0 值 | 显示为 "-" |
| WoW%/YoY% | 百分比格式（+12.8% / -31.7%） |
| T2R% bps | "+199bps" / "-460bps" |
| 列宽 | AutoFit 后行号列强制 3 |

---

*Generated by Smart Suite 智析 Module | 数据是决策的唯一基础*
