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
import ast, glob, json, os, re, subprocess, sys, tempfile, unittest

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
                        if p.startswith("vault/")
                        and not p.endswith("/README.md"))
        self.assertEqual(leaked, [], f"the vault is the user's and must never ship: {leaked}")

    def test_the_folders_a_user_puts_things_into_ship(self):
        """The vault used to be created entirely on first write, so a clean
        clone had no vault at all and nothing told a new user where their CV
        went. These five are the ones a PERSON writes into; the rest are written
        by the agent and are created when it first needs them."""
        for folder in ("sources", "migration", "settings", "secrets", "temp"):
            self.assertIn(f"vault/{folder}/README.md", tracked(),
                          f"vault/{folder}/ must ship, or nobody knows it exists")

    def test_the_users_own_instruction_file_is_a_template_not_a_tracked_file(self):
        """It is the one file in vault/ the USER writes, which makes tracking it
        the exact mistake the boundary exists to prevent: `git add -A` would
        publish their standing instructions. It ships in templates/ and
        career-init places a copy."""
        self.assertIn("templates/vault-AGENTS.md", tracked())
        self.assertNotIn("vault/AGENTS.md", tracked(),
                         "a file the user writes must never be tracked")
        for f in ("AGENTS.md", os.path.join(".claude", "skills", "career-init", "SKILL.md")):
            with open(os.path.join(ROOT, f), encoding="utf-8") as fh:
                self.assertIn("vault/AGENTS.md", fh.read(),
                              f"{f} must say where the user's instructions live")

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

    SHIPPED = {"vault/README.md", "vault/sources/README.md", "vault/settings/README.md",
               "vault/secrets/README.md", "vault/migration/README.md",
               "vault/temp/README.md"}

    def test_the_ignore_rule_the_hook_and_the_repo_agree_on_the_same_five(self):
        """Three lists that must agree cannot drift apart quietly.

        `!vault/**/README.md` was tried first because a pattern looked safer
        than a list -- and it was wrong here. The agent writes README files
        inside vault folders as it works, and the pattern made every one of them
        stageable by `git add -A`. The distinction that matters is not
        pattern-versus-list: it is whether the thing grows when the USER adds a
        file. This one only grows when the SYSTEM adds a folder."""
        with open(os.path.join(ROOT, ".gitignore"), encoding="utf-8") as fh:
            lines = [l.strip() for l in fh if l.strip() and not l.startswith("#")]
        self.assertIn("vault/**", lines)
        carved = {l[1:] for l in lines if l.startswith("!") and not l.endswith("/")}
        self.assertEqual(carved, self.SHIPPED, "the ignore rule and the shipped set disagree")

        with open(os.path.join(ROOT, "githooks", "pre-commit"), encoding="utf-8") as fh:
            hook = fh.read()
        for p in self.SHIPPED:
            self.assertIn(p, hook, f"the hook does not allow {p}")
        self.assertNotIn("vault/*/README.md", hook, "a wildcard waves through agent-written READMEs")

        self.assertEqual({p for p in tracked() if p.startswith("vault/")}, self.SHIPPED)

    def test_a_readme_the_agent_writes_is_still_ignored(self):
        """The probe that found the hole. It is not enough to assert the rules
        look right -- what matters is what git does with a path nobody listed."""
        import tempfile
        probe = os.path.join(ROOT, "vault", "wiki", "_boundary_probe")
        os.makedirs(probe, exist_ok=True)
        target = os.path.join(probe, "README.md")
        try:
            with open(target, "w") as fh:
                fh.write("written by the agent, not by the system\n")
            r = subprocess.run(["git", "-C", ROOT, "check-ignore", target],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0,
                             "a README the agent writes inside the vault is not ignored")
        finally:
            os.remove(target)
            os.removedirs(probe)

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
            os.makedirs(os.path.join(tmp, "vault", "sources"))
            files = {"vault/wiki/CV.md": "private\n",
                     # The agent writes these as it works. They are not the
                     # system's, and the hook must not wave them through.
                     "vault/wiki/README.md": "notes on this folder\n",
                     "vault/sources/README.md": "what goes here\n"}
            for rel, body in files.items():
                with open(os.path.join(tmp, rel), "w") as fh:
                    fh.write(body)
            git("add", "-f", *files)
            r = git("commit", "-m", "x")
            self.assertNotEqual(r.returncode, 0, "the hook let a vault file through")
            blocked = r.stderr.split("looks personal")[0]
            self.assertIn("vault/wiki/CV.md", blocked)
            self.assertIn("vault/wiki/README.md", blocked,
                          "only the five shipped READMEs are the system's")
            self.assertNotIn("vault/sources/README.md", blocked)


