# 智测 - AI Search Journey Simulation（独立模块）

## 定位
智测是 Smart Suite 的**独立并行模块**，与内容生产流水线（智库→智造→智优→智布）平行运作。
它不依赖流水线的输入输出，可以随时独立运行。

## 概述
智测模块模拟真实用户在不同 AI 检索平台上的多轮递进式搜索旅程（Search Journey），帮助分析：
- 用户决策路径上的关键检索节点
- 不同 AI 平台对同一问题的返回差异
- 我们内容是否在关键节点被 AI 引擎引用
- 内容覆盖缺口和优化机会

## 支持的 AI 检索平台

### WW（海外平台）

| 平台代号 | 平台名称 | 特点 |
|---------|---------|------|
| chatgpt | ChatGPT (OpenAI) | 对话式，上下文连续，偏长回答 |
| gemini | Gemini (Google) | Google 生态，搜索增强，结构化 |
| perplexity | Perplexity AI | 搜索增强，带来源引用，最接近搜索引擎 |

### CN（国内平台）

| 平台代号 | 平台名称 | 特点 |
|---------|---------|------|
| deepseek | DeepSeek | 技术导向，reasoning 强，开源生态 |
| doubao | 豆包 (字节跳动) | 中文场景，国内用户习惯，抖音生态 |
| kimi | Kimi (月之暗面) | 长文本处理，中文深度分析 |
| yuanbao | 元宝 (腾讯) | 微信生态，搜索+对话混合 |
| qianwen | 通义千问 (阿里) | 阿里生态，电商场景强 |

## 用户画像模板

```json
{
  "persona_id": "string",
  "name": "示例人物名",
  "background": "深圳3C配件卖家，35岁，年营收500万",
  "goal": "想开亚马逊美国站，寻找入门路径",
  "experience_level": "beginner|intermediate|advanced",
  "language_preference": "zh-CN|en-US|mixed",
  "decision_stage": "awareness|consideration|decision|action",
  "pain_points": ["不了解注册流程", "担心合规风险", "不确定选品方向"]
}
```

## 搜索旅程（Search Journey）结构

每个旅程包含多轮搜索（Rounds），每轮基于上一轮结果深入：

```json
{
  "journey_id": "string",
  "persona": "{persona object}",
  "platforms": ["chatgpt", "perplexity", "google_sge"],
  "rounds": [
    {
      "round_num": 1,
      "trigger": "为什么用户在此刻会问这个问题",
      "user_mindset": "用户此刻的心理状态和关注点",
      "queries": {
        "chatgpt": "中国卖家怎么注册亚马逊美国站？需要什么材料？",
        "perplexity": "amazon US seller registration requirements Chinese sellers 2025",
        "google_sge": "亚马逊美国站开店注册流程 2025"
      },
      "results_summary": {
        "chatgpt": {"key_points": [], "sources_cited": []},
        "perplexity": {"key_points": [], "sources_cited": []},
        "google_sge": {"key_points": [], "sources_cited": []}
      },
      "our_content_found": true/false,
      "next_question_trigger": "从结果中发现了X信息，引发了对Y的疑问"
    }
  ]
}
```

## 检测报告模板

报告分为以下部分：

### 1. 旅程概览
- 人物画像摘要
- 平台选择
- 旅程轮次数
- 总检索短语数

### 2. 逐轮分析
每轮包含：
- 用户意图和心理状态
- 各平台检索短语
- 各平台返回的关键内容摘要
- 引用来源列表（URL + 域名）
- 是否发现我们的内容
- 触发下一轮问题的逻辑

### 3. 覆盖率分析
- 总检索节点数 vs 我们内容出现的节点数
- 按平台分布的覆盖率
- 未覆盖的关键节点列表

### 4. 竞争分析
- 高频出现的竞品来源
- 竞品内容特点

### 5. 优化建议
- 应该新增的检索短语
- 应该优化的现有内容
- 内容缺口清单

## 执行规则

1. **递进逻辑必须自然** — 下一个问题必须从上一轮结果中逻辑推导出来
2. **平台差异化表达** — 同一意图在不同平台的表达方式不同（ChatGPT 偏口语对话，Google 偏关键词）
3. **至少 5 轮** — 一个完整旅程至少模拟 5 轮递进搜索
4. **实际执行搜索** — 每个检索短语都要实际用 web search 去查，不能编造结果
5. **来源必须标注** — 每条引用内容都标注 URL 和域名
6. **中英文双语** — 如果人物会使用中英文，模拟两种语言的搜索
7. **问题可修改** — 每轮生成检索短语后，先展示给用户确认，用户可以修改/替换/新增问题后再执行搜索

## 交互模式

智测支持两种模式：

### 模式 A：自动推演（Auto）
- 系统自动推演全部轮次，中间不停顿
- 适合快速出报告

### 模式 B：逐轮确认（Interactive）— 默认
- 每轮先展示推演出的检索短语
- 用户可以：
  - ✅ 确认 → 执行搜索
  - ✏️ 修改某个平台的问题
  - ➕ 新增一个问题
  - ❌ 删除某个问题
  - ⏭️ 跳过这一轮
- 确认后执行搜索，展示结果，再推演下一轮

## 输出路径

- 旅程数据: `output/zhice/journey_{persona_id}_{timestamp}.json`
- 检测报告: `output/zhice/zhice_report_{persona_id}_{timestamp}.csv`
- 汇总报告: `output/zhice/zhice_summary_{timestamp}.md`
