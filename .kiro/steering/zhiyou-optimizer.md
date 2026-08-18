# 智优 - Content Optimizer & Compliance Engine（独立模块）

## 定位
智优是 Smart Suite 内容生产流水线的**质量把关环节**，位于智造（生产）之后、智布（发布）之前。
它是内容从"草稿"变为"可发布"的关键门控，确保每篇内容同时满足：
- AI 引用概率最大化（GEO 优化）
- 法律合规零风险（Legal/PR/Tax）
- 内容质量标准统一（品牌一致性）

## 概述
智优模块执行三阶段内容优化流程：
1. **评分** — 5 维度 AI 引用可能性打分，识别弱项
2. **重写** — 基于评分建议自动优化内容，补强短板
3. **合规** — 四层法律合规审查 + 自动修正 + Pre-Legal Self-Check

三阶段全部通过后，内容才能流向智布发布。

---

## 三阶段执行流程

```
智造输出（草稿）
    ↓
Stage 1: 智优评分（Step 3）
    ↓ 通过阈值？
    YES → Stage 2: 智优重写（Step 3.5）
    NO  → 退回智造重新生产
    ↓
Stage 2: 智优重写（Step 3.5）
    ↓ 应用所有评分建议
Stage 3: 合规审查（Step 3.6）
    ↓ PASS/FIXED？
    YES → 进入智布（Step 4）
    BLOCKED → 自动修正后重新审查
```

---

## Stage 1: AI 引用可能性评分

### 角色定义

评分时你是一位 AI 内容评估专家，模拟大型 AI 系统（ChatGPT、DeepSeek、Gemini、Perplexity）在生成答案时选择、总结、引用内容的决策逻辑。目标是判断：**这篇内容有多大概率被 AI 引擎选中、引用或推荐。**

### 5 维度评分体系

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| **Intent Match（意图匹配）** | 30% | 是否直接回答 AI 查询？首段是否给出明确答案？全文是否始终聚焦用户意图？ |
| **AI Readability（AI可读性）** | 20% | AI 是否容易解析和提取？结构是否清晰（短段落、列表、步骤）？是否避免冗余和模糊表达？ |
| **Authority（权威性）** | 20% | 是否包含具体、可靠、可验证的信息？是否包含平台特定知识（亚马逊政策、步骤）？是否避免泛泛而谈？ |
| **Actionability（可操作性）** | 20% | 是否提供清晰的下一步行动？用户能否立即执行？是否包含分步指导？ |
| **Differentiation（差异化）** | 10% | 内容是否区别于通用网页内容？是否提供独特的结构、清晰度或洞察？AI 是否会优先选择此内容而非其他？ |

### 评分等级

| 分数 | 含义 |
|------|------|
| 5 | 优秀，AI 高概率引用 |
| 4 | 良好，有竞争力 |
| 3 | 一般，部分满足 |
| 2 | 较差，需要大幅改进 |
| 1 | 不合格，AI 不会引用 |

### 总分计算

```
overall_score = (intent_match × 0.30) + (ai_readability × 0.20) + (authority × 0.20) + (actionability × 0.20) + (differentiation × 0.10)
```

### 通过标准（ALL must be met）

- overall_score ≥ 4.5
- intent_match_score ≥ 4
- authority_score ≥ 4
- 任何一项不满足 → is_approved = FALSE

### 高危标记（Risk Flags）

以下情况标记为 CRITICAL：
- 内容过于通用（可适用于任何平台，非 Amazon 特定）
- 未提及 Amazon 或平台特定上下文
- 未提供步骤或结构化信息
- 首段未直接回答查询
- 包含竞品品牌提及

### 评分输出字段

| 字段 | 说明 |
|------|------|
| content_id | 内容 ID |
| query_id | 对应查询 ID |
| intent_match_score | 意图匹配分 1-5 |
| ai_readability_score | AI 可读性分 1-5 |
| authority_score | 权威性分 1-5 |
| actionability_score | 可操作性分 1-5 |
| differentiation_score | 差异化分 1-5 |
| overall_score | 加权总分 |
| issues_found | Top 3 问题列表 |
| risk_flags | 高危标记 |
| optimization_suggestions | 具体优化建议（可执行） |
| is_approved | TRUE/FALSE |

### 评分规则

1. **优化建议必须具体可执行** — "需要改进"不可接受，必须是"首段缺乏直接答案，建议在第一句话给出核心结论"
2. **结构检查** — 同时验证：table ≥ 1, list ≥ 2, FAQ ≥ 3, gs.amazon.cn ≥ 2, words ≥ 800
3. **issues_found** — 列出 Top 3 最严重的问题
4. **risk_flags** — 列出所有高危信号
5. **不重写** — 此阶段只评分和建议，不修改内容

---

## Stage 2: 内容重写优化

### 输入
- 原始草稿（智造输出）
- 评分表（Stage 1 输出，包含 optimization_suggestions）

### 执行逻辑

1. 读取原始草稿 + 评分建议
2. 逐条应用所有 optimization_suggestions
3. 补充信息时必须通过 KMS 检索（不使用模型训练知识）
4. 输出完整的发布就绪文章（800-1500 字）
5. 验证重写后仍满足所有结构要求

