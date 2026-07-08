---
inclusion: manual
---

# 智析 Performance Analyzer

## Overview
Full-channel GEO performance tracking and attribution analysis. Automatically generates Weekly/Monthly/YTD reports from SSR Funnel data, benchmarks against SSR total, tracks AI citation rates, and measures content ROI.

## Quick Start

| Command | Action |
|---------|--------|
| "生成智析报告 WK25" | Generate weekly Excel report |
| "更新智析数据" | Refresh all CSV data files from latest source |
| "打开智析 Dashboard" | Launch Streamlit dashboard |

## Data Sources
- Primary: `Downloads/SSR_Funnel_Metrics_*.csv` (QuickSight export)
- Stored: `output/metrics/geo_weekly_data.csv`, `geo_monthly_data.csv`, `geo_ytd_data.csv`

## Channel Definitions

| Channel | Filter |
|---------|--------|
| CN GEO | Rollup=GEO, Category=CN Website, Organic |
| WW GEO | Rollup=GEO, Category=NA/EU/JP Website, Organic |
| WW Direct | Rollup=Direct, Category=NA/EU/JP Website, Organic |
| SSR Total | All Rollups, All Categories (Organic + Paid) |

## Output Files
- `output/metrics/geo_weekly_data.csv` — WK1-25 weekly by channel
- `output/metrics/geo_monthly_data.csv` — M1-M5 + Jun MTD
- `output/metrics/geo_ytd_data.csv` — YTD summary
- `output/metrics/geo_regstart_full.csv` — Reg Start full year
- `output/metrics/geo_cleanlaunch_full.csv` — Clean Launch full year
- `output/metrics/geo_conversion_full.csv` — Conversion rates
- `output/metrics/zhixi_report_WK{XX}.xlsx` — Excel report

## Key Metrics (Latest)
- YTD Total (GEO+Direct): 39,166 vs PY 23,757 = **+65% YoY**
- SSR Total YTD: 237,627 vs PY 292,315 = **-19% YoY**
- vs SSR Benchmark: **+84 ppts = +8,400 bps**
- CN GEO YTD: 753 (+386% YoY)
- WW Direct YTD: 37,952 (+63% YoY)

## BPS Calculation Logic

BPS (Basis Points) formula: `(Our YoY% - SSR YoY%) × 100`

### Monthly BPS Trend (2025)
| Month | Our YoY | SSR YoY | Diff (ppts) | BPS |
|-------|---------|---------|-------------|-----|
| M1 (Jan) | +177% | +21% | +156 | +15,632 |
| M2 (Feb) | -20% | -58% | +38 | +3,834 |
| M3 (Mar) | +73% | -26% | +99 | +9,907 |
| M4 (Apr) | +72% | -18% | +89 | +8,922 |
| M5 (May) | +99% | -13% | +112 | +11,156 |
| M6 (Jun MTD) | +37% | -7% | +44 | +4,372 |
| **YTD** | **+65%** | **-19%** | **+84** | **+8,400** |

### Interpretation
- Consistently outperforming SSR benchmark every month
- Largest outperformance in M1 (+15,632 bps) and M5 (+11,156 bps)
- Jun MTD shows +4,372 bps — still strong but normalizing as SSR recovers
- WK25 showed first negative week (-2,903 bps) due to PY comp effect

### Weekly BPS (Recent)
| Week | Our YoY | SSR YoY | BPS |
|------|---------|---------|-----|
| WK20 | +83% | -14% | +9,740 |
| WK21 | +110% | -14% | +12,403 |
| WK22 | +138% | -1% | +13,894 |
| WK23 | +267% | +8% | +25,942 |
| WK24 | +75% | 0% | +7,455 |
| WK25 | -48% | -19% | -2,903 |

## Dashboard
Streamlit app at `ui/app.py` — includes Output Trends, RS vs CL, GEO Data Analysis, Input Production, AI Citation Tracking, Gap & Opportunities tabs.
