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
    def test_only_readmes_are_tracked_under_vault(self):
        """The folders ship so a new user knows where to put their CV without
        reading the docs first. Their READMEs are the system's words about the
        folder; everything else under vault/ is the user's."""
        leaked = sorted(p for p in tracked()
                        if p.startswith("vault/") and not p.endswith("/README.md"))
        self.assertEqual(leaked, [], f"the vault is the user's and must never ship: {leaked}")

    def test_the_folders_a_user_puts_things_into_ship(self):
        """The vault used to be created entirely on first write, so a clean
        clone had no vault at all and nothing told a new user where their CV
        went. These four are the ones a PERSON writes into; the rest are written
        by the agent and are created when it first needs them."""
        for folder in ("sources", "migration", "settings", "secrets"):
            self.assertIn(f"vault/{folder}/README.md", tracked(),
                          f"vault/{folder}/ must ship, or nobody knows it exists")

    def test_the_shipped_readmes_carry_no_personal_data(self):
        """They sit inside the user's folder, so they are the one place where a
        system file and a personal one are one keystroke apart."""
        personal = re.compile(r"[\w.%+-]+@(?!example\.com)[\w-]+\.\w+"
                              r"|linkedin\.com/in/[a-z0-9-]+"
                              r"|\b(my salary|current salary|notice period is)\b", re.I)
        for p in (p for p in tracked() if p.startswith("vault/")):
            with open(os.path.join(ROOT, p), encoding="utf-8") as fh:
                hit = personal.search(fh.read())
            self.assertIsNone(hit, f"{p} looks personal: {hit.group(0) if hit else ''}")

    def test_the_vault_is_ignored_by_a_pattern_not_a_list(self):
        """Eight rules with carve-outs naming individual files is what swallowed
        two files that had to ship. A carve-out that is a PATTERN cannot: it does
        not need maintaining when somebody adds a file."""
        with open(os.path.join(ROOT, ".gitignore"), encoding="utf-8") as fh:
            lines = [l.strip() for l in fh if l.strip() and not l.startswith("#")]
        self.assertIn("vault/**", lines)
        for carve in [l for l in lines if l.startswith("!")]:
            self.assertTrue(carve.endswith("/") or carve.endswith("README.md"),
                            f"{carve} names a file -- that is the failure mode, use a pattern")

    def test_the_hook_blocks_the_vault(self):
        with open(os.path.join(ROOT, "githooks", "pre-commit"), encoding="utf-8") as fh:
            hook = fh.read()
        self.assertIn("vault/*", hook)

    def test_the_hook_actually_refuses_a_vault_file(self):
        """Asserting the string is in the file proves nothing about what the
        shell does with it -- and this hook now has an exception in it."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            def git(*a):
                return subprocess.run(["git", "-C", tmp, *a], capture_output=True, text=True)
            git("init", "-q"); git("config", "user.email", "t@example.com")
            git("config", "user.name", "t"); git("config", "core.hooksPath",
                                                 os.path.join(ROOT, "githooks"))
            os.makedirs(os.path.join(tmp, "vault", "wiki"))
            for rel, body in (("vault/wiki/CV.md", "private\n"),
                              ("vault/wiki/README.md", "what goes here\n")):
                with open(os.path.join(tmp, rel), "w") as fh:
                    fh.write(body)
            git("add", "-f", "vault/wiki/CV.md", "vault/wiki/README.md")
            r = git("commit", "-m", "x")
            self.assertNotEqual(r.returncode, 0, "the hook let a vault file through")
            self.assertIn("vault/wiki/CV.md", r.stderr)
            self.assertNotIn("vault/wiki/README.md", r.stderr.split("looks personal")[0])


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
