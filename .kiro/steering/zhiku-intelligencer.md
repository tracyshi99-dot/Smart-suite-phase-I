# 智库 - AI Query Intelligencer（独立模块）

## 定位
智库是 Smart Suite 内容生产流水线的**第一环节**，负责将 SEO/SEM 关键词转化为高价值 AI 原生检索短语。
它是整个流水线的起点：没有短语就没有内容生产。

## 概述
智库模块连接主流 AI 检索平台的思维方式，基于 8 维度评分框架，将传统关键词转化为「用户真正会在 AI 平台上问出的问题」，帮助团队：
- 捕捉真实用户在 AI 搜索场景下的提问方式和语言风格
- 生成高引用概率的结构化检索短语
- 按优先级和商业价值对短语进行科学排序
- 确保短语组合覆盖多维度搜索空间（Intent × Journey × Context）

## 核心公式

```
Query Value = User Relevance × Intent Relevance × Business Relevance × AI Discoverability
```

一个高质量 GEO Query = 一个真实用户在特定场景下有可能向 AI 提出，并且能够触发目标品牌/产品/内容被考虑、推荐或引用的问题。

---

## 支持的 AI 检索平台

### WW（海外平台）

| 平台代号 | 平台名称 | 思维方式 |
|---------|---------|---------|
| chatgpt | ChatGPT (OpenAI) | 对话式，上下文连续，偏长回答 |
| gemini | Gemini (Google) | Google 生态，搜索增强，结构化 |
| perplexity | Perplexity AI | 搜索增强，带来源引用，最接近搜索引擎 |

### CN（国内平台）

| 平台代号 | 平台名称 | 思维方式 |
|---------|---------|---------|
| deepseek | DeepSeek | 技术导向，reasoning 强，开源生态 |
| doubao | 豆包 (字节跳动) | 中文场景，国内用户习惯，抖音生态 |
| kimi | Kimi (月之暗面) | 长文本处理，中文深度分析 |
| yuanbao | 元宝 (腾讯) | 微信生态，搜索+对话混合 |
| qianwen | 通义千问 (阿里) | 阿里生态，电商场景强 |

---

## 8 维度生成框架

### Dimension 1: User Context（用户场景）20%

| 维度 | 选项 |
|------|------|
| Audience | New seller / Experienced / SMB / Enterprise |
| Geography | China / Korea / Vietnam / TW / JP / NA / EU |
| Experience | Beginner / Intermediate / Advanced |
| Business Type | SMB / Factory / Trading Company / Brand Owner |
| Situation | First-time expansion / Multi-market / Re-entry / Scale-up |

### Dimension 2: Intent（意图分类）20%

8 类 Intent：
1. **Learn** — 了解概念："什么是亚马逊全球开店？"
2. **Solve** — 解决问题："中国卖家怎么开始跨境电商？"
3. **Compare** — 对比选择："亚马逊 vs 独立站 哪个适合新手？"
4. **Evaluate** — 评估判断："亚马逊对中国小卖家友好吗？"
5. **Recommend** — 寻求推荐："最适合中国卖家的跨境站点有哪些？"
6. **Decide** — 做决策："中国卖家先开美国站还是欧洲站？"
7. **Execute** — 执行操作："中国卖家注册亚马逊美国站的具体步骤？"
8. **Verify** — 验证信任："亚马逊全球开店是官方项目吗？"

### Dimension 3: Customer Journey Stage（旅程阶段）15%

Awareness → Exploration → Evaluation → Decision → Action

### Dimension 4: Query Pattern（问题模式）15%

- Definition: "什么是X？" / "X怎么运作？"
- How-to: "如何X？" / "X的步骤是什么？"
- Comparison: "X vs Y" / "X和Y的区别？"
- Recommendation: "最好的X有哪些？" / "推荐哪个X？"
- Evaluation: "X值得吗？" / "X的优缺点？"
- Scenario: "[人群]如何用X实现[目标]？"
- Objection: "X的风险是什么？" / "X难吗？"
- Decision: "应该选X还是Y？"

### Dimension 5: Specificity（具体度）

| 层级 | 占比 | 示例 |
|------|------|------|
| Broad | 15% | "亚马逊全球开店" |
| Contextual | 30% | "中国卖家亚马逊全球开店" |
| Specific | 35% | "中国卖家如何通过亚马逊全球开店进入美国市场？" |
| Decision-specific | 20% | "没有海外经验的中国中小企业通过亚马逊开始在美国卖货的最佳方式？" |

