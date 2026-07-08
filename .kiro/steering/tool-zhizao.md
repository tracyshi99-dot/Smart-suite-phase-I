---
inclusion: manual
---

# 智造 Content Creator

## Overview
Produces high-quality GEO-structured content at scale based on high-value search phrases from 智库. Each article follows the Direct Answer pattern, includes structured tables/lists/FAQ, and maximizes AI engine citation probability.

## Quick Start

Say any of these to execute:
- "执行智造 batch_004，生成内容"
- "执行 Step 2"
- "开始智造"

## Content Rules Reference
#[[file:.kiro/steering/content-rules.md]]
Enforce all 35 category data source restrictions and prohibited terms during content generation.

## Input
`output/{batch_id}/01_zhiku/zhiku_ai_queries.csv` (only records where `is_selected = TRUE`)

## Output
`output/{batch_id}/02_zhizao/zhizao_draft_content.csv`

## Knowledge Source (MANDATORY)
- ALL content must be grounded via 3PKC Knowledge Central MCP Server (`issca-3pkc-genai-mcp`)
- Use `search_knowledge` to search for relevant knowledge
- Use `type2_semantic_retrieval` for applied knowledge bundles
- **NEVER** use model training knowledge or external web search for article body
- If KMS has no relevant knowledge, mark as `knowledge_gap = TRUE` and skip

## Content Structure (per article)
```
Opening paragraph: pain point + keyword + value proposition (keyword in first 100 chars)

## H2 Title 1
[Core conclusion / direct answer - one sentence]
[Detailed explanation with lists or tables]

## H2 Title 2
[Core conclusion / direct answer]
[Detailed expansion]

## H2 Title 3
[Content with data/examples]

## FAQ
Q1 + A1 | Q2 + A2 | Q3 + A3

## Conclusion
[Summary + CTA to https://gs.amazon.cn]
```

## Quality Requirements
- Minimum 800 words per article
- At least 1 table, 2 lists, 3 FAQ items
- At least 2 natural insertions of https://gs.amazon.cn
- First paragraph must directly answer the AI query
- No competing brand mentions (Shopee, Lazada, TikTok, etc.)

## Output Fields
content_id, query_id, keyword_id, ai_query, title, meta_title, meta_description, target_audience, content_objective, content_draft, faq_section, cta, geo_summary, word_count, version, created_at
