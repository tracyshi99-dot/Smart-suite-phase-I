---
inclusion: manual
---

# Mario-GEO 数据映射规则

## 概述
每次从 Mario 处获得 SSR Funnel Metrics Sheet 1 数据后，按以下规则提取并汇总成 Sheet 2 格式。

## Sheet 2 结构

Sheet 2 分为三部分：
1. **Regstart** — 注册开始数据
2. **Clean Launch** — 清洁上线数据  
3. **Regstart to Clean Launch** — 转化率

每部分包含 Y2026 (Actual)、Y2025 (PY A2A)、YoY 三个区域。

## 列结构

| 列名 | 含义 | Sheet 1 对应列索引 |
|---|---|---|
| Jan (M1) | 1月累计 | Monthly 区域第1列 |
| Feb (M2) | 2月累计 | Monthly 区域第2列 |
| Mar (M3) | 3月累计 | Monthly 区域第3列 |
| Apr (M4) | 4月累计 | Monthly 区域第4列 |
| May (MTD) | 5月截至当周 | MTD 列 |
| Q1 | 一季度合计 | Quarterly 区域 Q1 列 |
| Q2 (QTD) | 二季度截至当周 | QTD 列 |
| YTD | 年初至今 | YTD 列 |

## 行映射

### Regstart 部分

| # | Sheet 2 标签 | Sheet 1 路径 (Metrics → Attr → Cat → Rollup) |
|---|---|---|
| 1 | GEO | Reg Start → Organic → (CN+NA+EU+JP Website) → GEO **求和** |
| 2 | CN Website | Reg Start → Organic → CN Website → GEO |
| 3 | NA Website | Reg Start → Organic → NA Website → GEO |
| 4 | EU Website | Reg Start → Organic → EU Website → GEO |
| 5 | JP Website | Reg Start → Organic → JP Website → GEO |
| 6 | WW Website Direct | Reg Start → Organic → (NA+EU+JP Website) → Direct **求和** |
| 7 | NA Website | Reg Start → Organic → NA Website → Direct |
| 8 | EU Website | Reg Start → Organic → EU Website → Direct |
| 9 | JP Website | Reg Start → Organic → JP Website → Direct |

### Clean Launch 部分

| # | Sheet 2 标签 | Sheet 1 路径 |
|---|---|---|
| 10 | GEO | Clean Launch → Organic → (CN+NA+EU+JP Website) → GEO **求和** |
| 11 | CN Website | Clean Launch → Organic → CN Website → GEO |
| 12 | NA Website | Clean Launch → Organic → NA Website → GEO |
| 13 | EU Website | Clean Launch → Organic → EU Website → GEO |
| 14 | JP Website | Clean Launch → Organic → JP Website → GEO |
| 15 | WW Website Direct | Clean Launch → Organic → (NA+EU+JP Website) → Direct **求和** |
| 16 | NA Website | Clean Launch → Organic → NA Website → Direct |
| 17 | EU Website | Clean Launch → Organic → EU Website → Direct |
| 18 | JP Website | Clean Launch → Organic → JP Website → Direct |

### 转化率部分

| # | Sheet 2 标签 | 计算方式 |
|---|---|---|
| 19 | GEO | Row 10 / Row 1 |
| 20 | CN Website | Row 11 / Row 2 |
| 21 | NA Website | Row 12 / Row 3 |
| 22 | EU Website | Row 13 / Row 4 |
| 23 | JP Website | Row 14 / Row 5 |
| 24 | WW Website Direct | Row 15 / Row 6 |
| 25 | NA Website | Row 16 / Row 7 |
| 26 | EU Website | Row 17 / Row 8 |
| 27 | JP Website | Row 18 / Row 9 |

## 计算规则

- **YoY** = (Actual - PY A2A) / PY A2A × 100%
- **转化率 BPS Change** = (当年转化率 - 去年转化率) × 10,000 基点
- 当 PY = 0 时，YoY 显示为空（.%）
- 当分母 = 0 时，转化率显示为空

## 数据验证示例 (2026 数据)

| 指标 | Jan | Feb | Mar | Apr | May(MTD) | YTD |
|---|---|---|---|---|---|---|
| GEO Total (Regstart) | 172 | 116 | 256 | 234 | 159 | 1,033 |
| WW Direct (Regstart) | 4,965 | 2,389 | 7,269 | 7,205 | 7,323 | 29,151 |
| GEO Total (Clean Launch) | 13 | 7 | 26 | 18 | 8 | 72 |
| WW Direct (Clean Launch) | 916 | 460 | 1,765 | 1,518 | 798 | 5,457 |

## UI 工具

独立 Streamlit 页面：`ui/mario_geo.py`
启动命令：`streamlit run ui/mario_geo.py`
也可以在主控制台 sidebar → Tools → Mario-GEO 访问。
