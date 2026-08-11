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
        queries = [q.strip().lstrip("0123456789.-) ") for q in response.strip().split("\n") if q.strip() and len(q.strip()) > 10]

        if not queries:
            raise HTTPException(status_code=500, detail="No phrases generated")

        # Save to S3 (persistent)
        try:
            from s3_storage import read_csv, write_csv

            # Dynamic scoring like Streamlit's _quick_score
            def _score(q):
                s = 3.0
                if 10 <= len(q) <= 25: s += 0.5
                elif len(q) > 25: s += 0.3
                if any(w in q for w in ["怎么","如何","多少","哪些","为什么","什么","能不能","how","what","why"]): s += 0.5
                if any(w in q.lower() for w in ["亚马逊","amazon","fba","注册","开店","选品","物流","广告","listing"]): s += 0.5
                if any(w in q for w in ["吗","呢","啊","吧","?","？"]): s += 0.3
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


@app.post("/api/zhiku/select")
def zhiku_select(batch_id: str, indices: List[int], selected: bool = True):
    """Select/deselect phrases by index. Persists to S3."""
    from s3_storage import read_csv, write_csv
    df = read_csv(batch_id, "01_zhiku", "zhiku_ai_queries.csv")
    if df.empty:
        raise HTTPException(status_code=404, detail="Phrase file not found")
    for idx in indices:
        if 0 <= idx < len(df):
            df.iloc[idx, df.columns.get_loc("is_selected")] = "TRUE" if selected else "FALSE"
    write_csv(batch_id, "01_zhiku", "zhiku_ai_queries.csv", df)
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
        if any(w in q for w in ["怎么","如何","多少","哪些","为什么","什么","能不能","how","what","why"]): s += 0.5
        if any(w in q.lower() for w in ["亚马逊","amazon","fba","注册","开店","选品","物流","广告","listing"]): s += 0.5
        if any(w in q for w in ["吗","呢","啊","吧","?","？"]): s += 0.3
        return min(5.0, round(s, 1))

    if "ai_query" in df.columns:
        df["priority_score"] = df["ai_query"].apply(_score)
        write_csv(batch_id, "01_zhiku", "zhiku_ai_queries.csv", df)

    return {"success": True, "rescored": len(df)}


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


# --- Agent Chat ---
class ChatRequest(BaseModel):
    message: str
    user: str = ""
    batch_id: str = "batch_001"
    history: List[dict] = []


@app.post("/api/chat/stream")
def chat_stream(req: ChatRequest):
    """Chat endpoint - detects action intent and executes operations."""
    try:
        from engine import call_bedrock_claude
        import re

        message_lower = req.message.lower()

        # Detect action intent: content generation takes priority over phrase expansion
        expand_keywords = ["检索短语", "裂变", "生成短语", "expand phrases", "搜索词", "热度高的"]
        content_keywords = ["创建内容", "生成内容", "写文章", "创建文章", "generate content", "write article", "create content", "对应内容", "文章内容", "创建一篇", "帮忙创建", "对应的内容"]

        wants_phrases = any(kw in message_lower for kw in expand_keywords)
        wants_content = any(kw in message_lower for kw in content_keywords)

        # Content generation takes priority if both detected
        if wants_content:
            # Extract the topic/phrase from the message
            topic_prompt = f"从用户请求中提取他想要创建内容的主题或检索短语（只输出主题本身，1-2句话，不要解释）: '{req.message}'"
            topic = call_bedrock_claude(topic_prompt).strip().strip('"').strip("'")

            # Generate actual content (article)
            content_prompt = f"""请为检索短语「{topic}」生成一篇 GEO 优化的文章。

要求：
1. 800-1500字
2. 开头直接回答问题（倒金字塔结构）
3. 包含表格或列表
4. 包含 FAQ 部分（3个常见问题）
5. 自然融入"亚马逊全球开店"品牌词
6. 语言风格：专业、实用、易懂

直接输出文章内容，不要输出标题标注。"""
            article = call_bedrock_claude(content_prompt)

            if article and len(article) > 100:
                result_text = f"已为「{topic}」生成内容：\n\n{article}\n\n💡 提示：前往智造页面可以批量生成更多内容。"
                return {"content": result_text, "role": "assistant"}

        # If user wants phrases
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
            queries = [q.strip().lstrip("0123456789.-) ") for q in response.strip().split("\n") if q.strip() and len(q.strip()) > 10]

            if queries:
                # Save to S3
                try:
                    from s3_storage import read_csv, write_csv
                    import pandas as pd
                    from datetime import datetime
                    new_df = pd.DataFrame({
                        "ai_query": queries,
                        "source": f"agent_chat_{topic}",
                        "is_selected": "FALSE",
                        "priority_score": 3.0,
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

        prompt = f"""You are Smart Suite Agent (智系列智能助手). You help users operate the Smart Suite platform.

Modules: 智库(phrases) → 智测(verify) → 智造(generate) → 智优(optimize) → 智布(publish) → 智析(analytics)

Rules:
- Answer about Smart Suite, GEO, cross-border e-commerce ONLY
- Be concise and actionable
- Use same language as user
- If user wants to generate/expand phrases, tell them to type specific requests like "帮我生成关于FBA的10条检索短语"

{f"History:{history_text}" if history_text else ""}

User: {req.message}"""

        response = call_bedrock_claude(prompt)
        return {"content": response, "role": "assistant"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Lambda Handler ---
handler = Mangum(app, lifespan="off")
