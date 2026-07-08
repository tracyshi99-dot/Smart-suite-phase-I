---
inclusion: manual
---

# 智库 Prompt Intelligencer

## Overview
Connects to mainstream AI search platforms (ChatGPT, Gemini, Perplexity, DeepSeek, Doubao, Kimi, etc.) to capture real-time, high-precision search phrases and generate structured queries with high citation probability.

## Quick Start

Say any of these to execute:
- "执行智库 batch_004，market=ALL，keyword_limit=10"
- "执行 Step 1"
- "开始智库"

## Input
`input/seo_sem_keywords.csv`

## Output
`output/{batch_id}/01_zhiku/zhiku_ai_queries.csv`

## Output Fields
- keyword_id, keyword, query_id, ai_query
- intent_type: informational / navigational / transactional / comparison
- query_type: branded / generic / industry / conversion-oriented
- priority_score: 1–5
- language, market, is_selected, created_at

## Execution Rules

1. Read keywords from input CSV
2. Generate multiple AI-native search queries per keyword
3. Score and rank queries by priority (1-5)
4. Only high-quality queries set `is_selected = TRUE`
5. Save output locally before next step

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| batch_id | batch_004 | Current batch identifier |
| market | ALL | Target market (ALL/CN/NA/EU/JP) |
| keyword_limit | 10 | Max keywords to process |

## Connected Platforms
ChatGPT, Gemini, Perplexity, DeepSeek, Doubao (豆包), Kimi, Yuanbao (元宝), Qianwen (通义千问)
