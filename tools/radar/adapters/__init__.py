"""Search adapters. Each exposes fetch(cfg, query, days) -> list[dict].

A posting dict is: {id, title, company, loc, date, url, body}
`body` may be empty at listing time; the runner fills it via fetch_body if the
adapter provides one.

Adding an adapter: write the module, expose fetch(), add it to ADAPTERS below.
"""
from . import adzuna, greenhouse, lever, linkedin

ADAPTERS = {
    "adzuna": adzuna,
    "greenhouse": greenhouse,
    "lever": lever,
    "linkedin": linkedin,
}
