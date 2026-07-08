# Smart Suite Harmony Builder Prompt

把以下 prompt 粘贴到 Harmony AI Builder (`beta.prototype.amazon.dev`) 的输入框里。

---

## Prompt (全部复制粘贴)

```
Build a full-featured React SPA called "Smart Suite" that replicates a Streamlit dashboard for an AI-powered SEO/GEO content production pipeline. The app needs a Python backend API (FastAPI on Lambda or included mock) for AI operations.

## CRITICAL REQUIREMENT: This app needs BOTH frontend AND backend
- Frontend: React + Vite + Tailwind
- Backend: A simple API layer that can call AWS Bedrock (Claude) for content generation
- If backend Lambda isn't possible, mock the API calls with realistic sample data

## DESIGN SYSTEM (must match exactly)
- Background: #0a0a0f (main), #12131a (cards), #1a1b25 (card hover)
- Borders: #1e2030
- Text: #fff (primary), #8892b0 (secondary), #5a6380 (tertiary)
- Font: system-ui, -apple-system, 'Segoe UI', 'Inter', sans-serif
- Card radius: 12px, border: 1px solid #1e2030
- Accent colors per module:
  - 智库: #ffa726
  - 智造: #ffcc02
  - 智优: #e91e63
  - 智布: #29b6f6
  - 智传: #26c6da
  - 智析: #ab47bc
  - 智中枢: gradient(#ff6b35, #e91e63, #2196f3)

## LAYOUT
- Fixed top header (height ~56px):
  - Left: Circular logo (44px, conic-gradient rainbow) with "智" text inside
  - Title "Smart Suite" with gradient text
  - Right: Language toggle button (中文/English)
- Left sidebar (width 240px, background #0f1117):
  - Radio-style navigation items with emoji + Chinese name
  - Batch selector dropdown (batch_001, batch_002, batch_003)
  - Market selector (ALL, CN, NA, EU, JP)
  - Keyword limit number input
  - Week text input (WK21)
- Main content area (scrollable)

## NAVIGATION ITEMS
🏠 总览, 📚 智库, ✍️ 智造, 🔧 智优, 📦 智布, 📡 智传, 📈 智析, 🎯 智中枢, � 智测, 🔮 智预, �📝 需求中心, ⚙️ Settings

## PAGE: 总览 (Overview)
- Embed an HTML wiki page (iframe or rendered HTML) showing the full Smart Suite documentation
- Include pipeline flow visualization: 智库 → 智造 → 智优 → 智布 → 智传 → 智析 → 智中枢
- Each step shows status (done/in-progress/pending) for the selected batch

## PAGE: 📚 智库 (Query Library)
This is the most complex page. Structure:

### Header
- Title "📚 智库 – AI 检索短语生成" with color #ffa726
- Subtitle "Step 1: 从 SEO/SEM 关键词或核心词根裂变生成 AI 原生检索短语"
- Pipeline flow bar showing current step highlighted

### Section ① 生成检索短语 (Generate Search Phrases)
Card with #1a1d2e background, contains two columns:

**Left column - Source A: SEO/SEM Keyword Expansion**
- File upload area (CSV only)
- Shows "165 个关键词 · 预估 ~1650 条" after upload
- Progress bar showing current/target (e.g., "库中 45/1650")
- Slider: "每次处理关键词数" (10, 20, 30, 50)
- Primary button "🚀 裂变源 A" (orange)

**Right column - Source B: Seed Word Expansion**
- Textarea for seed words (one per line), placeholder: "跨境电商\n亚马逊开店\n选品"
- Shows count "3 个词根 · 预估 ~45 条"
- Primary button "🚀 裂变源 B"

### Section ② 短语库 — 分类 & 校对
- Filter row: category dropdown + score range slider (1.0-5.0)
- Buttons: "✅ 全选", "⬜ 全不选"
- Editable data table with columns:
  - ai_query (text, wide)
  - category (dropdown with 35 options)
  - priority_score (number 1-5)
  - estimated_volume (number)
  - ai_fit_score (number)
  - target_market (dropdown: CN, WW, Both)
  - is_selected (checkbox)
- Export button "📥 导出筛选结果 CSV"

### Section: 📊 类别覆盖看板
- 4 metric cards: Total Phrases, Categories Covered (/35), Empty Categories, Selected Count
- Bar chart showing phrase count per category

### CTA Button
"➡️ 进入智造 (Step 2)" - navigates to 智造 page

## PAGE: ✍️ 智造 (Content Creation)
- Title with #ffcc02 color
- Pipeline flow (highlighting 智造)
- Upload area to skip 智库 (upload phrases directly)
- Table showing selected phrases from 智库

**Critical Level Config Panel (important!):**
- Show a config card at top with "Content Criticality Rules":
  - Critical=5 badge (red): "只读取官方网页 → 只能总结 → 不能自由发挥 → 禁止推测"
  - Categories #19,#20,#21,#23,#24,#25 auto-tagged as Critical=5
  - Critical=3/4 badge (yellow): "优先官方 + 允许行业通识补充"
- Quality scoring weights display (styled table):
  | 指标 | 权重 | 必须通过 |
  | 官方事实准确（政策、费用、品牌） | 40% | ✅ |
  | CTA和链接正确 | 25% | ✅ |
  | 与官方页面一致 | 15% | ✅ |
  | 是否覆盖目标Query Gap | 10% | ✅ |
  | 可读性/表达流畅 | 10% | ❌ |

- Execution section:
  - Progress bar "已生成 3/10 篇"
  - Number input "每批生成文章数" (1-20, default 5)
  - Button "🚀 执行智造" or "🔄 继续生成下一批 5 篇"
- Results section:
  - 3 metric cards: Articles Generated, Avg Word Count, Version
  - Data table: content_id, ai_query, title, word_count
  - Download/Upload/Clear buttons
  - Expandable article preview with editable text areas
  - Article confirmation checkboxes
- CTA "➡️ 进入智优 (Step 3)"

## PAGE: 🔧 智优 (Optimization)
- Title with #e91e63 color
- Pipeline flow (highlighting 智优)
- Upload area to skip previous steps
- Table showing confirmed content from 智造 (with "Include" checkboxes)
- One-click execution:
  - Progress bar showing optimization status
  - Button "🚀 一键智优全流程"
  - Executes 3 sub-steps: Score → Rewrite → Compliance
  - Each step shows progress percentage
- Results in expandable sections:
  - Scorecard table (article, score, breakdown)
  - Optimized content (before/after comparison)
  - Compliance results (pass/fail flags)
- CTA "➡️ 进入智布 (Step 4)"

## PAGE: 📦 智布 (Distribution)
- Title with #29b6f6 color
- Takes optimized content and formats to JSON for CMS
- Shows channel cards (CN, NA, EU, JP) with publish counts
- Button to generate distribution package
- JSON preview of output

## PAGE: 📈 智析 (Analytics)
- Title with #ab47bc color
- Weekly trend line chart (Recharts):
  - X-axis: WK17, WK18, WK19, WK20, WK21
  - Lines: CN_GEO (#ffa726), WW_GEO (#4caf50), WW_Direct (#29b6f6), Total (#e91e63)
  - Dark chart background matching theme
- YTD summary table:
  | Channel | YTD Actual | YTD PY | YoY |
  | CN GEO | 574 | 104 | +452% |
  | WW GEO | 364 | 188 | +94% |
  | WW Direct EST | 25,863 | 15,945 | +62% |
  | Total | 28,741 | 18,549 | +55% |
- Monthly breakdown table with M1-M5 columns
- Upload button to update metrics data (CSV)

## PAGE: 🔍 智测 (Testing - AI Search Simulation)
- Persona selector (dropdown with predefined personas)
- Platform checkboxes: ChatGPT, Perplexity, DeepSeek, 豆包, Kimi, 元宝, 通义千问
- Journey rounds display:
  - Each round shows: user mindset, query per platform, results summary
  - "Our content found" indicator (green/red)
  - Next question trigger explanation
- Coverage analysis summary

## PAGE: 🔮 智预 (Query Demand Forecaster)
Accent color: #ff9800. This module PREDICTS future search demand (complementary to 智测 which analyzes past).

### Header
- Title "🔮 智预 – Query Demand Forecaster" with color #ff9800
- Subtitle "推演未来 2-4 周即将爆发的检索需求，提前布局高价值 Query"
- Info banner: "智测看已发生的 Gap → 智预推演未发生但即将发生的需求"

### Section: 推演模式选择 (3 tabs)

**Tab 1: 信号驱动 (Signal-Driven)**
- Signal type dropdown: 政策变化, 产品上线, 市场事件, 竞品动态, 季节性
- Signal source text input (URL or description)
- Signal summary textarea
- Button "🔮 推演衍生 Query" (primary, orange)
- Results: table of predicted queries with columns:
  - query, language, confidence (0-1 progress bar), peak_window, reasoning
- Button "📤 导出到智库" to export high-confidence queries

**Tab 2: 生命周期推演 (Lifecycle Forecast)**
- Seller lifecycle stage selector (visual horizontal stepper):
  认知期 → 考虑期 → 决策期 → 注册期 → 新手期 → 成长期 → 成熟期 → 扩展期
- Persona selector (same as 智测)
- Target market: CN, NA, EU, JP
- Button "🔮 推演下一阶段需求"
- Results: cards showing predicted queries grouped by time window:
  - "注册后 1-3 天": query list with confidence bars
  - "注册后 3-7 天": query list
  - "注册后 1-2 周": query list

**Tab 3: 批量预测 (Batch Forecast)**
- Multi-signal input (add multiple signals)
- Multi-persona selection
- Button "🔮 批量推演"
- Results: priority-sorted table:
  | 排名 | Query | 综合分 | 置信度 | 壁垒等级 | 时间窗口 | 建议动作 |
- "一键全部导入智库" button

### Section: 推演历史 & 回测
- Historical forecasts list with accuracy tracking
- Each past forecast shows: predicted vs actual (did the query actually appear?)
- Accuracy rate metric card (e.g., "上月预测准确率 72%")

## DATA & STATE
- Use React context or Zustand for state management
- Store data in localStorage for persistence between sessions
- Sample data should be pre-loaded so the app looks functional immediately:
  - 智库: 20 sample search phrases with categories and scores
  - 智造: 4 sample articles with titles and word counts
  - 智析: Weekly metrics data (WK17-WK21)
  - 智预: 5 sample forecast signals with predicted queries and confidence scores
  - 智测: 1 sample journey with 3 rounds of search results

## INTERACTIONS
- All buttons should show loading spinners when "processing"
- Simulated delays (1-3 seconds) for AI operations to feel realistic
- Toast notifications for success/error states
- Data tables must be editable (inline edit, checkbox toggle)
- File upload must actually parse CSV and display contents
- Download buttons must generate real CSV files

## CHINESE LANGUAGE
- All UI text in Chinese by default
- English subtitles/labels where helpful
- Language toggle switches all text between 中文 and English
```
