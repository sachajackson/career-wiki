"""add_employer: verify before contributing, and never send more than one file.

Two things here were found by running the tool against the registry it was
written to extend. Its ATS sniffer reproduced three of five entries exactly --
and on the fourth it picked a friendly site name that Oracle does not recognise,
which would have produced an entry that verified successfully and silently
fetched the wrong thing.
"""
import importlib.util, json, os, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AE = os.path.join(ROOT, "tools", "add_employer.py")
spec = importlib.util.spec_from_file_location("add_employer", AE)
ae = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ae)


def sniff_html(html):
    """sniff() with the network replaced by a fixture."""
    real, ae.get = ae.get, lambda *a, **k: html
    try:
        return ae.sniff("https://example.com/careers")
    finally:
        ae.get = real


class Sniffing(unittest.TestCase):
    def test_greenhouse(self):
        ats, p = sniff_html('<a href="https://boards.greenhouse.io/monzo">Jobs</a>')
        self.assertEqual((ats, p["token"]), ("greenhouse", "monzo"))

    def test_lever(self):
        ats, p = sniff_html('<a href="https://jobs.lever.co/someco/">Jobs</a>')
        self.assertEqual((ats, p["handle"]), ("lever", "someco"))

    def test_workday_shared_host_carries_tenant_and_site(self):
        ats, p = sniff_html('href="https://wd1.myworkdaysite.com/recruiting/ssctech/SSCTechnologies"')
        self.assertEqual((p["host"], p["tenant"], p["site"]),
                         ("wd1.myworkdaysite.com", "ssctech", "SSCTechnologies"))

    def test_oracle_prefers_a_cx_number_over_a_friendly_name(self):
        """A friendly site name is not a siteNumber. Oracle ignores it and returns
        the tenant's whole unfiltered list, so an entry using one claims a filter
        it does not apply."""
        html = ('href="https://ehzq.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/'
                'sites/GrantThorntonIrelandExperiencedHires" '
                'href="https://ehzq.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001"')
        ats, p = sniff_html(html)
        self.assertEqual(p["site"], "CX_1001")
        self.assertFalse(p["_unfiltered"])

    def test_oracle_flags_when_it_only_found_a_friendly_name(self):
        html = ('href="https://ehzq.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/'
                'sites/GrantThorntonIrelandExperiencedHires"')
        _, p = sniff_html(html)
        self.assertTrue(p["_unfiltered"], "must warn rather than pass it off as a filtered site")

    def test_a_page_with_no_marker_explains_what_to_do(self):
        ats, why = sniff_html("<html>we are hiring, honestly</html>")
        self.assertIsNone(ats)
        self.assertIn("custom", why)


class TheCareersUrlGuard(unittest.TestCase):
    def run_cli(self, *args):
        r = subprocess.run([sys.executable, AE, *args], capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    def test_an_ats_address_is_refused(self):
        """The careers page is the recovery key; an ATS link expires when it is needed."""
        for url in ("https://boards.greenhouse.io/stripe",
                    "https://acme.wd1.myworkdayjobs.com/External",
                    "https://x.fa.us2.oraclecloud.com/hcmUI"):
            code, out = self.run_cli("Acme", url)
            self.assertEqual(code, 1, url)
            self.assertIn("ATS address", out)

    def test_it_needs_a_name_and_a_url(self):
        code, out = self.run_cli("Acme")
        self.assertNotEqual(code, 0)


class SendingOnlyOneFile(unittest.TestCase):
    def test_it_refuses_when_anything_else_is_dirty(self):
        """This runs from a working copy that also holds a private wiki."""
        real = ae.one_file_staged
        ae.one_file_staged = lambda: (False, ["wiki/CV.md", ae.REL])
        try:
            self.assertEqual(ae.contribute("Acme"), 1)
        finally:
            ae.one_file_staged = real

    def test_the_only_permitted_path_is_the_registry(self):
        self.assertEqual(ae.REL, "tools/radar/employers.json")


class Verification(unittest.TestCase):
    def test_an_endpoint_returning_nothing_is_not_a_working_entry(self):
        real, ae.get = ae.get, lambda *a, **k: "[]"
        try:
            n, _ = ae.verify("custom", {"list": "https://x/"})
            self.assertEqual(n, 0)
        finally:
            ae.get = real

    def test_it_knows_how_to_verify_every_ats_the_registry_uses(self):
        used = {e["ats"] for e in json.load(
            open(os.path.join(ROOT, "tools", "radar", "employers.json"), encoding="utf-8"))["employers"]}
        for ats in used:
            with self.assertRaises(Exception) as c:   # network fails; ValueError would mean no rule
                ae.verify(ats, {"host": "127.0.0.1:9", "tenant": "t", "site": "s", "token": "t",
                                "handle": "h", "list": "https://127.0.0.1:9/"})
            self.assertNotIsInstance(c.exception, ValueError, f"no verification rule for {ats}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
