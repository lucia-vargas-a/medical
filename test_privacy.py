"""
test_privacy.py
---------------
Unit tests for the privacy filter.
Run with:  python -m pytest test_privacy.py -v
"""

import pytest
from privacy import check_for_personal_info, is_clean, validate_fields


# ── Tests that SHOULD be blocked ─────────────────────────────────────────────

class TestShouldBlock:

    def test_blocks_email(self):
        assert not is_clean("Contact me at john.doe@gmail.com")

    def test_blocks_email_with_plus(self):
        assert not is_clean("my email is patient+health@yahoo.com")

    def test_blocks_phone_international(self):
        assert not is_clean("Call me at +34 612 345 678")

    def test_blocks_phone_us(self):
        assert not is_clean("My number is 555-123-4567")

    def test_blocks_url(self):
        assert not is_clean("See https://mywebsite.com for info")

    def test_blocks_www_url(self):
        assert not is_clean("visit www.example.com")

    def test_blocks_full_name(self):
        assert not is_clean("Diagnosed by John Smith")

    def test_blocks_street_address(self):
        assert not is_clean("I live at 42 Maple Street")

    def test_blocks_passport_number(self):
        assert not is_clean("My ID is AB1234567")

    def test_validate_fields_catches_multiple(self):
        result = validate_fields({
            "notes": "Call John Smith at john@example.com",
            "city": "Madrid"
        })
        assert result["ok"] == False
        assert len(result["errors"]) >= 2


# ── Tests that SHOULD pass through ───────────────────────────────────────────

class TestShouldAllow:

    def test_allows_plain_notes(self):
        assert is_clean("Pain started after walking for one hour")

    def test_allows_medication_name(self):
        assert is_clean("Ibuprofen 400mg caused severe headache and nausea")

    def test_allows_body_part(self):
        assert is_clean("Left knee, significant swelling after exercise")

    def test_allows_specialty(self):
        assert is_clean("Orthopedic specialist")

    def test_allows_city_and_country(self):
        assert is_clean("Madrid, Spain")

    def test_allows_treatment_description(self):
        assert is_clean("Physiotherapy twice a week for four weeks, mild improvement")

    def test_allows_empty_string(self):
        assert is_clean("")

    def test_allows_none(self):
        assert is_clean(None)

    def test_validate_fields_clean(self):
        result = validate_fields({
            "notes": "Swelling reduced after ice pack",
            "specialty": "Rheumatologist"
        })
        assert result["ok"] == True


# ── Regression tests — specific cases that were reported as issues ────────────

class TestRegression:

    def test_regression_naproxen_note(self):
        """Real-world note: medication with side effects, no personal info."""
        text = "Naproxen 500mg twice daily. No relief after one week. Stopped due to stomach pain."
        assert is_clean(text)

    def test_regression_physiotherapy_note(self):
        """Real-world note: treatment outcome, no personal info."""
        text = "Physiotherapy sessions helped reduce stiffness in left shoulder. Pain went from 8 to 5."
        assert is_clean(text)

    def test_regression_blocks_embedded_email(self):
        """Email hidden inside a longer sentence."""
        text = "For follow-up contact drsmith@hospital.org thanks"
        assert not is_clean(text)

    def test_regression_blocks_phone_in_notes(self):
        """Phone number embedded in notes field."""
        text = "Appointment confirmed, call 212-555-0199 to reschedule"
        assert not is_clean(text)
