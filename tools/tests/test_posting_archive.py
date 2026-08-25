"""The radar archives what it shortlists, before raw.json is overwritten.

A posting is the source document behind the score, the requirement tally, the CV
angle and the interview stories -- and it is the only input in this system
guaranteed to be deleted, usually at the point it becomes most useful.

Measured, not assumed: in one real vault five of forty-one assessed roles already
had unreachable postings, including the role a full pack had been built for and
the role the user was rejected from.
"""
import importlib.util, os, shutil, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "radar"))
spec = importlib.util.spec_from_file_location("radar", os.path.join(ROOT, "tools", "radar", "radar.py"))
radar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(radar)

BODY = "We are hiring a Head of Delivery. " * 40      # comfortably over the floor


def row(**kw):
    r = {"company": "Acme Corp", "title": "Head of Delivery", "loc": "Dublin, Ireland",
         "date": "2026-08-25", "url": "https://acme.example/jobs/1", "pay": "", "body": BODY}
    r.update(kw)
    return r


class Archiving(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir, True)
        self.cfg = {"postings_dir": self.dir}

    def files(self):
        return sorted(os.listdir(self.dir))

    def read(self, name):
        with open(os.path.join(self.dir, name), encoding="utf-8") as fh:
            return fh.read()

    def test_it_writes_one_file_per_role(self):
        radar.archive([row(), row(company="Beta Ltd", url="https://b/2")], self.cfg)
        self.assertEqual(len(self.files()), 2)

    def test_the_file_carries_what_the_url_will_not(self):
        """The URL dies. Everything needed to reconstruct the decision must be in the file."""
        radar.archive([row(pay="EUR120,000")], self.cfg)
        text = self.read(self.files()[0])
        for expected in ("Acme Corp", "Head of Delivery", "2026-08-25",
                         "Dublin, Ireland", "EUR120,000", "https://acme.example/jobs/1"):
            self.assertIn(expected, text)
        self.assertIn(BODY.strip()[:40], text)

    def test_a_floor_date_says_it_is_a_floor(self):
        """"30+ days ago" shown bare makes an ageing requisition look fresh."""
        radar.archive([row(date_is_floor=True)], self.cfg)
        self.assertIn("floor", self.read(self.files()[0]))

    def test_it_never_overwrites(self):
        """An archived posting is evidence of what was read at the time. A later
        fetch can return an edited posting, or a 404 page -- which would replace
        the evidence with nothing."""
        radar.archive([row()], self.cfg)
        first = self.read(self.files()[0])
        saved, skipped = radar.archive([row(body="COMPLETELY DIFFERENT TEXT " * 40)], self.cfg)
        self.assertEqual((saved, skipped), (0, 1))
        self.assertEqual(self.read(self.files()[0]), first)

    def test_two_roles_at_one_employer_do_not_collide(self):
        radar.archive([row(), row(title="Head of Platform", url="https://acme.example/jobs/2")], self.cfg)
        self.assertEqual(len(self.files()), 2)

    def test_a_listing_with_no_description_is_not_archived(self):
        """An empty file is worse than none: it looks like evidence and is not."""
        saved, _ = radar.archive([row(body=""), row(body="too short")], self.cfg)
        self.assertEqual(saved, 0)
        self.assertEqual(self.files(), [])

    def test_a_title_with_slashes_does_not_escape_the_directory(self):
        radar.archive([row(title="Head of Delivery / Ops (m/f/d)")], self.cfg)
        self.assertEqual(len(self.files()), 1)
        self.assertNotIn("/", self.files()[0])

    def test_an_unwritable_directory_warns_rather_than_killing_the_run(self):
        """A failed archive must not lose the shortlist the run just produced."""
        saved, skipped = radar.archive([row()], {"postings_dir": "/proc/nope/cannot-create"})
        self.assertEqual((saved, skipped), (0, 0))


class WiredIn(unittest.TestCase):
    def test_the_runner_archives_the_shortlist_not_everything_fetched(self):
        """Shortlisted is what an agent reads, and the standing rule is that
        everything read gets assessed. Archiving all ~130 fetched descriptions
        would keep mostly roles nobody ever looked at."""
        with open(os.path.join(ROOT, "tools", "radar", "radar.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertIn("archive(high + med, cfg", src)   # args may grow; the rows may not

    def test_it_runs_before_seen_json_is_updated(self):
        with open(os.path.join(ROOT, "tools", "radar", "radar.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertLess(src.index("archive(high + med, cfg"), src.index("json.dump(seen,"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
