"""batch: hand roles out for triage, then check they came back.

🔴 THE BUG THIS FILE EXISTS TO PREVENT, caught on the tool's first real use.

`corpus()` read `raw.json` — the corpus BEFORE the location filter. A batch built
from it handed three triage agents seventeen JPMorganChase roles described as
"Dublin", which were actually in Mumbai, Hyderabad, Glasgow, Jersey City,
Columbus, Palo Alto, Plano and Bengaluru. All three agents flagged it
independently.

The radar had been right the whole time: 20 such roles were fetched, 3 were in
Ireland, and the shortlist contained exactly those 3.

**Bypassing a filter to reach a richer source is how a filter comes to be
bypassed permanently.** A batch is built from the shortlist.
"""
import importlib.util, json, os, shutil, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("batch", os.path.join(ROOT, "tools", "batch.py"))
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

HDR = ("| SIGNAL | Posted | Company | Title | Location | Pay | Link |\n"
       "|---|---|---|---|---|---|---|\n")
def row(co, ti, loc, url):
    return f"| MED | 2026-08-01 | {co} | {ti} | {loc} |  | [link]({url}) |"


class Vault:
    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        for d in ("wiki", "roles", "state"):
            os.makedirs(os.path.join(self.dir, d))
        self._saved = b.paths.VAULT
        b.paths.use(self.dir)
        self.framework("")
        return self

    def shortlist(self, rows):
        self._w("state/shortlist.md", "# Shortlist\n\n## MED signal\n\n" + HDR + "\n".join(rows) + "\n")

    def raw(self, rows):
        self._w("state/raw.json", json.dumps({str(i): r for i, r in enumerate(rows)}))

    def framework(self, text):
        self._w("wiki/Role Scoring Framework.md", "# F\n\n" + text + "\n")

    def _w(self, rel, text):
        with open(os.path.join(self.dir, rel), "w", encoding="utf-8") as fh:
            fh.write(text)

    def __exit__(self, *a):
        b.paths.use(self._saved)
        shutil.rmtree(self.dir, ignore_errors=True)


class TheBatchRespectsTheFilters(unittest.TestCase):

    def test_a_role_the_location_filter_dropped_never_enters_a_batch(self):
        """🔴 THE BUG. raw.json holds Mumbai; the shortlist holds only Dublin."""
        with Vault() as v:
            v.shortlist([row("JPMC", "Director of SWE", "Dublin, Ireland",
                             "https://ex.invalid/jobs/1")])
            v.raw([{"title": "Director of SWE", "company": "JPMC", "loc": "Dublin, Ireland",
                    "url": "https://ex.invalid/jobs/1"},
                   {"title": "Director of SWE - Mumbai", "company": "JPMC",
                    "loc": "Mumbai, Maharashtra, India", "url": "https://ex.invalid/jobs/2"}])
            got = b.open_batch("t", employer="JPMC")
            urls = [r["url"] for r in got["roles"]]
            self.assertIn("https://ex.invalid/jobs/1", urls)
            self.assertNotIn("https://ex.invalid/jobs/2", urls,
                             "a role dropped on location reached the batch")

    def test_an_already_assessed_role_is_excluded(self):
        with Vault() as v:
            v.shortlist([row("JPMC", "A", "Dublin", "https://ex.invalid/jobs/1")])
            v.framework("| [[A\\|A]] | see https://ex.invalid/jobs/1 |")
            self.assertEqual(b.open_batch("t", employer="JPMC")["roles"], [])

    def test_status_counts_what_came_back(self):
        with Vault() as v:
            v.shortlist([row("JPMC", "A", "Dublin", "https://ex.invalid/jobs/1"),
                         row("JPMC", "B", "Dublin", "https://ex.invalid/jobs/2")])
            b.open_batch("t", employer="JPMC")
            _, done, left = b.status("t")
            self.assertEqual((len(done), len(left)), (0, 2))
            v.framework("| [[A\\|A]] | https://ex.invalid/jobs/1 |")
            _, done, left = b.status("t")
            self.assertEqual((len(done), len(left)), (1, 1))

    def test_a_url_written_differently_still_counts_as_assessed(self):
        """One role reaches the shortlist under several URLs; comparing raw
        strings reported assessed roles as outstanding, repeatedly."""
        with Vault() as v:
            v.shortlist([row("JPMC", "A", "Dublin", "https://www.ex.invalid/jobs/1/")])
            b.open_batch("t", employer="JPMC")
            v.framework("| [[A\\|A]] | http://ex.invalid/jobs/1 |")
            _, done, left = b.status("t")
            self.assertEqual((len(done), len(left)), (1, 0))

    def test_an_unknown_batch_is_not_a_crash(self):
        with Vault():
            self.assertEqual(b.status("nope"), (None, [], []))

    def test_no_shortlist_yields_no_batch(self):
        with Vault():
            self.assertEqual(b.corpus(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