class NoUsersPreferencesShipInTheSystem(unittest.TestCase):
    """🔴 The boundary test checked the FORM of the boundary, not the SUBSTANCE.

    Three leaks on 2026-08-26, none of which any check could see, all the same
    shape: content specific to ONE user, in files the repo ships to everyone.

      tools/radar/radar.py   one person's entire tiering vocabulary -- weights
                             for the phrases that suited them, heavy negatives
                             for an industry that kept mismatching their words,
                             a penalty for a commute they would not accept
      tools/cv_lint.py       one market's spelling, enforced with a non-zero
                             exit and no flag to turn it off
      templates/...json      two REAL employers in a file whose own README says
                             to replace every placeholder

    The existing tests assert no FILE under vault/ is tracked. They say nothing
    about user-specific CONTENT in tools/ or templates/, and that is the
    direction all three went.

    🔴 SCOPE IS THE WHOLE DESIGN. These rules apply ONLY to files whose purpose
    is to be generic -- templates and shipped defaults. They must never touch
    tools/radar/ats_registry.json, which is MADE of real employer names and is
    the one file strangers are invited to contribute to; nor docs/, which names
    real markets and regulators deliberately, to teach; nor the tests, which
    need the forbidden strings in order to search for them. A check that fires
    on the best content in the repo is one somebody switches off.
    """

    # The repo's established stand-ins. A template must use a <placeholder> or
    # one of these -- not somebody's real answer.
    FICTIONAL = re.compile(r"^(acme|beta|widget|example|foo|bar|employer (one|two|three)|"
                           r"first bank|second bank|halfling|statesman|obscure)\b", re.I)
    # A capitalised multi-word phrase: how a real organisation is written.
    PROPER_NOUN = re.compile(r"^[A-Z][a-z]+(?:\s+(?:[A-Z][a-z]+|&|and|of|the))+")

    def _strings(self, obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if str(k).startswith("_"):      # _comment / _README are prose
                    continue
                yield from self._strings(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                yield from self._strings(v, f"{path}[{i}]")
        elif isinstance(obj, str):
            yield path, obj

    def test_no_template_carries_a_real_organisation(self):
        """A template that quietly holds real answers teaches the reader that
        some of it is already right."""
        bad = []
        for f in glob.glob(os.path.join(ROOT, "templates", "**", "*.json"), recursive=True):
            with open(f, encoding="utf-8") as fh:
                doc = json.load(fh)
            for path, s in self._strings(doc):
                if s.startswith("<") or self.FICTIONAL.match(s):
                    continue
                if self.PROPER_NOUN.match(s):
                    bad.append(f"{os.path.relpath(f, ROOT)}{path} = {s!r}")
        self.assertEqual(bad, [], "a real organisation is named in a template: " + str(bad))

    def test_the_repos_own_fiction_still_passes(self):
        """🔴 THE FALSE-POSITIVE CASE, and it fired on the first draft.
        'Acme Corp' and 'Employer One' are deliberately fictional examples and
        must not be flagged -- otherwise the rule punishes good templates."""
        for ok in ("Acme Corp", "Employer One", "Beta Corp", "Widget Industries",
                   "First Bank", "Halfling Ltd"):
            self.assertTrue(self.FICTIONAL.match(ok) or not self.PROPER_NOUN.match(ok), ok)
        for real in ("State Street", "Grant Thornton Ireland", "Bank of Ireland"):
            self.assertTrue(self.PROPER_NOUN.match(real) and not self.FICTIONAL.match(real), real)

    def test_no_tool_ships_a_weighted_preference_table(self):
        """A literal list of (pattern, weight) pairs is a taste, not a mechanism.

        That shape IS the thing that leaked: a scoring vocabulary reads as code
        and is really a statement about one person's career. Tests are exempt --
        they must build such tables to check the loader."""
        bad = []
        for f in glob.glob(os.path.join(ROOT, "tools", "**", "*.py"), recursive=True):
            if os.sep + "tests" + os.sep in f:
                continue
            try:
                tree = ast.parse(open(f, encoding="utf-8").read())
            except SyntaxError:
                continue
            for node in tree.body:
                if not isinstance(node, ast.Assign) or not isinstance(node.value, (ast.List, ast.Tuple)):
                    continue
                pairs = [e for e in node.value.elts
                         if isinstance(e, (ast.Tuple, ast.List)) and len(e.elts) == 2
                         and isinstance(e.elts[0], ast.Constant) and isinstance(e.elts[0].value, str)
                         and isinstance(e.elts[1], ast.Constant)
                         and isinstance(e.elts[1].value, (int, float))]
                if len(pairs) >= 3:
                    name = node.targets[0].id if isinstance(node.targets[0], ast.Name) else "?"
                    bad.append(f"{os.path.relpath(f, ROOT)}:{node.lineno} {name}")
        self.assertEqual(bad, [], "a weighted preference table ships in tools/: " + str(bad))


class NoToolNamesAFileThatMoved(unittest.TestCase):
    """A reconciliation found sixteen live references to `config.json`, a file
    that became vault/settings/search.json. Docs rot silently; a user follows
    the instruction, creates the file where it says, and the tool reports
    nothing configured -- which reads as a broken tool, not a stale doc."""

    # Bare names of files that moved. A path-qualified mention is fine --
    # `templates/settings/employers.example.json` tells the reader where it is;
    # a bare `employers.example.json` sends them looking in the wrong folder.
    GONE = ("config.json", "sync-to-vault")
    BARE = ("employers.example.json", "search.example.json", "review.example.json")

    def test_no_user_facing_file_names_a_path_that_moved(self):
        offenders = []
        for base, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "vault", "tests")]
            for f in files:
                if not f.endswith((".py", ".md", ".sh", ".json")):
                    continue
                # BACKLOG.md is a dated record of what was done; rewriting the
                # history to match today's paths would make it a worse record.
                if f in ("BACKLOG.md",):
                    continue
                path = os.path.join(base, f)
                with open(path, encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()
                for token in self.GONE:
                    if token in text and "was deleted on" not in text:
                        offenders.append(f"{os.path.relpath(path, ROOT)}: {token}")
                for token in self.BARE:
                    for line in text.splitlines():
                        if token in line and f"settings/{token}" not in line:
                            offenders.append(f"{os.path.relpath(path, ROOT)}: bare {token}")
                            break
        self.assertEqual(sorted(offenders), [], f"stale paths: {offenders}")


class TheGuardInstallsItself(unittest.TestCase):
    """`git config core.hooksPath githooks` was a line in the setup docs, which
    means it was on for whoever read them. The person who skips setup is exactly
    the person who does not know the boundary exists."""

    def test_the_installer_ships_and_is_executable(self):
        rel = ".claude/hooks/install-guard.sh"
        self.assertIn(rel, tracked())
        self.assertTrue(os.access(os.path.join(ROOT, rel), os.X_OK), f"{rel} is not executable")

    def test_a_session_runs_it(self):
        import json
        with open(os.path.join(ROOT, ".claude", "settings.json"), encoding="utf-8") as fh:
            cfg = json.load(fh)
        cmds = [h.get("command", "") for g in cfg["hooks"].get("SessionStart", [])
                for h in g.get("hooks", [])]
        self.assertTrue(any("install-guard" in c for c in cmds),
                        "nothing installs the commit guard at session start")

    def test_it_is_idempotent_and_safe_outside_a_repo(self):
        import tempfile
        script = os.path.join(ROOT, ".claude", "hooks", "install-guard.sh")
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, CLAUDE_PROJECT_DIR=tmp)
            r = subprocess.run(["bash", script], env=env, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, "it must not fail on a ZIP download")
            subprocess.run(["git", "-C", tmp, "init", "-q"], check=True)
            os.makedirs(os.path.join(tmp, "githooks"), exist_ok=True)
            for _ in range(2):
                self.assertEqual(subprocess.run(["bash", script], env=env,
                                                capture_output=True).returncode, 0)
            got = subprocess.run(["git", "-C", tmp, "config", "core.hooksPath"],
                                 capture_output=True, text=True).stdout.strip()
            self.assertEqual(got, "githooks")


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
                     "wikilinks.py", "template_drift.py", "settings_drift.py"):
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


