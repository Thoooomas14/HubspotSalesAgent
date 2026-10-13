"""Tests for src/validator.py – runs all six briefing rows from the JSON fixture."""

import json
import pathlib

import pytest

from validator import validate

# ── load the fixture once ────────────────────────────────────────────────
_FIXTURE = pathlib.Path(__file__).resolve().parents[1] / "Briefings for Validator Tests.json"
_ROWS = json.loads(_FIXTURE.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "row",
    _ROWS,
    ids=[r["sample_id"] for r in _ROWS],
)
def test_validate_briefing(row: dict, capsys):
    passed, reasons = validate(row["briefing_markdown"], row["fetched_urls"])

    # Print verdict and reasons so ``pytest -v -s`` captures the full record.
    verdict = "PASS" if passed else "FAIL"
    print(f"\n-- {row['sample_id']} ({row['company_name']}) -- verdict: {verdict}")
    for r in reasons:
        print(f"   {r}")

    assert passed is row["expected_valid"], (
        f"[{row['sample_id']} / {row['company_name']}] "
        f"expected passed={row['expected_valid']}, got {passed}.\n"
        f"Reasons:\n" + "\n".join(f"  • {r}" for r in reasons)
    )

    # Every run must produce exactly 5 reason strings (one per check).
    assert len(reasons) == 5, (
        f"[{row['sample_id']}] expected 5 reasons, got {len(reasons)}: {reasons}"
    )
