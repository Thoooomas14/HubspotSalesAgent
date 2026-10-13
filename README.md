## Briefing contract
Sections, in order, as exact headings:
- `## What the company does`
- `## What changed in the last 90 days`
- `## Three talking points`

Rules:
1. Every factual sentence ends with a source URL in parentheses, and that URL must be a page the agent fetched.
2. A section with no sourced facts contains exactly this line: `Not found in sources`
3. The last line is exactly: `Tool calls used: N` where N is the count.
4. Budget: at most 8 tool calls.

Not factual, so no citation needed: headings, the gap line, the closing line.

## Validator

`src/validator.py` exposes a single function:

```python
from validator import validate

passed, reasons = validate(briefing_markdown, fetched_urls)
```

| Parameter            | Type                   | Description                                      |
|----------------------|------------------------|--------------------------------------------------|
| `briefing_markdown`  | `str`                  | Full text of a generated briefing (Markdown).     |
| `fetched_urls`       | `set[str] | list[str]` | URLs the agent actually fetched during the run.   |

**Returns** `(passed: bool, reasons: list[str])`:
- `passed` is `True` only when every check succeeds.
- `reasons` always contains exactly **5 strings** (one per check), so callers can log what passed and what broke:
  1. Headings present and in order
  2. Every factual sentence has a trailing `(URL)`
  3. Every cited URL appears in `fetched_urls`
  4. Every section has content (or the gap line)
  5. Closing line matches format and count <= 8

## Rep usage instructions
(left empty, filled in the final stage)

## Test run output

Tests load all six rows from `Briefings for Validator Tests.json` and compare
each `expected_valid` label against the validator verdict.

```
tests/test_validator.py::test_validate_briefing[SB-01]
-- SB-01 (Gusto) -- verdict: PASS
   Headings: all three present and in order.
   Citations: every factual sentence has a trailing URL.
   Fetched URLs: all cited URLs were fetched by the agent.
   Sections: every section has content (or the gap line).
   Closing line: matches format and count 6 <= 8.
PASSED

tests/test_validator.py::test_validate_briefing[SB-02]
-- SB-02 (Calendly) -- verdict: PASS
   Headings: all three present and in order.
   Citations: every factual sentence has a trailing URL.
   Fetched URLs: all cited URLs were fetched by the agent.
   Sections: every section has content (or the gap line).
   Closing line: matches format and count 5 <= 8.
PASSED

tests/test_validator.py::test_validate_briefing[SB-03]
-- SB-03 (Asana) -- verdict: PASS
   Headings: all three present and in order.
   Citations: every factual sentence has a trailing URL.
   Fetched URLs: all cited URLs were fetched by the agent.
   Sections: every section has content (or the gap line).
   Closing line: matches format and count 8 <= 8.
PASSED

tests/test_validator.py::test_validate_briefing[SB-04]
-- SB-04 (Zendesk) -- verdict: FAIL
   Headings: missing ['## What changed in the last 90 days'].
   Citations: every factual sentence has a trailing URL.
   Fetched URLs: all cited URLs were fetched by the agent.
   Sections: every section has content (or the gap line).
   Closing line: matches format and count 6 <= 8.
PASSED

tests/test_validator.py::test_validate_briefing[SB-05]
-- SB-05 (Mailchimp) -- verdict: FAIL
   Headings: all three present and in order.
   Citations: 1 sentence(s) missing a trailing URL: Mailchimp has been part of Intuit since its acquisition in 2021
   Fetched URLs: all cited URLs were fetched by the agent.
   Sections: every section has content (or the gap line).
   Closing line: matches format and count 7 <= 8.
PASSED

tests/test_validator.py::test_validate_briefing[SB-06]
-- SB-06 (Canva) -- verdict: FAIL
   Headings: all three present and in order.
   Citations: every factual sentence has a trailing URL.
   Fetched URLs: 1 cited URL(s) not in fetched set: https://www.canva.com/enterprise/
   Sections: every section has content (or the gap line).
   Closing line: matches format and count 6 <= 8.
PASSED

6 passed in 0.06s
```