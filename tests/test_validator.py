"""Tests for src/validator.py – one row per contract scenario."""

import textwrap

import pytest

from validator import validate

# ── shared URL pool ──────────────────────────────────────────────────────
FETCHED = {
    "https://example.com/about",
    "https://example.com/news",
    "https://example.com/products",
    "https://example.com/blog",
}

# ── helpers ──────────────────────────────────────────────────────────────

def _perfect_briefing() -> str:
    """A briefing that satisfies every rule in the contract."""
    return textwrap.dedent("""\
        ### What the company does
        They sell widgets to enterprises. (https://example.com/about)
        ### What changed in the last 90 days
        Launched a new product line in September. (https://example.com/news)
        ### Three talking points
        First, revenue grew 20 %. (https://example.com/products)
        Second, they hired a new CTO. (https://example.com/blog)
        Third, they expanded to Europe. (https://example.com/news)
        Tool calls used: 5 of 8""")


# ── test rows ────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "label, briefing, fetched_urls, expect_pass, expect_reason_substring",
    [
        # ── ROW 1: perfect briefing ──────────────────────────────────
        pytest.param(
            "all_rules_pass",
            _perfect_briefing(),
            FETCHED,
            True,
            None,
            id="row1-perfect",
        ),
        # ── ROW 2: missing heading ───────────────────────────────────
        pytest.param(
            "missing_heading",
            textwrap.dedent("""\
                ### What the company does
                They sell widgets. (https://example.com/about)
                ### Three talking points
                Revenue grew. (https://example.com/products)
                Tool calls used: 3 of 8"""),
            FETCHED,
            False,
            "missing",
            id="row2-missing-heading",
        ),
        # ── ROW 3: factual sentence without citation ─────────────────
        pytest.param(
            "uncited_sentence",
            textwrap.dedent("""\
                ### What the company does
                They sell widgets to enterprises.
                ### What changed in the last 90 days
                Launched a new product. (https://example.com/news)
                ### Three talking points
                Revenue grew. (https://example.com/products)
                Tool calls used: 4 of 8"""),
            FETCHED,
            False,
            "missing a trailing URL",
            id="row3-uncited-sentence",
        ),
        # ── ROW 4: cited URL not in fetched set ──────────────────────
        pytest.param(
            "url_not_fetched",
            textwrap.dedent("""\
                ### What the company does
                They sell widgets. (https://never-fetched.example.com/page)
                ### What changed in the last 90 days
                Launched a new product. (https://example.com/news)
                ### Three talking points
                Revenue grew. (https://example.com/products)
                Tool calls used: 4 of 8"""),
            FETCHED,
            False,
            "not in fetched",
            id="row4-url-not-fetched",
        ),
        # ── ROW 5: gap-line-only section counts as present ───────────
        pytest.param(
            "gap_line_section",
            textwrap.dedent("""\
                ### What the company does
                They sell widgets. (https://example.com/about)
                ### What changed in the last 90 days
                Not found in sources.
                ### Three talking points
                Revenue grew. (https://example.com/products)
                Tool calls used: 3 of 8"""),
            FETCHED,
            True,
            None,
            id="row5-gap-line-section-passes",
        ),
        # ── ROW 6: bad closing line / over budget ────────────────────
        pytest.param(
            "bad_closing_line",
            textwrap.dedent("""\
                ### What the company does
                They sell widgets. (https://example.com/about)
                ### What changed in the last 90 days
                Launched a new product. (https://example.com/news)
                ### Three talking points
                Revenue grew. (https://example.com/products)
                Tool calls used: 12 of 8"""),
            FETCHED,
            False,
            "exceeds budget",
            id="row6-over-budget",
        ),
    ],
)
def test_validate_briefing_row(
    label: str,
    briefing: str,
    fetched_urls: set,
    expect_pass: bool,
    expect_reason_substring: str | None,
):
    passed, reasons = validate(briefing, fetched_urls)

    assert passed is expect_pass, (
        f"[{label}] expected passed={expect_pass}, got {passed}.\n"
        f"Reasons: {reasons}"
    )

    # Every run should produce exactly five reason strings (one per check).
    assert len(reasons) == 5, (
        f"[{label}] expected 5 reasons, got {len(reasons)}: {reasons}"
    )

    if expect_reason_substring is not None:
        joined = "\n".join(reasons)
        assert expect_reason_substring.lower() in joined.lower(), (
            f"[{label}] expected reason containing {expect_reason_substring!r}, "
            f"got:\n{joined}"
        )
