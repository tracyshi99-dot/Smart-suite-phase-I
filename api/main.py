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


class PersonaExpansionRequest(BaseModel):
    identity: str
    company_type: str = ""
    marketplace: List[str] = []
    content_focus: List[str] = []
    count: int = 10
    language: str = "zh-CN"
    batch_id: str = "batch_001"


class UploadPhrasesRequest(BaseModel):
    phrases: List[str]
    source: str = "manual_upload"
    batch_id: str = "batch_001"


# --- Auth helper ---
def get_user_region(user: str) -> str:
    """Get user region from users.json (local or S3)."""
    import json
    data = _load_users_data()
    return data.get("user_region", {}).get(user, "CN")


def _load_users_data() -> dict:
    """Load users.json from local file or S3."""
    import json
    import os
    
    # Try local first
    users_file = Path(__file__).parent.parent / "output" / "users.json"
    if users_file.exists():
        return json.loads(users_file.read_text(encoding="utf-8"))
    
    # Try relative to current working dir (Lambda)
    users_file2 = Path("output") / "users.json"
    if users_file2.exists():
        return json.loads(users_file2.read_text(encoding="utf-8"))
    
    # Try S3
    try:
        import boto3
        bucket = os.environ.get("SMARTSUITE_S3_BUCKET", "smartsuite-sync-data")
        prefix = os.environ.get("SMARTSUITE_S3_PREFIX", "smartsuite/")
        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket=bucket, Key=f"{prefix}output/users.json")
        return json.loads(obj["Body"].read().decode("utf-8"))
    except Exception:
        pass
    
    return {"allowed": []}


# --- Health ---
@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


# --- Auth ---
@app.get("/api/auth/check")
def check_auth(user: str = Query(...)):
    """Check if user is allowed."""
    data = _load_users_data()
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
    import pandas as pd
    from datetime import datetime

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
    except Exception as e1:
        # Fallback: try direct Claude/Bedrock call
        try:
            from engine import call_bedrock_claude

            if req.language.startswith("zh"):
                prompt = f"""请为核心词「{req.seed_word}」生成 {req.count} 个检索短语。

关键规则：
1. 每条短语必须是15-40字的完整自然问句
2. 必须是问句形式（怎么/如何/什么/哪些/多少/为什么）
3. 模拟真实卖家在AI搜索平台上的对话式提问
4. 包含具体场景或限定条件
5. 禁止输出碎片关键词

每行一条，不要编号，不要解释。"""
            else:
                prompt = f"""Generate {req.count} natural question-format search phrases about '{req.seed_word}'.

Rules:
1. Each phrase must be a complete natural question, 10-30 words long
2. Must be in question form (How/What/Why/Can I/Is it/Do I need)
3. Include specific context (beginner/2026/small business)
4. Simulate real conversational queries, NOT keyword fragments

One phrase per line, no numbering, no explanation."""

            response = call_bedrock_claude(prompt)
            queries = [q.strip().lstrip("0123456789.-) ") for q in response.strip().split("\n") if q.strip() and len(q.strip()) > 10]

            if not queries:
                raise HTTPException(status_code=500, detail=f"No phrases generated. Engine error: {str(e1)}")

            # Save to CSV
            output_path = Path(__file__).parent.parent / "output"
            zhiku_file = output_path / req.batch_id / "01_zhiku" / "zhiku_ai_queries.csv"
            zhiku_file.parent.mkdir(parents=True, exist_ok=True)

            new_df = pd.DataFrame({
                "ai_query": queries,
                "source": f"seed_{req.seed_word}",
                "is_selected": "FALSE",
                "priority_score": 3.0,
                "intent_type": "",
                "estimated_volume": 0,
                "category": "",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })

            if zhiku_file.exists():
                existing = pd.read_csv(zhiku_file, encoding="utf-8-sig", on_bad_lines="skip")
                merged = pd.concat([existing, new_df], ignore_index=True)
                if "ai_query" in merged.columns:
                    merged = merged.drop_duplicates(subset=["ai_query"], keep="last")
            else:
                merged = new_df

            merged.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
            return {"success": True, "count": len(queries), "phrases": queries}
        except Exception as e2:
            raise HTTPException(status_code=500, detail=f"Expansion failed: {str(e1)} | Fallback failed: {str(e2)}")


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


