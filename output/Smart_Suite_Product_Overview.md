# Smart Suite 智系列产品功能全景

> 版本：2026 Q2 | 最后更新：2026-08-06

---

## 一、产品定位

Smart Suite（智系列）是一套 **AI 驱动的 GEO 内容全自动化平台**，服务于 Amazon Global Selling 的 Demand Generation 业务。覆盖从检索短语发现、内容生产、质量优化、合规审核、页面发布、效果追踪到需求预测的完整闭环。

**核心价值：** 让 Amazon 品牌内容被 AI 搜索引擎（ChatGPT、DeepSeek、Gemini、豆包、元宝、Kimi、千问）主动引用和推荐，驱动 Reg Start 增长。

---

## 二、产品矩阵总览

| 模块 | 中文名 | 定位 | 运行方式 |
|------|--------|------|---------|
| 智库 | Zhiku | 检索短语发现与扩展 | 流水线第1步 |
| 智造 | Zhizao | AI 内容生产 | 流水线第2步 |
| 智优 | Zhiyou | 评分 + 优化 + 合规审核 | 流水线第3步 |
| 智布 | Zhibu | CMS 页面发布 | 流水线第4步 |
| 智测 | Zhice | AI 搜索旅程模拟 | 独立并行模块 |
| 智析 | Zhixi | 全渠道绩效追踪与分析 | 独立并行模块 |
| 智预 | Zhiyu | 检索需求预测 | 独立并行模块 |
| 智中枢 | Orchestrator | 工作流决策引擎 | 独立并行模块 |

---

## 三、各模块详细功能

---

### 1. 智库 (Zhiku) — 检索短语发现与扩展

**一句话：** 从 SEO/SEM 关键词出发，生成适合 AI 搜索平台的自然问句检索短语。

**核心功能：**
- 连接 8 大 AI 平台（ChatGPT / Gemini / Perplexity / DeepSeek / 豆包 / Kimi / 元宝 / 千问）
- 将碎片关键词扩展为 15-40 字的自然问句
- 自动分类：意图类型（informational / navigational / transactional / comparison）
- 自动分类：短语类型（branded / generic / industry / conversion-oriented）
- 优先级评分（1-5 分），高质量短语标记 is_selected = TRUE
- 支持语义扩展（Semantic Expansion）：从种子短语推演相关检索路径

**输入：** `input/seo_sem_keywords.csv`
**输出：** `output/{batch}/01_zhiku/zhiku_ai_queries.csv`

**Q2 升级点：**
- 短语长度从碎片关键词（3-8字）升级为自然问句（15-40字）
- 新增语义扩展引擎，从1个种子扩展出10-20个相关短语
- 多区域支持（CN / NA / EU / JP / ROA）

---

### 2. 智造 (Zhizao) — AI 内容生产

**一句话：** 基于知识库自动生成 SEO + GEO 双优化的高质量文章。

**核心功能：**
- 基于 3PKC KMS 知识库检索事实和数据（严禁模型自由发挥）
- 生成 800-1500 字结构化文章，遵循 SEO + GEO 双标准
- 自动植入官网链接（≥2次 gs.amazon.cn）
- 每篇文章包含：Meta Title / Description / 表格 / 列表 / FAQ / CTA
- 35 个内容品类覆盖（跨境电商全生命周期）
- 支持模板复用（注册类 / 费用类 / 物流类 / 广告类等）
- 内置 2026 年敏感词库自动过滤

**内容结构规范：**
```
开头段落：痛点引入 + 关键词 + 核心结论（金字塔原则）
H2 标题 1：核心结论一句话 → 详细展开（表格/列表）
H2 标题 2：核心结论一句话 → 详细展开
H2 标题 3：核心结论一句话 → 详细展开
FAQ（≥3 问答）
结语 + CTA
```

**AI 模型：** Claude 3 Sonnet（AWS Bedrock），回退通义千问

**输入：** `output/{batch}/01_zhiku/zhiku_ai_queries.csv`（is_selected=TRUE）
**输出：** `output/{batch}/02_zhizao/zhizao_draft_content.csv`

**Q2 升级点：**
- 从独立工具升级为 workflow 自动串联（智库产出直接流入）
- 新增注册类专用知识库和写作技巧模板
- 敏感词库嵌入 system prompt
- 三段式模型架构（Claude 生产 → Claude 合规 → Qwen 润色）

---

### 3. 智优 (Zhiyou) — 评分 + 优化 + 合规审核

**一句话：** 三合一质量把关系统 — 评分告诉你问题在哪，优化帮你改好，合规确保能发布。

#### 3.1 智优评分 (Score)

5 维度评估 AI 引用概率：

| 维度 | 权重 | 评估内容 |
|------|------|---------|
| Intent Match 意图匹配 | 30% | 是否直接回答检索问题？首段是否给出明确答案？ |
| AI Readability AI可读性 | 20% | AI 是否容易解析提取？结构是否清晰？ |
| Authority 权威性 | 20% | 是否包含具体可靠的平台知识？ |
| Actionability 可操作性 | 20% | 是否提供清晰的下一步行动？ |
| Differentiation 差异化 | 10% | 是否区别于通用网页内容？ |

