"""The verdicts sources_check.py renders, in one module so they cannot drift.

Kept out of the package __init__ because the adapters import them and __init__
imports the adapters -- a cycle. Out of _http.py because they are not about HTTP.

Two of these exist because collapsing them is the failure this was built for,
and both are the same mistake in different clothes:

  NOT_CONFIGURED is not FAILED. An adapter nobody set up has not been tried.
  Reporting it as broken sends someone to debug a source they never wanted;
  reporting it as fine claims coverage that does not exist.

  NO_COVERAGE is not BAD_CREDENTIALS. A job API returning 404 for one country
  while serving others is saying it does not cover that country -- not that the
  key is wrong. One probe cannot tell those apart, which is why any adapter that
  can hit this must probe a KNOWN-GOOD control alongside the user's own country.
  Guessing wrong here cost a real user an hour.
"""
OK = "OK"
EMPTY = "EMPTY"
NOT_CONFIGURED = "NOT CONFIGURED"
NO_COVERAGE = "NO COVERAGE"
BAD_CREDENTIALS = "BAD CREDENTIALS"
BLOCKED = "BLOCKED"
FAILED = "FAILED"

# Ordered worst-first, so a report can lead with what needs doing.
SEVERITY = [BAD_CREDENTIALS, NO_COVERAGE, BLOCKED, FAILED, EMPTY, NOT_CONFIGURED, OK]
