"""
Ahrefs Brand Radar API Client (v3)
Encapsulates Brand Radar mentions-overview and mentions-history endpoints.
Only accessible to rickylan user.

Endpoints:
  POST /v3/brand-radar/mentions-overview  — AI visibility overview (brand vs competitors)
  POST /v3/brand-radar/mentions-history   — Brand mention trend over time

Report ID: 019e4f11-83ad-7648-a3d4-5a0d3760861e
"""
import requests
import json
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd


# --- Config ---
AHREFS_API_BASE = "https://api.ahrefs.com/v3"
DEFAULT_REPORT_ID = "019e4f11-83ad-7648-a3d4-5a0d3760861e"
ALLOWED_USERS = ["rickylan"]  # Only these users can see Ahrefs data

# Brand definition
BRAND_CONFIG = {
    "names": ["Amazon", "Amazon Global Selling", "亞馬遜全球開店", "亞馬遜開店"],
    "url_groups": [{"target": "gs.amazon.com.tw", "scope": "subdomains"}],
}

# Competitors
COMPETITORS_CONFIG = [
    {"names": ["Alibaba", "阿里巴巴"], "url_groups": [{"target": "alibaba.com", "scope": "subdomains"}]},
    {"names": ["eBay"], "url_groups": [{"target": "ebay.com", "scope": "subdomains"}]},
    {"names": ["Etsy"], "url_groups": [{"target": "etsy.com", "scope": "subdomains"}]},
    {"names": ["Walmart"], "url_groups": [{"target": "walmart.com", "scope": "subdomains"}]},
    {"names": ["Coupang", "酷澎"], "url_groups": [{"target": "coupang.com", "scope": "subdomains"}]},
    {"names": ["Shopline"], "url_groups": [{"target": "shopline.tw", "scope": "subdomains"}]},
    {"names": ["cyberbiz"], "url_groups": [{"target": "www.cyberbiz.io", "scope": "subdomains"}]},
    {"names": ["Shopee"], "url_groups": [{"target": "shopee.co.id", "scope": "subdomains"}]},
    {"names": ["Rakuten", "樂天"], "url_groups": [{"target": "rakuten.com", "scope": "subdomains"}]},
]

# AI data sources
DATA_SOURCES = [
    "chatgpt", "google_ai_overviews", "google_ai_overviews_keywords",
    "google_ai_mode", "google_ai_mode_keywords", "gemini", "perplexity", "copilot",
]

# Country
COUNTRY = ["tw"]


