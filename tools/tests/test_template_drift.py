"""template_drift: what the template gained that a vault never got.

career-init copies templates/ into wiki/ ONCE and nothing revisits it.
an update never touches vault/wiki/, because that directory is
the person rather than the tool. So the tool improves and the vault does not,
silently, for as long as somebody keeps using it.

Not hypothetical: on 2026-08-25 the framework template gained a standing-gaps
table, a known-locations table, a baseline row, an internal-move row and a
seven-value outcome vocabulary, and SCHEMA.md -- which IS synced -- was updated
to instruct the agent to use all five. Every vault made before that morning has
an agent looking for tables that are not there.

The case worth understanding: two of those five were ROWS INSIDE A TABLE THE
VAULT ALREADY HAD. A section-level check walks straight past them, which is why
seeded rows are compared as well.
"""
import importlib.util, io, os, sys, tempfile, unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TD = os.path.join(ROOT, "tools", "template_drift.py")
spec = importlib.util.spec_from_file_location("td", TD)
td = importlib.util.module_from_spec(spec)
spec.loader.exec_module(td)

TEMPLATE = """---
type: synthesis
---

# Framework

## Three scores

| | Scale |
|---|---|
| **FIT** | /15 |

## Standing gaps

| The gap | Status |
|---|---|
| | *confirmed absent* |

## The table

| Role | Status |
|---|---|
| **Staying put — the current job** | `Not applied` |
| | |
"""


class Vault:
    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        self.templates = tempfile.mkdtemp()
        self.write(self.templates, "Framework.md", TEMPLATE)
        return self

    def write(self, where, name, text):
        with open(os.path.join(where, name), "w", encoding="utf-8") as fh:
            fh.write(text)

    def page(self, text):
        self.write(self.dir, "Framework.md", text)

    def run(self):
        argv = sys.argv
        sys.argv = ["td", "--wiki", self.dir, "--templates", self.templates]
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                code = td.main()
        finally:
            sys.argv = argv
        return code, buf.getvalue()

    def __exit__(self, *a):
        import shutil
        shutil.rmtree(self.dir, ignore_errors=True)
        shutil.rmtree(self.templates, ignore_errors=True)


class WhatItFinds(unittest.TestCase):

    def test_a_current_vault_is_clean(self):
        """The case that decides whether anyone keeps this switched on."""
        with Vault() as v:
            v.page(TEMPLATE)
            code, out = v.run()
            self.assertEqual(code, 0, out)
            self.assertIn("Nothing missing", out)

    def test_a_filled_in_vault_is_still_clean(self):
        """A real page has placeholders replaced and its own rows added. If that
        reads as drift the check is noise and gets ignored."""
        with Vault() as v:
            v.page(TEMPLATE.replace("| | |",
                                    "| Head of Delivery, <Employer> | `Submitted` |"))
            code, out = v.run()
            self.assertEqual(code, 0, out)

    def test_a_section_the_template_gained_is_reported(self):
        with Vault() as v:
            v.page(TEMPLATE.replace("## Standing gaps", "## Something else entirely"))
            code, out = v.run()
            self.assertEqual(code, 1)
            self.assertIn("Standing gaps", out)
            self.assertIn("section the template has", out)

    def test_a_section_present_without_its_table_is_reported(self):
        """Ship the empty table, applied to vaults: a heading with nothing under
        it is a place to write nothing."""
        with Vault() as v:
            v.page(TEMPLATE.replace("| The gap | Status |\n|---|---|\n| | *confirmed absent* |",
                                    "To be added."))
            code, out = v.run()
            self.assertEqual(code, 1)
            self.assertIn("the table under it is not", out)

    def test_a_seeded_row_inside_a_table_the_vault_already_had(self):
        """The case a section-level check misses entirely, and two of the five
        real changes were exactly this."""
        with Vault() as v:
            v.page(TEMPLATE.replace("| **Staying put — the current job** | `Not applied` |\n", ""))
            code, out = v.run()
            self.assertEqual(code, 1)
            self.assertIn("row missing", out)
            self.assertIn("Staying put", out)

    def test_a_reworded_heading_is_not_reported_as_missing(self):
        """The agent owns these pages and may phrase a heading its own way.
        Reporting that as drift is the noise that gets a check switched off."""
        with Vault() as v:
            v.page(TEMPLATE.replace("## Standing gaps", "## Standing gaps (capabilities)"))
            code, out = v.run()
            self.assertEqual(code, 0, out)

    def test_a_page_the_vault_never_created_is_named(self):
        with Vault() as v:
            v.page(TEMPLATE)
            v.write(v.templates, "Standing Answers.md", "# Standing Answers\n\n## A section\n")
            code, out = v.run()
            self.assertEqual(code, 1)
            self.assertIn("Standing Answers.md", out)


class WhatItRefusesToDo(unittest.TestCase):

    def test_it_never_writes_to_the_vault(self):
        """Merging a section into a page holding somebody's history is a
        judgement -- where it goes, what carries over. A bad merge there costs
        them their notes, and this owns none of it."""
        with Vault() as v:
            page = TEMPLATE.replace("## Standing gaps", "## Something else entirely")
            v.page(page)
            v.run()
            with open(os.path.join(v.dir, "Framework.md"), encoding="utf-8") as fh:
                self.assertEqual(fh.read(), page)

    def test_an_empty_vault_is_not_out_of_date(self):
        """Before /career-init there is nothing to be behind."""
        with Vault() as v:
            code, out = v.run()
            self.assertEqual(code, 0)
            self.assertIn("career-init", out)

    def test_a_missing_vault_is_not_an_error(self):
        argv = sys.argv
        sys.argv = ["td", "--wiki", "/nonexistent/vault"]
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                code = td.main()
        finally:
            sys.argv = argv
        self.assertEqual(code, 0)
        self.assertIn("nothing to compare", buf.getvalue())

    def test_it_says_what_a_clean_run_does_not_prove(self):
        """Structure matching is not contents being current, and a check that
        implies otherwise is worse than none."""
        with Vault() as v:
            v.page(TEMPLATE)
            _, out = v.run()
            self.assertIn("does not mean", out)


if __name__ == "__main__":
    unittest.main()


class TheFreshScaffoldIsClean(unittest.TestCase):
    """🔴 The first thing a new user sees from this tool must not be wrong.

    A vault scaffolded straight from templates/ was told three pages were
    missing -- vault-AGENTS.md, sources-README.md and OVERSIGHT.md -- none of
    which is a wiki page. They are copied elsewhere in the vault entirely. Three
    findings, all false, on a vault that had done nothing wrong yet.
    """

    def test_a_vault_copied_from_the_templates_reports_nothing(self):
        import shutil
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        templates = os.path.join(root, "templates")
        wiki = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, wiki, ignore_errors=True)
        for f in os.listdir(templates):
            if f.endswith(".md") and f not in td.SKIP:
                shutil.copy(os.path.join(templates, f), os.path.join(wiki, f))
        buf = io.StringIO()
        argv = sys.argv
        sys.argv = ["template_drift.py", "--wiki", wiki, "--templates", templates]
        try:
            with redirect_stdout(buf):
                code = td.main()
        finally:
            sys.argv = argv
        self.assertEqual(code, 0, buf.getvalue())
        self.assertNotIn("vault-AGENTS.md", buf.getvalue())
