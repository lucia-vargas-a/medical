"""
test_privacy.py
---------------
Tests for privacy.py.
NOTE: validate_fields() no longer blocks any input — all tests verify
that fields are accepted regardless of content.
"""

from privacy import check_for_personal_info, is_clean, validate_fields


# ── check_for_personal_info (detection still works for informational use) ─────

def test_detects_email():
    assert "email address" in check_for_personal_info("Contact me at user@example.com please")

def test_detects_phone():
    assert "phone number" in check_for_personal_info("Call +34 612 345 678 tomorrow")

def test_detects_url():
    assert "URL / website" in check_for_personal_info("See https://clinic.example.com for details")

def test_detects_full_name():
    assert "full name (First Last)" in check_for_personal_info("Referred by Maria Garcia")

def test_clean_text_returns_empty():
    assert check_for_personal_info("knee pain level 7 after walking") == []


# ── is_clean always returns True ──────────────────────────────────────────────

def test_is_clean_always_true_for_email():
    assert is_clean("user@example.com") is True

def test_is_clean_always_true_for_name():
    assert is_clean("John Smith") is True

def test_is_clean_always_true_for_plain():
    assert is_clean("lower back stiffness") is True


# ── validate_fields always returns ok ────────────────────────────────────────

def test_validate_fields_passes_email():
    result = validate_fields({"notes": "email: user@example.com"})
    assert result["ok"] is True

def test_validate_fields_passes_phone():
    result = validate_fields({"notes": "+34 612 345 678"})
    assert result["ok"] is True

def test_validate_fields_passes_full_name():
    result = validate_fields({"specialty": "Dr. Ana Lopez"})
    assert result["ok"] is True

def test_validate_fields_passes_clean():
    result = validate_fields({"name": "Rheumatoid Arthritis", "notes": "Flare since Monday"})
    assert result["ok"] is True

def test_validate_fields_passes_multiple_fields():
    result = validate_fields({
        "name": "John Smith",
        "notes": "email john@smith.com, phone +1 800 555 0100",
        "city": "Madrid",
    })
    assert result["ok"] is True