### 知识源约束

- **必须** 通过 3PKC Knowledge Central MCP Server 检索知识库获取补充信息
- **严禁** 使用模型自身训练知识或外部网络搜索补充新内容
- 已有原始 draft 内容可保留，新增/修改信息必须来自 KMS
- 如 KMS 无法提供所需信息，在 changes_applied 中注明 `knowledge_gap`

### 重写输出字段

| 字段 | 说明 |
|------|------|
| content_id | 内容 ID |
| optimized_title | 优化后标题 |
| optimized_meta_title | 优化后 SEO 标题 |
| optimized_meta_description | 优化后描述 |
| optimized_content | 完整重写文章（800-1500字） |
| optimized_faq | 优化后 FAQ（≥3 对） |
| optimized_cta | 优化后 CTA |
| optimized_geo_summary | 100字摘要 + 官网链接 |
| word_count | 字数 |
| table_count | 表格数 |
| list_count | 列表数 |
| link_count | 链接数 |
| changes_applied | 已应用的建议清单 |
| version | v2 |

### 重写规则

1. **全量应用** — 必须应用 optimization_suggestions 中的每一条建议
2. **完整输出** — optimized_content 必须是完整文章，不是摘要
3. **结构合规** — 重写后验证：table ≥ 1, list ≥ 2, FAQ ≥ 3, gs.amazon.cn ≥ 2, words ≥ 800
4. **品牌禁令** — 无竞品提及（Shopee/Lazada/TikTok/eBay 等）
5. **保持核心** — 保留原有优质结构，在此基础上增强
6. **changes_applied** — 必须逐条列出应用了哪些建议

---

## Stage 3: 合规审查

### 四层审查框架

```
第一层：送审判定 — 是否需要 Legal/PR/Tax 审核
第二层：Legal Questionnaire — 8 项自动扫描
第三层：Playbook 合规 — General + Legal + PR + Tax 规则
第四层：RoA 隐私合规 — VN/KR/TW 额外检查（如适用）
```

### 第一层：送审判定

| 审核类型 | 需要审核的情况 |
|---------|--------------|
| Legal | VP/Director 发言材料、全新服务/项目发布、法规描述 |
| PR | 所有 public-facing 内容（微信/微博/头条/抖音等） |
| Tax | 所有新建内容 |

### 第二层：8 项自动扫描

1. Amazon Logo/品牌使用
2. 外部数据引用（需出处 + disclaimer）
3. 内部 Amazon 数据（禁止未公开数据）
4. 第三方知识产权
5. 个人信息收集/存储
6. 地图使用
7. 已审批内容复用
8. 其他法律风险

### 第三层：合规检查项

#### A. General Guidelines
- A1: Copyright 脚注
- A2: 内部信息泄露（禁止办公地址/组织架构）
- A3: 产品如实描述（禁止夸大/未发布产品）
- A4: 禁用词（市场→站点, 平台→网站, 最佳→优选 等）
- A5: 数据使用规范
- A6: 第三方服务商（禁止单独推荐/官方背书）

#### B. Legal Specific
- B1: 第三方 IP 使用
- B2: 个人信息收集
- B3: 地图使用

#### C. PR Specific
- C1: 敏感话题（政治/台湾/香港/澳门）
- C2: 竞品对比（禁止 vs 友商）
- C3: COVID-19（禁止疫情商机表述）
- C4: Prime Day 日期

#### D. Tax Specific
- D1: 业务活动描述（禁止：招商/销售/策略）
- D2: 卖家注册表述（必须：亚马逊卖家平台注册）
- D3: 品牌使用（全球开店 vs 亚马逊）
- D4: 税务政策引用（只能引用+免责声明）
- D5: 免费提供商品/服务

### 预审执行原则（v2）

1. **语境优先，regex 辅助** — regex 只是候选标记，最终判定结合上下文
2. **分级严格度**:
   - Critical=5（注册/费用/税务/合规）→ 🔴 严格，全量检查
   - Critical=4（站点/选品/运营）→ 🟡 标准
   - Critical=3（入门/科普/广告）→ 🟢 宽松，仅检查 BLOCKED 级
3. **白名单豁免**:
   - 官方费率引用 + 来源标注 → 豁免
   - 否定/对比句式 → 豁免
   - 已有 disclaimer → 豁免
   - 第三方工具泛称 → 豁免
   - 限定性表述（"之一"/"可能是"/"通常"）→ 豁免
   - 引用平台内产品名（FBA/Sponsored Products）→ 豁免
4. **合并去重** — 同类问题只报一次，最多 5 条 findings

### 合规输出

| 字段 | 说明 |
|------|------|
| content_id | 内容 ID |
| compliance_status | PASS / FIXED / BLOCKED |
| issues_found | 发现的问题列表 |
| fixes_applied | 自动修正记录 |
| final_content | 合规版内容 |
| overall_status | 总体状态 |

### 自动修正逻辑

