## Briefing contract
Sections, in order, as exact headings:
## What the company does
## What changed in the last 90 days
## Three talking points
Rules:
1. Every factual sentence ends with a source URL in parentheses, and that URL must be a page the agent fetched.
2. A section with no sourced facts contains exactly this line: Not found in sources.
3. The last line is exactly: Tool calls used: N of 8
4. Budget: at most 8 tool calls.
Not factual, so no citation needed: headings, the gap line, the closing line.
## Rep usage instructions
(left empty, filled in the final stage)


========================================== test session starts ==========================================
platform win32 -- Python 3.13.5, pytest-9.1.1, pluggy-1.5.0 -- C:\Users\thoma\miniconda3\python.exe       
cachedir: .pytest_cache
rootdir: C:\Users\thoma\Projects\Zero\HubspotSalesAgent
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.13.0
collected 6 items                                                                                        

tests/test_validator.py::test_validate_briefing[SB-01] PASSED                                      [ 16%] 
tests/test_validator.py::test_validate_briefing[SB-02] PASSED                                      [ 33%] 
tests/test_validator.py::test_validate_briefing[SB-03] PASSED                                      [ 50%]
tests/test_validator.py::test_validate_briefing[SB-04] PASSED                                      [ 66%] 
tests/test_validator.py::test_validate_briefing[SB-05] PASSED                                      [ 83%] 
tests/test_validator.py::test_validate_briefing[SB-06] PASSED                                      [100%]

=========================================== 6 passed in 0.16s =========================================== 