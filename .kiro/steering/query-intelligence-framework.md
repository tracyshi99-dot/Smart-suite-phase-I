# Query Intelligence Framework - 智库评分与生成规范

## 核心定义

一个高质量 GEO Query = 一个真实用户在特定场景下有可能向 AI 提出，并且能够触发目标品牌/产品/内容被考虑、推荐或引用的问题。

公式：Query Value = User Relevance × Intent Relevance × Business Relevance × AI Discoverability

## 一、Query 生成 8 维度框架

### Dimension 1: User Context（用户场景）20%
- Audience: New seller / Experienced / SMB / Enterprise
- Geography: China / Korea / Vietnam / TW
- Experience: Beginner / Intermediate / Advanced
- Business Type: SMB / Factory / Trading Company
- Situation: First-time expansion / Multi-market / Re-entry

### Dimension 2: Intent（意图分类）20%
8 类 Intent（不是传统 SEO 4 类）：
1. **Learn** - 了解概念："什么是亚马逊全球开店？"
2. **Solve** - 解决问题："中国卖家怎么开始跨境电商？"
3. **Compare** - 对比选择："亚马逊 vs 独立站 哪个适合新手？"
4. **Evaluate** - 评估判断："亚马逊对中国小卖家友好吗？"
5. **Recommend** - 寻求推荐："最适合中国卖家的跨境平台有哪些？"
6. **Decide** - 做决策："中国卖家先开美国站还是欧洲站？"
7. **Execute** - 执行操作："中国卖家注册亚马逊美国站的具体步骤？"
8. **Verify** - 验证信任："亚马逊全球开店是官方项目吗？"

### Dimension 3: Customer Journey Stage（旅程阶段）15%
- Awareness → Exploration → Evaluation → Decision → Action

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
分布要求（不是全部追求 long-tail）：
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

## 二、双层评分体系

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

---

## 三、前端显示映射（1-5 星）

将 Quality Score (0-100) 映射到前端 1-5 分显示：
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

## 四、评分实现规则

### 快速评分（前端/本地，用于实时显示）
基于规则的轻量评分，不调用 AI：
- 长度 15-30 字 +0.5，>30 字 +0.3
- 问句形式（怎么/如何/什么/哪些/为什么/how/what/why）+0.5
- 含亚马逊/Amazon/FBA/注册/开店/选品/物流/广告/listing +0.5
- 含疑问语气词（吗/呢/啊/吧/？/?）+0.3
- 含具体场景词（新手/2026/中国卖家/美国站/欧洲站）+0.3
- 含对比词（vs/还是/区别/对比/哪个好）+0.3
- 含决策词（应该/值得/适合/推荐/最好）+0.3
- 基础分 3.0，上限 5.0

### AI 评分（批量处理，精确评分）
调用 Claude/Bedrock 对 Query 进行 8 维度打分，返回 0-100 Quality Score + 分类标签。

---

## 五、生成规范

### Prompt 约束
1. 每条短语必须是 15-40 字的完整自然问句
2. 必须是问句形式
3. 模拟真实卖家在 AI 搜索平台上的对话式提问
4. 包含具体场景或限定条件
5. 禁止输出碎片关键词
6. 确保覆盖至少 3 种以上 Intent 类型
7. 确保覆盖至少 2 个 Journey Stage
8. 避免语义高度相似的重复

### 生成不等于评分
- Agent 1: Query Generator（生成）
- Agent 2: Query Scorer（评分，独立于生成）
- 不允许同一个 AI 调用既生成又自评
