# SmartSuite Console - 快速开始

## 前提
- 已安装 Python 3.12+
- 已 clone 本项目

## 一键启动

在 PowerShell 或 Kiro Terminal 中运行：

```powershell
.\ui\setup_and_run.ps1
```

首次会自动安装依赖（约 30 秒），之后每次启动只需几秒。

浏览器自动打开 `http://localhost:8501`

## AWS 凭证（执行智库/智造等功能需要）

运行前确保 AWS credentials 有效：

```powershell
ada credentials update --account 830279064391 --provider conduit --role IibsAdminAccess-DO-NOT-DELETE --once --profile default
```

或者在 `ui/.streamlit/secrets.toml` 中配置：

```toml
[aws]
access_key_id = "你的AK"
secret_access_key = "你的SK"
region = "us-east-1"
```

## 功能
- 智库：AI 检索短语生成
- 智造：内容生产
- 智优：评分 + 优化
- 智布：JSON 格式化发布
- 智测：AI 搜索旅程模拟
- 智析：数据分析报表
