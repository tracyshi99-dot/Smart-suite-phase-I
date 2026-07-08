---
inclusion: manual
---

# 智优 Content Optimizer

## Overview
Three-stage content optimization: (1) 5-dimension AI citation scoring, (2) automated rewriting based on score gaps, (3) Amazon legal compliance verification. Only content passing all checks proceeds to publishing.

## Quick Start

| Command | Action |
|---------|--------|
| "执行智优评分 batch_004" | Score only (Step 3) |
| "执行智优执行 batch_004" | Score + Rewrite (Step 3.5) |
| "执行合规审查 batch_004" | Compliance check (Step 3.6) |

## Content Rules Reference
#[[file:.kiro/steering/content-rules.md]]
Enforce all 35 category prohibited terms during compliance checking. Auto-delete sentences with violations.

## Stage 1: Scoring (Step 3)

**Input:** `output/{batch_id}/02_zhizao/zhizao_draft_content.csv`
**Output:** `output/{batch_id}/03_zhiyou/zhiyou_scorecard.csv`

### 5 Scoring Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Intent Match | 30% | Does it directly answer the AI query? Clear first-paragraph answer? |
| AI Readability | 20% | Easy for AI to parse? Clear structure (short paragraphs, lists, steps)? |
| Authority | 20% | Specific, verifiable info? Platform-specific knowledge? |
| Actionability | 20% | Clear next steps? Actionable guidance? |
| Differentiation | 10% | Unique vs generic content? Would AI prefer this? |

### Approval: overall_score >= 4.5 AND intent_match >= 4 AND authority >= 4

## Stage 2: Rewrite (Step 3.5)

**Input:** Draft content + Scorecard
**Output:** `output/{batch_id}/03_zhiyou/zhiyou_optimized_content.csv`
- Apply ALL suggestions from scorecard
- Must use 3PKC KMS for new information
- Output complete article (800-1500 words)

## Stage 3: Compliance (Step 3.6)

**Input:** `output/{batch_id}/03_zhiyou/zhiyou_optimized_content.csv`
**Output:** `output/{batch_id}/03_zhiyou/zhiyou_compliance_checked.csv`

### Key Compliance Rules
- Replace banned terms (站点→平台, 最好→领导者, etc.)
- Data citations must include source + year
- Registration guidance must reference "亚马逊卖家平台" not "全球开店官网"
- No undisclosed Amazon data (MAU, seller counts, GMS)
- Taiwan/HK/Macau must use "中国台湾/中国香港/中国澳门"
- Footer copyright: Copyright © 2026 Amazon. All rights Reserved.

### Status: PASS (no changes) / FIXED (auto-corrected) / BLOCKED (needs human review)

## Auto-Routing After Compliance

After Step 3.6 completes for ALL articles:

### Critical 3-4 categories (AI-智优 review only):
- PASS/FIXED → Ready for next step (waiting in pool)

### Critical 5 categories (POC Manual Review required):
Categories: #19, #20, #21, #23, #24, #25

**Automatic flow:**
1. 智优 completes ALL steps (score → rewrite → compliance) for ALL articles including Critical-5
2. Critical-5 articles auto-submit to `output/review/review_queue.csv` for POC review
3. POC receives link: `http://rem-5cg31524zw.ant.amazon.com:8502/?reviewer={name}`
4. POC reviews → edits if needed → clicks Approve
5. Approved articles return to 智优's "ready pool"

### Final Step in 智优:
- 智优 page shows combined list: all PASS/FIXED articles (Critical 3-4) + all POC-APPROVED articles (Critical 5)
- User clicks "Next Step → 智布" to send ALL approved articles together to Step 4
- Only when ALL Critical-5 POC reviews are complete can user proceed

### POC Assignment:
| Category | POC |
|----------|-----|
| #19 新手怎么注册亚马逊 | Murphy |
| #20 亚马逊开店成本费用详解 | Joyce |
| #21 开店审核常见问题解答 | Eva Zheng |
| #23 欧洲增值税VAT介绍 | Eva Zheng |
| #24 其他站点税务要求 | Eva Zheng |
| #25 合规政策及操作流程 | Eva Zheng |
