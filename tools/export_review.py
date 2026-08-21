#!/usr/bin/env python3
"""export_review -- build a self-contained folder safe to open in another vendor's tool.

    python3 tools/export_review.py "wiki/applications/Acme R-12345"
    -> review-exports/Acme R-12345/   (OVERSIGHT.md, posting, CV, cover letter)

WHY THIS EXISTS RATHER THAN JUST POINTING THE REVIEWER AT THE APPLICATION FOLDER

OVERSIGHT.md tells the reviewer not to read the wiki. That is an instruction to
a model, and an instruction to a model is not a boundary. An application folder
that lives inside the wiki is one `cd ..` away from the applicant's salary
floor, their reasons for leaving, and notes about their colleagues.

So containment is done with the filesystem instead. This copies the four kinds
of file a reviewer is allowed to see into a directory that sits outside the
wiki and contains nothing else. Opening that folder is safe by construction,
and the instruction becomes a belt to the filesystem's braces rather than the
only thing standing between a third-party service and everything the applicant
has ever said.

WHAT IT DELIBERATELY DOES NOT COPY

  application.json  -- internal configuration. do_not_claim in particular is a
                       list of the applicant's gaps, and it is none of the
                       reviewer's business: the cover letter concedes what it
                       chooses to concede.
  anything else     -- working notes, drafts, correspondence, ATS packs.

Everything copied is going to a recruiter anyway, so a review costs no
additional exposure.
"""
import os, re, shutil, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(HERE, "templates", "OVERSIGHT.md")

ALLOWED = [
    (re.compile(r"posting", re.I), "the job advertisement"),
    (re.compile(r"\bcv\b|resume|résumé", re.I), "the CV"),
    (re.compile(r"cover.?letter", re.I), "the cover letter"),
    (re.compile(r"answers", re.I), "form answers"),
]
READABLE = (".txt", ".md", ".html", ".htm")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__.strip().splitlines()[2].strip())
    src = os.path.abspath(sys.argv[1].rstrip("/"))
    if not os.path.isdir(src):
        sys.exit(f"not a directory: {src}")

    out_root = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "review-exports")
    dst = os.path.join(out_root, os.path.basename(src))
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)

    copied, skipped = [], []
    for name in sorted(os.listdir(src)):
        path = os.path.join(src, name)
        if not os.path.isfile(path):
            skipped.append((name, "not a file"))
            continue
        if name == "application.json":
            skipped.append((name, "internal configuration -- deliberately withheld"))
            continue
        why = next((w for rx, w in ALLOWED if rx.search(name)), None)
        if not why:
            skipped.append((name, "not one of the four reviewable kinds"))
            continue
        if not name.lower().endswith(READABLE):
            skipped.append((name, f"binary -- export text alongside it (pdftotext -layout '{name}' out.txt)"))
            continue
        shutil.copy2(path, os.path.join(dst, name))
        copied.append((name, why))

    if os.path.exists(TEMPLATE):
        shutil.copy2(TEMPLATE, os.path.join(dst, "OVERSIGHT.md"))
        copied.append(("OVERSIGHT.md", "the reviewer's instructions"))
    else:
        print(f"WARNING: {TEMPLATE} missing -- the reviewer will have no brief", file=sys.stderr)

    print(f"\nexport -> {dst}\n")
    for n, w in copied:
        print(f"  copied   {n}  ({w})")
    for n, w in skipped:
        print(f"  withheld {n}  ({w})")

    if not any(re.search(r"posting", n, re.I) for n, _ in copied):
        print("\n  WARNING: no posting found. The reviewer cannot check the documents against what the"
              "\n  employer asked for, which removes the most useful half of the review.")
    if not any(re.search(r"\bcv\b|resume", n, re.I) for n, _ in copied):
        print("\n  WARNING: no CV found in a readable format.")

    print(f"""
Open ONLY that folder in the other tool, and say:

    Read OVERSIGHT.md and follow it.

It sits outside the wiki, so there is nothing above it to wander into. Bring the
review back here; do not let the other tool edit anything.""")


if __name__ == "__main__":
    main()
