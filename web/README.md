# Smart Suite Web (Next.js)

## Architecture

```
geo-smartsuite.app/
├── Frontend: Next.js 14 (App Router) + Tailwind CSS + shadcn/ui
├── Backend: FastAPI (Python) → AWS Lambda + API Gateway
├── Data: AWS S3 (smartsuite-sync-data bucket)
└── Auth: URL param → JWT (phase 2)
```

## Phase 1: FastAPI Backend
- Wraps engine.py into REST endpoints
- Deployed as Lambda function via API Gateway
- Endpoints: /api/zhiku, /api/zhice, /api/zhizao, /api/zhiyou, /api/zhibu, /api/zhixi

## Phase 2: Next.js Frontend (智库 first)
- Start with 智库 page as pilot
- Domain: geo-smartsuite.app (Vercel)
- Design: Reference from Protozoa prototype

## Migration Timeline
- Week 1: FastAPI backend + 智库 page
- Week 2: 智测 + 智造 pages
- Week 3: 智优 + 智布 + 智析 pages
- Week 4: Polish, testing, cutover

## Running Locally
```bash
# Backend
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd web
npm install
npm run dev
```
