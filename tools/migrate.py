#!/usr/bin/env python3
"""Empty vault/migration/, file what is recognisable, and name what is not.

WHY THIS EXISTS

`vault/migration/README.md` promised this behaviour and nothing implemented it.
It was an instruction, and every instruction-shaped control in this repo has
failed at least once.

It is also the only route onto this system from an existing vault, and the first
person to use it will have a large one -- hundreds of files, years of wikilinks,
a state folder, and a fork of the tooling that has since diverged.

WHAT IT REFUSES TO DO, AND WHY EACH REFUSAL IS THE POINT

  A file it cannot classify        Left where it is, named in the report. A file
                                   quietly left in a drop zone looks exactly
                                   like a file that was dealt with.

  Code                             tools/ and radar/ are the SYSTEM, not the
                                   vault. Somebody arriving from an older clone
                                   will have edited theirs, and migrating it
                                   silently reinstates every bug fixed since.

  Regenerable state                seen.json and a description cache are worth
                                   nothing on the far side and carry the most
                                   weight. Reported as droppable, never moved.

  A filename already in the vault  Obsidian resolves wikilinks by filename
                                   regardless of folder, so two pages with one
                                   name break both links silently.

  Anything, without --apply        The default is a report. A sorter that moves
                                   hundreds of files on its first run, before
                                   anybody has read what it decided, is not a
                                   tool anybody should trust.

AFTER IT RUNS, RUN `wikilinks.py --fix`. Moving files does not break wikilinks
-- Obsidian resolves by filename -- but arriving from another vault usually
does, and this is the moment to find out.
"""
import argparse
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import paths  # noqa: E402

PLACED, KEEP, SYSTEM, COLLIDES, UNKNOWN = "PLACED", "DROP", "SYSTEM", "COLLIDES", "UNKNOWN"

# Regenerable. Named exactly rather than by extension: a user's own notes.json
# is not state, and guessing wrong here deletes something irreplaceable.
REGENERABLE = {"seen.json", "raw.json", "shortlist.md"}

CODE = {".py", ".sh", ".js", ".ts", ".rb", ".go", ".pyc", ".bat", ".ps1"}
DOCS = {".pdf", ".docx", ".doc", ".rtf", ".odt", ".pages"}
DATA = {".csv", ".xlsx", ".json", ".zip", ".htm", ".html", ".txt"}

FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)
TYPE = re.compile(r"^type:\s*([a-z-]+)", re.M)

# Filename shapes that are load-bearing elsewhere in this system.
COMPANY_PAGE = re.compile(r" - Company Research\.md$", re.I)
POSTING_FILE = re.compile(r"^posting\.(txt|md)$", re.I)


def read_head(path, n=2000):
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            return fh.read(n)
    except OSError:
        return ""


def frontmatter_type(text):
    m = FRONTMATTER.match(text)
    if not m:
        return None
    t = TYPE.search(m.group(1))
    return t.group(1) if t else None


def classify(rel, abspath):
    """(verdict, destination_dir_or_None, why).

    Order matters. The refusals come first, because a confident wrong placement
    is worse than an honest UNKNOWN -- somebody can act on UNKNOWN.
    """
    name = os.path.basename(rel)
    ext = os.path.splitext(name)[1].lower()
    folders = rel.replace("\\", "/").split("/")[:-1]
    # Matched lowercase, rebuilt from the original: "Personio Senior PM Internal
    # AI" is a folder name a person reads, and lowercasing it loses the
    # requisition-style capitals that make an application folder identifiable.
    parts = [p.lower() for p in folders]

    if name in REGENERABLE:
        return KEEP, None, "regenerable -- delete it rather than carrying it"
    if ext in CODE:
        return SYSTEM, None, "code is the system, not the vault -- do not migrate a fork"
    if name in (".env",) or name.endswith(".env"):
        return SYSTEM, None, f"a secret: copy the values into {paths.rel(paths.ENV)} by hand"

    # A path hint from the old vault beats anything in the file. Somebody who
    # had it under applications/ knew what it was.
    #
    # 🔴 applications/ and oversight/ are FOLDER-STRUCTURED and the rest are
    # flat. Flattening them was the second bug a real vault found: every
    # application folder holds a cv.txt, a posting.txt and an application.json,
    # so flattening turns a clean migration into a pile of collisions and
    # strands the surviving files from the application that gives them meaning.
    for hint, dest, nested in (("application", paths.APPLICATIONS, True),
                               ("oversight", paths.OVERSIGHT, True),
                               ("posting", paths.POSTINGS, False),
                               ("compan", paths.COMPANIES, False),
                               ("role", paths.ROLES, False),
                               ("source", paths.SOURCES, False),
                               ("raw", paths.SOURCES, False)):
        match = next((i for i, p in enumerate(parts) if hint in p), None)
        if match is None:
            continue
        if nested and folders[match + 1:]:
            return PLACED, os.path.join(dest, *folders[match + 1:]), f"path said {hint}, folder kept"
        return PLACED, dest, f"path said {hint}"

    if COMPANY_PAGE.search(name):
        return PLACED, paths.COMPANIES, "named as company research"
    if POSTING_FILE.match(name):
        return PLACED, paths.POSTINGS, "a captured posting"

    if ext in (".md", ".markdown"):
        t = frontmatter_type(read_head(abspath))
        # 🔴 `type: source` means a PAGE ABOUT a source, not the source file.
        # Routing it to sources/ was the first bug a real vault found, and it
        # was about to move the user's CV.md -- the most linked page they have
        # -- into the folder the agent is forbidden to edit. The two words are
        # the same and the things are opposites.
        by_type = {"role": paths.ROLES, "entity": paths.COMPANIES,
                   "hub": paths.WIKI, "topic": paths.WIKI, "log": paths.WIKI,
                   "synthesis": paths.WIKI, "source": paths.WIKI,
                   "achievement": paths.WIKI}
        if t in by_type:
            return PLACED, by_type[t], f"frontmatter type: {t}"
        if t:
            return UNKNOWN, None, f"frontmatter type '{t}' is not one this system files"
        # 🔴 No frontmatter is NOT enough to call it a wiki page. Notes from
        # another tool, a pasted job ad and a page of someone's history all look
        # identical here, and they belong in three different folders.
        return UNKNOWN, None, "markdown with no frontmatter -- could be a page, a note or a posting"

    if ext in DOCS:
        return PLACED, paths.SOURCES, "a document: raw material until something is built from it"
    if ext in DATA:
        return UNKNOWN, None, f"{ext} could be an export, a settings file or a posting"
    if ext in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
        return PLACED, paths.SOURCES, "an image"
    return UNKNOWN, None, "unrecognised"


