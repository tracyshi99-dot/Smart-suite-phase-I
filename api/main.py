"""
Smart Suite FastAPI Backend
Wraps engine.py into REST endpoints for Next.js frontend.
Deployed via AWS Lambda + API Gateway using Mangum.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sys
from pathlib import Path
from mangum import Mangum

# Add parent dir for engine imports
sys.path.insert(0, str(Path(__file__).parent.parent / "ui"))

app = FastAPI(title="Smart Suite API", version="2.0.0")

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://geo-smartsuite.app",
        "https://smartsuite-geo.vercel.app",
        "https://smartsuite-geo-cngs.vercel.app",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Models ---
class SeedExpansionRequest(BaseModel):
    seed_word: str
    count: int = 15
    language: str = "zh-CN"
    market: str = "CN"
    batch_id: str = "batch_001"


class ZhiceRequest(BaseModel):
    phrases: List[str]
    platforms: List[str] = ["deepseek", "qianwen"]
    user: str = ""


class ZhizaoRequest(BaseModel):
    batch_id: str
    content_limit: int = 5
    content_language: str = "zh-CN"
    template_id: str = "auto"


class ZhiyouRequest(BaseModel):
    batch_id: str
    content_language: str = "zh-CN"


# --- Auth helper ---
def get_user_region(user: str) -> str:
    """Get user region from users.json."""
    import json
    users_file = Path(__file__).parent.parent / "output" / "users.json"
    if users_file.exists():
        data = json.loads(users_file.read_text(encoding="utf-8"))
        return data.get("user_region", {}).get(user, "CN")
    return "CN"


# --- Health ---
@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


# --- Auth ---
@app.get("/api/auth/check")
def check_auth(user: str = Query(...)):
    """Check if user is allowed."""
    import json
    users_file = Path(__file__).parent.parent / "output" / "users.json"
    if users_file.exists():
        data = json.loads(users_file.read_text(encoding="utf-8"))
        allowed = data.get("allowed", [])
        if user.lower() in [u.lower() for u in allowed]:
            region = data.get("user_region", {}).get(user.lower(), "CN")
            sub_region = data.get("user_sub_region", {}).get(user.lower(), "")
            is_admin = user.lower() in data.get("admins", [])
            return {
                "allowed": True,
                "user": user.lower(),
                "region": region,
                "sub_region": sub_region,
                "is_admin": is_admin,
            }
    return {"allowed": False, "user": user}


# --- 智库 ---
@app.post("/api/zhiku/expand")
def zhiku_expand(req: SeedExpansionRequest):
    """Expand a seed word into AI search phrases."""
    try:
        from engine import run_semantic_expansion
        result = run_semantic_expansion(
            core_semantic=req.seed_word,
            market=req.market,
            count=req.count,
            language=req.language,
            batch_id=req.batch_id,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/zhiku/phrases")
def zhiku_get_phrases(batch_id: str = "batch_001", user: str = ""):
    """Get current phrase list for a batch."""
    import pandas as pd
    output_path = Path(__file__).parent.parent / "output"
    zhiku_file = output_path / batch_id / "01_zhiku" / "zhiku_ai_queries.csv"
    if not zhiku_file.exists():
        return {"phrases": [], "total": 0}
    df = pd.read_csv(zhiku_file, encoding="utf-8-sig", on_bad_lines="skip")
    # Filter out ahrefs for CN users
    region = get_user_region(user) if user else "CN"
    if region == "CN" and "source" in df.columns:
        df = df[~df["source"].astype(str).str.lower().str.contains("ahrefs", na=False)]
    phrases = df.to_dict(orient="records")
    return {"phrases": phrases, "total": len(phrases)}


@app.post("/api/zhiku/select")
def zhiku_select(batch_id: str, indices: List[int], selected: bool = True):
    """Select/deselect phrases by index."""
    import pandas as pd
    output_path = Path(__file__).parent.parent / "output"
    zhiku_file = output_path / batch_id / "01_zhiku" / "zhiku_ai_queries.csv"
    if not zhiku_file.exists():
        raise HTTPException(status_code=404, detail="Phrase file not found")
    df = pd.read_csv(zhiku_file, encoding="utf-8-sig", on_bad_lines="skip")
    for idx in indices:
        if 0 <= idx < len(df):
            df.iloc[idx, df.columns.get_loc("is_selected")] = "TRUE" if selected else "FALSE"
    df.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
    return {"success": True, "updated": len(indices)}


# --- 智测 ---
@app.post("/api/zhice/verify")
def zhice_verify(req: ZhiceRequest):
    """Run AI platform verification on phrases."""
    # This would call the zhice verification logic
    # For now return structure
    return {"status": "pending", "message": "Verification queued", "phrases": len(req.phrases), "platforms": req.platforms}


# --- 智造 ---
@app.post("/api/zhizao/generate")
def zhizao_generate(req: ZhizaoRequest):
    """Generate content for selected phrases."""
    try:
        from engine import run_zhizao
        result = run_zhizao(
            batch_id=req.batch_id,
            content_limit=req.content_limit,
            content_language=req.content_language,
            template_id=req.template_id,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- 智优 ---
@app.post("/api/zhiyou/score")
def zhiyou_score(req: ZhiyouRequest):
    """Score content for AI citation likelihood."""
    try:
        from engine import run_zhiyou_score
        result = run_zhiyou_score(batch_id=req.batch_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/zhiyou/optimize")
def zhiyou_optimize(req: ZhiyouRequest):
    """Rewrite and optimize content."""
    try:
        from engine import run_zhiyou_execute
        result = run_zhiyou_execute(batch_id=req.batch_id, content_language=req.content_language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- 智析 ---
@app.get("/api/zhixi/monthly")
def zhixi_monthly():
    """Get monthly GEO metrics."""
    import pandas as pd
    metrics_path = Path(__file__).parent.parent / "output" / "metrics"
    monthly_file = metrics_path / "geo_monthly_data.csv"
    if not monthly_file.exists():
        return {"data": [], "columns": []}
    df = pd.read_csv(monthly_file, encoding="utf-8-sig")
    return {"data": df.to_dict(orient="records"), "columns": df.columns.tolist()}


@app.get("/api/zhixi/citations")
def zhixi_citations():
    """Get citation tracking data."""
    import pandas as pd
    metrics_path = Path(__file__).parent.parent / "output" / "metrics"
    gap_file = metrics_path / "gap_verification_cn.csv"
    if not gap_file.exists():
        return {"data": [], "total": 0}
    df = pd.read_csv(gap_file, encoding="utf-8-sig")
    return {"data": df.to_dict(orient="records"), "total": len(df)}


@app.get("/api/zhixi/summary")
def zhixi_summary():
    """Get GEO input summary metrics."""
    import pandas as pd
    metrics_path = Path(__file__).parent.parent / "output" / "metrics"
    summary_file = metrics_path / "geo_input_summary.csv"
    if not summary_file.exists():
        return {"data": []}
    df = pd.read_csv(summary_file, encoding="utf-8-sig")
    return {"data": df.to_dict(orient="records")}


# --- Lambda Handler ---
handler = Mangum(app, lifespan="off")
