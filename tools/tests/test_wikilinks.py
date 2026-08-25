"""wikilinks: the three ways a link fails without looking broken.

Every case here is one that actually happened. The wrapped-link bug broke 83
links in one vault; the repair for it then pulled blockquote markers into the
link text and broke 7 more; and renamed headings had quietly orphaned 40
section links that all still opened the right page.
"""
import importlib.util, os, shutil, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WL = os.path.join(ROOT, "tools", "wikilinks.py")

spec = importlib.util.spec_from_file_location("wikilinks", WL)
wikilinks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wikilinks)


class Vault:
    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        return self

    def add(self, name, text):
        with open(os.path.join(self.dir, name), "w", encoding="utf-8") as fh:
            fh.write(text)

    def read(self, name):
        with open(os.path.join(self.dir, name), encoding="utf-8") as fh:
            return fh.read()

    def kinds(self):
        return [f[0] for f in wikilinks.check(self.dir)]

    def cli(self, *args):
        p = subprocess.run([sys.executable, WL, self.dir, *args], capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def __exit__(self, *a):
        shutil.rmtree(self.dir, ignore_errors=True)


class TargetParsing(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(wikilinks.split_target("Some Page"), ("Some Page", ""))

    def test_alias(self):
        self.assertEqual(wikilinks.split_target("Some Page|shown"), ("Some Page", ""))

    def test_anchor(self):
        self.assertEqual(wikilinks.split_target("Some Page#A Heading"), ("Some Page", "A Heading"))

    def test_escaped_pipe_inside_a_table(self):
        """A markdown table needs \\| and a naive split on | gets this wrong."""
        self.assertEqual(wikilinks.split_target(r"Some Page#A Heading\|shown"),
                         ("Some Page", "A Heading"))

    def test_same_page_anchor(self):
        self.assertEqual(wikilinks.split_target("#A Heading"), ("", "A Heading"))


class Wrapped(unittest.TestCase):
    def test_a_link_split_across_lines_is_broken(self):
        with Vault() as v:
            v.add("Target.md", "# Target\n")
            v.add("A.md", "See [[Target\nPage]] for more.\n")
            self.assertIn("WRAPPED", v.kinds())

    def test_fix_joins_it(self):
        with Vault() as v:
            v.add("Some Page.md", "# Some Page\n")
            v.add("A.md", "See [[Some\nPage]] for more.\n")
            wikilinks.fix_wrapped(v.dir)
            self.assertIn("[[Some Page]]", v.read("A.md"))
            self.assertEqual(v.kinds(), [])

    def test_fix_strips_a_blockquote_marker(self):
        """The first attempt at this repair produced [[Some > Page]]."""
        with Vault() as v:
            v.add("Some Page.md", "# Some Page\n")
            v.add("A.md", "> See [[Some\n> Page]] for more.\n")
            wikilinks.fix_wrapped(v.dir)
            self.assertIn("[[Some Page]]", v.read("A.md"))
            self.assertNotIn(">", v.read("A.md").split("[[")[1].split("]]")[0])

    def test_fix_leaves_alone_what_it_cannot_resolve(self):
        with Vault() as v:
            v.add("A.md", "See [[No Such\nPage]] here.\n")
            wikilinks.fix_wrapped(v.dir)
            self.assertIn("WRAPPED", v.kinds())


class MissingHeadings(unittest.TestCase):
    def test_a_renamed_heading_is_caught(self):
        with Vault() as v:
            v.add("Target.md", "# Target\n\n## The New Name\n")
            v.add("A.md", "See [[Target#The Old Name]].\n")
            self.assertIn("NO HEADING", v.kinds())

    def test_an_existing_heading_passes(self):
        with Vault() as v:
            v.add("Target.md", "# Target\n\n## The Name\n")
            v.add("A.md", "See [[Target#The Name|alias]].\n")
            self.assertEqual(v.kinds(), [])

    def test_headings_inside_blockquotes_count(self):
        with Vault() as v:
            v.add("Target.md", "# Target\n\n> ## Quoted Heading\n")
            v.add("A.md", "See [[Target#Quoted Heading]].\n")
            self.assertEqual(v.kinds(), [])

    def test_emoji_headings_match(self):
        with Vault() as v:
            v.add("Target.md", "# Target\n\n## \U0001f534 A Warning\n")
            v.add("A.md", "See [[Target#\U0001f534 A Warning]].\n")
            self.assertEqual(v.kinds(), [])

    def test_a_same_page_anchor_is_checked_against_its_own_headings(self):
        with Vault() as v:
            v.add("A.md", "# A\n\n## Real\n\nSee [[#Not Real]].\n")
            self.assertIn("NO HEADING", v.kinds())


class MissingPages(unittest.TestCase):
    def test_reported_but_not_fatal_by_default(self):
        """In this schema a link to an unwritten page marks that it should exist."""
        with Vault() as v:
            v.add("A.md", "See [[Not Written Yet]].\n")
            self.assertEqual(v.kinds(), ["NO PAGE"])
            self.assertEqual(v.cli()[0], 0)

    def test_strict_makes_it_fatal(self):
        with Vault() as v:
            v.add("A.md", "See [[Not Written Yet]].\n")
            self.assertEqual(v.cli("--strict")[0], 1)


class NotOurBusiness(unittest.TestCase):
    def test_deliverables_are_skipped(self):
        with Vault() as v:
            v.add("A.md", "The pack: [[Name - CV - Acme R1.pdf|CV]] and [[x.docx]].\n")
            self.assertEqual(v.kinds(), [])

    def test_block_references_are_skipped(self):
        with Vault() as v:
            v.add("A.md", "See [[^abc123]].\n")
            self.assertEqual(v.kinds(), [])


class ExitStatus(unittest.TestCase):
    def test_broken_links_exit_one_so_it_can_gate(self):
        with Vault() as v:
            v.add("Target.md", "# Target\n")
            v.add("A.md", "See [[Target\nPage]].\n")
            self.assertEqual(v.cli()[0], 1)

    def test_a_clean_vault_exits_zero(self):
        with Vault() as v:
            v.add("Target.md", "# Target\n\n## Bit\n")
            v.add("A.md", "See [[Target#Bit]].\n")
            self.assertEqual(v.cli()[0], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)


class SourcesAreNeverWritten(unittest.TestCase):
    """The schema's one absolute rule about sources/ is that it is not edited.
    A --fix that rewrites a CV export breaks it invisibly: a joined wikilink
    looks like an improvement."""

    def test_fix_reads_sources_but_does_not_write_them(self):
        import shutil, tempfile
        tmp = tempfile.mkdtemp()
        try:
            wrapped = "see [[Some\nPage]] here\n"
            for folder in ("wiki", "sources"):
                os.makedirs(os.path.join(tmp, folder))
                with open(os.path.join(tmp, folder, "note.md"), "w") as fh:
                    fh.write(wrapped)
            with open(os.path.join(tmp, "wiki", "Some Page.md"), "w") as fh:
                fh.write("# Some Page\n")
            wikilinks.fix_wrapped(tmp)
            with open(os.path.join(tmp, "sources", "note.md")) as fh:
                self.assertEqual(fh.read(), wrapped, "sources/ was rewritten")
            with open(os.path.join(tmp, "wiki", "note.md")) as fh:
                self.assertIn("[[Some Page]]", fh.read())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class AMarkdownExtensionStillResolves(unittest.TestCase):
    def test_the_extension_is_optional_as_in_obsidian(self):
        self.assertEqual(wikilinks.split_target("CLAUDE.md"), ("CLAUDE", ""))
        self.assertEqual(wikilinks.split_target("Weight Log.md#Table"), ("Weight Log", "Table"))
        # A page whose name genuinely ends in something else is untouched.
        self.assertEqual(wikilinks.split_target("Sacha Jackson.pdf"), ("Sacha Jackson.pdf", ""))
