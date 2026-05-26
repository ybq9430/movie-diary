"""
Root config — re-exports shared constants from backend.config,
plus CLI-specific settings (CHINESE_FONTS, OUTPUT_DIR).
"""
import importlib.util
import sys
from pathlib import Path

# Load backend/config.py explicitly to avoid circular self-import
_backend_config = Path(__file__).resolve().parent / "backend" / "config.py"
_spec = importlib.util.spec_from_file_location("backend_config", _backend_config)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

HEADERS_TEMPLATE = _mod.HEADERS_TEMPLATE
DELAY_LIST_PAGE = _mod.DELAY_LIST_PAGE
DELAY_DETAIL_PAGE = _mod.DELAY_DETAIL_PAGE
PAGE_SIZE = _mod.PAGE_SIZE
MAX_RETRIES = _mod.MAX_RETRIES
BACKOFF_BASE = _mod.BACKOFF_BASE
random_delay = _mod.random_delay

# CLI-specific settings
CHINESE_FONTS = ["SimHei", "Microsoft YaHei", "WenQuanYi Micro Hei"]
OUTPUT_DIR = "output"
