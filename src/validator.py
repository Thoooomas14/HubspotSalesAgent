"""Briefing-contract validator.

Checks every rule defined in the README § Briefing contract and returns
``(passed: bool, reasons: list[str])``.  One check per rule, each adding
its own reason so callers can see exactly what failed (or that everything
passed).
"""

from __future__ import annotations

import re
from typing import List, Set, Tuple

# ── constants ────────────────────────────────────────────────────────────
HEADINGS = [
    "### What the company does",
    "### What changed in the last 90 days",
    "### Three talking points",
]

GAP_LINE = "Not found in sources."

CLOSING_RE = re.compile(r"^Tool calls used: (\d+) of 8$")

# Factual-sentence citation: ends with ``(https://…)`` (or ``(http://…)``).
_CITATION_RE = re.compile(r"\(https?://[^\s)]+\)\s*$")

# Extract the bare URL from the trailing parenthetical.
_URL_EXTRACT_RE = re.compile(r"\((https?://[^\s)]+)\)\s*$")


# ── helpers ──────────────────────────────────────────────────────────────

def _is_skip_line(line: str, closing_line: str | None) -> bool:
    """Return True for lines that are NOT factual sentences per the README:
    headings, the exact gap line, and the closing tool-call line.
    """
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith("#"):
        return True
    if stripped == GAP_LINE:
        return True
    if closing_line is not None and stripped == closing_line:
        return True
    return False


# ── public API ───────────────────────────────────────────────────────────

def validate(
    briefing_markdown: str,
    fetched_urls: Set[str] | List[str],
) -> Tuple[bool, List[str]]:
    """Validate *briefing_markdown* against every briefing-contract rule.

    Parameters
    ----------
    briefing_markdown:
        The full text of a generated briefing (Markdown).
    fetched_urls:
        Collection of URLs the agent actually fetched during the run.

    Returns
    -------
    (passed, reasons)
        *passed* is ``True`` only when **all** checks succeed.
        *reasons* always contains one entry per check so the caller can
        log exactly what happened.
    """
    fetched: set[str] = set(fetched_urls)
    reasons: list[str] = []
    lines = briefing_markdown.splitlines()

    # ── 1. All three headings present, in order ──────────────────────
    heading_positions: list[int] = []
    for heading in HEADINGS:
        found_idx: int | None = None
        for i, line in enumerate(lines):
            if line.strip() == heading:
                found_idx = i
                break
        heading_positions.append(found_idx if found_idx is not None else -1)

    all_found = all(pos >= 0 for pos in heading_positions)
    in_order = all(
        heading_positions[i] < heading_positions[i + 1]
        for i in range(len(heading_positions) - 1)
    ) if all_found else False

    if all_found and in_order:
        reasons.append("Headings: all three present and in order.")
    else:
        missing = [
            h for h, p in zip(HEADINGS, heading_positions) if p < 0
        ]
        if missing:
            reasons.append(
                f"Headings: missing {missing}."
            )
        elif not in_order:
            reasons.append("Headings: present but out of order.")

    # ── 2 & 3. Factual-sentence citations and URL membership ─────────
    # Determine the closing line (last non-blank line) so we can skip it.
    closing_line: str | None = None
    for rev_line in reversed(lines):
        if rev_line.strip():
            closing_line = rev_line.strip()
            break

    uncited: list[str] = []
    bad_urls: list[str] = []

    for line in lines:
        if _is_skip_line(line, closing_line):
            continue

        # This is a factual sentence – it must end with a cited URL.
        match = _CITATION_RE.search(line)
        if not match:
            uncited.append(line.strip())
            continue

        url_match = _URL_EXTRACT_RE.search(line)
        if url_match:
            url = url_match.group(1)
            if url not in fetched:
                bad_urls.append(url)

    if not uncited:
        reasons.append("Citations: every factual sentence has a trailing URL.")
    else:
        reasons.append(
            f"Citations: {len(uncited)} sentence(s) missing a trailing URL: "
            + "; ".join(uncited[:5])
        )

    if not bad_urls:
        reasons.append("Fetched URLs: all cited URLs were fetched by the agent.")
    else:
        reasons.append(
            f"Fetched URLs: {len(bad_urls)} cited URL(s) not in fetched set: "
            + "; ".join(bad_urls[:5])
        )

    # ── 4. Gap-line sections count as present ────────────────────────
    # A section whose only non-blank content is the gap line is still
    # considered *present* (not missing).  We verify that every section
    # between headings has at least one content line OR the gap line.
    empty_sections: list[str] = []
    for idx, heading in enumerate(HEADINGS):
        h_pos = heading_positions[idx]
        if h_pos < 0:
            continue  # already flagged in check 1
        # Section runs from h_pos+1 up to (but not including) the next
        # heading or end-of-file.
        next_pos = (
            heading_positions[idx + 1]
            if idx + 1 < len(heading_positions) and heading_positions[idx + 1] >= 0
            else len(lines)
        )
        section_lines = [
            l.strip()
            for l in lines[h_pos + 1 : next_pos]
            if l.strip()
            and not CLOSING_RE.match(l.strip())
        ]
        if not section_lines:
            empty_sections.append(heading)

    if not empty_sections:
        reasons.append(
            "Sections: every section has content (or the gap line)."
        )
    else:
        reasons.append(
            f"Sections: {len(empty_sections)} section(s) are truly empty "
            f"(not even the gap line): {empty_sections}"
        )

    # ── 5. Closing line format and budget ────────────────────────────
    last_line = ""
    for rev_line in reversed(lines):
        if rev_line.strip():
            last_line = rev_line.strip()
            break

    m = CLOSING_RE.match(last_line)
    if m:
        n = int(m.group(1))
        if n <= 8:
            reasons.append(
                f"Closing line: matches format and count {n} ≤ 8."
            )
        else:
            reasons.append(
                f"Closing line: matches format but count {n} exceeds budget of 8."
            )
    else:
        reasons.append(
            f"Closing line: does not match expected pattern. Got: {last_line!r}"
        )

    # ── aggregate ────────────────────────────────────────────────────
    passed = (
        all_found
        and in_order
        and not uncited
        and not bad_urls
        and not empty_sections
        and (m is not None and int(m.group(1)) <= 8)
    )

    return passed, reasons
