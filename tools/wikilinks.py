#!/usr/bin/env python3
"""wikilinks -- the third deterministic check. Finds links that quietly go nowhere.

    python3 tools/wikilinks.py wiki
    python3 tools/wikilinks.py wiki --fix

WHY THIS EXISTS

Three ways a wikilink fails, and none of them looks broken while you are reading:

  1. WRAPPED   A link split across two lines by a wrapping convention. Obsidian
               does not match [[ ]] across a newline, so it renders as literal
               text. The prose still reads correctly. In one vault this had
               broken 83 links across 26 files before anyone noticed.

  2. NO PAGE   The target file does not exist. In this schema a link to a page
               that has not been written yet is legitimate -- it marks that the
               page should exist -- so this is reported but does not fail the
               run unless --strict. It is still where typos show up.

  3. NO HEADING  The page exists but the heading was renamed. This is the
               quietest of the three: the link opens the page and silently
               lands at the top instead of the section being cited.

None of these throws an error, and a knowledge base whose failure mode is
silence is one you stop being able to trust. An instruction not to wrap inside
[[ ]] failed three times in a single session, which is what a check is for.

--fix repairs WRAPPED only, and only where the joined target resolves. It strips
a blockquote continuation marker if the link was inside a quote -- the first
attempt at this repair pulled "> " into the link text and created seven new
broken links, so that case is tested.

Exit status is 1 if anything was flagged, so it can gate a build.
"""
import argparse, os, re, sys, glob

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import paths  # noqa: E402

LINK = re.compile(r"\[\[(.+?)\]\]", re.S)
HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*$")
# Deliverables and anything path-like are not wiki pages and are not our business.
NOT_A_PAGE = (".pdf", ".docx", ".doc", ".png", ".jpg", ".xlsx", ".pptx", ".py", ".sh", ".json")


def split_target(inner):
    """[[Page#Heading|Alias]] -> (page, heading). Handles the \\| a markdown
    table needs, which is why a naive split on | gets this wrong."""
    target = re.split(r"\\?\|", inner, maxsplit=1)[0]
    page, _, anchor = target.partition("#")
    return page.strip().rstrip("\\"), anchor.strip().rstrip("\\")


def scan(root):
    files = sorted(glob.glob(os.path.join(root, "**", "*.md"), recursive=True))
    headings, exists = {}, {}
    for path in files:
        name = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        hs = set()
        for line in text.splitlines():
            m = HEADING.match(line.lstrip("> ").rstrip())
            if m:
                hs.add(m.group(1).strip())
        headings[name] = hs
        exists[name] = path
    return files, headings, exists


def check(root):
    files, headings, exists = scan(root)
    findings = []
    for path in files:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        this = os.path.splitext(os.path.basename(path))[0]
        for m in LINK.finditer(text):
            inner = m.group(1)
            line = text.count("\n", 0, m.start()) + 1
            if "\n" in inner:
                findings.append(("WRAPPED", path, line,
                                 f"link split across lines: {inner.splitlines()[0][:48]!r}..."))
                continue
            if inner.startswith("^"):
                continue                                   # block reference
            page, anchor = split_target(inner)
            page = page or this
            if page.lower().endswith(NOT_A_PAGE) or "/" in page:
                continue
            if page not in exists:
                findings.append(("NO PAGE", path, line, f"no page named {page!r}"))
                continue
            if anchor and not anchor.startswith("^") and anchor not in headings[page]:
                findings.append(("NO HEADING", path, line,
                                 f"{page!r} has no heading {anchor[:56]!r}"))
    return findings


def fix_wrapped(root):
    """Join links split across lines, where the joined target resolves."""
    _, _, exists = scan(root)
    repaired = 0
    for path in sorted(glob.glob(os.path.join(root, "**", "*.md"), recursive=True)):
        with open(path, encoding="utf-8") as fh:
            text = original = fh.read()
        this = os.path.splitext(os.path.basename(path))[0]

        def join(m):
            nonlocal repaired
            inner = m.group(1)
            if "\n" not in inner:
                return m.group(0)
            # A wrapped link inside a blockquote carries the "> " continuation
            # marker into the link text. Strip it, or the repair breaks the link
            # in a new way -- which is exactly what happened the first time.
            flat = re.sub(r"\s*\n\s*(?:>\s*)?", " ", inner).strip()
            page, _ = split_target(flat)
            if (page or this) in exists or (page or "").lower().endswith(NOT_A_PAGE):
                repaired += 1
                return "[[" + flat + "]]"
            return m.group(0)

        text = LINK.sub(join, text)
        if text != original:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
    return repaired


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("root", nargs="?", default=paths.WIKI, help="folder to scan (default: the vault wiki)")
    ap.add_argument("--fix", action="store_true", help="join links split across lines, then re-check")
    ap.add_argument("--only", help="report findings in this file only. The scan still reads the whole "
                                   "folder, because a link's validity depends on every other page -- but "
                                   "blaming a writer for pre-existing rot on every save makes a check "
                                   "noisy, and a noisy check gets ignored")
    ap.add_argument("--strict", action="store_true",
                    help="also fail on NO PAGE. Off by default: a link to an unwritten page is a "
                         "valid marker in this schema, not an error")
    args = ap.parse_args()
    if not os.path.isdir(args.root):
        sys.exit(f"wikilinks: no folder at {args.root}")

    if args.fix:
        n = fix_wrapped(args.root)
        print(f"wikilinks: joined {n} wrapped link(s). Re-checking.\n")

    findings = check(args.root)
    total = len(glob.glob(os.path.join(args.root, "**", "*.md"), recursive=True))
    if args.only:
        want = os.path.realpath(args.only)
        findings = [f for f in findings if os.path.realpath(f[1]) == want]
        total = 1
    hard = [f for f in findings if f[0] != "NO PAGE"]
    soft = [f for f in findings if f[0] == "NO PAGE"]
    print(f"wikilinks: {len(hard)} broken, {len(soft)} pointing at unwritten pages, "
          f"across {total} pages")
    for kind, path, line, msg in hard + soft:
        print(f"  [{kind}] {path}:{line} -- {msg}")
    if not findings:
        print("  every link resolves, headings included.")
    else:
        print("\nWRAPPED is mechanical -- re-run with --fix. NO HEADING is judgement: the heading was\n"
              "renamed, so repoint the link at whatever replaced it. NO PAGE is usually a page still to\n"
              "write, and sometimes a typo; --strict fails on it too.")
    sys.exit(1 if (findings if args.strict else hard) else 0)


if __name__ == "__main__":
    main()