@app.post("/api/zhiku/expand-persona")
def zhiku_expand_persona(req: PersonaExpansionRequest):
    """Expand phrases based on seller persona."""
    try:
        from engine import call_bedrock_claude
        import pandas as pd
        from datetime import datetime

        marketplace_str = ", ".join(req.marketplace) if req.marketplace else "US"
        content_str = ", ".join(req.content_focus) if req.content_focus else "Getting Started"

        if req.language.startswith("zh"):
            prompt = f"""请为以下画像的卖家推演 {req.count} 个他们在 AI 搜索引擎中最可能输入的检索短语。

画像：身份={req.identity}, 企业类型={req.company_type}, 目标站点={marketplace_str}, 关注内容={content_str}

要求：
1. 每条短语必须是15-40字的完整自然问句
2. 必须是问句形式（怎么/如何/什么/哪些/多少/为什么）
3. 模拟真实卖家在AI搜索平台上的对话式提问
4. 与该画像的身份、站点、关注内容高度相关
5. 每行一条，不要编号，不要解释"""
        else:
            prompt = f"""Generate {req.count} natural question-format search phrases that a seller with the following profile would type into AI search engines.

Profile: Identity={req.identity}, Company={req.company_type}, Target Marketplace={marketplace_str}, Content Focus={content_str}

Requirements:
1. Each phrase must be a complete natural question, 10-30 words long
2. Must be in question form (How/What/Why/Can I/Is it)
3. Include specific context relevant to the persona
4. One phrase per line, no numbering, no explanation"""

        response = call_bedrock_claude(prompt)
        queries = [q.strip().lstrip("0123456789.-) ") for q in response.strip().split("\n") if q.strip() and len(q.strip()) > 10]

        if not queries:
            raise HTTPException(status_code=500, detail="No phrases generated")

        # Save to zhiku CSV
        output_path = Path(__file__).parent.parent / "output"
        zhiku_file = output_path / req.batch_id / "01_zhiku" / "zhiku_ai_queries.csv"
        zhiku_file.parent.mkdir(parents=True, exist_ok=True)

        new_df = pd.DataFrame({
            "ai_query": queries,
            "source": f"persona_{req.identity}",
            "is_selected": "FALSE",
            "priority_score": 3.5,
            "intent_type": "",
            "estimated_volume": 0,
            "category": content_str.split(",")[0].strip() if content_str else "",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })

        if zhiku_file.exists():
            existing = pd.read_csv(zhiku_file, encoding="utf-8-sig", on_bad_lines="skip")
            merged = pd.concat([existing, new_df], ignore_index=True)
            if "ai_query" in merged.columns:
                merged = merged.drop_duplicates(subset=["ai_query"], keep="last")
        else:
            merged = new_df

        merged.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
        return {"success": True, "count": len(queries), "phrases": queries}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/zhiku/upload")
def zhiku_upload(req: UploadPhrasesRequest):
    """Upload phrases directly to the knowledge base."""
    import pandas as pd
    from datetime import datetime

    if not req.phrases:
        raise HTTPException(status_code=400, detail="No phrases provided")

    output_path = Path(__file__).parent.parent / "output"
    zhiku_file = output_path / req.batch_id / "01_zhiku" / "zhiku_ai_queries.csv"
    zhiku_file.parent.mkdir(parents=True, exist_ok=True)

    new_df = pd.DataFrame({
        "ai_query": req.phrases,
        "source": req.source,
        "is_selected": "TRUE",
        "priority_score": 3.0,
        "intent_type": "",
        "estimated_volume": 0,
        "category": "",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })

    if zhiku_file.exists():
        existing = pd.read_csv(zhiku_file, encoding="utf-8-sig", on_bad_lines="skip")
        merged = pd.concat([existing, new_df], ignore_index=True)
        if "ai_query" in merged.columns:
            merged = merged.drop_duplicates(subset=["ai_query"], keep="last")
    else:
        merged = new_df

    merged.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
    return {"success": True, "count": len(req.phrases)}


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