class TheSuiteDoesNotReadTheUsersVault(unittest.TestCase):
    """🔴 A test that reads the user's configuration is not testing the code.

    THE INCIDENT. On 2026-08-26 the tiering vocabulary moved out of radar.py and
    into vault/settings/signal.json, which was right -- it was one user's
    preferences sitting in shared code. But radar's POS/NEG/HIGH_AT/MED_AT then
    loaded AT IMPORT from whatever vault happened to be present, and the suite
    imports radar. On the author's machine signal.json exists, so 530 checks
    passed and the change looked finished.

    On a fresh clone, five failed. Nothing could ever score HIGH, because the
    vocabulary was empty. The suite had been measuring the author's vault.

    Found by simulating an update rather than arguing about one: clone, rewind,
    populate a vault, git pull, run the tests. This check is that simulation,
    kept, so the next thing to load user config at import fails here instead of
    on somebody else's first day.
    """

    GUARD = "CAREER_TESTS_WITHOUT_A_VAULT"

    def test_every_check_passes_against_an_empty_vault(self):
        if os.environ.get(self.GUARD):
            self.skipTest("this is the child run; it must not spawn another")
        here = os.path.dirname(os.path.abspath(__file__))
        with tempfile.TemporaryDirectory() as empty:
            env = dict(os.environ, CAREER_VAULT=empty, **{self.GUARD: "1"})
            r = subprocess.run([sys.executable, os.path.join(here, "run.py")],
                               capture_output=True, text=True, env=env)
        self.assertEqual(
            r.returncode, 0,
            "The suite passes here and fails on a vault that is not this one, so "
            "something under test is reading the user's own settings at import.\n"
            "A default of 'empty' is what makes this silent: nothing errors, the "
            "vocabulary is simply blank and every role tiers LOW.\n\n"
            + (r.stdout or "")[-3000:])


if __name__ == "__main__":
    unittest.main(verbosity=2)
