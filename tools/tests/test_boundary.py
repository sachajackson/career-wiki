"""The boundary: everything the user owns is under vault/, and nothing else is.

WHY THIS FILE EXISTS

For months user data sat inside tools/ -- a config, a watch list, three files of
regenerable state, and an API key. That is what made an update mechanism
impossible: you cannot replace tools/ wholesale while somebody's working life is
in it.

It also made .gitignore complicated, and complicated ignore rules fail quietly.
The rule `tools/radar/*.json` silently swallowed two files that had to ship, and
each was found only because somebody noticed a clone was broken.

These tests assert the property rather than the list. A list has to be
maintained by hand and had already failed twice; a boundary does not.
"""
import os, re, subprocess, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS = os.path.join(ROOT, "tools")


def tracked():
    out = subprocess.run(["git", "-C", ROOT, "ls-files", "-z"], capture_output=True, text=True).stdout
    return {p for p in out.split("\0") if p}


def py_files():
    for base, dirs, files in os.walk(TOOLS):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", "tests")]
        for f in files:
            if f.endswith(".py"):
                yield os.path.join(base, f)


class NothingOfTheUsersIsTracked(unittest.TestCase):
    def test_no_file_under_vault_is_tracked(self):
        leaked = sorted(p for p in tracked() if p.startswith("vault/"))
        self.assertEqual(leaked, [], f"the vault is the user's and must never ship: {leaked}")

    def test_the_vault_is_ignored_by_one_rule_not_a_list(self):
        """Eight rules with hand-maintained carve-outs is what swallowed two
        files that had to ship. One rule cannot do that."""
        with open(os.path.join(ROOT, ".gitignore"), encoding="utf-8") as fh:
            lines = [l.strip() for l in fh if l.strip() and not l.startswith("#")]
        self.assertIn("vault/", lines)
        self.assertEqual([l for l in lines if l.startswith("!")], [],
                         "a `!` carve-out means the ignore rule is too broad again")

    def test_the_hook_blocks_the_vault(self):
        with open(os.path.join(ROOT, "githooks", "pre-commit"), encoding="utf-8") as fh:
            hook = fh.read()
        self.assertIn("vault/*", hook)


class NothingOfTheUsersLivesOutsideIt(unittest.TestCase):
    """The failure this catches is a tool quietly writing beside its own code."""

    USER_ISH = re.compile(
        r'os\.path\.join\(\s*HERE\s*,\s*"(config|employers|seen|raw)\.json"'
        r'|os\.path\.join\(\s*HERE\s*,\s*"shortlist\.md"'
        r'|["\']tools/radar/(config|employers|seen|raw)\.json["\']')

    def test_no_tool_pins_a_user_path_beside_its_own_code(self):
        offenders = []
        for path in py_files():
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            for m in self.USER_ISH.finditer(src):
                offenders.append(f"{os.path.relpath(path, ROOT)}: {m.group(0)[:60]}")
        self.assertEqual(offenders, [],
                         f"user data must come from paths.py, not from a literal: {offenders}")

    def test_every_tool_that_touches_user_data_imports_paths(self):
        """Nine files pinned their own paths before this. Missing one is silent:
        a tool reading a path nobody writes to reports 'nothing here' rather than
        'I am looking in the wrong place'."""
        for name in ("radar/radar.py", "radar/employers.py", "radar/sources_check.py",
                     "doctor.py", "export_review.py", "verify.py", "known.py",
                     "wikilinks.py", "template_drift.py"):
            with open(os.path.join(TOOLS, name), encoding="utf-8") as fh:
                self.assertIn("import paths", fh.read(), f"{name} should resolve paths centrally")


class TheFourKinds(unittest.TestCase):
    """They all live under vault/ because they are all the user's. A tool that
    bundles a vault still has to know which is which -- carrying an API key or a
    2MB cache is how secrets end up in a zip somebody emails."""

    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "paths", os.path.join(TOOLS, "lib", "paths.py"))
        self.paths = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.paths)

    def test_secrets_and_state_are_never_carried(self):
        for p in (self.paths.SECRETS, self.paths.STATE):
            self.assertIn(p, self.paths.NEVER)
            self.assertNotIn(p, self.paths.CARRY)

    def test_the_knowledge_is_carried(self):
        for p in (self.paths.WIKI, self.paths.SOURCES, self.paths.POSTINGS,
                  self.paths.APPLICATIONS, self.paths.SETTINGS):
            self.assertIn(p, self.paths.CARRY)

    def test_everything_is_inside_the_vault(self):
        for p in self.paths.LAZY:
            self.assertTrue(p.startswith(self.paths.VAULT), f"{p} is outside the vault")

    def test_a_vault_can_be_re_rooted(self):
        """A layout nothing can relocate is a layout nothing can test -- and the
        first thing that needed to relocate one was a test."""
        original = self.paths.VAULT
        try:
            self.paths.use("/tmp/somewhere-else")
            self.assertTrue(self.paths.SEARCH.startswith("/tmp/somewhere-else"))
            self.assertTrue(self.paths.ENV.startswith("/tmp/somewhere-else"))
        finally:
            self.paths.use(original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