通过条件：overall ≥ 4.5 且 intent_match ≥ 4 且 authority ≥ 4

#### 3.2 智优执行 (Execute)

- 读取评分建议，自动改写全文
- Claude 做结构性改写 + 合规调整
- Qwen-Max 做中文自然度润色（新增）
- 输出完整 v2 版本文章

#### 3.3 智优合规 (Compliance)

自动执行 9 大合规规则：
1. **禁用词替换**（站点→平台、最好→优选、合作伙伴→第三方服务提供商...）
2. **数据使用规范**（必须标明出处，禁止未披露敏感数据）
3. **卖家注册表述**（通过 Seller Central 注册，不能是"前往全球开店官网注册"）
4. **品牌使用规范**（服务提供方是"亚马逊"不是"亚马逊全球开店"）
5. **产品描述规范**（不夸大、不透露未推出产品）
6. **第三方规范**（不给服务商官方认可/背书）
7. **税务政策引用**（只引用官方政策+免责声明）
8. **地图与敏感地区**（中国台湾/中国香港/中国澳门）
9. **版权声明**（Copyright © 2026 Amazon）

**审核双轨制：**
- Critical 3-4 类（30个品类）：AI 智优全自动审核
- Critical 5 类（6个品类：注册/费用/审核/VAT/税务/合规）：AI 审核 + 人工 POC 审批

**AI 模型：** Claude 3 Sonnet（评分+合规） + Qwen-Max（润色）
**输出：** `output/{batch}/03_zhiyou/zhiyou_scorecard.csv` + `zhiyou_optimized_content.csv` + `zhiyou_compliance_checked.csv`

---

### 4. 智布 (Zhibu) — CMS 页面发布

**一句话：** 将优化后的文章转换为 Amazon LEGO CMS 可直接导入的 JSON 格式。

**核心功能：**
- Markdown → LEGO JSON 结构化转换
- 自动设置 H1（large）/ H2（medium）/ H3（small）字号
- 表格转换为 LEGO Table widget（border/header bg/列宽等标准化）
- Meta Title / Meta Description 注入顶层 Container
- Markdown 星号/加粗标记自动清理
- 输出可直接导入 LEGO CMS 发布

**输出：** `output/{batch}/04_zhibu/zhibu_output.json`

---

### 5. 智测 (Zhice) — AI 搜索旅程模拟

**一句话：** 模拟真实卖家在 AI 平台上的多轮递进式搜索旅程，检测内容是否被引用。

**核心功能：**
- 模拟用户在 7 个 AI 平台上的搜索行为
- 每个旅程 ≥ 5 轮递进搜索（从浅到深）
- 支持用户画像定义（背景/目标/经验水平/决策阶段）
- 检测每轮搜索中我们的内容是否被引用
- 生成覆盖率分析报告

**支持平台：**
- 海外：ChatGPT、Gemini、Perplexity
- 国内：DeepSeek、豆包、Kimi、元宝、千问

**交互模式：**
- 模式 A：自动推演（快速出报告）
- 模式 B：逐轮确认（可修改/新增/删除检索问题）

**输出：**
- `output/zhice/journey_{persona}_{timestamp}.json`
- `output/zhice/zhice_report_{persona}_{timestamp}.csv`
- `output/zhice/zhice_summary_{timestamp}.md`

---

### 6. 智析 (Zhixi) — 全渠道绩效追踪与分析

**一句话：** 实时追踪 GEO 带来的业务增长、AI 平台引用率，以及内容 ROI。

**核心功能：**

#### 6.1 Output 趋势追踪
- Weekly / Monthly / YTD 三个时间维度
- 渠道拆分：CN GEO / WW GEO / WW Direct / CN Direct / SSR 大盘
- 自动计算 YoY、WoW、MoM
- vs 大盘 BPS（Basis Points）自动对比
- Q1 / Q2 季度汇总

#### 6.2 AI 引用追踪（Citation Tracking）
- 646 条检索短语 × 7 平台的逐条引用状态
- 品牌提及率追踪（品牌/产品名称是否被 AI 提及）
- 官网链接提及率追踪（gs.amazon.cn 是否出现在 AI 回答中）
- 按品牌词 / 行业词分组分析
- 各平台月度趋势对比（元宝/DeepSeek/豆包/ChatGPT/Kimi/千问/Gemini）
- "无品牌提及"短语筛选，定向优化

#### 6.3 GEO Input 总表
- 提示词数量月度增长
- 品牌提及率 / 链接提及率月度趋势
- 品牌词 vs 行业词分开展示
- 新建内容 / 旧内容优化产出量

#### 6.4 Ahrefs 品牌雷达
- 竞品 AI 引用数据追踪
- 按国家/区域标注（当前 TW，后续扩展）