### Dimension 6: Business Value（商业价值）15%

| 分数 | 定义 |
|------|------|
| 0 | 与业务无关 |
| 1 | 泛相关 |
| 2 | 产品/服务相关 |
| 3 | 明确业务需求 |
| 4 | 明确考虑解决方案 |
| 5 | 强决策/转化意图 |

### Dimension 7: GEO Opportunity（AI可见性机会）

考虑因素：
- AI 是否容易生成答案
- 是否存在多品牌竞争空间
- 是否容易出现 citation
- 是否有 recommendation 需求
- 是否能够产生 brand mention
- 是否能够产生 official-link citation

### Dimension 8: Query Diversity（多样性）

- 语义距离检测：Similarity > 0.85 的 Query 视为重复
- 需要覆盖不同 Intent × Journey × Context 的组合
- 不是 100 个最高分 Query，而是能最大代表搜索空间的 Query Portfolio

---

## 双层评分体系

### Layer 1: Query Quality Score（质量分）0-100

公式：Q = 0.20×I + 0.20×B + 0.15×C + 0.15×J + 0.15×G + 0.05×N + 0.05×U + 0.05×D

| 维度 | 权重 | 说明 |
|------|------|------|
| I - Intent Clarity | 20% | 意图是否清晰明确 |
| B - Business Relevance | 20% | 商业价值高低 |
| C - Context Specificity | 15% | 场景是否具体 |
| J - Journey/Decision Value | 15% | 在决策链中的价值 |
| G - GEO Opportunity | 15% | AI可见性测试价值 |
| N - Naturalness | 5% | 语言自然度 |
| U - Uniqueness | 5% | 是否与其他Query重复 |
| D - Diversity Contribution | 5% | 对整体覆盖的贡献 |

### Layer 2: Query Priority Score（优先级分）

公式：P = Quality × Demand × StrategicValue

Priority 决定最终排序，Quality ≠ Priority。

### 前端显示映射（1-5 星）

| Quality Score | 显示分 | 含义 |
|---|---|---|
| 0-39 | 2.0 | 低价值，可能不值得测试 |
| 40-54 | 2.5 | 泛相关 |
| 55-64 | 3.0 | 中等价值 |
| 65-74 | 3.5 | 良好 |
| 75-84 | 4.0 | 高价值 |
| 85-94 | 4.5 | 非常高价值 |
| 95-100 | 5.0 | 极高价值，优先测试 |

---

## 短语来源分类

### Source A: SEO/SEM 关键词转化
- 输入: `input/seo_sem_keywords.csv`
- 方法: 将传统关键词重写为 AI 对话式问句
- 适用: 有现成 SEO 数据时

### Source B: 内容类目种子扩展
- 输入: `content-rules.md` 35 个类目定义
- 方法: 每个类目推演 5-10 条代表性短语
- 适用: 批量扩充短语池

### Source C: 智预推演导入
- 输入: 智预模块的预测短语（经智测验证后）
- 方法: 验证通过后标记 source="zhiyu" 导入
- 适用: 前瞻布局

### Source D: 竞品反推
- 输入: 智测验证中发现的高频竞品覆盖话题
- 方法: 反推「如果用户搜这个话题，我们应该覆盖什么」
- 适用: 弥补竞品优势领域

---

## 生成规范

### Prompt 约束
1. 每条短语必须是 15-40 字的完整自然问句
2. 必须是问句形式（以疑问词或问号结尾）
3. 模拟真实卖家在 AI 搜索平台上的对话式提问
4. 包含具体场景或限定条件
5. 禁止输出碎片关键词（如"FBA"、"亚马逊注册"）
6. 确保覆盖至少 3 种以上 Intent 类型
7. 确保覆盖至少 2 个 Journey Stage
8. 避免语义高度相似的重复

### 快速评分规则（前端本地评分，不调 AI）

- 长度 15-30 字 +0.5，>30 字 +0.3
- 问句形式（怎么/如何/什么/哪些/为什么/how/what/why）+0.5
- 含亚马逊/Amazon/FBA/注册/开店/选品/物流/广告/listing +0.5
- 含疑问语气词（吗/呢/啊/吧/？/?）+0.3
- 含具体场景词（新手/2026/中国卖家/美国站/欧洲站）+0.3
- 含对比词（vs/还是/区别/对比/哪个好）+0.3
- 含决策词（应该/值得/适合/推荐/最好）+0.3
- 基础分 3.0，上限 5.0

---

## 执行规则

