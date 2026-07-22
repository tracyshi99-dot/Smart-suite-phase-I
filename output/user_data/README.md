# User Data Directory

Each subfolder is named by the user's login and contains their operation history:

```
user_data/
├── fanting/
│   ├── 01_zhiku/zhiku_ai_queries.csv    # 智库短语
│   ├── 02_zhizao/zhizao_draft_content.csv  # 智造文章
│   ├── 03_zhiyou/...                    # 智优结果
│   └── requests/                        # 智析数据/需求
├── czhaamzn/
│   └── ...
└── ...
```

This data is automatically synced from S3 (`s3://smartsuite-sync-data/user_data/`).
Do NOT manually edit these files — they are overwritten by the sync process.