**数据来源：**
- `output/metrics/geo_monthly_data.csv` — 月度渠道数据
- `output/metrics/geo_input_summary.csv` — 引用率汇总
- `output/metrics/gap_verification_cn.csv` — 646条短语明细
- `output/metrics/geo_platform_mentions.csv` — 各平台分布

---

### 7. 智预 (Zhiyu) — 检索需求预测

**一句话：** 预测卖家未来 2-4 周会搜什么，提前布局高价值内容。

**三大推演引擎：**

#### 引擎 1：卖家生命周期推演
- 8 个阶段：认知→考虑→决策→注册→新手→成长→成熟→扩展
- 每个阶段转换时推演新检索需求
- 标注置信度 + 预计爆发时间窗口

#### 引擎 2：政策/产品/市场变化推演
- 信号源：Amazon 公告 / 法规更新 / 新功能发布 / 旺季节点 / 关税变化
- 捕获信号 → 推演衍生 Query → 标注行动建议

#### 引擎 3：站内搜索 + FAQ 趋势外推
- Help Center 高频页面趋势
- FAQ 量 WoW +30% → 预测 2 周内 AI 搜索同话题 +50%

**竞争壁垒价值：**

| 来源 | 竞对复制难度 |
|------|------------|
| AI 回答中的 Gap | 容易（人人能做） |
| 站内搜索/客服 FAQ | 较难（需内部数据） |
| 生命周期推演 | 不容易（需深度业务理解） |
| 政策/市场变化预测 | 最难复制（需前瞻判断力） |

**输出：**
- `output/zhiyu/forecast_{type}_{timestamp}.json`
- `output/zhiyu/zhiyu_summary_{timestamp}.md`

---

### 8. 智中枢 (Orchestrator) — 工作流决策引擎

**一句话：** 读取智析数据，自动判断"本周该做什么"，输出执行计划。

**7 条决策规则：**

| 规则 | 触发条件 | 行动 |
|------|---------|------|
| 增长加速 | 渠道 WoW > +30% 连续 2 周 | 加大该渠道内容产出 |
| 下降预警 | 渠道 WoW < -20% | 暂停该渠道，启动归因分析 |
| 绝对值过低 | GEO 周 < 50 但 YoY > +50% | 扩大关键词覆盖 |
| 高增长站点扩展 | 站点 YoY > +100% | 分配 30%+ 资源到该站点 |
| 内容缺口 | 有流量但 2 周无内容产出 | 重启全流程生产 |
| 大盘对比 | YoY < SSR 大盘 | 需策略调整，Gap 分析 |
| 投入产出滞后 | 内容发布 2-3 周无 lift | 重审内容质量，考虑改写 |

**输出格式：**
```
📋 Smart Suite Weekly Plan - WK[XX]

🟢 ACCELERATE: [Channel] → [Action]
🔴 INVESTIGATE: [Channel] → [Action]
📝 THIS WEEK'S EXECUTION PLAN:
  - 智库: X 个新关键词
  - 智造: X 篇文章
  - 智优: Review X 篇
  - 智布: 发布 X 篇
```

---

## 四、技术架构

### 模型架构（三段式）

```
智造 (Production)     → Claude 3 Sonnet (AWS Bedrock)
智优 Score/Compliance → Claude 3 Sonnet (AWS Bedrock)
智优 Polish (润色)    → 通义千问 Qwen-Max
智库/智布             → Claude 3 Sonnet (AWS Bedrock)
```

### 部署架构

```
代码仓库: GitHub (tracyshi99-dot/Smart-suite-phase-I)
前端: Streamlit Cloud (自动部署)
数据同步: AWS S3 (smartsuite-sync-data)
定时任务: AWS Lambda (smartsuite-automation, 5min interval)
凭证: AWS Bedrock (us-east-1)
```

### 代码规模

| 组件 | 行数 |
|------|------|
| UI 主程序 (app.py) | ~7,200 |
| AI 引擎 (engine.py) | ~1,740 |
| LEGO 转换器 (lego_converter.py) | ~530 |
| 智测独立模块 (app_zhice.py) | ~450 |
| 其他 (Lambda/MCP/API) | ~650 |
| **Python 代码总计** | **~10,600** |
| Steering 规范文件 (20个) | ~2,700 |
| 知识库文档 (50个) | ~数万字 |

---

## 五、业务成果（截至 2026 Q2）

| 指标 | 数值 |
|------|------|
| Q2 GEO+Direct Reg Start | 42,844 (+29% YoY) |
| 占 SSR 大盘比例 | 29.0% (+891 bps YoY) |
| 品牌提及率 | 75% → 86.5% |
| 官网链接提及率 | 18.1% → 56.88% |
| YTD 内容产出 | 648 篇 |
| 监控检索短语 | 646 条 (487品牌 + 159行业) |
| 覆盖 AI 平台 | 7 个 |
| 持续跑赢大盘 | 每月 +5,000~15,000 bps |

---

*Generated by Smart Suite | 2026-08-06*
