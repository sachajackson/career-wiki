#!/usr/bin/env python3
"""What has another tool left beside the code that names the user's files?

    python3 tools/foreign_state.py            # report; exit 1 if anything found

WHAT HAPPENED

`.obsidian/` sat at the repository root, **untracked but not ignored**. Its
`workspace.json` records open and recently-opened files BY PATH, so it named
`vault/settings/employers.json`, `vault/AGENTS.md` and whichever pages had been
read last. One `git add -A` would have published a list of a user's private files
to a public remote.

🔴 UNTRACKED IS NOT IGNORED. That is the whole idea. A file nobody has added is
one command away from being added, and `.gitignore` is the only thing standing
between the two.

WHY THE EXISTING GUARDS ALL MISSED IT, WITHOUT ANY OF THEM MALFUNCTIONING

  test_boundary.py   checks what THIS repo writes outside vault/. Obsidian wrote
                     this. The guard covers the agent, not the desk it works on.
  pre-commit rule 1  blocks staged paths under vault/. This is not under vault/.
  pre-commit rule 2  looks for emails, LinkedIn URLs and salary phrasing. A JSON
                     file listing vault PATHS matches none of them.

The class is every tool that drops state next to a repository -- `.idea/`,
`.vscode/`, `.trash/`, editor swap files, sync-tool conflict copies. **The next
one will not be Obsidian.**

🔴 THE TWO WAYS THIS CHECK COULD BE USELESS, BOTH DESIGNED AGAINST

1. "Fail on any untracked, non-ignored file" fires during ordinary development
   every time somebody creates a source file, and is switched off within a day.
   So a file must ALSO name a specific vault file to be reported.

2. Matching the bare string `vault/` flags the repository's own documentation.
   `paths.py`, `SCHEMA.md`, `AGENTS.md` and every skill refer to `vault/`
   constantly and legitimately. **The content heuristic in `pre-commit` has
   already fired on its own postmortem twice**, which is how a good check earns
   the reputation that gets it overridden. So the pattern requires
   `vault/<folder>/<file>` -- a specific file, two segments deep.
"""
import argparse
import os
import re
import subprocess
import sys

# 🔴 Two segments after vault/, so a bare mention of the folder never matches.
# `vault/settings/employers.json` is somebody's file; `vault/` is a sentence
# about the layout, and this repository writes that sentence hundreds of times.
VAULT_FILE = re.compile(r"vault/[A-Za-z0-9._-]+/[A-Za-z0-9._-]+")
READ_LIMIT = 512_000        # a workspace file is small; a cache is not worth reading

# 🔴 DIRECTORIES THIS REPOSITORY MAINTAINS, AND THE THIRD WAY THE CHECK COULD BE
# USELESS -- which it demonstrated on its own first run by flagging ITSELF.
#
# This file's docstring names a vault path as an example, and while it was still
# untracked the check reported it as a leak. That is the same failure the
# `pre-commit` content heuristic has had twice, on its own postmortems.
#
# A new file under tools/ or docs/ is the author writing the system, and it is
# ALREADY covered: test_boundary.py checks what this repo writes outside vault/,
# and pre-commit rules 1 and 2 scan everything staged. This check exists for the
# other thing -- state some OTHER tool dropped beside the code.
#
# 🔴 The hole this leaves, stated rather than hidden: a foreign tool that wrote
# into one of these directories would be missed. No editor or sync tool does --
# they write to dot-directories and the repository root -- and narrowing here is
# what keeps the check quiet enough to stay switched on.
OURS = ("tools/", "docs/", "templates/", "examples/", "githooks/", ".claude/skills/",
        "vault/")   # vault/ is the user's own and is ignored wholesale anyway


def untracked_not_ignored(root="."):
    """Exactly the dangerous state: git knows nothing about it AND would add it."""
    try:
        out = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"],
                             cwd=root, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return []
    if out.returncode != 0:
        return []
    return [p for p in out.stdout.splitlines() if p.strip()]


def names_a_vault_file(path):
    """The vault paths a file mentions, or []. Binary and huge files are skipped."""
    try:
        if os.path.getsize(path) > READ_LIMIT:
            return []
        with open(path, "rb") as fh:
            blob = fh.read(READ_LIMIT)
    except OSError:
        return []
    if b"\0" in blob:
        return []                       # binary: no readable paths to leak
    text = blob.decode("utf-8", "replace")
    return sorted(set(VAULT_FILE.findall(text)))


def scan(root="."):
    """[(path, [vault files it names])] for everything that qualifies."""
    found = []
    for rel in untracked_not_ignored(root):
        if rel.startswith(OURS):
            continue
        hits = names_a_vault_file(os.path.join(root, rel))
        if hits:
            found.append((rel, hits))
    return sorted(found)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--quiet", action="store_true", help="print only when something is found")
    args = ap.parse_args()

    found = scan(args.root)
    if not found:
        if not args.quiet:
            print("  Nothing untracked names a file under vault/.\n"
                  "  That is not a statement about what IS tracked — "
                  "`git status` still owns that question.")
        return 0

    print(f"\n  🔴 {len(found)} untracked, un-ignored file(s) name a file under vault/:\n")
    for path, hits in found:
        print(f"     {path}")
        for h in hits[:4]:
            print(f"        names {h}")
        if len(hits) > 4:
            print(f"        …and {len(hits) - 4} more")
    print("\n  Untracked is not ignored: one `git add -A` publishes these to a public remote.\n"
          "  Add each to .gitignore, or delete it.\n"
          "\n  🟡 If this is an editor or note-taking app, point it at `vault/` instead of the\n"
          "     repository root. That scopes it to the boundary this repo already draws, and\n"
          "     removes the symptom and the leak together.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
