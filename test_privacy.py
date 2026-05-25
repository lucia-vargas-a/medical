"""
test_privacy.py
---------------
Unit tests for the privacy filter.
Note: URLs are now ALLOWED (used for attachments).
"""
import pytest
from privacy import check_for_personal_info, is_clean, validate_fields


class TestEmail:
    def test_blocks_email(self):
        assert check_for_personal_info("contact me at user@example.com") != []

    def test_allows_no_email(self):
        assert check_for_personal_info("pain in lower back, level 7") == []


class TestPhone:
    def test_blocks_phone(self):
        result = check_for_personal_info("call +34 612 345 678")
        assert result != []

    def test_allows_medical_numbers(self):
        # Dosage numbers should not trigger
        result = check_for_personal_info("Ibuprofen 400mg three times daily")
        assert result == []


class TestFullName:
    def test_blocks_full_name(self):
        result = check_for_personal_info("visited Doctor Garcia Martinez today")
        assert result != []

    def test_allows_single_word(self):
        assert is_clean("visited physio today, DR-1")

    def test_allows_code_system(self):
        assert is_clean("DR-1 recommended rest for 5 days")


class TestURLsAllowed:
    def test_allows_http_url(self):
        # URLs are now allowed (for attachments)
        assert is_clean("https://results.hospital.com/report/123")

    def test_allows_www_url(self):
        assert is_clean("www.labresults.com/my/report")


class TestValidateFields:
    def test_clean_fields(self):
        result = validate_fields({
            "symptoms": "pain in lower back, stiffness in the morning",
            "context": "worked from home, sat for long hours",
        })
        assert result["ok"] is True

    def test_dirty_field(self):
        result = validate_fields({
            "symptoms": "call me at user@email.com",
        })
        assert result["ok"] is False
        assert len(result["errors"]) >= 1

    def test_empty_fields_ok(self):
        result = validate_fields({"symptoms": "", "context": ""})
        assert result["ok"] is True
