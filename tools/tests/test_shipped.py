"""Does a clone actually contain what the tools need?

THE FAILURE THIS EXISTS FOR

Twice in two days a file was written, used, tested and pushed -- and was never
in the repository. Both times an ignore rule matched it, `git add -A` skipped it
without a word, and the working tree looked perfect. The tools worked for the
person who wrote them and were broken for everyone else.

WHY THE EXISTING CHECKS ALL MISSED IT

  - The test suite reads the working tree, where the file exists.
  - `git status --porcelain` was clean: the file was not unexpectedly staged,
    it was expectedly absent, and those look identical.
  - CONTRIBUTING already said to check status before pushing. That instruction
    was followed and the bug went through it, because it asks whether anything
    UNEXPECTED is there, never whether something EXPECTED is missing.

So the only check that catches this is one that asks git what a clone would get,
rather than asking the filesystem what this machine has.
"""
import json, os, re, subprocess, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def tracked():
    """Split on newlines, not whitespace: this repo has filenames with spaces in
    them and .split() turned `templates/Role Scoring Framework.md` into three."""
    out = subprocess.run(["git", "-C", ROOT, "ls-files", "-z"], capture_output=True, text=True).stdout
    return {p for p in out.split("\0") if p}


# Files the tools open by name. If one of these is not tracked, a clone is broken
# in a way no test reading the working tree can see.
REQUIRED = [
    "tools/radar/ats_registry.json",
    "tools/radar/config.example.json",
    "tools/radar/employers.example.json",
    "tools/radar/radar.py",
    "tools/radar/registry.py",
    "tools/registry_check.py",
    "tools/add_employer.py",
    "tools/verify.py",
    "tools/cv_lint.py",
    "tools/wikilinks.py",
    "tools/known.py",
    "tools/export_review.py",
    "oversight/OVERSIGHT.md",
    ".claude/settings.json",
    ".claude/hooks/verify-artefact.sh",
    "githooks/pre-commit",
]

# Files that must NEVER be tracked. The mirror image, and the reason the ignore
# rule that hid the registry has to stay: employers.json is one user's private
# positions on named companies, and it sits one letter from a file that ships.
MUST_NOT_SHIP = [
    "tools/radar/employers.json",
    "tools/radar/config.json",
    "tools/radar/seen.json",
    "tools/radar/raw.json",
    "tools/radar/shortlist.md",
    "tools/review/config.json",
]


class WhatACloneGets(unittest.TestCase):
    def test_every_file_the_tools_need_is_tracked(self):
        t = tracked()
        missing = [f for f in REQUIRED if f not in t]
        self.assertEqual(missing, [], f"a clone would not contain: {missing}")

    def test_nothing_private_is_tracked(self):
        t = tracked()
        leaked = [f for f in MUST_NOT_SHIP if f in t]
        self.assertEqual(leaked, [], f"these must never ship: {leaked}")

    def test_every_adapter_is_tracked(self):
        """A module in ADAPTERS but not in the repo breaks the import on a clone."""
        t = tracked()
        import sys
        sys.path.insert(0, os.path.join(ROOT, "tools", "radar"))
        from adapters import ADAPTERS
        for name in ADAPTERS:
            self.assertIn(f"tools/radar/adapters/{name}.py", t, f"{name} adapter is not tracked")

    def test_every_test_file_is_tracked(self):
        """An untracked test is a check that only ever runs for its author."""
        t = tracked()
        here = os.path.dirname(os.path.abspath(__file__))
        for f in os.listdir(here):
            if f.startswith("test_") and f.endswith(".py"):
                self.assertIn(f"tools/tests/{f}", t, f"{f} is not tracked")


class TheIgnoreRuleThatKeepsCatchingThings(unittest.TestCase):
    """`tools/radar/*.json` is correct and has now hidden two files that had to
    ship. Every carve-out is named individually, on purpose."""

    def test_each_shipped_json_under_radar_has_an_explicit_carve_out(self):
        gitignore = open(os.path.join(ROOT, ".gitignore"), encoding="utf-8").read()
        for f in [f for f in REQUIRED if f.startswith("tools/radar/") and f.endswith(".json")]:
            self.assertIn(f"!{f}", gitignore,
                          f"{f} ships but has no `!` line -- it will be silently dropped")

    def test_the_pre_commit_hook_carves_out_the_same_files(self):
        hook = open(os.path.join(ROOT, "githooks", "pre-commit"), encoding="utf-8").read()
        for f in [f for f in REQUIRED if f.startswith("tools/radar/") and f.endswith(".json")]:
            self.assertIn(os.path.basename(f), hook,
                          f"{f} is carved out of .gitignore but the hook will still block it")


