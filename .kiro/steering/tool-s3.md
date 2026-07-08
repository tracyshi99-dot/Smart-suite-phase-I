---
inclusion: manual
---

# S3 Memory Keeper

## Overview
AWS S3-based persistent knowledge storage layer serving as the unified data foundation for all Smart Suite modules. Provides version-controlled storage, cross-module data sharing, and batch archival.

## Quick Start

| Command | Action |
|---------|--------|
| "同步 batch_004 数据到 S3" | Upload batch data to cloud |
| "从 S3 下载最新 batch 数据" | Download latest from cloud |
| "列出 S3 上的所有 batch" | List available batches in S3 |

## Storage Structure
```
s3://smartsuite-data/
├── input/                    # Source keywords
├── batches/
│   ├── batch_001/
│   │   ├── 01_zhiku/
│   │   ├── 02_zhizao/
│   │   ├── 03_zhiyou/
│   │   └── 04_zhibu/
│   ├── batch_002/
│   └── ...
├── metrics/                  # Performance data
│   ├── geo_weekly_data.csv
│   ├── geo_monthly_data.csv
│   └── zhixi_reports/
└── archive/                  # Historical versions
```

## Configuration
- Bucket: `smartsuite-data`
- Region: Configured via AWS credentials
- Credentials: `ui/refresh_creds.ps1` for STS token refresh

## Rules
- All uploads use UTF-8 encoding
- Version tagging on each upload (timestamp-based)
- Never overwrite — always create new version
- Cross-module references use S3 paths
