---
inclusion: manual
---

# 智布&智传 Publisher & Distributor

## Overview
Converts optimized and compliance-checked content into LEGO CMS standard JSON format for multi-channel publishing. Handles format conversion, metadata population, and structured output generation.

## Quick Start

- "执行智布 batch_004，生成JSON"
- "执行 Step 4"
- "开始智布"

## Input
`output/{batch_id}/03_zhiyou/zhiyou_compliance_checked.csv` (only PASS/FIXED records)

## Output
`output/{batch_id}/04_zhibu/zhibu_output.json`

## JSON Structure

```json
{
  "batch_id": "batch_004",
  "created_at": "2026-06-24 17:00:00",
  "total_items": 0,
  "source_keywords": [],
  "items": [
    {
      "content_id": "",
      "query_id": "",
      "keyword_id": "",
      "meta": {"title": "", "description": ""},
      "structure": {"h1": "", "h2": [], "h3": []},
      "body": "[FULL optimized content]",
      "faq": [{"question": "", "answer": ""}],
      "cta": "",
      "geo_summary": "",
      "seo": {"keywords": [], "intent_type": "", "internal_links": ["https://gs.amazon.cn"]},
      "ai_friendly": {"intent_match_score": 0, "overall_score": 0.00},
      "compliance": {"status": "", "copyright": "Copyright © 2026 Amazon. All rights Reserved."},
      "quality_metrics": {"word_count": 0, "table_count": 0, "list_count": 0, "link_count": 0}
    }
  ]
}
```

## Rules
- `body` field must contain FULL optimized_content (not a summary)
- Include all 5 scoring dimensions in `ai_friendly`
- Include compliance status and copyright in `compliance`
- Maintain full traceability: keyword_id → query_id → content_id
- Use UTF-8 encoding
