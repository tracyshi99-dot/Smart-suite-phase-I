# Smart Suite REST API

FastAPI wrapper for the Smart Suite pipeline engine. Runs independently alongside Streamlit UI.

## Quick Start

```bash
# Install dependencies (one-time)
pip install -r api/requirements.txt

# Run the API server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

API docs available at: http://localhost:8000/docs (Swagger UI)

## Architecture

```
Streamlit UI (port 8501)  ←──┐
FastAPI (port 8000)       ←──┼── engine.py ←── Bedrock Claude
MCP Server (stdio)        ←──┘
```

All three layers share the same `engine.py` and read/write to the same `output/` directory.

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Detailed health |
| POST | `/api/zhiku/run` | Run Step 1: AI query generation from keywords |
| POST | `/api/zhiku/expand` | Run Source B: Semantic expansion from seed word |
| POST | `/api/zhiku/upload-keywords` | Upload SEO/SEM keyword CSV |
| POST | `/api/zhizao/run` | Run Step 2: Content generation |
| POST | `/api/zhiyou/score` | Run Step 3: AI citation scoring |
| POST | `/api/zhiyou/rewrite` | Run Step 3.5: Content rewrite |
| POST | `/api/zhiyou/compliance` | Run Step 3.6: Compliance check |
| POST | `/api/zhiyou/full` | Run full optimization (score+rewrite+compliance) |
| POST | `/api/zhibu/run` | Run Step 4: JSON formatting |
| GET | `/api/zhibu/download/{batch_id}` | Download JSON output |
| POST | `/api/pipeline/run` | Run full pipeline (Steps 1-4) |
| GET | `/api/output/list` | List output files for a batch |
| GET | `/api/output/download` | Download any output file |
| GET | `/api/batches` | List all batches |

## Example Usage

```bash
# Generate AI queries from keywords
curl -X POST http://localhost:8000/api/zhiku/run \
  -H "Content-Type: application/json" \
  -d '{"batch_id": "batch_004", "market": "CN", "keyword_limit": 5}'

# Expand seed word
curl -X POST http://localhost:8000/api/zhiku/expand \
  -H "Content-Type: application/json" \
  -d '{"core_semantic": "跨境电商", "count": 20, "batch_id": "batch_004"}'

# Generate content
curl -X POST http://localhost:8000/api/zhizao/run \
  -H "Content-Type: application/json" \
  -d '{"batch_id": "batch_004", "content_limit": 3}'

# Full pipeline
curl -X POST http://localhost:8000/api/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{"batch_id": "batch_004", "market": "CN", "keyword_limit": 5, "content_limit": 3}'

# List outputs
curl http://localhost:8000/api/output/list?batch_id=batch_004

# Download JSON
curl http://localhost:8000/api/zhibu/download/batch_004 -o output.json
```
