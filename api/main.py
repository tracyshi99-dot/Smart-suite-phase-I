"""
Smart Suite FastAPI Backend
Wraps engine.py into REST endpoints for Next.js frontend.
Deployed via AWS Lambda + API Gateway using Mangum.
"""
from fastapi import FastAPI, HTTPException, Query, Header, Request
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
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Auto-log POST actions to user workspace ---
@app.middleware("http")
async def log_actions_middleware(request: Request, call_next):
    """Automatically log POST actions to user's S3 workspace."""
    response = await call_next(request)
    # Only log successful POST/PUT actions (not GET, not errors)
    if request.method in ("POST", "PUT") and response.status_code == 200:
        user = request.headers.get("x-user", "")
        if user and "/api/user/log" not in str(request.url):
            path = request.url.path
            action = path.split("/api/")[-1].replace("/", "_") if "/api/" in path else "unknown"
            try:
                from s3_storage import user_log_action
                user_log_action(user.lower(), action, {"endpoint": path})
            except Exception:
                pass
    return response


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
def _log_user_action_safe(user: str, action: str, details: dict = None):
    """Best-effort log to user workspace. Never raises."""
    if not user:
        return
    try:
        from s3_storage import user_log_action
        user_log_action(user.lower(), action, details or {})
    except Exception:
        pass


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
    """Expand a seed word into AI search phrases. Uses direct Bedrock call for speed."""
    import pandas as pd
    from datetime import datetime

    # Direct Bedrock call (fast, single API call, same as Streamlit)
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
        import re as _re_seed
        queries = [_re_seed.sub(r"^\d+[\.\)\-\s]+", "", q.strip()) for q in response.strip().split("\n") if q.strip() and len(q.strip()) > 10]

        if not queries:
            raise HTTPException(status_code=500, detail="No phrases generated")

        # Save to S3 (persistent)
        try:
            from s3_storage import read_csv, write_csv

            # Dynamic scoring - Query Intelligence Framework
            def _score(q):
                s = 3.0
                if 15 <= len(q) <= 30: s += 0.5
                elif len(q) > 30: s += 0.3
                if any(w in q for w in ["怎么","如何","多少","哪些","为什么","什么","能不能","how","what","why","which","can"]): s += 0.5
                if any(w in q.lower() for w in ["亚马逊","amazon","fba","注册","开店","选品","物流","广告","listing"]): s += 0.5
                if any(w in q for w in ["吗","呢","啊","吧","?","？"]): s += 0.3
                if any(w in q for w in ["新手","小白","2026","2025","中国卖家","美国站","欧洲站","日本站","beginner"]): s += 0.3
                if any(w in q for w in ["vs","还是","区别","对比","哪个好","应该","值得","适合","推荐","最好","compare","recommend"]): s += 0.3
                return min(5.0, round(s, 1))

            new_df = pd.DataFrame({
                "ai_query": queries,
                "source": f"seed_{req.seed_word}",
                "is_selected": "FALSE",
                "priority_score": [_score(q) for q in queries],
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            existing = read_csv(req.batch_id, "01_zhiku", "zhiku_ai_queries.csv")
            if not existing.empty:
                merged = pd.concat([existing, new_df], ignore_index=True).drop_duplicates(subset=["ai_query"], keep="last")
            else:
                merged = new_df
            write_csv(req.batch_id, "01_zhiku", "zhiku_ai_queries.csv", merged)
        except Exception:
            pass  # S3 save is best-effort; phrases are returned in response

        return {"success": True, "count": len(queries), "phrases": queries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/zhiku/phrases")
def zhiku_get_phrases(batch_id: str = "batch_001", user: str = ""):
    """Get current phrase list for a batch from S3."""
    try:
        from s3_storage import read_csv
        import numpy as np
        import pandas as pd
        df = read_csv(batch_id, "01_zhiku", "zhiku_ai_queries.csv")
        if df.empty:
            return {"phrases": [], "total": 0}
        # Replace NaN/inf with defaults to prevent JSON serialization errors
        df = df.fillna("")
        df = df.replace([np.inf, -np.inf], 0)
        # Ensure priority_score is numeric
        if "priority_score" in df.columns:
            df["priority_score"] = pd.to_numeric(df["priority_score"], errors="coerce").fillna(3.0)
        # Filter out ahrefs for CN users
        try:
            region = get_user_region(user) if user else "CN"
        except Exception:
            region = "CN"
        if region == "CN" and "source" in df.columns:
            df = df[~df["source"].astype(str).str.lower().str.contains("ahrefs", na=False)]
        phrases = df.to_dict(orient="records")
        return {"phrases": phrases, "total": len(phrases)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"zhiku_get_phrases error: {str(e)}")


class SelectRequest(BaseModel):
    batch_id: str
    indices: List[int]
    selected: bool = True


@app.post("/api/zhiku/select")
def zhiku_select(req: SelectRequest):
    """Select/deselect phrases by index. Persists to S3."""
    from s3_storage import read_csv, write_csv
    df = read_csv(req.batch_id, "01_zhiku", "zhiku_ai_queries.csv")
    if df.empty:
        raise HTTPException(status_code=404, detail="Phrase file not found")
    if "is_selected" not in df.columns:
        df["is_selected"] = "FALSE"
    for idx in req.indices:
        if 0 <= idx < len(df):
            df.iloc[idx, df.columns.get_loc("is_selected")] = "TRUE" if req.selected else "FALSE"
    write_csv(req.batch_id, "01_zhiku", "zhiku_ai_queries.csv", df)
    return {"success": True, "updated": len(req.indices)}


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
        import re as _re_persona
        queries = [_re_persona.sub(r"^\d+[\.\)\-\s]+", "", q.strip()) for q in response.strip().split("\n") if q.strip() and len(q.strip()) > 10]

        if not queries:
            raise HTTPException(status_code=500, detail="No phrases generated")

        # Save to S3
        try:
            from s3_storage import read_csv, write_csv

            def _score_p(q):
                s = 3.5
                if 10 <= len(q) <= 25: s += 0.5
                elif len(q) > 25: s += 0.3
                if any(w in q for w in ["怎么","如何","多少","哪些","为什么","什么","能不能","how","what","why"]): s += 0.5
                if any(w in q.lower() for w in ["亚马逊","amazon","fba","注册","开店","选品","物流","广告"]): s += 0.3
                if any(w in q for w in ["吗","呢","啊","吧","?","？"]): s += 0.2
                return min(5.0, round(s, 1))

            new_df = pd.DataFrame({
                "ai_query": queries,
                "source": f"persona_{req.identity}",
                "is_selected": "FALSE",
                "priority_score": [_score_p(q) for q in queries],
                "intent_type": "",
                "estimated_volume": 0,
                "category": content_str.split(",")[0].strip() if content_str else "",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            existing = read_csv(req.batch_id, "01_zhiku", "zhiku_ai_queries.csv")
            if not existing.empty:
                merged = pd.concat([existing, new_df], ignore_index=True).drop_duplicates(subset=["ai_query"], keep="last")
            else:
                merged = new_df
            write_csv(req.batch_id, "01_zhiku", "zhiku_ai_queries.csv", merged)
        except Exception:
            pass  # S3 save best-effort

        return {"success": True, "count": len(queries), "phrases": queries}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/zhiku/upload")
def zhiku_upload(req: UploadPhrasesRequest):
    """Upload phrases directly to the knowledge base via S3."""
    import pandas as pd
    from datetime import datetime
    from s3_storage import read_csv, write_csv

    if not req.phrases:
        raise HTTPException(status_code=400, detail="No phrases provided")

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

    existing = read_csv(req.batch_id, "01_zhiku", "zhiku_ai_queries.csv")
    if not existing.empty:
        merged = pd.concat([existing, new_df], ignore_index=True)
        if "ai_query" in merged.columns:
            merged = merged.drop_duplicates(subset=["ai_query"], keep="last")
    else:
        merged = new_df

    write_csv(req.batch_id, "01_zhiku", "zhiku_ai_queries.csv", merged)
    return {"success": True, "count": len(req.phrases)}


# --- Archive & Restore ---
class ArchiveRequest(BaseModel):
    batch_id: str
    step: str  # e.g., "01_zhiku", "zhice", "02_zhizao"
    filename: str = "zhiku_ai_queries.csv"
    indices: List[int] = []  # indices to archive (empty = all)


class RestoreRequest(BaseModel):
    batch_id: str
    step: str
    filename: str = "zhiku_ai_queries.csv"
    queries: List[str] = []  # ai_query values to restore (empty = all)


@app.post("/api/archive")
def archive_items_endpoint(req: ArchiveRequest):
    """Archive selected items (move to _archived.csv in S3)."""
    from s3_storage import read_csv, write_csv, archive_items
    import pandas as pd

    df = read_csv(req.batch_id, req.step, req.filename)
    if df.empty:
        raise HTTPException(status_code=404, detail="No data found")

    if req.indices:
        mask = pd.Series([False] * len(df))
        for idx in req.indices:
            if 0 <= idx < len(df):
                mask.iloc[idx] = True
    else:
        mask = pd.Series([True] * len(df))

    df_to_archive = df[mask]
    df_remaining = df[~mask]

    if df_to_archive.empty:
        return {"success": True, "archived": 0}

    archive_items(req.batch_id, req.step, req.filename, df_to_archive)
    write_csv(req.batch_id, req.step, req.filename, df_remaining)

    return {"success": True, "archived": len(df_to_archive), "remaining": len(df_remaining)}


@app.get("/api/archive")
def get_archived_items(batch_id: str = "batch_001", step: str = "01_zhiku"):
    """Get archived items for a step."""
    from s3_storage import get_archived
    df = get_archived(batch_id, step)
    if df.empty:
        return {"items": [], "total": 0}
    return {"items": df.to_dict(orient="records"), "total": len(df)}


@app.post("/api/restore")
def restore_items_endpoint(req: RestoreRequest):
    """Restore items from archive back to main file."""
    from s3_storage import restore_items
    merged = restore_items(req.batch_id, req.step, req.filename, req.queries)
    return {"success": True, "total": len(merged)}


@app.post("/api/zhiku/rescore")
def zhiku_rescore(batch_id: str = "batch_001"):
    """Rescore all phrases in a batch using the dynamic scoring algorithm."""
    from s3_storage import read_csv, write_csv

    df = read_csv(batch_id, "01_zhiku", "zhiku_ai_queries.csv")
    if df.empty:
        return {"success": True, "rescored": 0}

    def _score(q):
        q = str(q)
        s = 3.0
        if 15 <= len(q) <= 30: s += 0.5
        elif len(q) > 30: s += 0.3
        if any(w in q for w in ["怎么","如何","多少","哪些","为什么","什么","能不能","how","what","why","which","can"]): s += 0.5
        if any(w in q.lower() for w in ["亚马逊","amazon","fba","注册","开店","选品","物流","广告","listing"]): s += 0.5
        if any(w in q for w in ["吗","呢","啊","吧","?","？"]): s += 0.3
        if any(w in q for w in ["新手","小白","2026","2025","中国卖家","美国站","欧洲站","日本站","beginner"]): s += 0.3
        if any(w in q for w in ["vs","还是","区别","对比","哪个好","应该","值得","适合","推荐","最好","compare","recommend"]): s += 0.3
        return min(5.0, round(s, 1))

    if "ai_query" in df.columns:
        df["priority_score"] = df["ai_query"].apply(_score)
        write_csv(batch_id, "01_zhiku", "zhiku_ai_queries.csv", df)

    return {"success": True, "rescored": len(df)}


# --- 智测 ---
@app.post("/api/zhice/verify")
def zhice_verify(req: ZhiceRequest):
    """Run AI platform verification on phrases."""
    try:
        from engine import call_claude
    except ImportError:
        # Fallback: return simulated results if engine not available
        results = []
        for phrase in req.phrases:
            for platform in req.platforms:
                results.append({
                    "query": phrase,
                    "platform": platform,
                    "has_official_link": False,
                    "has_brand_mention": False,
                    "answer_preview": "Engine unavailable",
                    "error": "call_claude not available",
                })
        return {"status": "error", "message": "Engine not available", "results": results}

    import concurrent.futures

    BRAND_KEYWORDS = [
        "\u4e9a\u9a6c\u900a", "\u5168\u7403\u5f00\u5e97", "Amazon", "amazon",
        "Global Selling", "Seller Central", "\u5356\u5bb6\u5e73\u53f0",
        "FBA", "\u4e9a\u9a6c\u900a\u7269\u6d41", "Amazon Global",
        "gs.amazon", "sell.amazon",
    ]

    COMPETITOR_KEYWORDS = {
        "Shopee": ["shopee", "\u867e\u76ae"],
        "TikTok Shop": ["tiktok shop", "tiktok", "\u6296\u97f3\u7535\u5546"],
        "Alibaba": ["alibaba", "\u963f\u91cc\u5df4\u5df4", "1688", "\u901f\u5356\u901a", "aliexpress"],
        "eBay": ["ebay"],
        "Walmart": ["walmart", "\u6c83\u5c14\u739b"],
        "Temu": ["temu", "\u62fc\u591a\u591a\u8de8\u5883"],
    }

    def verify_one(phrase: str, platform: str) -> dict:
        answer = ""
        try:
            system_prompt = f"\u4f60\u662f AI \u641c\u7d22\u5f15\u64ce {platform}\u3002\u7528100\u5b57\u4ee5\u5185\u56de\u7b54\u5356\u5bb6\u7684\u95ee\u9898\u3002"
            answer = call_claude(system_prompt, phrase, max_tokens=200)
        except Exception:
            answer = ""

        answer_lower = answer.lower() if answer else ""
        has_brand = any(kw.lower() in answer_lower for kw in BRAND_KEYWORDS) if answer else False
        has_link = ("amazon" in answer_lower or "gs.amazon" in answer_lower or "sell.amazon" in answer_lower) if answer else False

        return {
            "query": phrase,
            "platform": platform,
            "has_official_link": has_link,
            "has_brand_mention": has_brand,
            "answer_preview": answer[:120] if answer else "",
        }

    # Run verifications in parallel (max 5 concurrent) to stay within timeout
    results = []
    tasks = [(phrase, platform) for phrase in req.phrases for platform in req.platforms]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(verify_one, phrase, platform): (phrase, platform) for phrase, platform in tasks}
        for future in concurrent.futures.as_completed(futures):
            try:
                results.append(future.result())
            except Exception:
                phrase, platform = futures[future]
                results.append({
                    "query": phrase,
                    "platform": platform,
                    "has_official_link": False,
                    "has_brand_mention": False,
                    "answer_preview": "",
                    "error": "timeout",
                })

    return {"status": "success", "results": results}


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


# --- Agent Chat ---
class ChatRequest(BaseModel):
    message: str
    user: str = ""
    batch_id: str = "batch_001"
    history: List[dict] = []


@app.post("/api/chat/stream")
def chat_stream(req: ChatRequest):
    """Chat endpoint - detects action intent and executes Smart Suite operations."""
    try:
        from engine import call_bedrock_claude
        import re

        message_lower = req.message.lower()

        # === INTENT DETECTION ===
        # Priority order: compliance > scoring > content > phrases > decision > general

        compliance_keywords = ["合规", "审核", "compliance", "legal check", "走合规", "合规检查", "pre-legal"]
        scoring_keywords = ["评分", "打分", "智优评分", "score", "rate this", "这篇怎么样", "质量"]
        content_keywords = ["创建内容", "生成内容", "写文章", "创建文章", "generate content", "write article", "create content", "对应内容", "文章内容", "创建一篇", "帮忙创建", "对应的内容", "执行智造", "智造"]
        expand_keywords = ["检索短语", "裂变", "生成短语", "expand phrases", "搜索词", "热度高的", "智库", "扩词"]
        decision_keywords = ["本周计划", "该做什么", "智中枢", "决策", "weekly plan", "周计划"]
        zhice_keywords = ["智测", "覆盖检测", "验证", "跑一轮", "coverage", "verify"]

        wants_compliance = any(kw in message_lower for kw in compliance_keywords)
        wants_scoring = any(kw in message_lower for kw in scoring_keywords)
        wants_content = any(kw in message_lower for kw in content_keywords)
        wants_phrases = any(kw in message_lower for kw in expand_keywords)
        wants_decision = any(kw in message_lower for kw in decision_keywords)
        wants_zhice = any(kw in message_lower for kw in zhice_keywords)

        # === 1. COMPLIANCE CHECK ===
        if wants_compliance:
            # Use the last content from history or ask for it
            content_to_check = ""
            if req.history:
                for msg in reversed(req.history):
                    if msg.get("role") == "assistant" and len(msg.get("content", "")) > 200:
                        content_to_check = msg["content"]
                        break
            if not content_to_check and len(req.message) > 100:
                content_to_check = req.message

            if not content_to_check:
                return {"content": "请提供需要审核的内容，或者先让我生成一篇内容再执行合规检查。", "role": "assistant"}

            compliance_prompt = f"""你是亚马逊全球开店内容合规审核专家。请对以下内容执行 Pre-Legal Self-Check。

检查项（逐一核对）：
1. 禁用词：市场→站点、平台→网站/站点（卖家平台除外）、生态→服务、最好/最佳→优选/之一、保证/确保→有助于/帮助、合作伙伴→第三方服务提供商、招商→卖家拓展
2. 第三方服务商：不得点名推荐（如 Jungle Scout/连连支付/PingPong），泛化为"第三方工具"
3. 品牌使用：gs.amazon.cn=全球开店页面（非卖家平台）、Seller Central=卖家平台、境外产品主体=亚马逊（非全球开店）、审核主体=亚马逊（非我们）
4. 数据规范：费率需标来源+时效、佣金给范围非单一数字、效果声明无来源百分比禁用
5. 绝对化表述：禁止"确保/保证/一定/显著提升"
6. 注册引导：必须"通过亚马逊卖家平台注册"，禁止"前往全球开店官网注册"
7. Copyright 格式：Copyright © 2026 Amazon.com, Inc. or its affiliates. All rights reserved.
8. 免责声明：文末必须包含 disclaimer

对每个问题标注：✅ PASS / ⚠️ WARNING（需确认）/ 🔴 BLOCKED（必须修改）
对 BLOCKED 项给出具体修改建议。

待审核内容：
{content_to_check[:3000]}"""

            result = call_bedrock_claude(compliance_prompt)
            return {"content": f"📋 合规审核结果：\n\n{result}", "role": "assistant"}

        # === 2. SCORING ===
        if wants_scoring:
            content_to_score = ""
            if req.history:
                for msg in reversed(req.history):
                    if msg.get("role") == "assistant" and len(msg.get("content", "")) > 200:
                        content_to_score = msg["content"]
                        break

            if not content_to_score:
                return {"content": "请先生成一篇内容，然后我来为它打分。", "role": "assistant"}

            scoring_prompt = f"""你是 AI 内容评估专家，模拟 ChatGPT/DeepSeek/Gemini 选择和引用内容的逻辑。

评分维度（每项 1-5 分）：
1. Intent Match 意图匹配 (30%): 是否直接回答查询？首段是否给出明确答案？
2. AI Readability AI可读性 (20%): 结构清晰？短段落+列表+表格？AI容易提取？
3. Authority 权威性 (20%): 包含具体可靠信息？平台特定知识？避免泛泛而谈？
4. Actionability 可操作性 (20%): 提供清晰下一步？用户能否立即执行？
5. Differentiation 差异化 (10%): 区别于通用内容？有独特结构或洞察？

输出格式：
各维度分数 + 加权总分 + 是否通过（≥4.5且各项≥4）+ 3条具体优化建议

待评分内容：
{content_to_score[:3000]}"""

            result = call_bedrock_claude(scoring_prompt)
            return {"content": f"📊 智优评分结果：\n\n{result}", "role": "assistant"}

        # === 3. CONTENT GENERATION (aligned with 智造 engine.py) ===
        if wants_content:
            from s3_storage import read_csv as _s3_read

            # Extract target phrase
            topic_prompt = f"从用户消息中提取他想要创建内容的核心检索短语或主题（只输出短语本身，不要解释）: '{req.message}'"
            topic = call_bedrock_claude(topic_prompt).strip().strip('"').strip("'")

            # Try to find matching phrase in library
            target_phrase = topic
            try:
                df_lib = _s3_read(req.batch_id, "01_zhiku", "zhiku_ai_queries.csv")
                if not df_lib.empty and "ai_query" in df_lib.columns:
                    phrases_list = df_lib["ai_query"].tolist()
                    num_match = re.search(r"top\s*(\d+)|第(\d+)", req.message)
                    if num_match:
                        idx = int(num_match.group(1) or num_match.group(2)) - 1
                        if 0 <= idx < len(phrases_list):
                            target_phrase = phrases_list[idx]
                    else:
                        for p in phrases_list:
                            if topic.lower() in p.lower() or any(w in p for w in topic.split() if len(w) > 2):
                                target_phrase = p
                                break
            except Exception:
                pass

            # --- Auto-detect template type (same logic as engine.py) ---
            query_lower = target_phrase.lower()
            if any(kw in query_lower for kw in ["注册", "开店", "开户", "register", "sign up", "create account", "申请", "审核"]):
                actual_template = "registration"
            elif any(kw in query_lower for kw in ["费用", "成本", "多少钱", "价格", "收费", "佣金", "cost", "fee", "price", "how much"]):
                actual_template = "fees"
            elif any(kw in query_lower for kw in ["物流", "仓储", "fba", "fbm", "发货", "配送", "运费", "shipping", "fulfillment"]):
                actual_template = "logistics"
            elif any(kw in query_lower for kw in ["广告", "推广", "ppc", "cpc", "acos", "sponsor", "advertis", "营销", "引流"]):
                actual_template = "advertising"
            elif any(kw in query_lower for kw in ["listing", "标题", "图片", "关键词", "a+", "详情页", "五点", "bullet"]):
                actual_template = "listing"
            else:
                actual_template = "general"

            # --- Template structure instructions (same as engine.py TEMPLATES) ---
            CHAT_TEMPLATES = {
                "registration": """## 文章结构模板（注册流程类）
请严格按照以下结构填充内容：
1. **开篇直答**（100字）：直接回答"如何注册"
2. **注册前准备**（150字）：需要的材料清单（表格形式）
3. **注册步骤详解**（300字）：分步骤说明（编号列表）
4. **常见审核问题**（150字）：审核失败原因+解决方案
5. **注册后下一步**（100字）：注册成功后的行动指引
6. **FAQ**（3个问答，每答案50字以上）
7. **CTA**：引导访问 https://gs.amazon.cn
必须包含：1个材料清单表格 + 1个步骤编号列表 + 1个费用对比列表""",
                "fees": """## 文章结构模板（费用成本类）
请严格按照以下结构填充内容：
1. **开篇直答**（80字）：一句话总结费用范围
2. **费用总览表**（200字）：所有费用项的表格（费用类型/金额/频率/说明）
3. **各项费用详解**（300字）：逐项解释每笔费用
4. **费用计算示例**（150字）：用具体数字举例月度/年度总费用
5. **省钱技巧**（100字）：降低费用的方法（列表形式）
6. **FAQ**（3个问答，每答案50字以上）
7. **CTA**：引导访问 https://gs.amazon.cn
必须包含：1个费用总览表格 + 1个计算示例列表 + 1个省钱技巧列表""",
                "logistics": """## 文章结构模板（物流仓储类）
请严格按照以下结构填充内容：
1. **开篇直答**（80字）：FBA vs FBM 核心区别
2. **物流方案对比表**（200字）：FBA/FBM/第三方的优劣势表格
3. **FBA 详细流程**（250字）：从发货到入仓的步骤
4. **费用结构**（150字）：仓储费+配送费的计算方式
5. **常见问题与解决**（100字）：丢件/延迟/退货处理
6. **FAQ**（3个问答，每答案50字以上）
7. **CTA**：引导访问 https://gs.amazon.cn
必须包含：1个方案对比表格 + 1个流程步骤列表 + 1个费用结构列表""",
                "advertising": """## 文章结构模板（广告推广类）
请严格按照以下结构填充内容：
1. **开篇直答**（80字）：广告类型概述和预期效果
2. **广告类型对比表**（200字）：SP/SB/SD 三种广告的对比表格
3. **新手广告策略**（250字）：从0到1的广告启动步骤
4. **预算分配建议**（150字）：不同阶段的预算分配方案
5. **优化技巧**（100字）：提升 ACOS 的实操建议（列表形式）
6. **FAQ**（3个问答，每答案50字以上）
7. **CTA**：引导访问 https://gs.amazon.cn
必须包含：1个广告类型对比表格 + 1个策略步骤列表 + 1个优化技巧列表""",
                "listing": """## 文章结构模板（Listing优化类）
请严格按照以下结构填充内容：
1. **开篇直答**（80字）：优质Listing的核心要素
2. **Listing要素评分表**（200字）：各要素重要性+评分标准的表格
3. **标题优化公式**（150字）：标题结构公式+好坏示例
4. **图片与A+内容**（200字）：图片要求+A+内容制作要点
5. **关键词策略**（100字）：前台/后台关键词布局
6. **FAQ**（3个问答，每答案50字以上）
7. **CTA**：引导访问 https://gs.amazon.cn
必须包含：1个要素评分表格 + 1个标题公式列表 + 1个关键词布局列表""",
                "general": """## 文章结构模板（通用类）
请严格按照以下结构填充内容：
1. **开篇直答**（100字）：直接回答检索问题的核心结论
2. **核心要点展开**（300字）：用 H2 标题分3-4个板块，每个板块先给结论再展开
3. **数据/方案对比表**（200字）：至少1个表格辅助说明
4. **实操步骤/建议清单**（150字）：结构化列表
5. **FAQ**（3个问答，每答案50字以上）
6. **CTA**：引导访问 https://gs.amazon.cn
必须包含：1个表格 + 2个列表 + 3个FAQ""",
            }

            template_instruction = CHAT_TEMPLATES.get(actual_template, CHAT_TEMPLATES["general"])

            # --- Load knowledge base if available ---
            knowledge_section = ""
            try:
                import os
                knowledge_dir = os.path.join(os.path.dirname(__file__), "..", "input", "knowledge")
                if os.path.exists(knowledge_dir):
                    for fname in os.listdir(knowledge_dir):
                        if fname.endswith(".md"):
                            # Match by template type or query keywords
                            if actual_template == "registration" and any(k in fname for k in ["注册", "register", "开店"]):
                                with open(os.path.join(knowledge_dir, fname), "r", encoding="utf-8") as f:
                                    knowledge_section = f"\n\n【官方知识库参考（只能使用以下信息，不得编造）】\n{f.read()[:3000]}\n"
                                break
            except Exception:
                pass

            # --- Full system prompt (same as engine.py zhizao) ---
            system_prompt = f"""你是跨境电商内容专家。用户会给你一个检索短语，你必须写一篇围绕该短语的文章。
{knowledge_section}
输出规则：
- 第一行 = 文章标题（不加#号，必须含检索短语的核心词）
- 第二行空行
- 然后是正文（Markdown格式，## H2/### H3）
- 首段直接回答检索短语的问题（金字塔原理：先结论后展开）
- 至少800字，含1个表格、2个列表
- 末尾3个FAQ（完整问答，每答案50字以上）
- 自然植入2次 https://gs.amazon.cn
- 不提及竞品（Shopee/Lazada/TikTok/速卖通/eBay）

严禁跑题。文章每一段都必须和检索短语直接相关。

【数据与引用铁律 — 违反任何一条视为不合格】
1. ❌ 绝对禁止编造报告/数据：不得使用"根据亚马逊XX年XX报告"等表述
2. ❌ 禁止捏造百分比：不得使用"提升XX%"等具体百分比，除非有明确数据来源
3. ❌ 禁止使用绝对化用语：不得说"全球最大"、"流量最大"、"最XX的"
4. ✅ 如需描述费率/佣金，只能引用 Seller Central 公开可查的标准费率，并标注"以卖家平台实际显示为准"
5. ✅ 如需举例说明，使用假设性表述："假设一件售价$25的商品…"
6. ❌ 禁止提及具体第三方品牌名：用"某知名电子品牌"等泛称代替
7. ❌ 禁止对税务/法规做解读：税务信息只能引用官方原文+注明"请咨询专业税务顾问"

【敏感词禁用清单（以下词汇绝对不能出现在文章中）】
一、禁止使用：平台（→网站/站点，"亚马逊卖家平台"除外）、市场/细分市场（→站点/国家/地区/行业）
二、禁止使用：最佳/最好/顶级（→优选/之一/推荐做法）、保证/确保/显著提升（→有助于/帮助）
三、禁止使用：合作伙伴（→第三方服务提供商）、招商（→卖家拓展）
四、禁止使用：疫情、全球（泛用时）、仅限、秒杀、破解、屏蔽、担保、稳赚、必爆
五、注册引导规则：必须写"通过亚马逊卖家平台注册"，禁止"前往全球开店官网注册"
六、审核主体="亚马逊"，禁止用"我们"

注意：以上词汇即使在正面语境中也不得使用。请用中性客观的表述替代。"""

            # --- User prompt with template instruction ---
            user_prompt = f"""检索短语：「{target_phrase}」

{template_instruction}

请严格按照上述模板结构生成内容，每个部分都必须有内容。
标题和正文必须精确围绕「{target_phrase}」展开。

文末必须包含：
- 免责声明："本文仅供参考，不构成商业承诺。实际费率和政策以亚马逊卖家平台最新公告为准。"
- 版权：Copyright © 2026 Amazon.com, Inc. or its affiliates. All rights reserved."""

            article = call_bedrock_claude(f"{system_prompt}\n\n{user_prompt}")

            if article and len(article) > 200:
                result_text = (
                    f"✅ 已为短语「{target_phrase}」按智造标准生成内容（模板: {actual_template}）：\n\n"
                    f"{article}\n\n---\n"
                    f"💡 你可以说「评分」让我打分，或说「合规检查」让我审核。"
                )
                return {"content": result_text, "role": "assistant"}
            else:
                return {"content": f"内容生成失败，请重试。目标短语：{target_phrase}", "role": "assistant"}

        # === 4. DECISION (智中枢) ===
        if wants_decision:
            decision_prompt = """基于以下最新智析数据（Jun WK25），按7条决策规则生成本周执行计划：

当前数据快照：
- GEO+Direct YTD: 28,741 (+55% YoY)，跑赢SSR大盘(-23%) 78 ppts
- CN GEO: WK20=41, WoW +24%, YoY +452%
- WW GEO: WK20=31, WoW +41%, YoY +94%
- WW Direct EST: WK20=1,914, WoW +32%, YoY +62%
- JP Direct YoY +103%
- 品牌链接提及率: 56.9%（5月46.6%→6月56.9%回升）
- 行业词提及率: 37.2%（5月7.4%→6月37.2%大幅上升但仍低）
- ChatGPT链接率仅28.5%（7平台最低）
- 总短语: 646条（品牌487+行业159）
- 新建内容 YTD: 648篇

7条规则检查：
Rule 1 增长加速: WoW>+30% 连续2周? → CN GEO ✓
Rule 2 下降预警: WoW<-20%? → 无
Rule 3 低量高增: weekly<50 且 YoY>+50%? → WW GEO (31, +94%) ✓
Rule 4 高增站点: YoY>+100%? → JP +103%, CN GEO +452% ✓
Rule 5 内容缺口: 有流量无内容2周? → 无
Rule 6 大盘对标: Our<SSR? → +7800 BPS ✅ 远超大盘
Rule 7 投入产出滞后: 发布2-3周无提升? → ChatGPT 28.5%链接率需排查 ✓

请输出标准格式周计划：
🟢 ACCELERATE + 🟡 MONITOR + 🔴 INVESTIGATE + 📝 执行任务列表 + KPI目标"""

            result = call_bedrock_claude(decision_prompt)
            return {"content": f"📋 智中枢周度决策：\n\n{result}", "role": "assistant"}

        # === 5. ZHICE (Coverage Test) ===
        if wants_zhice:
            return {"content": "智测功能需要实际调用 AI 平台 API 进行搜索验证。请前往智测页面执行，或提供具体短语我帮你分析该如何测试。\n\n💡 你也可以说「执行智造 [短语]」先生成内容，再到智测页面验证覆盖。", "role": "assistant"}

        # === 6. PHRASE GENERATION (智库) ===
        if wants_phrases:
            # Extract the core topic (not "检索短语" itself)
            topic_prompt = f"从用户请求中提取核心主题词（只输出1-3个词，不要包含'检索短语''搜索词'等元描述词）: '{req.message}'"
            topic = call_bedrock_claude(topic_prompt).strip().strip('"').strip("'").strip()
            # Remove meta words that might leak through
            for remove_word in ["检索短语", "搜索词", "关键词", "top", "热度"]:
                topic = topic.replace(remove_word, "").strip()
            if not topic:
                topic = "跨境电商"

            # Determine count
            count = 10
            num_match = re.search(r"(\d+)", req.message)
            if num_match:
                count = min(int(num_match.group(1)), 20)

            # Generate phrases - same prompt as seed expansion
            prompt = f"""请为核心词「{topic}」生成 {count} 个检索短语。

关键规则：
1. 每条短语必须是15-40字的完整自然问句
2. 必须是问句形式（怎么/如何/什么/哪些/多少/为什么）
3. 模拟真实卖家在ChatGPT/DeepSeek/豆包等AI搜索平台上的对话式提问
4. 包含具体场景或限定条件（如"2026年""新手""中国卖家"）
5. 必须围绕「{topic}」这个核心概念

每行一条，不要编号，不要解释。"""
            response = call_bedrock_claude(prompt)
            import re as _re_chat
            queries = [_re_chat.sub(r"^\d+[\.\)\-\s]+", "", q.strip()) for q in response.strip().split("\n") if q.strip() and len(q.strip()) > 10]

            if queries:
                # Save to S3
                try:
                    from s3_storage import read_csv, write_csv
                    import pandas as pd
                    from datetime import datetime

                    def _score_chat(q):
                        s = 3.0
                        if 15 <= len(q) <= 30: s += 0.5
                        elif len(q) > 30: s += 0.3
                        if any(w in q for w in ["怎么","如何","多少","哪些","为什么","什么","能不能","how","what","why","which","can"]): s += 0.5
                        if any(w in q.lower() for w in ["亚马逊","amazon","fba","注册","开店","选品","物流","广告","listing"]): s += 0.5
                        if any(w in q for w in ["吗","呢","啊","吧","?","？"]): s += 0.3
                        if any(w in q for w in ["新手","小白","2026","2025","中国卖家","美国站","欧洲站","日本站","beginner"]): s += 0.3
                        if any(w in q for w in ["vs","还是","区别","对比","哪个好","应该","值得","适合","推荐","最好","compare","recommend"]): s += 0.3
                        return min(5.0, round(s, 1))

                    new_df = pd.DataFrame({
                        "ai_query": queries,
                        "source": f"agent_chat_{topic}",
                        "is_selected": "FALSE",
                        "priority_score": [_score_chat(q) for q in queries],
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    })
                    existing = read_csv(req.batch_id, "01_zhiku", "zhiku_ai_queries.csv")
                    if not existing.empty:
                        merged = pd.concat([existing, new_df], ignore_index=True).drop_duplicates(subset=["ai_query"], keep="last")
                    else:
                        merged = new_df
                    write_csv(req.batch_id, "01_zhiku", "zhiku_ai_queries.csv", merged)
                except Exception:
                    pass

                # Format as readable result
                result_text = f"已为「{topic}」生成 {len(queries)} 条检索短语，已保存到智库：\n\n"
                for i, q in enumerate(queries, 1):
                    result_text += f"{i}. {q}\n"
                result_text += f"\n💡 提示：前往智库页面查看完整列表并选择短语。"
                return {"content": result_text, "role": "assistant"}

        # Regular chat (no action detected)
        history_text = ""
        if req.history:
            for msg in req.history[-6:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_text += f"\n{role}: {content}"

        prompt = f"""你是 Smart Suite 智能助手。帮助用户操作智系列模块完成 GEO 内容生产全流程。

你能做的事：
- "生成内容 [短语]" → 按智造标准生产内容
- "评分" → 对上一篇内容进行5维AI引用概率评分
- "合规检查" → 对内容执行合规审核（禁用词/品牌/数据/注册引导等）
- "生成短语 [主题]" → 扩展AI检索短语并保存到智库
- "本周计划" → 基于智析数据生成智中枢决策计划
- "智测" → 覆盖检测指引

请用和用户相同的语言回答。简洁、专业、可操作。

{f"对话历史:{history_text}" if history_text else ""}

用户: {req.message}"""

        response = call_bedrock_claude(prompt)
        return {"content": response, "role": "assistant"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- User Workspace ---
@app.get("/api/user/workspace")
def get_user_workspace(user: str = Query(...), x_user: Optional[str] = Header(None, alias="X-User")):
    """Get user's workspace data (files, history). Users can only see their own."""
    requesting_user = x_user or user
    data = _load_users_data()
    is_admin = requesting_user.lower() in data.get("admins", [])
    
    # Non-admin can only see their own workspace
    target_user = user.lower()
    if not is_admin and target_user != requesting_user.lower():
        raise HTTPException(status_code=403, detail="Access denied")
    
    from s3_storage import user_get_workspace_data
    return user_get_workspace_data(target_user)


@app.get("/api/user/history")
def get_user_history(user: str = Query(...), limit: int = 50, x_user: Optional[str] = Header(None, alias="X-User")):
    """Get operation history for a user."""
    requesting_user = x_user or user
    data = _load_users_data()
    is_admin = requesting_user.lower() in data.get("admins", [])
    
    target_user = user.lower()
    if not is_admin and target_user != requesting_user.lower():
        raise HTTPException(status_code=403, detail="Access denied")
    
    from s3_storage import user_list_history
    history = user_list_history(target_user, limit)
    return {"user": target_user, "history": history}


@app.post("/api/user/log")
def log_user_action(user: str = Query(...), action: str = Query(...), details: dict = None):
    """Log an action to user's workspace history."""
    from s3_storage import user_log_action
    user_log_action(user.lower(), action, details or {})
    return {"success": True}


@app.get("/api/user/settings")
def get_user_settings(user: str = Query(...)):
    """Get user settings from their workspace."""
    from s3_storage import user_read_json
    settings = user_read_json(user.lower(), "settings.json")
    return settings or {"language": "zh-CN", "theme": "dark"}


@app.post("/api/user/settings")
def save_user_settings(user: str = Query(...), settings: dict = {}):
    """Save user settings to their workspace."""
    from s3_storage import user_write_json
    user_write_json(user.lower(), "settings.json", settings)
    return {"success": True}


# --- Admin: All Users Overview ---
@app.get("/api/admin/workspaces")
def admin_list_workspaces(x_user: Optional[str] = Header(None, alias="X-User")):
    """Admin only: list all user workspaces with stats."""
    data = _load_users_data()
    requesting_user = (x_user or "").lower()
    if requesting_user not in data.get("admins", []):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from s3_storage import user_list_all_workspaces
    workspaces = user_list_all_workspaces()
    return {"workspaces": workspaces, "total_users": len(workspaces)}


@app.get("/api/admin/user-data")
def admin_get_user_data(user: str = Query(...), x_user: Optional[str] = Header(None, alias="X-User")):
    """Admin only: get full workspace data for any user."""
    data = _load_users_data()
    requesting_user = (x_user or "").lower()
    if requesting_user not in data.get("admins", []):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from s3_storage import user_get_workspace_data, user_list_history
    workspace = user_get_workspace_data(user.lower())
    history = user_list_history(user.lower(), 20)
    workspace["recent_history"] = history
    return workspace


# --- Lambda Handler ---
handler = Mangum(app, lifespan="off")
