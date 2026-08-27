"""pipeline: is a stage of work actually finished, or does it just claim to be?

🔴 THE TWO FAILURES THIS EXISTS FOR, both from one session, both the same shape.

  1. `.claude/agents/role-triage.md` has existed for the life of the repo and the
     radar skill names it twice. IT HAS NEVER RUN. An instruction-shaped control
     that never fired once, and nothing noticed because nothing was looking.

  2. A cluster page said "recorded so the radar does not re-surface them" and
     shipped with no posting URLs. It re-surfaced all ten. Written twice, the
     same way, an hour apart.

Both are a stage claiming completion with nothing computing it. The deterministic
layer already checks outgoing ARTEFACTS -- cv_lint, verify and known decide
whether a CV is fit to send. Nothing checked whether a BATCH finished.
"""
import datetime
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("pipeline", os.path.join(ROOT, "tools", "pipeline.py"))
pl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pl)

ROW = ("| [[{page}\\|X]] — a role | 5·4·3 | **12** | 3 | 4 | TBC | TBC | Not applied "
       "| [LinkedIn](https://www.linkedin.com/jobs/view/{jid}/) | note |")


class Vault:
    """A whole vault, because every criterion is computed from real files."""

    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        for d in ("wiki", "roles", "state"):
            os.makedirs(os.path.join(self.dir, d))
        self._saved = pl.paths.VAULT
        pl.paths.use(self.dir)
        self.sweep(0)
        self.log(datetime.date.today().isoformat())
        self.framework([])
        self.shortlist([])
        return self

    def sweep(self, days_ago):
        when = (datetime.date.today() - datetime.timedelta(days=days_ago)).isoformat()
        self._w("state/last-all-open.json", json.dumps({"last_all_open": when}))

    def log(self, day):
        self._w("wiki/log.md", f"# Log\n\n## [{day}] radar | something\n\nText.\n")

    def framework(self, rows):
        self._w("wiki/Role Scoring Framework.md",
                "# Framework\n\n| Role | N·D·E |\n|---|---|\n" + "\n".join(rows) + "\n")

    def shortlist(self, high_rows):
        body = ("# Radar shortlist\n\n## HIGH signal\n\n"
                "| SIGNAL | Posted | Company | Title | Location | Pay | Link |\n"
                "|---|---|---|---|---|---|---|\n" + "\n".join(high_rows) + "\n")
        self._w("state/shortlist.md", body)

    def role(self, name, body="# A role\n"):
        self._w(f"roles/{name}.md", body)

    def _w(self, rel, text):
        with open(os.path.join(self.dir, rel), "w", encoding="utf-8") as fh:
            fh.write(text)

    def __exit__(self, *a):
        pl.paths.use(self._saved)
        shutil.rmtree(self.dir, ignore_errors=True)


class TheRecordedStage(unittest.TestCase):
    """🔴 The check the cluster pages needed. A page, a table row, and a URL."""

    def test_a_complete_assessment_passes(self):
        with Vault() as v:
            v.role("Acme Head of Delivery")
            v.framework([ROW.format(page="Acme Head of Delivery", jid="111")])
            done, detail, _ = pl.stage_recorded()
            self.assertTrue(done, detail)

    def test_a_page_with_no_table_row_is_caught(self):
        with Vault() as v:
            v.role("Acme Head of Delivery")
            done, _, problems = pl.stage_recorded()
            self.assertFalse(done)
            self.assertIn("no row in the scoring table", problems[0])

    def test_a_page_and_row_with_no_url_anywhere_is_caught(self):
        """🔴 THE ACTUAL FAILURE, TWICE. Without a posting URL the radar
        re-surfaces the role next sweep, so a page whose stated purpose is to
        stop that causes exactly what it claims to prevent."""
        with Vault() as v:
            v.role("Cluster of nine")
            v.framework(["| [[Cluster of nine\\|X]] — nine roles | — | 8 | — | — | — |"])
            done, _, problems = pl.stage_recorded()
            self.assertFalse(done)
            self.assertIn("no posting URL anywhere", problems[0])

    def test_a_url_on_the_page_counts_even_when_the_row_has_none(self):
        """The remedy actually used on the cluster pages: list the postings on
        the page itself."""
        with Vault() as v:
            v.role("Cluster of nine", "# Cluster\n\n- Role: https://example.invalid/jobs/1\n")
            v.framework(["| [[Cluster of nine\\|X]] — nine roles | — | 8 | — | — | — |"])
            done, detail, _ = pl.stage_recorded()
            self.assertTrue(done, detail)


