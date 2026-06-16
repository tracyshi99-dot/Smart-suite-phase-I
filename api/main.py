"""
Smart Suite REST API
FastAPI wrapper around engine.py — independent of Streamlit UI.
Run: uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
"""
import sys
from pathlib import Path

# Add parent directory so we can import engine
sys.path.insert(0, str(Path(__file__).parent.parent / "ui"))

from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional
import pandas as pd
import json

from engine import (
    run_zhiku,
    run_semantic_expansion,
    run_zhizao,
    run_zhiyou_score,
    run_zhiyou_execute,
    run_zhiyou_compliance,
    run_zhibu,
    run_full_pipeline,
    OUTPUT_PATH,
    INPUT_PATH,
)

app = FastAPI(
    title="Smart Suite API",
    description="REST API for Smart Suite GEO content pipeline (智库→智造→智优→智布→智传→智析→智中枢)",
    version="1.0.0",
)


# ============================================================
# Health Check
# ============================================================
@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "service": "Smart Suite API", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "output_path": str(OUTPUT_PATH), "input_path": str(INPUT_PATH)}


# ============================================================
# 智库 (Step 1) — Query Generation
# ============================================================
class ZhikuRequest(BaseModel):
    batch_id: str = Field(default="batch_001", description="Batch identifier")
    market: str = Field(default="ALL", description="Market filter: ALL, CN, NA, EU, JP")
    keyword_limit: int = Field(default=10, ge=1, le=200, description="Max keywords to process")


class ZhikuExpansionRequest(BaseModel):
    batch_id: str = Field(default="batch_001", description="Batch identifier")
    core_semantic: str = Field(description="Core seed word for expansion")
    market: str = Field(default="CN", description="Target market: CN or WW")
    count: int = Field(default=15, ge=5, le=50, description="Number of phrases to generate")
    language: str = Field(default="zh", description="Output language: zh or en")


