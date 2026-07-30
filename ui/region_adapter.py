"""
Region Adapter — loads region-specific configuration based on user_region.
Provides region config to all Smart Suite modules (Zhiku, Zhice, Zhizao, etc.)
"""
import json
from pathlib import Path
from typing import Optional

# Config paths
_BASE = Path(__file__).parent.parent
CONFIG_DIR = _BASE / "config" / "regions"
USERS_FILE = _BASE / "output" / "users.json"

# Supported regions
SUPPORTED_REGIONS = ["ROA", "CN", "NA", "EU"]
SUPPORTED_SUB_REGIONS = ["TW", "KR", "VN"]

# Cache loaded configs in memory
_config_cache: dict = {}


def load_region_config(region_code: str) -> dict:
    """Load and validate a region config JSON file. Falls back to _default.json."""
    if region_code in _config_cache:
        return _config_cache[region_code]

    config_path = CONFIG_DIR / f"{region_code}.json"
    if not config_path.exists():
        config_path = CONFIG_DIR / "_default.json"
        if not config_path.exists():
            raise FileNotFoundError(f"No config found for region '{region_code}' and no _default.json fallback")

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Malformed JSON in config for region '{region_code}': {e}")

    # Validate required fields
    required_fields = {
        "ai_platforms": dict,
        "official_links": list,
        "knowledge_base_paths": list,
        "default_seeds": list,
        "verification_platforms": list,
        "content_languages": list,
    }
    for field, expected_type in required_fields.items():
        if field not in config:
            raise ValueError(f"Region '{region_code}' config missing required field: {field}")
        if not isinstance(config[field], expected_type):
            raise ValueError(f"Region '{region_code}' field '{field}' expected {expected_type.__name__}, got {type(config[field]).__name__}")

    _config_cache[region_code] = config
    return config


def get_user_region(username: str) -> str:
    """Look up user's region from users.json. Returns 'CN' as default."""
    if not USERS_FILE.exists():
        return "CN"
    try:
        users_data = json.loads(USERS_FILE.read_text(encoding="utf-8"))
        region_map = users_data.get("user_region", {})
        return region_map.get(username, "CN")
    except Exception:
        return "CN"


def get_user_sub_region(username: str) -> Optional[str]:
    """Look up user's sub_region from users.json (for ROA users). Returns None if not set."""
    if not USERS_FILE.exists():
        return None
    try:
        users_data = json.loads(USERS_FILE.read_text(encoding="utf-8"))
        sub_region_map = users_data.get("user_sub_region", {})
        return sub_region_map.get(username)
    except Exception:
        return None


def save_user_sub_region(username: str, sub_region: str):
    """Save user's sub_region choice to users.json."""
    if not USERS_FILE.exists():
        return
    try:
        users_data = json.loads(USERS_FILE.read_text(encoding="utf-8"))
        if "user_sub_region" not in users_data:
            users_data["user_sub_region"] = {}
        users_data["user_sub_region"][username] = sub_region
        USERS_FILE.write_text(json.dumps(users_data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def get_ai_platforms(config: dict) -> tuple:
    """Returns (default_selected, available) platform lists from config."""
    platforms = config.get("ai_platforms", {})
    default_selected = platforms.get("default_selected", ["chatgpt", "gemini"])
    available = platforms.get("available", [])
    return default_selected, available


def get_content_languages(config: dict) -> list:
    """Returns list of content language dicts [{"code": "...", "name": "..."}]."""
    return config.get("content_languages", [{"code": "en", "name": "English"}])


def get_official_links(config: dict, sub_region: Optional[str] = None) -> list:
    """Returns official links, filtered by sub_region if applicable."""
    if sub_region and "sub_regions" in config:
        sub_config = config["sub_regions"].get(sub_region, {})
        if "official_links" in sub_config:
            return sub_config["official_links"]
    return config.get("official_links", [])


def get_default_content_language(config: dict, sub_region: Optional[str] = None) -> str:
    """Returns the default content language code based on sub_region."""
    if sub_region and "sub_regions" in config:
        sub_config = config["sub_regions"].get(sub_region, {})
        if "default_content_language" in sub_config:
            return sub_config["default_content_language"]
    # Return first content language as default
    langs = get_content_languages(config)
    return langs[0]["code"] if langs else "en"


def get_default_seeds(config: dict) -> list:
    """Returns default seed phrases for the region."""
    return config.get("default_seeds", [])


def get_verification_platforms(config: dict) -> list:
    """Returns verification platform list."""
    return config.get("verification_platforms", [])
