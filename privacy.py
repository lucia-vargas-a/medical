import re

PATTERNS_ICASE = {
    "email address": r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    "phone number":  r"(\+?\d[\s\-\.]?){8,15}",
}

PATTERNS_CASE = {
    "full name (First Last)": r"\b[A-Z][a-z]{2,}\s[A-Z][a-z]{2,}\b",
}


def check_for_personal_info(text):
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


def validate_fields(fields):
    all_errors = []
    for field_name, value in fields.items():
        for v in check_for_personal_info(str(value)):
            all_errors.append(
                f"Field '{field_name}' appears to contain a {v}. Please remove personal information."
            )
    if all_errors:
        return {"ok": False, "errors": all_errors}
    return {"ok": True}
