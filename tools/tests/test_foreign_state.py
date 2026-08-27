"""foreign_state: what another tool left beside the code that names the user's files.

🔴 THE INCIDENT. `.obsidian/` sat at the repository root, untracked but not
ignored. Its `workspace.json` records open files BY PATH, so it named
settings and wiki pages under vault/. One `git add -A` would have published a
list of a user's private files to a public remote.

Three existing controls missed it and none was malfunctioning: test_boundary
checks what THIS repo writes, and both pre-commit rules look at staged paths or
at email/salary patterns. **The guard covered the agent, not the desk it works
on.**

Most of the tests below are false-positive tests, because this check has three
separate ways to become useless and it demonstrated the third on its own first
run -- by flagging itself.
"""
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("foreign_state",
                                              os.path.join(ROOT, "tools", "foreign_state.py"))
fs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fs)


class Repo:
    """A throwaway git repo, because the check reads real git state."""

    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        for cmd in (["init", "-q"], ["config", "user.email", "t@e.invalid"],
                    ["config", "user.name", "t"]):
            subprocess.run(["git"] + cmd, cwd=self.dir, capture_output=True)
        self.write(".gitignore", "vault/\n")
        subprocess.run(["git", "add", ".gitignore"], cwd=self.dir, capture_output=True)
        subprocess.run(["git", "commit", "-qm", "init"], cwd=self.dir, capture_output=True)
        return self

    def write(self, rel, text):
        p = os.path.join(self.dir, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True) if os.path.dirname(rel) else None
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        return p

    def track(self, rel):
        subprocess.run(["git", "add", rel], cwd=self.dir, capture_output=True)
        subprocess.run(["git", "commit", "-qm", "x"], cwd=self.dir, capture_output=True)

    def scan(self):
        return fs.scan(self.dir)

    def __exit__(self, *a):
        import shutil
        shutil.rmtree(self.dir, ignore_errors=True)


class TheIncident(unittest.TestCase):

    WORKSPACE = ('{"main":{"children":[{"state":{"file":"vault/settings/employers.json"}},'
                 '{"state":{"file":"vault/AGENTS.md"}}]},'
                 '"lastOpenFiles":["vault/wiki/Compensation.md"]}')

    def test_an_editor_workspace_file_is_caught(self):
        with Repo() as r:
            r.write(".obsidian/workspace.json", self.WORKSPACE)
            found = r.scan()
            self.assertEqual([p for p, _ in found], [".obsidian/workspace.json"])
            self.assertIn("vault/settings/employers.json", found[0][1])

    def test_the_class_and_not_just_obsidian(self):
        """🔴 The next one will not be Obsidian."""
        for path in (".idea/workspace.xml", ".vscode/settings.json",
                     ".trash/notes.md", "sync-conflict-2026.json", ".zed/state.json"):
            with Repo() as r:
                r.write(path, "recent: vault/wiki/Compensation.md")
                self.assertEqual([p for p, _ in r.scan()], [path], path)

    def test_ignoring_it_is_what_clears_the_finding(self):
        """The remedy the tool recommends must actually work."""
        with Repo() as r:
            r.write(".obsidian/workspace.json", self.WORKSPACE)
            self.assertTrue(r.scan())
            r.write(".gitignore", "vault/\n.obsidian/\n")
            self.assertEqual(r.scan(), [])

    def test_tracking_it_also_clears_it(self):
        """Tracked is a decision somebody made. This check is about the ones
        nobody has decided about yet."""
        with Repo() as r:
            r.write("notes.md", "see vault/wiki/Compensation.md")
            self.assertTrue(r.scan())
            r.track("notes.md")
            self.assertEqual(r.scan(), [])


class TheFalsePositives(unittest.TestCase):
    """🔴 Three ways to be useless, and it managed the third on its first run."""

    def test_an_ordinary_new_source_file_is_not_reported(self):
        """"Fail on anything untracked" fires every time somebody creates a file
        and is switched off within a day."""
        with Repo() as r:
            r.write("newmodule.py", "def f():\n    return 1\n")
            self.assertEqual(r.scan(), [])

    def test_a_bare_mention_of_the_vault_folder_is_not_a_leak(self):
        """🔴 THE TRAP NAMED IN THE BACKLOG ENTRY. This repository writes the
        string `vault/` hundreds of times, legitimately, in paths.py, SCHEMA.md,
        AGENTS.md and every skill. A check on the bare string flags its own
        documentation -- which the pre-commit heuristic has already done twice."""
        with Repo() as r:
            r.write("design.md", "Everything about the user lives under vault/ and "
                                 "nothing else does. Never write outside vault/.")
            self.assertEqual(r.scan(), [])

    def test_the_repos_own_directories_are_exempt(self):
        """🔴 FOUND BY THE CHECK FLAGGING ITSELF. A new file under tools/ or
        docs/ is the author writing the system, and it is already covered by
        test_boundary and by both pre-commit rules."""
        with Repo() as r:
            for path in ("tools/newtool.py", "docs/NOTE.md", "templates/x.md",
                         "githooks/hook", ".claude/skills/s/SKILL.md"):
                r.write(path, "reads vault/settings/employers.json")
            self.assertEqual(r.scan(), [])

    def test_a_binary_file_is_skipped(self):
        with Repo() as r:
            p = os.path.join(r.dir, "cache.bin")
            with open(p, "wb") as fh:
                fh.write(b"vault/wiki/Compensation.md\x00\x01\x02")
            self.assertEqual(r.scan(), [])

    def test_a_huge_file_is_skipped(self):
        """A cache can be enormous and is not worth reading to find a path."""
        with Repo() as r:
            r.write("big.log", "x" * (fs.READ_LIMIT + 10) + " vault/wiki/Compensation.md")
            self.assertEqual(r.scan(), [])

    def test_a_directory_outside_a_git_repo_returns_nothing(self):
        d = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        self.assertEqual(fs.scan(d), [])


class TheRealRepository(unittest.TestCase):

    def test_this_repository_is_clean(self):
        """🔴 The check must pass on the repo it ships in, or it is noise from
        the first run and nobody looks at the second."""
        found = fs.scan(ROOT)
        self.assertEqual(found, [], f"untracked files naming vault paths: {found}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
