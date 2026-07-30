---
inclusion: auto
---

# Smart Suite 流水线流程规则 — 短语验证闭环

## 核心原则

**所有检索短语进入智造之前，必须经过智测验证。没有验证过的短语不允许直接生产内容。**

---

## 完整流程

```
智库（产出短语）
  ↓ 所有短语
智测（逐条验证覆盖状态）
  ↓ 验证结果
智析（Gap 分析汇总展示）
  ↓ 指导行动
  ├── 完全 Gap → 智造（生产新内容）
  ├── 部分 Gap → 智优（优化现有内容）
  └── 已覆盖 → 无需行动（归档）
```

---

## 智测验证维度

### 按短语类型分类验证

| 短语类型 | 判定依据 | 验证内容 | Gap 标准 |
|---------|---------|---------|---------|
| **品牌类短语** | 含"亚马逊""全球开店""Amazon"等品牌词 | ① 官方品牌提及（"亚马逊全球开店""Amazon Global Selling"等）② 官网链接（含"amazon"的URL） | 缺任一 = Gap |
| **行业类短语** | 含"跨境电商""FBA""Listing"等行业词但无品牌词 | ① 官方提及（AI 回答中是否提到亚马逊相关信息） | 无官方提及 = Gap |

### 验证输出字段

每条短语验证后标记：
- `has_brand_mention`: 是否有品牌提及（TRUE/FALSE）
- `has_official_link`: 是否有官网链接（TRUE/FALSE）
- `gap_status`: 覆盖状态（covered / partial_gap / full_gap）
- `gap_type`: Gap 类型（none / no_link / no_mention / no_content）
- `platforms_tested`: 验证过的平台列表
- `verified_at`: 验证时间

### Gap 状态判定规则

```
IF 品牌类短语:
  IF has_brand_mention AND has_official_link → gap_status = "covered"
  IF has_brand_mention AND NOT has_official_link → gap_status = "partial_gap", gap_type = "no_link"
  IF NOT has_brand_mention AND has_official_link → gap_status = "partial_gap", gap_type = "no_mention"
  IF NOT has_brand_mention AND NOT has_official_link → gap_status = "full_gap", gap_type = "no_content"

IF 行业类短语:
  IF has_brand_mention → gap_status = "covered"
  IF NOT has_brand_mention → gap_status = "full_gap", gap_type = "no_mention"
```

---

## 验证后的行动路由

| Gap 状态 | 行动 | 目标模块 |
|---------|------|---------|
| `covered` | 无需行动，记录到智析 | 智析（已覆盖统计） |
| `partial_gap` (no_link) | 现有内容需补链接 | 智优（优化） |
| `partial_gap` (no_mention) | 现有内容需加强品牌露出 | 智优（优化） |
| `full_gap` (no_content) | 需要生产全新内容 | 智造（生产） |

---

## 智析的 Gap 分析维度

智析从智测结果中提取以下分析：

1. **覆盖率总览：** covered / partial / full_gap 各占比
2. **按平台覆盖率：** 每个 AI 平台的品牌提及率和链接出现率
3. **按类别覆盖率：** 35 个内容类别各自的 Gap 率
4. **趋势变化：** 周度 Gap 率变化（是在改善还是恶化）
5. **优先行动清单：** full_gap 短语按 priority_score 排序

---

## 各模块职责边界（严格执行）

| 模块 | 职责 | 不做什么 |
|------|------|---------|
| 智库 | 产出和管理检索短语 | 不判断 Gap，不生产内容 |
| 智测 | 验证短语的覆盖状态 | 不产出新短语，不优化内容 |
| 智预 | 推演未来可能的短语 | 推演结果必须经智测验证才能使用 |
| 智析 | 展示 Gap 分析和覆盖率数据 | 不执行行动，只提供决策依据 |
| 智造 | 为 full_gap 短语生产新内容 | 只接收经过智测验证有 Gap 的短语 |
| 智优 | 优化 partial_gap 对应的现有内容 | 不生产全新内容 |

---

## 禁止行为

1. ❌ 智库短语未经智测验证直接进入智造
2. ❌ 智预推演结果未经智测验证直接进入智库
3. ❌ 智造接收 gap_status = "covered" 的短语
4. ❌ 跳过智测直接从智库到智造（除非是手动强制覆盖）
