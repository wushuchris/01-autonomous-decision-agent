import base64
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".py", ".md", ".json", ".txt", ".yml", ".yaml", ".csv"}

FORBIDDEN_MARKERS_B64 = {
    "QWdlbnQgRW5naW5lZXJpbmcgTWFzdGVyIEN1cnJpY3VsdW0=",
    "V09SS0lOR19NRVRIT0QubWQ=",
    "YWdlbnRfZW5nX2N1cnJpY3VsdW0=",
    "MTUgRXF1aXR5",
    "SEZfMDFfQWdlbnQ=",
    "QWR2aXNvckxlYWQ=",
    "YWR2aXNvcl9uYW1l",
    "dXNlc19tb2RlbF9tYXJrZXRwbGFjZQ==",
}

SECRET_PATTERNS = [
    re.compile(r"hf_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"(?i)(?:api[_-]?key|token|secret)\s*=\s*['\"][A-Za-z0-9_\-]{20,}['\"]"),
]


def decoded_forbidden_markers():
    return {
        base64.b64decode(value).decode("utf-8")
        for value in FORBIDDEN_MARKERS_B64
    }


def iter_public_text_files():
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in {".git", ".pytest_cache", "__pycache__"} for part in path.parts):
            continue
        yield path


def test_public_checkout_contains_no_private_source_markers():
    violations = []
    markers = decoded_forbidden_markers()
    for path in iter_public_text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for marker in markers:
            if marker in text:
                violations.append(str(path.relative_to(ROOT)))
    assert violations == []


def test_public_checkout_contains_no_common_literal_secret_patterns():
    violations = []
    for path in iter_public_text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                violations.append(str(path.relative_to(ROOT)))
    assert violations == []