def vault_filenames():
    """Every filename already in the vault. Obsidian resolves wikilinks by
    filename regardless of folder, so a duplicate breaks both links silently."""
    seen = {}
    for root in paths.CARRY:
        for base, _, files in os.walk(root):
            for f in files:
                seen.setdefault(f, os.path.join(base, f))
    return seen


def walk(root):
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".obsidian")]
        for f in sorted(files):
            if f in (".DS_Store", "README.md"):
                continue
            full = os.path.join(base, f)
            yield os.path.relpath(full, root), full


def plan(migration=None):
    migration = migration or paths.MIGRATION
    existing = vault_filenames()
    out = []
    for rel, full in walk(migration):
        verdict, dest, why = classify(rel, full)
        if verdict == PLACED:
            name = os.path.basename(rel)
            # A file inside its own application folder is identified by that
            # folder, so cv.txt in two packs is not a collision.
            if dest.startswith(paths.APPLICATIONS) or dest.startswith(paths.OVERSIGHT):
                out.append((rel, full, verdict, dest, why))
                continue
            clash = existing.get(name)
            if clash and os.path.abspath(clash) != os.path.abspath(full):
                out.append((rel, full, COLLIDES, None,
                            f"{name} already exists at {paths.rel(clash)} -- "
                            "two files with one name break both wikilinks"))
                continue
            existing[name] = os.path.join(dest, name)
        out.append((rel, full, verdict, dest, why))
    return out


def apply(items):
    moved = []
    for rel, full, verdict, dest, _ in items:
        if verdict != PLACED:
            continue
        paths.ensure(dest)
        target = os.path.join(dest, os.path.basename(rel))
        if os.path.exists(target):      # a collision that appeared since planning
            continue
        shutil.move(full, target)
        moved.append((rel, target))
    return moved


def prune_empty(root):
    for base, dirs, files in os.walk(root, topdown=False):
        if base != root and not os.listdir(base):
            os.rmdir(base)


def report(items, applied):
    if not items:
        print("\n  migration/ is empty. Nothing to sort.\n")
        return 0
    order = [PLACED, COLLIDES, SYSTEM, KEEP, UNKNOWN]
    head = {PLACED: "Filed" if applied else "Would file",
            COLLIDES: "🔴 Refused — the filename is already used in the vault",
            SYSTEM: "🔴 Refused — this is the system, not the vault",
            KEEP: "Regenerable — delete rather than carry",
            UNKNOWN: "🔴 Could not classify — left where they are"}
    print()
    for v in order:
        rows = [i for i in items if i[2] == v]
        if not rows:
            continue
        print(f"  {head[v]}  ({len(rows)})")
        for rel, _, _, dest, why in rows:
            rel = rel if len(rel) <= 58 else "…" + rel[-57:]
            where = f"→ {os.path.relpath(dest, paths.VAULT)}/" if dest else ""
            print(f"    {rel:<58}  {where:<14}  {why}")
        print()

    left = [i for i in items if i[2] != PLACED]
    if not applied:
        print(f"  Nothing has moved. Re-run with --apply to file "
              f"{len([i for i in items if i[2] == PLACED])} file(s).\n")
    else:
        print(f"  Filed {len([i for i in items if i[2] == PLACED])}. "
              f"{len(left)} still in migration/.\n")
        print("  🔴 Now run:  python3 tools/wikilinks.py --fix\n"
              "     Moving files does not break wikilinks, but arriving from another "
              "vault usually does.\n")
    if left:
        print("  🔴 Everything above that was not filed is still in the drop zone, by design.\n"
              "     Tell the user what they are, by name. A file quietly left in a drop zone\n"
              "     looks exactly like a file that was dealt with.\n")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true",
                    help="actually move the files (the default is a report)")
    ap.add_argument("--from", dest="src", default=None, help="a folder other than vault/migration")
    args = ap.parse_args(argv)

    src = os.path.abspath(args.src) if args.src else paths.MIGRATION
    if not os.path.isdir(src):
        print(f"\n  No {paths.rel(src)} to sort. Create it and drop files in.\n")
        return 0
    items = plan(src)
    if args.apply:
        apply(items)
        prune_empty(src)
    return report(items, args.apply)


if __name__ == "__main__":
    sys.exit(main())
