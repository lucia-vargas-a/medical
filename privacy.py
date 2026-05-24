"""
privacy.py
----------
Detects and blocks personal information from being saved to the database.
Checks for: emails, phone numbers, URLs, full names, addresses, ID numbers.
"""

import re

# Patterns applied case-insensitively (except full_name which must be case-sensitive)
PATTERNS_ICASE = {
    "email address":      r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    "phone number":       r"(\+?\d[\s\-\.]?){8,15}",
    "URL / website":      r"https?://[^\s]+|www\.[^\s]+",
    "ID or passport number": r"\b[A-Z]{1,3}\d{6,9}\b",
    "street address":     r"\b\d{1,5}\s+\w+\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Way|Place|Pl)\b",
}

# Case-sensitive: only matches ProperCase ProperCase (real names)
PATTERNS_CASE = {
    "full name (First Last)": r"\b[A-Z][a-z]{2,}\s[A-Z][a-z]{2,}\b",
}


def check_for_personal_info(text: str) -> list:
    """
    Returns a list of violation descriptions found in the text.
    Returns an empty list if the text is clean.
    """
    if not text or not isinstance(text, str):
        return []

    violations = []

    for label, pattern in PATTERNS_ICASE.items():
        if re.search(pattern, text, re.IGNORECASE):
            violations.append(label)

    for label, pattern in PATTERNS_CASE.items():
        if re.search(pattern, text):  # NO IGNORECASE — must be ProperCase
            violations.append(label)

    return violations


def is_clean(text: str) -> bool:
    """Returns True if no personal information is detected."""
    return len(check_for_personal_info(text)) == 0


def validate_fields(fields: dict) -> dict:
    """
    Pass a dict of {field_name: value} for all free-text fields.
    Returns {"ok": True} if clean, or {"ok": False, "errors": [...]} if not.
    """
    all_errors = []
    for field_name, value in fields.items():
        violations = check_for_personal_info(str(value))
        for v in violations:
            all_errors.append(f"Field '{field_name}' appears to contain a {v}. Please remove personal information.")

    if all_errors:
        return {"ok": False, "errors": all_errors}
    return {"ok": True}