class TheTriageStage(unittest.TestCase):

    def test_an_unassessed_high_role_is_reported(self):
        with Vault() as v:
            v.shortlist(["| HIGH | 2026-08-01 | Acme | Head of Delivery | Dublin |  | "
                         "[link](https://www.linkedin.com/jobs/view/999/) |"])
            done, _, left = pl.stage_triage()
            self.assertFalse(done)
            self.assertIn("Acme", left[0])

    def test_a_role_assessed_on_a_page_is_not_reported(self):
        with Vault() as v:
            v.shortlist(["| HIGH | 2026-08-01 | Acme | Head of Delivery | Dublin |  | "
                         "[link](https://www.linkedin.com/jobs/view/999/) |"])
            v.role("Acme", "Ingested from https://www.linkedin.com/jobs/view/999/\n")
            done, detail, _ = pl.stage_triage()
            self.assertTrue(done, detail)

    def test_the_same_url_written_differently_still_matches(self):
        """🔴 Matching on a bare id reported assessed roles as outstanding,
        repeatedly, because one role reaches the shortlist through several
        sources under several URLs. Normalise, do not compare raw."""
        with Vault() as v:
            v.shortlist(["| HIGH | 2026-08-01 | Acme | Head of Delivery | Dublin |  | "
                         "[link](https://www.linkedin.com/jobs/view/999/) |"])
            v.role("Acme", "see http://linkedin.com/jobs/view/999\n")
            done, detail, _ = pl.stage_triage()
            self.assertTrue(done, detail)


class TheSweepStage(unittest.TestCase):

    def test_a_recent_sweep_passes(self):
        with Vault() as v:
            v.sweep(1)
            self.assertTrue(pl.stage_sweep()[0])

    def test_a_stale_sweep_names_the_command(self):
        with Vault() as v:
            v.sweep(30)
            done, detail, fix = pl.stage_sweep()
            self.assertFalse(done)
            self.assertIn("--all-open", fix[0])

    def test_the_key_radar_actually_writes_is_the_one_read(self):
        """🔴 Guessing it wrong reported a healthy sweep as unreadable on this
        tool's first run. Read the writer; do not assume the shape."""
        with Vault() as v:
            v._w("state/last-all-open.json", json.dumps({"on": "2026-08-26"}))
            self.assertFalse(pl.stage_sweep()[0])


class TheLoggedStage(unittest.TestCase):
    """🔴 An assessment that exists only in a reply gets re-derived next week.
    This repo has lost five that way."""

    def test_a_role_page_newer_than_the_newest_log_entry_is_caught(self):
        with Vault() as v:
            v.log("2020-01-01")
            v.role("Acme")
            done, detail, _ = pl.stage_logged()
            self.assertFalse(done)
            self.assertIn("2020-01-01", detail)

    def test_a_current_log_passes(self):
        with Vault() as v:
            v.role("Acme")
            v.log(datetime.date.today().isoformat())
            self.assertTrue(pl.stage_logged()[0])


class TheReport(unittest.TestCase):

    def test_it_names_the_next_stage_not_all_of_them(self):
        with Vault() as v:
            v.sweep(99)
            text = pl.render(pl.run())
            self.assertIn("NEXT: sweep", text)

    def test_a_finished_pipeline_says_so_without_claiming_there_is_nothing_to_do(self):
        with Vault() as v:
            v.role("Acme")
            v.framework([ROW.format(page="Acme", jid="111")])
            v.shortlist([])
            text = pl.render(pl.run())
            self.assertIn("nothing outstanding", text)
            self.assertIn("not the same as nothing to do", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
