"""The sorter's refusals, which are the part that matters.

Placing a file correctly is the easy half. What makes a migration survivable is
what it declines to do: a confident wrong placement is worse than an honest
UNKNOWN, because somebody can act on UNKNOWN.
"""
import importlib.util, os, shutil, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class MigrateCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.paths = load("paths", "tools/lib/paths.py")
        self.paths.use(os.path.join(self.tmp, "vault"))
        self.migrate = load("migrate", "tools/migrate.py")
        self.migrate.paths = self.paths
        self.drop = self.paths.MIGRATION
        os.makedirs(self.drop)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def drop_file(self, rel, body=""):
        full = os.path.join(self.drop, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(body)
        return full

    def verdicts(self):
        return {rel: (v, dest) for rel, _, v, dest, _ in self.migrate.plan(self.drop)}


class ItRefuses(MigrateCase):
    def test_a_forked_tool_is_never_migrated(self):
        """The worst outcome in the whole migration. Somebody from an older
        clone has an edited radar.py that is behind on the scoring model, the
        adapters and the registry -- carrying it reinstates every fixed bug."""
        self.drop_file("radar/radar.py", "# their fork\n")
        self.assertEqual(self.verdicts()["radar/radar.py"][0], self.migrate.SYSTEM)

    def test_a_secret_is_never_moved_for_them(self):
        self.drop_file(".env", "ANTHROPIC_API_KEY=sk-ant-real\n")
        v, dest = self.verdicts()[".env"]
        self.assertEqual(v, self.migrate.SYSTEM)
        self.assertIsNone(dest)

    def test_regenerable_state_is_reported_not_carried(self):
        for f in ("seen.json", "raw.json", "shortlist.md"):
            self.drop_file(f, "{}")
        got = self.verdicts()
        for f in ("seen.json", "raw.json", "shortlist.md"):
            self.assertEqual(got[f][0], self.migrate.KEEP)

    def test_a_users_own_json_is_not_mistaken_for_state(self):
        """Named exactly rather than matched by extension. Guessing wrong here
        deletes something irreplaceable."""
        self.drop_file("interview notes.json", "{}")
        self.assertEqual(self.verdicts()["interview notes.json"][0], self.migrate.UNKNOWN)

    def test_a_filename_already_in_the_vault_is_refused(self):
        """Obsidian resolves wikilinks by filename regardless of folder, so two
        pages with one name break both links, silently."""
        self.paths.ensure(self.paths.ROLES)
        with open(os.path.join(self.paths.ROLES, "Head of Data.md"), "w") as fh:
            fh.write("---\ntype: role\n---\n")
        self.drop_file("Head of Data.md", "---\ntype: role\n---\n")
        v, dest = self.verdicts()["Head of Data.md"]
        self.assertEqual(v, self.migrate.COLLIDES)
        self.assertIsNone(dest)

    def test_two_incoming_files_with_one_name_collide_with_each_other(self):
        """The vault does not have to be populated for this to bite."""
        self.drop_file("a/Notes.md", "---\ntype: topic\n---\n")
        self.drop_file("b/Notes.md", "---\ntype: topic\n---\n")
        got = list(self.verdicts().values())
        self.assertEqual(sorted(v for v, _ in got), [self.migrate.COLLIDES, self.migrate.PLACED])

    def test_bare_markdown_is_unknown_rather_than_guessed(self):
        """A note from another tool, a pasted job ad and a page of somebody's
        history look identical without frontmatter, and belong in three folders."""
        self.drop_file("something.md", "# just a heading\n")
        self.assertEqual(self.verdicts()["something.md"][0], self.migrate.UNKNOWN)

    def test_nothing_moves_without_apply(self):
        self.drop_file("CV.pdf", "x")
        self.migrate.plan(self.drop)
        self.assertTrue(os.path.exists(os.path.join(self.drop, "CV.pdf")))


class ItPlaces(MigrateCase):
    def test_a_path_hint_from_the_old_vault_wins(self):
        """Somebody who filed it under applications/ knew what it was."""
        self.drop_file("wiki/career/CV.docx", "x")
        self.drop_file("wiki/career/postings/Acme.txt", "x")
        got = self.verdicts()
        self.assertEqual(got["wiki/career/postings/Acme.txt"][1], self.paths.POSTINGS)

    def test_an_application_folder_survives_as_a_folder(self):
        """🔴 Flattening these was the second bug a real vault found. Every pack
        holds a cv.txt, a posting.txt and an application.json, so flattening
        turns a clean migration into a pile of collisions and strands the files
        from the application that gives them meaning."""
        for pack in ("Acme R1", "Globex R2"):
            self.drop_file(f"wiki/career/applications/{pack}/cv.txt", "x")
        got = self.verdicts()
        for pack in ("Acme R1", "Globex R2"):
            v, dest = got[f"wiki/career/applications/{pack}/cv.txt"]
            self.assertEqual(v, self.migrate.PLACED)
            self.assertEqual(dest, os.path.join(self.paths.APPLICATIONS, pack),
                             "the folder name is what identifies the pack")

    def test_the_folder_name_keeps_its_capitals(self):
        """Matched lowercase, rebuilt from the original -- a requisition number
        is unreadable once it has been case-folded."""
        self.drop_file("applications/CrowdStrike R28621/cv.txt", "x")
        _, dest = self.verdicts()["applications/CrowdStrike R28621/cv.txt"]
        self.assertTrue(dest.endswith("CrowdStrike R28621"), dest)

    def test_frontmatter_type_routes_the_page(self):
        for body, dest in (("---\ntype: role\n---\n", self.paths.ROLES),
                           ("---\ntype: entity\n---\n", self.paths.COMPANIES),
                           ("---\ntype: topic\n---\n", self.paths.WIKI)):
            name = f"{dest.split(os.sep)[-1]}-page.md"
            self.drop_file(name, body)
        got = self.verdicts()
        self.assertEqual(got["roles-page.md"][1], self.paths.ROLES)
        self.assertEqual(got["companies-page.md"][1], self.paths.COMPANIES)
        self.assertEqual(got["wiki-page.md"][1], self.paths.WIKI)

    def test_company_research_is_recognised_by_name(self):
        self.drop_file("RWS Holdings - Company Research.md", "# no frontmatter\n")
        v, dest = self.verdicts()["RWS Holdings - Company Research.md"]
        self.assertEqual((v, dest), (self.migrate.PLACED, self.paths.COMPANIES))

    def test_documents_become_sources(self):
        self.drop_file("old cv.pdf", "x")
        self.assertEqual(self.verdicts()["old cv.pdf"][1], self.paths.SOURCES)

    def test_apply_moves_and_leaves_the_rest_behind(self):
        self.drop_file("old cv.pdf", "x")
        self.drop_file("mystery.csv", "a,b\n")
        self.drop_file("seen.json", "{}")
        items = self.migrate.plan(self.drop)
        self.migrate.apply(items)
        self.migrate.prune_empty(self.drop)
        self.assertTrue(os.path.exists(os.path.join(self.paths.SOURCES, "old cv.pdf")))
        self.assertFalse(os.path.exists(os.path.join(self.drop, "old cv.pdf")))
        # 🔴 Left on purpose. A file quietly removed from a drop zone looks
        # exactly like a file that was dealt with.
        self.assertTrue(os.path.exists(os.path.join(self.drop, "mystery.csv")))
        self.assertTrue(os.path.exists(os.path.join(self.drop, "seen.json")))

    def test_it_is_safe_to_run_twice(self):
        self.drop_file("old cv.pdf", "x")
        for _ in range(2):
            self.migrate.apply(self.migrate.plan(self.drop))
        self.assertTrue(os.path.exists(os.path.join(self.paths.SOURCES, "old cv.pdf")))

    def test_an_empty_drop_zone_is_not_an_error(self):
        self.assertEqual(self.migrate.report(self.migrate.plan(self.drop), False), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
