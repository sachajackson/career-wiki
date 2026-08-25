#!/usr/bin/env python3
"""cv_lint — mechanical checks against the writing standard.

    python3 tools/cv_lint.py cv.txt
    pdftotext -layout cv.pdf - | python3 tools/cv_lint.py -

Checks only what can be checked mechanically: characters, vocabulary, sentence
shapes, cadence and round numbers. It cannot check the swap test, the stranger
test or the interview test -- those need judgement, and they are the ones that
decide whether the CV works. Run the audit prompt as well, in a fresh session.

Exit status is 1 if anything was flagged, so this can gate a build.
"""
import re, sys, unicodedata
from collections import Counter

BAD_CHARS = {
    "—": "em dash", "–": "en dash", "‘": "curly quote (left single)",
    "’": "curly quote (right single)", "“": "curly quote (left double)",
    "”": "curly quote (right double)", "…": "ellipsis character",
    " ": "non-breaking space", "​": "zero-width space",
    " ": "thin space", " ": "narrow no-break space",
    "→": "arrow", "▪": "decorative bullet", "‣": "decorative bullet",
    "◦": "decorative bullet", "●": "decorative bullet",
}
ALLOWED_NON_ASCII = set("€£")

BANNED = """spearheaded leveraged leverage delve delved pivotal intricate intricacies showcasing
showcased realm underscore underscored meticulous meticulously synergy synergies seamless
seamlessly cutting-edge best-in-class world-class tapestry testament fostering elevate
resonate paramount commendable unwavering holistic myriad plethora instrumental orchestrated
championed results-driven detail-oriented self-starter go-getter passionate dynamic
transformative game-changing groundbreaking thought-leadership value-add""".split()

HEDGES = ["helped to", "worked on", "was involved in", "contributed to", "responsible for",
          "duties included", "tasked with"]

TAILS = [", resulting in", ", driving", ", enabling", ", leading to", ", allowing",
         ", ensuring", ", providing", ", creating"]

US_SPELLING = [r"\b\w+ize\b", r"\b\w+ization\b", r"\bcolor\b", r"\bcenter\b",
               r"\banalyze\b", r"\bfavorite\b", r"\bbehavior\b", r"\borganization\b"]

# Third-person SINGULAR only, and the omission is the whole design.
#
# A CV written about its own subject leaks these when it is generated from a
# wiki that describes the person in the third person -- "the function he now
# leads", "six of his fifteen". Against the impersonal register these documents
# use ("Leads a function of fifteen") every one of them is a visible break, and
# it reads as a profile somebody else wrote. Six CVs carried seventeen of them
# and five went to employers before anybody noticed, because nothing looked at
# it: cv_lint called the worst of them clean.
#
# they/them/their are NOT here. In a CV they almost always point at an employer,
# a client or a team -- "the product owner sits inside the client, and works
# with them, their operations teams and their management" is correct English and
# correct content. Flagging those fires on nearly every real document, and a
# check that cries wolf is a check somebody switches off.
THIRD_PERSON = ["he", "him", "his", "himself", "she", "her", "hers", "herself"]


def bullets(text):
    return [l.strip().lstrip("-*• ").strip()
            for l in text.splitlines() if l.strip().startswith(("-", "*", "•"))]


def main():
    # A checker that passes when it checked nothing is worse than no checker.
    # This used to default to stdin and report "clean" on an empty pipe, which
    # is a green light nobody earned.
    if len(sys.argv) > 1:
        path = sys.argv[1]
    elif not sys.stdin.isatty():
        path = "-"
    else:
        sys.exit("cv_lint: give me a file, or pipe text in.\n"
                 "    python3 tools/cv_lint.py cv.txt\n"
                 "    pdftotext -layout cv.pdf - | python3 tools/cv_lint.py -")
    text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    if not text.strip():
        sys.exit(f"cv_lint: {'stdin' if path == '-' else path} is empty. "
                 "Nothing was checked, so nothing is clean.")
    lines = text.splitlines()
    findings = []

    # 1. characters
    for n, line in enumerate(lines, 1):
        for ch in line:
            if ch in BAD_CHARS:
                findings.append(f"L{n}: {BAD_CHARS[ch]} ({ch!r})")
            elif ord(ch) > 127 and ch not in ALLOWED_NON_ASCII and not unicodedata.combining(ch):
                if unicodedata.category(ch) not in ("Ll", "Lu"):   # accented letters are fine
                    findings.append(f"L{n}: non-ascii {ch!r} ({unicodedata.name(ch, '?')})")

    low = text.lower()
    # 2. vocabulary
    for w in BANNED:
        for m in re.finditer(r"\b" + re.escape(w) + r"\b", low):
            findings.append(f"banned word: {w!r} at offset {m.start()}")
    for h in HEDGES:
        if h in low:
            findings.append(f"hedge: {h!r}")

    # 3. sentence shapes
    for t in TAILS:
        for m in re.finditer(re.escape(t), low):
            findings.append(f"participial tail: {t!r} at offset {m.start()}")
    if re.search(r"not just .{1,40}? but", low) or re.search(r"it'?s not .{1,30}?, it'?s", low):
        findings.append("banned shape: 'not just X but Y'")

    # 4. round numbers
    for m in re.finditer(r"\b(\d+)\s?%", text):
        if int(m.group(1)) % 5 == 0:
            findings.append(f"round-number tell: {m.group(0)} (a real figure is more convincing)")

    # 5. US spelling
    for rx in US_SPELLING:
        for m in re.finditer(rx, low):
            if m.group(0) not in ("size", "prize", "seize"):
                findings.append(f"US spelling: {m.group(0)!r}")

    # 6. third person -- the register leak
    for n, line in enumerate(lines, 1):
        for w in THIRD_PERSON:
            for m in re.finditer(r"\b" + w + r"\b", line, re.I):
                findings.append(
                    f"L{n}: THIRD PERSON {m.group(0)!r} -- a CV about its own subject "
                    f"should not name him or her: {line.strip()[:70]!r}")

    # 7. cadence
    bs = bullets(text)
    stats = ""
    if len(bs) >= 4:
        counts = [len(b.split()) for b in bs]
        mean = sum(counts) / len(counts)
        sd = (sum((c - mean) ** 2 for c in counts) / len(counts)) ** 0.5
        stats = (f"bullets={len(bs)} min={min(counts)} max={max(counts)} "
                 f"mean={mean:.1f} sd={sd:.1f}")
        if sd < 4:
            findings.append(f"UNIFORM CADENCE: {stats} -- sd under 4 reads as generated")
        openers = Counter(b.split()[0].lower() for b in bs if b.split())
        if openers:                      # all-empty bullets used to crash here
            top, n = openers.most_common(1)[0]
            if n / len(bs) > 0.6:
                findings.append(f"uniform openings: {n}/{len(bs)} bullets start with {top!r}")

    # Two spelling patterns can match the same word, so the same fact was
    # reported twice. Dedupe while keeping order.
    seen, unique = set(), []
    for f in findings:
        if f not in seen:
            seen.add(f); unique.append(f)
    findings = unique

    print(f"cv_lint: {len(findings)} finding(s)" + (f" | {stats}" if stats else ""))
    for f in findings:
        print("  " + f)
    if not findings:
        print("  clean on the mechanical checks.")
    print("\nNot checked here, and they matter more: the swap test, the stranger test,\n"
          "the interview test, and whether every number sits on the right role.")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