class DocumentationPointsAtThingsThatExist(unittest.TestCase):
    """wikilinks.py covers [[wiki links]]. Nothing covered [](markdown links),
    which is what the README, BACKLOG and CONTRIBUTING use -- and the README is
    now linked from job applications, so a dead link in it has an audience."""

    EXPECTED_MISSING = {
        # templates/ links at what the agent will generate, not at shipped files.
        # A link to a page that does not exist yet is a valid marker in this
        # schema; see wikilinks.py, which treats the same case as NO PAGE.
        ("templates/index.md", "CV.md"),
    }

    def test_every_relative_link_resolves(self):
        import glob, re, urllib.parse
        broken = []
        for f in glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True):
            rel = os.path.relpath(f, ROOT)
            if rel.startswith((".git", "wiki/")):
                continue
            with open(f, encoding="utf-8") as fh:
                text = fh.read()
            for m in re.finditer(r"\[[^\]]*\]\(([^)\s]+)\)", text):
                target = urllib.parse.unquote(m.group(1).split("#")[0])
                if not target or target.startswith(("http", "mailto", "#")):
                    continue
                if (rel, target) in self.EXPECTED_MISSING:
                    continue
                if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(f), target))):
                    broken.append(f"{rel} -> {target}")
        self.assertEqual(broken, [], f"dead links in shipped documentation: {broken}")

    def test_every_anchor_link_resolves(self):
        """The quietest link failure: the page still opens and lands at the top.

        The relative-link check above skips the `#fragment` entirely, so an
        anchor pointing at a renamed heading passed it. That happened here
        within one session -- an entry was renamed on being marked fixed, and a
        link to it three hundred lines away silently stopped landing anywhere.

        Same failure wikilinks.py was built for on the wiki side: 40 section
        links in one vault all still opened the right page and none of them went
        where they said.
        """
        import glob, re
        broken = []
        for f in glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True):
            rel = os.path.relpath(f, ROOT)
            if rel.startswith((".git", "wiki/")):
                continue
            with open(f, encoding="utf-8") as fh:
                text = fh.read()
            # GitHub's heading anchor: lowercase, drop anything that is not word,
            # space or hyphen, then spaces to hyphens. Emoji and em-dashes vanish
            # and leave their surrounding spaces behind, which is why real
            # anchors here start with "-" and carry "--" in the middle.
            anchors = {re.sub(r"\s", "-", re.sub(r"[^\w\s-]", "", h.strip().lower()))
                       for h in re.findall(r"^#{1,6}\s+(.*)$", text, re.M)}
            for m in re.finditer(r"\]\((#[^)\s]+)\)", text):
                if m.group(1)[1:] not in anchors:
                    broken.append(f"{rel} -> {m.group(1)}")
        self.assertEqual(broken, [], f"anchor links pointing at no heading: {broken}")


class ThePersonalDataHeuristicScopesCorrectly(unittest.TestCase):
    """The content scan skips the directories written about users rather than by
    them. That exemption is the kind that quietly grows, and the last time one
    grew it waved through a file containing a real person's home county."""

    def hook(self):
        with open(os.path.join(ROOT, "githooks", "pre-commit"), encoding="utf-8") as fh:
            return fh.read()

    def test_it_still_scans_where_a_user_actually_writes(self):
        """wiki/ and sources/ are the user's own words. They must never be skipped."""
        for d in ("wiki/", "sources/", "oversight/"):
            self.assertNotIn(f"{d}*|", self.hook(), f"{d} must not be exempt from the content scan")
            self.assertNotIn(f"|{d}*", self.hook(), f"{d} must not be exempt from the content scan")

    def test_the_exemption_is_the_three_system_directories_and_no_more(self):
        import re
        m = re.search(r"^\s*([^\n]*?)\)\s*continue ;;\s*$", self.hook(), re.M)
        exempt = set()
        for line in self.hook().splitlines():
            line = line.strip()
            if line.endswith(") continue ;;") and "*" in line:
                exempt.update(p.strip() for p in line[:line.index(")")].split("|"))
        expected = {
            # Skipped because grep cannot read them, not because they are trusted.
            # A binary in a user directory is still blocked by the path rules above.
            "*.png", "*.jpg", "*.pdf", "*.docx", "*.zip",
            # Skipped because they necessarily contain the patterns they describe.
            "githooks/*", "CONTRIBUTING.md", "PRIVACY.md",
            # Skipped because they are written about users, never by them.
            ".claude/skills/*", "templates/*", "tools/*",
            # Files that must ship despite matching an ignore rule, named one at a time.
            "*/config.example.json", "*/employers.example.json", "*/ats_registry.json",
        }
        unexpected = exempt - expected
        self.assertEqual(unexpected, set(),
                         f"the exemption list has grown: {unexpected}. Every addition needs a reason "
                         f"written beside it, and a filename is not one")


class TheRegistryIsUsable(unittest.TestCase):
    def test_it_parses_and_is_not_empty(self):
        p = os.path.join(ROOT, "tools", "radar", "ats_registry.json")
        d = json.load(open(p, encoding="utf-8"))
        self.assertGreater(len(d["employers"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
