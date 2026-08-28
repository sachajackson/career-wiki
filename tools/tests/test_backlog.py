"""BACKLOG.md must not lie about its own state.

This file's own audit sections say it twice: "a backlog that has drifted is
worse than a long one -- it sends work at problems that no longer exist and
leaves real ones looking handled". It was written down, audited twice, and drifted
again inside a single session:

  A fixed item was written as a NEW entry beside the old one, so Greenhouse
  yield appeared twice, once fixed and once not, 1,160 lines apart.

  An entry recorded a tool as built in its body while its heading still read
  as an open problem, so anything skimming headings saw a gap that was closed.

"Delete an item when it is done" is an instruction, and instructions in this
repo have a perfect record of failing. These are the two parts of it a machine
can check. Judgement -- whether an entry is ACCURATE -- is not testable, and is
not attempted here.
"""
import difflib, os, re, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKLOG = os.path.join(ROOT, "BACKLOG.md")

# Status decoration, so "X — FIXED" and "X" compare as the same subject.
DECORATION = re.compile(
    r"—.*$|--.*$|\b(fixed|built|removed|shipped|enforced|corrected|now\b.*|check built|"
    r"tool built|made non-numeric|prefilter fixed|and wired in)\b", re.I)
NOISE = re.compile(r"[^a-z0-9 ]+")


def sections(body):
    """Every '### ' heading with the text under it, up to the next one."""
    out, parts = [], re.split(r"^(### .*)$", body, flags=re.M)
    for i in range(1, len(parts), 2):
        out.append((parts[i][4:].strip(), parts[i + 1]))
    return out


# Continuation headings. These legitimately repeat under different entries --
# several fixed items keep their original write-up under one -- so they are not
# duplicate ITEMS and comparing them produces noise that gets the check ignored.
CONTINUATION = {
    "the original design", "the original entry", "the defect",
    "the defect it was built for", "the design", "the original write up",
}


def subject(heading):
    h = DECORATION.sub(" ", heading.lower())
    return " ".join(NOISE.sub(" ", h).split())


class NoTwoEntriesForOneThing(unittest.TestCase):
    """A fixed item edited into a new entry leaves the old one saying it is open.

    Greenhouse yield is low was written twice -- "PREFILTER FIXED" near the top
    and the untouched original near the bottom. Whichever a reader found first
    decided whether they thought there was work to do.
    """

    def test_no_two_headings_describe_the_same_item(self):
        subs = [(subject(h), h) for h, _ in sections(open(BACKLOG, encoding="utf-8").read())]
        subs = [(s, h) for s, h in subs
                if len(s.split()) >= 3 and s not in CONTINUATION]
        for i, (a, ha) in enumerate(subs):
            for b, hb in subs[i + 1:]:
                ratio = difflib.SequenceMatcher(None, a, b).ratio()
                self.assertLess(
                    ratio, 0.8,
                    f"these two headings describe the same item ({ratio:.0%} alike). "
                    f"Update the entry, do not add a second one:\n"
                    f"    {ha}\n    {hb}")


class AHeadingMustAgreeWithItsBody(unittest.TestCase):
    """An entry that records a fix in its body and reads as open in its heading.

    Nobody reads 1,900 lines. They skim headings, so the heading IS the entry
    for most purposes, and one that disagrees with its own body sends work at a
    problem that is already solved.
    """

    DONE_IN_BODY = re.compile(r"\*\*Status:\s*✅|^✅ \*\*(built|fixed|delivered)", re.M | re.I)
    OPEN_IN_BODY = re.compile(r"\*\*Status:[^\n]*\b(not built|not fixed|designed, not built)\b", re.I)

    def sections(self):
        """Items only. A continuation heading carries the parent entry's tail,
        so its 'body' is not its own and cannot be checked against it."""
        return [(h, b) for h, b in sections(open(BACKLOG, encoding="utf-8").read())
                if subject(h) not in CONTINUATION]

    def test_a_body_saying_done_needs_a_heading_saying_done(self):
        for heading, body in self.sections():
            if self.DONE_IN_BODY.search(body) and "✅" not in heading:
                self.fail(f"this entry records a fix in its body and reads as open in its "
                          f"heading — put ✅ in the heading:\n    ### {heading}")

    def test_a_heading_saying_done_must_not_have_an_open_body(self):
        for heading, body in self.sections():
            if "✅" in heading and self.OPEN_IN_BODY.search(body):
                self.fail(f"this heading claims done and its own status line says "
                          f"otherwise:\n    ### {heading}")


if __name__ == "__main__":
    unittest.main()


class TheBacklogIsFutureWorkOnly(unittest.TestCase):
    """🔴 The charter added 2026-08-28, made executable — because the two rules
    above are about a backlog that LIES, and this is about one that HOARDS.

    The file had reached 1,917 lines and about 500 of them were future work. The
    rest was finished work, functional specifications and settled lessons, all
    of it accumulating at roughly 250 lines a day for one banal reason: **a
    backlog is the file that happens to be open while the work is happening.**

    🔴 A lesson in a backlog reads as a task. A design reads as a proposal. And
    real outstanding items sit buried under both.

    🟢 The destinations exist now — `docs/SHIPPED.md`, `docs/DESIGN.md`,
    `docs/LESSONS.md` — so this is cheap to obey and was not before.

    🟡 Where a job is half done, the finished half moves and only the remainder
    stays. A stub POINTING at the record is fine; the record itself is not.
    """

    # A heading claiming completion. `docs/SHIPPED.md` is where these belong.
    DONE = re.compile(r"✅|\b(FIXED|BUILT|SHIPPED|DONE)\b")

    def headings(self):
        return [l for l in open(BACKLOG, encoding="utf-8").read().split("\n")
                if re.match(r"^#{2,3} ", l)]

    def test_no_heading_announces_completed_work(self):
        bad = [h for h in self.headings() if self.DONE.search(h)]
        self.assertEqual(bad, [], "a completed item is still in the backlog. Move the record to "
                                  "docs/SHIPPED.md and leave only what is outstanding: " + str(bad))

    def test_the_charter_names_where_the_other_kinds_go(self):
        """🔴 A rule with nowhere to put the thing is a rule that gets ignored.
        The file must tell a reader the destination, not just the prohibition."""
        text = open(BACKLOG, encoding="utf-8").read()
        for dest in ("docs/SHIPPED.md", "docs/DESIGN.md", "docs/LESSONS.md"):
            self.assertIn(dest, text, f"the charter does not name {dest}")

    def test_a_pointer_to_a_record_is_still_allowed(self):
        """🟡 The false-positive direction, and it matters: half-finished items
        must stay, and they need to say what was already done. Only HEADINGS are
        checked, so a body may freely reference the record."""
        body_mentions = [l for l in open(BACKLOG, encoding="utf-8").read().split("\n")
                         if "docs/SHIPPED.md" in l and not l.startswith("#")]
        self.assertTrue(body_mentions, "no entry points at its own record — expected at least one")
