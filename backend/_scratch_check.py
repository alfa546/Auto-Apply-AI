import sys

sys.path.insert(0, ".")
from src.app.config import _normalize_str_list, Settings

assert _normalize_str_list("https://a.com,https://b.com") == ["https://a.com", "https://b.com"], _normalize_str_list("https://a.com,https://b.com")
assert _normalize_str_list('["https://a.com", "https://b.com"]') == ["https://a.com", "https://b.com"]
assert _normalize_str_list("https://a.com") == ["https://a.com"]
assert _normalize_str_list(None) == []
assert _normalize_str_list(["x", "  y  "]) == ["x", "y"]

# Verify a Settings instance loads fine with plain string env vars via env_file-style parsing
import os
os.environ["CORS_ORIGINS"] = "https://a.com,https://b.com"
os.environ["ALLOWED_HOSTS"] = "api.example.com,localhost"
s = Settings(_env_file=None)
print("CORS parsed:", s.CORS_ORIGINS)
print("ALLOWED parsed:", s.ALLOWED_HOSTS)
assert s.CORS_ORIGINS == ["https://a.com", "https://b.com"]
assert s.ALLOWED_HOSTS == ["api.example.com", "localhost"]
print("CONFIG CHECKS PASSED")