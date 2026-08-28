"""oracle: an employer is a TENANT plus a site, not a site.

🔴 `CX_1001` is Oracle's default site value and two shipped registry entries
already use it. Everything downstream keyed on `site` alone, so:

  - both employers' rows were labelled with one name, or with the slug
  - `employers.py` matches every avoid, avoid_sectors and watch rule against
    that company field, so on this adapter NONE of them could fire
  - two roles with the same title at two different employers looked like one
    role to dedup

🔴 AND THE FALSE-POSITIVE CASE, which is the harder half: several employers have
a genuinely unique site and their labels are written against it. Requiring the
compound key would leave every one of those lookups missing and silently revert
good labels to raw slugs — the fix for unhelpful labels producing no labels.
"""
import importlib.util
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "radar"))
sys.path.insert(0, os.path.join(ROOT, "tools", "lib"))
from adapters import oracle  # noqa: E402

SHARED = "CX_1001"
CFG = {"employers": [{"host": "acme.fa.oraclecloud.com", "site": SHARED},
                     {"host": "other.fa.oraclecloud.com", "site": SHARED},
                     {"host": "widget.fa.oraclecloud.com", "site": "CX_9"}],
       "names": {SHARED: "Acme Bank",
                 "CX_9": "Acme Corp",
                 "other.fa.oraclecloud.com|" + SHARED: "Other Bank"}}


class TheCompoundKey(unittest.TestCase):

    def test_a_host_qualified_label_wins(self):
        self.assertEqual(
            oracle.employer_name(CFG, "other.fa.oraclecloud.com", SHARED), "Other Bank")

    def test_a_site_only_label_is_REFUSED_when_two_tenants_share_the_site(self):
        """🔴 The whole point. A confidently wrong employer name is worse than a
        slug, because a slug is obviously not an answer and a name gets believed."""
        self.assertNotEqual(
            oracle.employer_name(CFG, "acme.fa.oraclecloud.com", SHARED), "Acme Bank")

    def test_the_fallback_is_unique_per_tenant(self):
        """🔴 Falling back to the SITE made two employers identical, which is how
        dedup could collapse across them. The host's first label cannot."""
        a = oracle.employer_name(CFG, "acme.fa.oraclecloud.com", SHARED)
        b = oracle.employer_name({"employers": CFG["employers"], "names": {}},
                                 "other.fa.oraclecloud.com", SHARED)
        self.assertNotEqual(a, b)
        self.assertEqual(a, "acme")


class TheLabelsThatAlreadyWorked(unittest.TestCase):
    """🔴 The false-positive case, and the one the backlog said to test first."""

    def test_a_site_only_label_still_works_when_the_site_is_unique(self):
        self.assertEqual(oracle.employer_name(CFG, "widget.fa.oraclecloud.com", "CX_9"), "Acme Corp")

    def test_a_site_only_label_works_with_no_employers_list_at_all(self):
        """A config that names a site but never lists employers — the lookup must
        not decide it is ambiguous and drop a good label."""
        self.assertEqual(
            oracle.employer_name({"names": {"CX_9": "Acme Corp"}},
                                 "widget.fa.oraclecloud.com", "CX_9"), "Acme Corp")

    def test_no_names_map_at_all_does_not_raise(self):
        self.assertEqual(oracle.employer_name({}, "widget.fa.oraclecloud.com", "CX_9"), "widget")


class TheTenantSlug(unittest.TestCase):

    def test_it_is_the_first_label_of_the_host(self):
        self.assertEqual(oracle.tenant("widget.fa.us2.oraclecloud.com"), "widget")

    def test_an_empty_host_does_not_produce_an_empty_employer(self):
        """🔴 An empty company field matches nothing and is matched BY nothing —
        including every avoid rule, silently."""
        self.assertEqual(oracle.tenant(""), "oracle")
        self.assertEqual(oracle.tenant(None), "oracle")


class TheFailOpen(unittest.TestCase):
    """🔴 An unrecognised site does not fail, it WIDENS: Oracle ignores a
    siteNumber it does not know and returns the whole tenant, so a typo returns
    MORE roles rather than none. probe() has caught this since 2026-08-25, but
    only when somebody runs sources_check — a real run never asked."""

    def test_the_control_site_is_something_no_tenant_could_own(self):
        self.assertNotIn(oracle.CONTROL_SITE.lower(), ("cx_1", "cx_1001", "default", ""))

    def test_the_control_count_is_cached_per_tenant_not_per_employer(self):
        """🟡 Several employers share one host, and the control count is a
        property of the tenant. Probing per employer would multiply requests for
        an answer that cannot differ."""
        self.assertIsInstance(oracle._control_cache, dict)
        with open(os.path.join(ROOT, "tools", "radar", "adapters", "oracle.py"),
                  encoding="utf-8") as fh:
            src = fh.read()
        self.assertIn("if host not in _control_cache", src)

    def test_a_real_run_warns_and_does_not_silently_widen(self):
        with open(os.path.join(ROOT, "tools", "radar", "adapters", "oracle.py"),
                  encoding="utf-8") as fh:
            src = fh.read()
        self.assertIn("searching the whole tenant", src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