1. **生成不等于评分** — 生成和评分必须分两步，不允许同一次调用既生成又自评
2. **质量 > 数量** — 宁愿 20 条高质量短语，也不要 100 条泛泛而谈
3. **必须问句形式** — 碎片关键词一律淘汰
4. **多维覆盖** — 每批次必须覆盖 ≥ 3 种 Intent、≥ 2 个 Journey Stage
5. **去重检查** — 同批次内语义相似度 > 0.85 的视为重复，保留分数高的
6. **市场标签** — 每条短语必须标注 language + market
7. **来源标注** — 每条短语标注来源（Source A/B/C/D）
8. **验证闭环** — 生成后的短语必须经智测验证后才能进入智造

---

## 交互模式

### 模式 A：关键词转化（Keyword → Query）— 默认
1. 读取 `input/seo_sem_keywords.csv` 中的关键词
2. 每个关键词生成 3-5 条 AI 原生短语
3. 按 Quality Score 排序
4. 用户确认 `is_selected = TRUE` 的短语
5. 输出到 `output/{batch}/01_zhiku/zhiku_ai_queries.csv`

### 模式 B：类目扩展（Category Expansion）
1. 选择目标内容类目（1-35）
2. 系统推演该类目下的代表性短语
3. 8 维度评分
4. 用户确认/修改
5. 导入短语池

### 模式 C：自由输入（Free Input）
1. 用户直接输入短语或话题
2. 系统评分 + 改写优化
3. 用户确认
4. 导入短语池

### 模式 D：批量导入（Batch Import）
1. 从智预/竞品分析批量导入候选短语
2. 系统批量评分
3. 按阈值（Quality ≥ 65）筛选
4. 输出到短语池

---

## 输出格式

### CSV 输出字段

| 字段 | 说明 |
|------|------|
| keyword_id | 源关键词 ID |
| keyword | 源关键词文本 |
| query_id | 生成的短语 ID |
| ai_query | AI 检索短语全文 |
| intent_type | Learn/Solve/Compare/Evaluate/Recommend/Decide/Execute/Verify |
| query_type | branded/generic/industry/conversion-oriented |
| priority_score | 1-5（前端显示分） |
| quality_score | 0-100（内部质量分） |
| language | zh-CN / en-US / ja-JP 等 |
| market | CN / NA / EU / JP / ALL |
| source | keyword_transform / category_expand / zhiyu / competitor |
| is_selected | TRUE/FALSE |
| gap_status | pending / covered / partial_gap / full_gap（智测验证后填入） |
| created_at | 创建时间 |

---

## 输出路径

- 短语输出: `output/{batch_id}/01_zhiku/zhiku_ai_queries.csv`
- 短语池汇总: `output/zhiku/query_pool_master.csv`（全量短语池）
- 评分记录: `output/zhiku/scoring_log_{timestamp}.json`

---

## 与其他模块的关系

```
输入来源:
  - SEO/SEM 关键词 CSV → 智库
  - 智预推演结果（经智测验证）→ 智库
  - 竞品分析结果 → 智库

输出去向:
  - 智库短语 → 智测（验证覆盖状态）
  - 智测确认 full_gap → 智造（生产内容）
  - 智测确认 partial_gap → 智优（优化内容）
  - 智测确认 covered → 归档（无需行动）
```

**核心规则：智库产出的短语不能直接进智造，必须先过智测验证。**

---

## 词池健康指标

| 指标 | 健康阈值 | 说明 |
|------|---------|------|
| 总短语数 | ≥ 200 | 低于 200 需扩充 |
| Intent 覆盖度 | ≥ 6/8 类 | 单一 Intent 占比不超过 40% |
| 市场分布 | 每个活跃市场 ≥ 20% | 避免过度集中 |
| 验证率 | ≥ 80% 已验证 | 未验证短语积压不超过 20% |
| Gap 率 | — | 仅作参考，不设阈值 |
| 每周新增 | ≥ 10 条 | 保持短语池活力 |

---

## 触发命令

| 命令 | 动作 |
|------|------|
| "执行智库" / "开始智库" / "Step 1" | 模式 A 关键词转化 |
| "智库扩词 [类目]" | 模式 B 类目扩展 |
| "评分 [短语]" | 对指定短语做 8 维度评分 |
| "词池状态" / "短语健康" | 输出词池健康指标 |
| "导入智预结果" | 模式 D 批量导入 |

---

*Generated by Smart Suite 智库 Module | 短语是一切的起点*
