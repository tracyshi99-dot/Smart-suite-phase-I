"""
Ahrefs Brand Radar API Client (v3)
Encapsulates Brand Radar mentions-overview, mentions-history, and ai-responses endpoints.
Only accessible to rickylan user.

Endpoints:
  POST /v3/brand-radar/mentions-overview  — AI visibility overview (brand vs competitors)
  POST /v3/brand-radar/mentions-history   — Brand mention trend over time
  POST /v3/brand-radar/ai-responses       — Query-level data (questions, links, data_source)

Report ID: 019e4f11-83ad-7648-a3d4-5a0d3760861e
"""
import requests
import json
from datetime import datetime, timedelta
from typing import Optional, List
import pandas as pd

from detection_rules import check_brand_mention, check_official_link, get_brand_keywords, get_official_link_patterns


# --- Config ---
AHREFS_API_BASE = "https://api.ahrefs.com/v3"
DEFAULT_REPORT_ID = "019e4f11-83ad-7648-a3d4-5a0d3760861e"
ALLOWED_USERS = ["rickylan", "yujiashi"]  # Only these users can see Ahrefs data

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
# DETECTION HELPERS (using detection_rules module)
# ============================================================

def _check_has_official_link(links: List[dict], question: str = "") -> bool:
    """Check if any link URL contains an official link pattern (e.g. .amazon).
    Uses detection_rules patterns for consistency.
    """
    patterns = get_official_link_patterns()
    for link in links:
        url = (link.get("url", "") or "").lower()
        for pattern in patterns:
            if pattern.lower() in url:
                return True
    return False


def _check_has_brand_mention(question: str, links: List[dict]) -> bool:
    """Check if question or any link title contains a brand keyword.
    Uses detection_rules keywords for consistency.
    """
    keywords = get_brand_keywords()
    # Check question
    q_lower = question.lower()
    for kw in keywords:
        if kw.lower() in q_lower:
            return True
    # Check link titles
    for link in links:
        title = (link.get("title", "") or "").lower()
        for kw in keywords:
            if kw.lower() in title:
                return True
    return False


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


def get_ai_responses(report_id: str = DEFAULT_REPORT_ID, limit: int = 1000) -> List[dict]:
    """POST /v3/brand-radar/ai-responses
    Returns query-level data: question, links, data_source, last_updated.
    Each item is enriched with has_official_link and has_brand_mention.
    """
    url = f"{AHREFS_API_BASE}/brand-radar/ai-responses"
    payload = {
        "report_id": report_id,
        "data_source": DATA_SOURCES,
        "country": COUNTRY,
        "select": ["question", "links", "data_source", "last_updated"],
        "limit": limit,
    }
    try:
        resp = requests.post(url, headers=_headers(), json=payload, timeout=90)
        if resp.status_code != 200:
            return []
        raw = resp.json()
    except Exception:
        return []

    # API returns {"ai_responses": [...]}
    items = raw.get("ai_responses", raw.get("responses", raw.get("metrics", raw.get("items", []))))
    if not isinstance(items, list):
        return []

    results = []
    for item in items:
        question = item.get("question", "") or ""
        links = item.get("links", []) or []
        if not isinstance(links, list):
            links = []
        data_source = item.get("data_source", "") or ""
        last_updated = item.get("last_updated", "") or ""

        results.append({
            "question": question,
            "links": links,
            "data_source": data_source,
            "last_updated": last_updated,
            "has_official_link": _check_has_official_link(links, question),
            "has_brand_mention": _check_has_brand_mention(question, links),
            "links_count": len(links),
        })

    return results


