"""Regression coverage for audit integrity, API calculations and page source."""
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from fastapi import HTTPException
from agents.api import CalculationRequest, api_calculate, browser_app
from agents.base import AuditTrail
from cli import parse_csv_boolean

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = {
    "sodium": 140, "potassium": 4, "ionized_calcium": 1.2,
    "ionized_magnesium": 0.8, "chloride": 104, "lactate": 1.5,
    "ph": 7.4, "pco2": 40, "albumin": 40, "phosphate": 1.2,
}


def test_api_calculator_parity():
    assert api_calculate(CalculationRequest(**EXAMPLE))["sig_mEq_L"] == 5.128


def test_api_rejects_invalid_co2():
    with pytest.raises(HTTPException) as caught:
        api_calculate(CalculationRequest(**{**EXAMPLE, "pco2": 0}))
    assert caught.value.status_code == 422


def test_api_rejects_nonfinite_values():
    with pytest.raises(ValueError):
        CalculationRequest(**{**EXAMPLE, "pco2": float("nan")})


def test_local_server_can_serve_browser():
    assert browser_app().path == str(ROOT / "index.html")


def test_audit_hmac_verification_and_defensive_copy():
    trail = AuditTrail("local-test-secret")
    trail.log("tester", "research", "example", {"state": "ok"})
    assert trail.verify_integrity()
    trail.get_trail()[0]["actor"] = "external"
    assert trail.verify_integrity()
    trail.logs[0]["actor"] = "tampered"
    assert not trail.verify_integrity()


def test_audit_signature_substitution_detected():
    trail = AuditTrail("local-test-secret")
    trail.log("tester", "research", "example", {"state": "ok"})
    trail.logs[0]["current_hash"] = "0" * 64
    assert not trail.verify_integrity()


@pytest.mark.parametrize("raw,expected", [("true", True), ("FALSE", False),
                                          ("0", False), ("yes", True), ("", False)])
def test_critical_flag_parsing(raw, expected):
    assert parse_csv_boolean(raw) is expected


def test_reject_ambiguous_csv_boolean():
    with pytest.raises(ValueError):
        parse_csv_boolean("unknown")


def test_browser_script_has_valid_javascript():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js not installed")
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    script = re.findall(r"<script>(.*?)</script>", text, flags=re.DOTALL)
    assert len(script) == 1
    result = subprocess.run([node, "--check"], input=script[0], text=True,
                            capture_output=True, timeout=10, check=False)
    assert result.returncode == 0, result.stderr


def test_browser_has_no_backend_dependency():
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "fetch(" not in text
    assert "localhost" not in text
    assert "http://" not in text