@app.post("/api/zhiku/run", tags=["智库"])
async def api_zhiku_run(req: ZhikuRequest):
    """Run 智库 Step 1: Generate AI queries from SEO/SEM keywords."""
    result = run_zhiku(
        batch_id=req.batch_id,
        market=req.market,
        keyword_limit=req.keyword_limit,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
    return result


@app.post("/api/zhiku/expand", tags=["智库"])
async def api_zhiku_expand(req: ZhikuExpansionRequest):
    """Run 智库 Source B: Semantic expansion from seed word."""
    result = run_semantic_expansion(
        core_semantic=req.core_semantic,
        market=req.market,
        count=req.count,
        language=req.language,
        batch_id=req.batch_id,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
    return result


@app.post("/api/zhiku/upload-keywords", tags=["智库"])
async def api_zhiku_upload(file: UploadFile = File(...)):
    """Upload SEO/SEM keyword CSV to input directory."""
    if not file.filename.endswith((".csv", ".xlsx")):
        raise HTTPException(status_code=400, detail="Only CSV/XLSX files supported")
    INPUT_PATH.mkdir(parents=True, exist_ok=True)
    dest = INPUT_PATH / "seo_sem_keywords.csv"
    content = await file.read()
    if file.filename.endswith(".xlsx"):
        df = pd.read_excel(content, engine="openpyxl")
        df.to_csv(dest, index=False, encoding="utf-8-sig")
    else:
        dest.write_bytes(content)
    return {"success": True, "file": str(dest), "message": "Keywords uploaded"}


# ============================================================
# 智造 (Step 2) — Content Generation
# ============================================================
class ZhizaoRequest(BaseModel):
    batch_id: str = Field(default="batch_001", description="Batch identifier")
    content_limit: int = Field(default=5, ge=1, le=20, description="Max articles to generate per run")


@app.post("/api/zhizao/run", tags=["智造"])
async def api_zhizao_run(req: ZhizaoRequest):
    """Run 智造 Step 2: Generate draft content from selected queries."""
    result = run_zhizao(batch_id=req.batch_id, content_limit=req.content_limit)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
    return result


# ============================================================
# 智优 (Step 3) — Optimization
# ============================================================
class ZhiyouRequest(BaseModel):
    batch_id: str = Field(default="batch_001", description="Batch identifier")


@app.post("/api/zhiyou/score", tags=["智优"])
async def api_zhiyou_score(req: ZhiyouRequest):
    """Run 智优 Step 3: Score content across 5 AI citation dimensions."""
    result = run_zhiyou_score(batch_id=req.batch_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
    return result


@app.post("/api/zhiyou/rewrite", tags=["智优"])
async def api_zhiyou_rewrite(req: ZhiyouRequest):
    """Run 智优 Step 3.5: Rewrite content based on scoring suggestions."""
    result = run_zhiyou_execute(batch_id=req.batch_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
    return result


@app.post("/api/zhiyou/compliance", tags=["智优"])
async def api_zhiyou_compliance(req: ZhiyouRequest):
    """Run 智优 Step 3.6: Legal compliance check with auto-fix."""
    result = run_zhiyou_compliance(batch_id=req.batch_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
    return result


@app.post("/api/zhiyou/full", tags=["智优"])
async def api_zhiyou_full(req: ZhiyouRequest):
    """Run full 智优 pipeline: Score → Rewrite → Compliance in one call."""
    results = {}

    score_result = run_zhiyou_score(batch_id=req.batch_id)
    results["score"] = score_result
    if not score_result.get("success"):
        raise HTTPException(status_code=400, detail=f"Score failed: {score_result.get('error')}")

    rewrite_result = run_zhiyou_execute(batch_id=req.batch_id)
    results["rewrite"] = rewrite_result
    if not rewrite_result.get("success"):
        raise HTTPException(status_code=400, detail=f"Rewrite failed: {rewrite_result.get('error')}")

    compliance_result = run_zhiyou_compliance(batch_id=req.batch_id)
    results["compliance"] = compliance_result
    if not compliance_result.get("success"):
        raise HTTPException(status_code=400, detail=f"Compliance failed: {compliance_result.get('error')}")

    return {"success": True, "results": results}


# ============================================================
# 智布 (Step 4) — Publishing Format
# ============================================================
class ZhibuRequest(BaseModel):
    batch_id: str = Field(default="batch_001", description="Batch identifier")


@app.post("/api/zhibu/run", tags=["智布"])
async def api_zhibu_run(req: ZhibuRequest):
    """Run 智布 Step 4: Convert optimized content to JSON."""
    result = run_zhibu(batch_id=req.batch_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
    return result


@app.get("/api/zhibu/download/{batch_id}", tags=["智布"])
async def api_zhibu_download(batch_id: str):
    """Download the generated JSON output file."""
    json_path = OUTPUT_PATH / batch_id / "04_zhibu" / "zhibu_output.json"
    if not json_path.exists():
        raise HTTPException(status_code=404, detail="JSON output not found. Run zhibu first.")
    return FileResponse(json_path, media_type="application/json", filename=f"zhibu_output_{batch_id}.json")


# ============================================================
# 全流程 (Full Pipeline)
# ============================================================
class FullPipelineRequest(BaseModel):
    batch_id: str = Field(default="batch_001", description="Batch identifier")
    market: str = Field(default="ALL", description="Market filter")
    keyword_limit: int = Field(default=10, ge=1, le=200, description="Max keywords")
    content_limit: int = Field(default=5, ge=1, le=20, description="Max articles per run")


@app.post("/api/pipeline/run", tags=["全流程"])
async def api_pipeline_run(req: FullPipelineRequest):
    """Run full pipeline: 智库 → 智造 → 智优(Score+Rewrite+Compliance) → 智布."""
    result = run_full_pipeline(
        batch_id=req.batch_id,
        market=req.market,
        keyword_limit=req.keyword_limit,
        content_limit=req.content_limit,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Pipeline failed"))
    return result


# ============================================================
# Output Files — Browse & Download
# ============================================================
@app.get("/api/output/list", tags=["Output"])
async def api_output_list(batch_id: str = Query(default="batch_001")):
    """List all output files for a batch."""
    batch_dir = OUTPUT_PATH / batch_id
    if not batch_dir.exists():
        return {"batch_id": batch_id, "files": []}

    files = []
    for f in batch_dir.rglob("*"):
        if f.is_file():
            files.append({
                "path": str(f.relative_to(OUTPUT_PATH)),
                "size_kb": round(f.stat().st_size / 1024, 1),
                "modified": f.stat().st_mtime,
            })
    return {"batch_id": batch_id, "files": sorted(files, key=lambda x: x["path"])}


@app.get("/api/output/download", tags=["Output"])
async def api_output_download(path: str = Query(description="Relative path from output dir")):
    """Download any output file by relative path."""
    full_path = OUTPUT_PATH / path
    if not full_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    mime = "application/json" if full_path.suffix == ".json" else "text/csv"
    return FileResponse(full_path, media_type=mime, filename=full_path.name)


# ============================================================
# Batches
# ============================================================
@app.get("/api/batches", tags=["Batches"])
async def api_batches():
    """List all available batches."""
    batches = []
    if OUTPUT_PATH.exists():
        for d in sorted(OUTPUT_PATH.iterdir()):
            if d.is_dir() and d.name.startswith("batch_"):
                batches.append(d.name)
    return {"batches": batches}