def get_ahrefs_queries_df(report_id: str = DEFAULT_REPORT_ID, limit: int = 1000) -> pd.DataFrame:
    """Return a pandas DataFrame of Ahrefs ai-responses data.
    Columns: ai_query, source, data_source, has_official_link, has_brand_mention, links_count, last_updated
    Caches in session_state for 10 minutes (same pattern as fetch_all_data).
    """
    try:
        import streamlit as st
        cache_key = f"ahrefs_queries_cache_{report_id}"
        cache_time_key = f"ahrefs_queries_cache_time_{report_id}"
        if cache_key in st.session_state:
            cached_time = st.session_state.get(cache_time_key, datetime.min)
            if datetime.now() - cached_time < timedelta(minutes=10):
                return st.session_state[cache_key]
    except Exception:
        pass

    responses = get_ai_responses(report_id, limit)
    if not responses:
        return pd.DataFrame(columns=[
            "ai_query", "source", "data_source", "has_official_link",
            "has_brand_mention", "links_count", "last_updated",
        ])

    rows = []
    for item in responses:
        rows.append({
            "ai_query": item["question"],
            "source": "ahrefs",
            "data_source": item["data_source"],
            "has_official_link": item["has_official_link"],
            "has_brand_mention": item["has_brand_mention"],
            "links_count": item["links_count"],
            "last_updated": item["last_updated"],
        })

    df = pd.DataFrame(rows)

    # Cache
    try:
        import streamlit as st
        st.session_state[cache_key] = df
        st.session_state[cache_time_key] = datetime.now()
    except Exception:
        pass

    return df


# ============================================================
# HIGH-LEVEL DATA METHODS (for UI consumption)
# ============================================================

def fetch_all_data(report_id: str = DEFAULT_REPORT_ID) -> dict:
    """Fetch all Brand Radar data. Caches in session_state for 10 minutes.
    Includes overview, history, and ai_responses (query-level).
    If ai_responses fails, overview/history still work (backward compatible).
    """
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

    # Add ai_responses — graceful fallback if it fails
    try:
        data["ai_responses"] = get_ai_responses(report_id)
    except Exception:
        data["ai_responses"] = []

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
    API returns: {"metrics": [{"brand": "Amazon", "only_target_brand": 1245, ...}, ...]}
    First item is our brand (Amazon), rest are competitors.
    """
    if "error" in overview_data:
        return {"error": overview_data["error"]}

    metrics_list = overview_data.get("metrics", [])
    if not metrics_list:
        return {"raw": overview_data}

    # First item is our brand
    our_brand = metrics_list[0] if metrics_list else {}

    return {
        "brand": our_brand.get("brand", "Amazon"),
        "only_target_brand": our_brand.get("only_target_brand", 0),
        "only_competitors_brands": our_brand.get("only_competitors_brands", 0),
        "target_and_competitors_brands": our_brand.get("target_and_competitors_brands", 0),
        "no_tracked_brands": our_brand.get("no_tracked_brands", 0),
        "total": our_brand.get("total", 0),
    }


def overview_to_competitor_df(overview_data: dict) -> pd.DataFrame:
    """Extract competitor comparison from overview data into a DataFrame.
    API returns metrics for each brand (our brand + all competitors).
    """
    if "error" in overview_data:
        return pd.DataFrame({"Error": [overview_data["error"]]})

    metrics_list = overview_data.get("metrics", [])
    if not metrics_list:
        return pd.DataFrame()

    rows = []
    for item in metrics_list:
        rows.append({
            "Brand": item.get("brand", ""),
            "Our Brand Only": item.get("only_target_brand", 0),
            "Competitor Only": item.get("only_competitors_brands", 0),
            "Both Mentioned": item.get("target_and_competitors_brands", 0),
            "Total": item.get("total", 0),
        })

    return pd.DataFrame(rows)


def history_to_dataframe(history_data: dict) -> pd.DataFrame:
    """Convert mentions-history response to DataFrame for chart rendering.
    API returns: {"metrics": [{"date": "2026-04-22T00:00:00Z", "mentions": 928}, ...]}
    """
    if "error" in history_data:
        return pd.DataFrame()

    points = history_data.get("metrics", [])
    if not points:
        return pd.DataFrame()

    rows = []
    for point in points:
        if isinstance(point, dict):
            rows.append({
                "Date": point.get("date", ""),
                "Mentions": point.get("mentions", 0),
            })

    df = pd.DataFrame(rows)
    if not df.empty and "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"]).sort_values("Date")
    return df