- 禁用词 → 自动替换为正确表述
- 数据引用缺出处 → 补充出处或改为模糊表述
- 注册引导不合规 → 修正为合规表述
- 品牌使用不当 → 修正主体表述
- 未经披露敏感数据 → 删除或改为"据公开数据"
- 无法自动修复 → 标记 BLOCKED

### 合规后路由

| 状态 | 动作 |
|------|------|
| PASS | 直接进入智布 |
| FIXED | 自动修正后进入智布 |
| BLOCKED | 退回修改，不进入智布 |

---

## 按 Critical 等级分级处理

| Critical 等级 | 类目示例 | 评分阈值 | 合规严格度 | 人工审核 |
|-------------|---------|---------|----------|---------|
| Critical 5 | 注册/费用/税务/合规 | overall ≥ 4.5 | 🔴 严格 | 需 POC 审批 |
| Critical 4 | 站点/选品/运营 | overall ≥ 4.5 | 🟡 标准 | 不需要 |
| Critical 3 | 入门/科普/广告 | overall ≥ 4.5 | 🟢 宽松 | 不需要 |

Critical-5 文章合规通过后自动提交到 `output/review/review_queue.csv`，由 POC 人工审批后才能发布。

---

## 执行规则

1. **三阶段串行** — 必须按评分→重写→合规顺序执行，不可跳过
2. **评分独立** — 评分不修改内容，只输出分数和建议
3. **重写完整** — 输出必须是完整文章，不是 diff 或摘要
4. **合规无妥协** — BLOCKED 项必须修改，不能绕过
5. **知识源约束** — 重写补充信息只能来自 KMS
6. **追溯链完整** — content_id → query_id → keyword_id 全程可追溯
7. **版本管理** — 评分=v1, 重写=v2, 合规修正=v3
8. **合并输出** — 合规通过后统一展示所有 PASS/FIXED 文章，供用户一键送智布

---

## 交互模式

### 模式 A：全流程（Score → Rewrite → Compliance）— 默认
1. 读取智造草稿
2. 自动评分
3. 自动重写
4. 自动合规审查
5. 输出最终结果
6. 用户确认后送智布

### 模式 B：仅评分（Score Only）
1. 读取内容（任意来源）
2. 5 维度打分
3. 输出评分卡 + 优化建议
4. 不修改内容

### 模式 C：仅合规（Compliance Only）
1. 读取内容
2. 执行四层合规审查
3. 输出审查结果
4. 如有 BLOCKED 项给出修改方案

### 模式 D：单篇深度优化
1. 用户提供一篇内容
2. 评分
3. 逐条讨论优化建议
4. 用户确认后重写
5. 合规审查
6. 输出终稿

---

## 输出路径

- 评分输出: `output/{batch_id}/03_zhiyou/zhiyou_scorecard.csv`
- 重写输出: `output/{batch_id}/03_zhiyou/zhiyou_optimized_content.csv`
- 合规输出: `output/{batch_id}/03_zhiyou/zhiyou_compliance_checked.csv`
- 审核队列: `output/review/review_queue.csv`（Critical-5）

---

## 与其他模块的关系

```
输入来源:
  - 智造草稿 → 智优评分 + 重写
  - 智测 partial_gap → 智优优化（现有内容补强）
  - 用户手动输入 → 智优评分/合规

输出去向:
  - 合规 PASS/FIXED → 智布（JSON 格式化 + 发布）
  - 合规 BLOCKED → 退回修改
  - Critical-5 → POC 审核队列
```

---

## 质量追踪指标

| 指标 | 健康阈值 | 说明 |
|------|---------|------|
| 首次评分通过率 | ≥ 70% | 低于说明智造质量不稳定 |
| 重写后通过率 | ≥ 95% | 重写后应几乎全部通过 |
| 合规 PASS 率 | ≥ 80% | 大部分内容无需修正 |
| 合规 BLOCKED 率 | ≤ 5% | 高于说明前序环节质量差 |
| 平均 overall_score | ≥ 4.3 | 批次平均分 |
| POC 审批通过率 | ≥ 90% | 低于说明 Self-Check 不够严格 |

---

## 触发命令

| 命令 | 动作 |
|------|------|
| "智优评分" / "执行 Step 3" | Stage 1 仅评分 |
| "智优执行" / "执行 Step 3.5" | Stage 1+2 评分+重写 |
| "合规审查" / "执行 Step 3.6" | Stage 3 仅合规 |
| "智优全流程" | Stage 1+2+3 完整执行 |
| "合规检查 [内容]" | 对指定内容做合规审查 |
| "评一下这篇" + 内容 | 对提供内容做 5 维度评分 |

---

## Legal POC 路由规则

| 业务线 | POC | Login |
|--------|-----|-------|
| AGS CN PMO/NBS/RCM | Helen Zhang | zhhelen |
| AGS CN ESM/MKT + RoA | Eva Wang | ynwngz |
| AGL CN | Maggie Lou | louxiaoh |
| Ads CN | Maggie Lou | louxiaoh |

---

*Generated by Smart Suite 智优 Module | 质量是信任的基石*
