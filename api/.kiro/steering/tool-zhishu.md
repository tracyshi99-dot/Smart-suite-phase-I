---
inclusion: manual
---

# 智中枢 Workflow Orchestrator

## Overview
Central orchestration hub that connects 智库→智造→智优→智布→智析 into a complete E2E pipeline. Built-in 7-rule decision engine automatically generates weekly action plans based on performance data.

## Quick Start

| Command | Action |
|---------|--------|
| "智中枢决策 WK25" | Generate weekly decision plan |
| "本周该做什么" | Same as above (Chinese trigger) |
| "全流程执行 batch_004" | Run full pipeline Steps 1→5 |
| "智中枢 Gap 分析" | Identify content gaps |

## 7 Decision Rules

### Rule 1: Growth Acceleration
```
IF channel WoW > +30% for 2+ consecutive weeks
→ Increase content production for that channel
ACTION: Run 智库 + 智造, +5 keywords next batch
PRIORITY: High
```

### Rule 2: Decline Alert
```
IF channel WoW < -20%
→ Pause new content, investigate cause
ACTION: Generate attribution analysis
PRIORITY: High
```

### Rule 3: Low Absolute Volume
```
IF GEO weekly < 50 AND YoY > +50%
→ Strategy working but scale small, expand coverage
ACTION: Run 智库 to expand keyword list
PRIORITY: Medium
```

### Rule 4: High-Performing Site Expansion
```
IF site YoY > +100%
→ Prioritize content expansion for that site
ACTION: Allocate 30%+ keywords to that site
PRIORITY: High
```

### Rule 5: Content Gap Detection
```
IF market has traffic but no content produced in 2 weeks
→ Pipeline stalled, restart production
ACTION: Run full pipeline for that market
PRIORITY: Medium
```

### Rule 6: Benchmark Comparison
```
IF our YoY < SSR benchmark YoY
→ Underperforming, strategy review needed
ACTION: Generate gap analysis, new keyword angles
PRIORITY: Critical

BPS Formula: (Our YoY% - SSR YoY%) × 100
Current YTD: +65% vs -19% = +84 ppts = +8,400 bps
Target: Maintain positive BPS every month
Alert: If weekly BPS < 0 for 2+ consecutive weeks → Escalate
```

### Rule 7: Input-Output Lag Check
```
IF content published 2-3 weeks ago AND no GEO/Direct lift
→ Content may not be indexed by AI engines
ACTION: Review quality scores, consider rewrite
PRIORITY: Medium
```

## Output Format
```
📋 Smart Suite Weekly Plan - WK[XX]

🟢 ACCELERATE:
- [Channel]: [Reason] → [Action]

🔴 INVESTIGATE:
- [Channel]: [Reason] → [Action]

📝 EXECUTION PLAN:
- 智库: [X] keywords for [Market]
- 智造: [X] articles targeting [Topic]
- 智优: Review [X] articles
- 智布: Publish [X] articles

⏰ ESTIMATED TIME: [X] hours
```

## Full Pipeline Execution Order
1. 智库 (query generation) → Review output
2. 智造 (content creation) → Review output
3. 智优评分 (scoring) → Review scores
4. 智优执行 (rewrite) → Review optimized content
5. 合规审查 (compliance) → Review compliance status
6. 智布 (JSON formatting) → Verify JSON
7. Batch Report (summary) → Done
