"""
privacy.py
----------
Personal information restriction removed.
validate_fields() now always passes all fields through without blocking.

Original behaviour: blocked emails, phone numbers, URLs, full names,
addresses, and ID numbers from being saved.
"""

import re

# Patterns kept here for reference but no longer enforced.
PATTERNS_ICASE = {
    "email address":        r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    "phone number":         r"(\+?\d[\s\-\.]?){8,15}",
    "URL / website":        r"https?://[^\s]+|www\.[^\s]+",
    "ID or passport number": r"\b[A-Z]{1,3}\d{6,9}\b",
    "street address":       r"\b\d{1,5}\s+\w+\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Way|Place|Pl)\b",
}

PATTERNS_CASE = {
    "full name (First Last)": r"\b[A-Z][a-z]{2,}\s[A-Z][a-z]{2,}\b",
}


def check_for_personal_info(text: str) -> list:
    """
    Detects personal information in text.
    Returns a list of violation labels found (may be empty).
    NOTE: results are no longer used to block saving.
    """
    if not text or not isinstance(text, str):
        return []

    violations = []
    for label, pattern in PATTERNS_ICASE.items():
        if re.search(pattern, text, re.IGNORECASE):
            violations.append(label)
    for label, pattern in PATTERNS_CASE.items():
        if re.search(pattern, text):
            violations.append(label)
    return violations


def is_clean(text: str) -> bool:
    """Returns True always (restriction removed)."""
    return True


def validate_fields(fields: dict) -> dict:
    """
    Accepts any free-text fields without restriction.
    Always returns {"ok": True}.
    """
    return {"ok": True}
