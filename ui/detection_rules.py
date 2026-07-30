"""
Detection Rules Engine for Smart Suite
Configurable rules for brand mention and official link detection.
Rules are stored per-user in output/rules/{user}_rules.json
Shared default rules in output/rules/_default_rules.json

Used by: 智测 (gap verification), 智析 (analytics), app_zhice (request submission)
"""
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

# --- Paths ---
BASE_PATH = Path(__file__).parent.parent
OUTPUT_PATH = BASE_PATH / "output"
RULES_DIR = OUTPUT_PATH / "rules"

# On Streamlit Cloud, use temp directory
import tempfile
if not OUTPUT_PATH.exists():
    OUTPUT_PATH = Path(tempfile.gettempdir()) / "smartsuite_output"
    RULES_DIR = OUTPUT_PATH / "rules"

RULES_DIR.mkdir(parents=True, exist_ok=True)

# --- Default Rules ---
DEFAULT_RULES = {
    "version": "1.0",
    "updated_at": "",
    "updated_by": "",
    "brand_mention": {
        "description": "品牌提及判定规则：AI 回答中出现「亚马逊」或「Amazon」即判定为 Brand Mention",
        "keywords": [
            "亚马逊", "Amazon", "amazon", "亞馬遜",
        ],
        "logic": "any",  # 任一品牌关键词出现即算
        "case_sensitive": False,
        "additional_rule": "有亚马逊或者Amazon就算brand mention。有特殊要求的按特殊要求写。",
        "special_overrides": [],
        "notes": "默认逻辑：AI 回答中只要出现亚马逊或Amazon即判定为品牌提及。有特殊要求的按special_overrides配置。",
    },
    "official_link": {
        "description": "官方链接判定规则：AI 回答中出现 .amazon 域名即判定为 Official Link Mention",
        "link_patterns": [
            ".amazon",
        ],
        "logic": "any",
        "case_sensitive": False,
        "special_overrides": [],  # 特殊规则覆盖，格式: [{"query_pattern": "...", "patterns": ["specific.url"]}]
        "notes": "默认逻辑：只要 AI 回答包含 .amazon 域名下的任何链接即算官方链接提及。有特殊要求的按特殊要求写。",
    },
    "zhiku_seeds": {
        "description": "智库检索种子词设置：用于裂变生成检索短语的核心种子",
        "seeds": [
            "亚马逊开店", "跨境电商", "FBA", "亚马逊注册",
            "亚马逊费用", "亚马逊选品", "亚马逊广告",
            "亚马逊物流", "亚马逊Listing", "亚马逊运营",
        ],
        "notes": "种子词用于智库的核心语义裂变，每个种子可生成 10-15 条检索短语",
    },
}


def _get_rules_path(user: str = "") -> Path:
    """Get rules file path for a user. Empty user = default rules."""
    if user:
        return RULES_DIR / f"{user}_rules.json"
    return RULES_DIR / "_default_rules.json"


def _load_rules_from_s3(user: str = "") -> Optional[dict]:
    """Try to load rules from S3 (for Streamlit Cloud)."""
    try:
        from s3_sync import load_user_data, s3_available
        if s3_available():
            filename = f"{user}_rules.json" if user else "_default_rules.json"
            data = load_user_data("rules", filename)
            if data:
                return data
    except Exception:
        pass
    return None


def _save_rules_to_s3(rules: dict, user: str = ""):
    """Try to save rules to S3."""
    try:
        from s3_sync import save_user_data
        filename = f"{user}_rules.json" if user else "_default_rules.json"
        save_user_data("rules", filename, rules)
    except Exception:
        pass


def load_rules(user: str = "") -> dict:
    """Load detection rules. Priority: user-specific > S3 > default file > hardcoded defaults."""
    # Try user-specific file first
    if user:
        user_path = _get_rules_path(user)
        if user_path.exists():
            try:
                return json.loads(user_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        # Try S3
        s3_data = _load_rules_from_s3(user)
        if s3_data:
            return s3_data

    # Try default rules file
    default_path = _get_rules_path("")
    if default_path.exists():
        try:
            return json.loads(default_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    # Try S3 default
    s3_default = _load_rules_from_s3("")
    if s3_default:
        return s3_default

    # Hardcoded defaults
    return DEFAULT_RULES.copy()


def save_rules(rules: dict, user: str = ""):
    """Save detection rules for a user (or default)."""
    rules["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rules["updated_by"] = user or "system"

    path = _get_rules_path(user)
    RULES_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rules, ensure_ascii=False, indent=2), encoding="utf-8")

    # Also save to S3
    _save_rules_to_s3(rules, user)


# ============================================================
# DETECTION FUNCTIONS (used by zhice_engine, app_zhice, etc.)
# ============================================================

def check_brand_mention(answer: str, query: str = "", user: str = "") -> bool:
    """Check if an AI answer contains a brand mention.
    Default logic: 有亚马逊或Amazon就算 brand mention.
    """
    if not answer:
        return False

    rules = load_rules(user)
    brand_rules = rules.get("brand_mention", DEFAULT_RULES["brand_mention"])
    keywords = brand_rules.get("keywords", [])
    case_sensitive = brand_rules.get("case_sensitive", False)

    text = answer if case_sensitive else answer.lower()

    # Check special overrides first
    special = brand_rules.get("special_overrides", [])
    if special and query:
        for override in special:
            pattern = override.get("query_pattern", "")
            if pattern and pattern.lower() in query.lower():
                override_kws = override.get("keywords", keywords)
                for kw in override_kws:
                    check_kw = kw if case_sensitive else kw.lower()
                    if check_kw in text:
                        return True
                return False

    # Default: any brand keyword present = brand mention
    for kw in keywords:
        check_kw = kw if case_sensitive else kw.lower()
        if check_kw in text:
            return True

    return False


def check_official_link(answer: str, query: str = "", user: str = "") -> bool:
    """Check if an AI answer contains an official link based on configured rules.
    Default logic: any .amazon domain = official link.
    """
    if not answer:
        return False

    rules = load_rules(user)
    link_rules = rules.get("official_link", DEFAULT_RULES["official_link"])
    patterns = link_rules.get("link_patterns", [])
    case_sensitive = link_rules.get("case_sensitive", False)

    text = answer if case_sensitive else answer.lower()

    # Check special overrides first
    special = link_rules.get("special_overrides", [])
    if special and query:
        for override in special:
            pattern = override.get("query_pattern", "")
            if pattern and pattern.lower() in query.lower():
                override_patterns = override.get("patterns", patterns)
                for p in override_patterns:
                    check_p = p if case_sensitive else p.lower()
                    if check_p in text:
                        return True
                return False

    # Default logic: any pattern match
    for pattern in patterns:
        check_pattern = pattern if case_sensitive else pattern.lower()
        if check_pattern in text:
            return True

    return False


def get_brand_keywords(user: str = "") -> List[str]:
    """Get list of brand mention keywords."""
    rules = load_rules(user)
    return rules.get("brand_mention", {}).get("keywords", DEFAULT_RULES["brand_mention"]["keywords"])


def get_official_link_patterns(user: str = "") -> List[str]:
    """Get list of official link patterns."""
    rules = load_rules(user)
    return rules.get("official_link", {}).get("link_patterns", DEFAULT_RULES["official_link"]["link_patterns"])


def get_zhiku_seeds(user: str = "") -> List[str]:
    """Get list of zhiku seed keywords."""
    rules = load_rules(user)
    return rules.get("zhiku_seeds", {}).get("seeds", DEFAULT_RULES["zhiku_seeds"]["seeds"])
