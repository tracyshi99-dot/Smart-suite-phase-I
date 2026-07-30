"""
i18n - Internationalization strings for Smart Suite UI.
Supports 5 languages: en, zh-CN, zh-TW, ko, vi

Usage:
    from i18n import t, set_language
    set_language("zh-TW")
    label = t("ui.save")  # returns "儲存"
"""
import json
from pathlib import Path

_current_lang = "en"

# Load translations from JSON file
_STRINGS_FILE = Path(__file__).parent / "i18n_strings.json"
if _STRINGS_FILE.exists():
    STRINGS = json.loads(_STRINGS_FILE.read_text(encoding="utf-8"))
else:
    STRINGS = {}


def set_language(lang_code: str):
    """Set the active UI language."""
    global _current_lang
    if lang_code in ("en", "zh-CN", "zh-TW", "ko", "vi"):
        _current_lang = lang_code


def get_language() -> str:
    """Get current active UI language code."""
    return _current_lang


def t(key: str, lang: str = None) -> str:
    """Translate a key to the current (or specified) language.
    Falls back: requested lang → zh-CN (if zh-TW requested) → en → key itself.
    """
    lang = lang or _current_lang
    entry = STRINGS.get(key)
    if not entry:
        return key  # Key not found, return as-is
    # Try exact match
    if lang in entry and entry[lang]:
        return entry[lang]
    # Fallback chain
    if lang == "zh-TW" and entry.get("zh-CN"):
        return entry["zh-CN"]
    if lang.startswith("zh") and entry.get("zh-CN"):
        return entry["zh-CN"]
    # Final fallback to English
    return entry.get("en", key)