def get_api_key() -> str:
    """Get Ahrefs API key from Streamlit secrets."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "ahrefs" in st.secrets:
            return st.secrets["ahrefs"].get("api_key", "")
    except Exception:
        pass
    # Fallback: environment variable
    import os
    return os.environ.get("AHREFS_API_KEY", "")


def is_user_authorized(user: str) -> bool:
    """Check if user is authorized to view Ahrefs data."""
    return user.lower().strip() in [u.lower() for u in ALLOWED_USERS]


def _headers() -> dict:
    """Build request headers with API key."""
    key = get_api_key()
    if not key:
        raise RuntimeError("Ahrefs API Key not configured. Add [ahrefs] api_key to Streamlit secrets.")
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


# ============================================================
# API CALLS
# ============================================================

def get_mentions_overview(report_id: str = DEFAULT_REPORT_ID) -> dict:
    """POST /v3/brand-radar/mentions-overview
    Returns AI visibility overview: brand mentions vs competitors across AI platforms.
    """
    url = f"{AHREFS_API_BASE}/brand-radar/mentions-overview"
    payload = {
        "brands": [BRAND_CONFIG],
        "competitors": COMPETITORS_CONFIG,
        "data_source": DATA_SOURCES,
        "report_id": report_id,
        "country": COUNTRY,
        "select": [
            "brand", "only_target_brand", "only_competitors_brands",
            "target_and_competitors_brands", "no_tracked_brands", "total",
        ],
    }
    try:
        resp = requests.post(url, headers=_headers(), json=payload, timeout=60)
        if resp.status_code == 200:
            return resp.json()
        return {"error": f"HTTP {resp.status_code}", "detail": resp.text[:500]}
    except Exception as e:
        return {"error": str(e)}


def get_mentions_history(report_id: str = DEFAULT_REPORT_ID,
                         date_from: str = None,
                         date_to: str = None) -> dict:
    """POST /v3/brand-radar/mentions-history
    Returns brand mention trend over time (daily data points).
    """
    if not date_to:
        date_to = datetime.now().strftime("%Y-%m-%d")
    if not date_from:
        date_from = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

    url = f"{AHREFS_API_BASE}/brand-radar/mentions-history"
    payload = {
        "select": ["date", "mentions"],
        "brands": [BRAND_CONFIG],
        "data_source": DATA_SOURCES,
        "report_id": report_id,
        "country": COUNTRY,
        "date_from": date_from,
        "date_to": date_to,
    }
    try:
        resp = requests.post(url, headers=_headers(), json=payload, timeout=60)
        if resp.status_code == 200:
            return resp.json()
        return {"error": f"HTTP {resp.status_code}", "detail": resp.text[:500]}
    except Exception as e:
        return {"error": str(e)}


# ============================================================
# HIGH-LEVEL DATA METHODS (for UI consumption)
# ============================================================

def fetch_all_data(report_id: str = DEFAULT_REPORT_ID) -> dict:
    """Fetch all Brand Radar data. Caches in session_state for 10 minutes."""
    try:
        import streamlit as st
        cache_key = f"ahrefs_cache_{report_id}"
        cache_time_key = f"ahrefs_cache_time_{report_id}"
        if cache_key in st.session_state:
            cached_time = st.session_state.get(cache_time_key, datetime.min)
            if datetime.now() - cached_time < timedelta(minutes=10):
                return st.session_state[cache_key]
    except Exception:
        pass

    data = {
        "overview": get_mentions_overview(report_id),
        "history": get_mentions_history(report_id),
        "fetched_at": datetime.now().isoformat(),
    }

    # Cache
    try:
        import streamlit as st
        st.session_state[cache_key] = data
        st.session_state[cache_time_key] = datetime.now()
    except Exception:
        pass

    return data


def overview_to_metrics(overview_data: dict) -> dict:
    """Extract key metrics from mentions-overview response.
    Returns dict with brand mentions breakdown.
    """
    if "error" in overview_data:
        return {"error": overview_data["error"]}

    # The API returns data in various structures — handle flexibly
    # Expected fields: brand, only_target_brand, only_competitors_brands,
    # target_and_competitors_brands, no_tracked_brands, total
    metrics = {}

    # Try direct top-level keys
    for key in ["brand", "only_target_brand", "only_competitors_brands",
                "target_and_competitors_brands", "no_tracked_brands", "total"]:
        if key in overview_data:
            metrics[key] = overview_data[key]

    # Try nested under "data" or "result"
    if not metrics:
        inner = overview_data.get("data", overview_data.get("result", overview_data.get("items", [])))
        if isinstance(inner, dict):
            for key in ["brand", "only_target_brand", "only_competitors_brands",
                        "target_and_competitors_brands", "no_tracked_brands", "total"]:
                if key in inner:
                    metrics[key] = inner[key]
        elif isinstance(inner, list) and inner:
            # First item might contain the metrics
            first = inner[0] if inner else {}
            for key in ["brand", "only_target_brand", "only_competitors_brands",
                        "target_and_competitors_brands", "no_tracked_brands", "total"]:
                if key in first:
                    metrics[key] = first[key]

    return metrics if metrics else {"raw": overview_data}


def overview_to_competitor_df(overview_data: dict) -> pd.DataFrame:
    """Extract competitor comparison from overview data into a DataFrame."""
    if "error" in overview_data:
        return pd.DataFrame({"Error": [overview_data["error"]]})

    # Try to extract competitor-level breakdown
    # The overview might have per-brand breakdown in nested structures
    competitors_data = overview_data.get("competitors", overview_data.get("brands_data", []))

    if not competitors_data:
        # Build from config names + available metrics
        metrics = overview_to_metrics(overview_data)
        if "raw" in metrics:
            return pd.DataFrame()

        rows = [{"Brand": "Amazon Global Selling (我方)", "Mentions": metrics.get("only_target_brand", "—")}]
        rows.append({"Brand": "竞品合计", "Mentions": metrics.get("only_competitors_brands", "—")})
        rows.append({"Brand": "共同提及", "Mentions": metrics.get("target_and_competitors_brands", "—")})
        rows.append({"Brand": "无品牌提及", "Mentions": metrics.get("no_tracked_brands", "—")})
        rows.append({"Brand": "Total", "Mentions": metrics.get("total", "—")})
        return pd.DataFrame(rows)

    # If we have per-competitor data
    rows = []
    for comp in competitors_data:
        rows.append({
            "Brand": comp.get("name", comp.get("names", [""])[0] if isinstance(comp.get("names"), list) else ""),
            "Mentions": comp.get("mentions", comp.get("total", comp.get("count", "—"))),
        })
    return pd.DataFrame(rows)


def history_to_dataframe(history_data: dict) -> pd.DataFrame:
    """Convert mentions-history response to DataFrame for chart rendering."""
    if "error" in history_data:
        return pd.DataFrame()

    # The response should have date + mentions data points
    points = history_data.get("data", history_data.get("items",
             history_data.get("history", history_data.get("mentions", []))))

    if not points:
        # Try top-level list
        if isinstance(history_data, list):
            points = history_data
        else:
            return pd.DataFrame()

    rows = []
    for point in points:
        if isinstance(point, dict):
            rows.append({
                "Date": point.get("date", ""),
                "Mentions": point.get("mentions", point.get("count", point.get("total", 0))),
            })

    df = pd.DataFrame(rows)
    if not df.empty and "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"]).sort_values("Date")
    return df
