"""The templates a fresh vault gets must contain what SCHEMA.md tells it to use.

An audit on 2026-08-25 found six of nine "documented rules" were not in force.
All nine were written where the backlog said they were -- which is what the
previous audit checked, and it passed everything. The failures were of a
different kind, and none of them is visible from reading the rule:

  A rule told the agent to keep a table on a page that had no such table.
  A rule told it to score a row that the table had no row for.
  A rule closed a vocabulary, and the template shipped a different, shorter one.

So these tests ask the second question instead: does the thing a rule prescribes
have somewhere to live, and do the two copies of a vocabulary agree?

SHIP THE EMPTY TABLE. A rule saying "keep a table of X on page Y" is not in
force until page Y has an empty table of X on it.
"""
import os, re, re, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLAUDE = os.path.join(ROOT, "SCHEMA.md")
FRAMEWORK = os.path.join(ROOT, "templates", "Role Scoring Framework.md")
RADAR_SKILL = os.path.join(ROOT, ".claude", "skills", "role-radar", "SKILL.md")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


class TheOutcomeVocabulary(unittest.TestCase):
    """One concept, two files. They drifted, and the user saw the broken one.

    SCHEMA.md closed this set specifically because "Rejected" was ambiguous
    between the employer turning someone down and the applicant choosing not to
    apply -- two rows four days apart had carried the same word for opposite
    facts. The template then shipped "submitted, not applied, closed or vetoed",
    dropping exactly the three values that fixed it, so a fresh vault's table
    could not express "the employer turned me down" at all. That is the number
    that says whether the level is right.
    """

    def statuses_in_claude(self):
        m = re.search(r"closed set:\s*\*\*(.+?)\.\*\*", read(CLAUDE), re.S)
        self.assertIsNotNone(m, "SCHEMA.md no longer states a closed set of outcomes")
        # The source is hard-wrapped markdown, so a value can straddle a newline.
        return {re.sub(r"\s+", " ", s).strip().strip("*` ") for s in m.group(1).split("·")}

    def statuses_in_template(self):
        body = read(FRAMEWORK)
        m = re.search(r"### Status — a closed set(.+?)(?=\n## |\Z)", body, re.S)
        self.assertIsNotNone(m, "the framework template has no Status section")
        return set(re.findall(r"`([A-Z][A-Za-z ]+)`", m.group(1)))

    def test_the_two_copies_agree_exactly(self):
        self.assertEqual(self.statuses_in_template(), self.statuses_in_claude())

    def test_the_ambiguous_pair_is_still_split(self):
        """The whole reason the set was closed. If these ever merge again the
        table stops answering the question it exists for."""
        s = self.statuses_in_claude()
        self.assertIn("Rejected by employer", s)
        self.assertIn("Not applied", s)
        self.assertNotIn("Rejected", s)


class TablesTheRulesPrescribe(unittest.TestCase):
    """Each of these was prescribed by a rule and existed nowhere."""

    def setUp(self):
        self.body = read(FRAMEWORK)

    def _table_after(self, heading_pattern):
        m = re.search(heading_pattern + r"(.+?)(?=\n## |\Z)", self.body, re.S)
        self.assertIsNotNone(m, f"no section matching {heading_pattern!r}")
        rows = [l for l in m.group(1).splitlines() if l.strip().startswith("|")]
        self.assertGreaterEqual(len(rows), 2, "a heading with no table under it")
        return rows[0]

    def test_the_standing_gaps_table_exists(self):
        """SCHEMA.md: "keep an explicit table, ON THE FRAMEWORK PAGE, of every
        capability found to be absent". There was no such table."""
        header = self._table_after(r"## .*Standing gaps")
        for column in ("gap", "Status", "Resolved", "Demanded", "substitute"):
            self.assertIn(column.lower(), header.lower(), column)

    def test_the_known_locations_table_exists(self):
        """"Store employment clusters once and reuse them" prescribed a store
        that did not exist, so every role re-derived it and got it wrong
        differently each time."""
        header = self._table_after(r"## .*Known locations")
        for column in ("Legs", "Door to door", "usable", "Verdict"):
            self.assertIn(column.lower(), header.lower(), column)

    def test_the_scoring_table_carries_the_baseline_and_the_internal_move(self):
        """Both were prescribed as rows of this table. Neither was in it.

        Without the baseline, top-of-scale means "best of what we found" rather
        than "no worse than today", and a downgrade scores 5/5. Without the
        internal move, every external role is compared against nothing.
        """
        m = re.search(r"## The table(.+?)(?=\n## |\Z)", self.body, re.S)
        self.assertIsNotNone(m)
        section = m.group(1)
        self.assertTrue(re.search(r"\|.*current job.*\|", section),
                        "the scoring table has no baseline row for the current job")
        self.assertTrue(re.search(r"\|.*[Ii]nternal move.*\|", section),
                        "the scoring table has no row for the internal move")

    def test_the_internal_move_is_prompted_for_not_just_mentioned(self):
        """SCHEMA.md: a user in a stable job will not raise this unprompted, and
        the employer's internal job site carries requisitions the public one
        does not. \W tolerates the markdown emphasis inside the phrase."""
        self.assertTrue(re.search(r"(?i)internal\W{0,3}(job site|board)", self.body),
                        "the template never points at the employer's internal job site")
        self.assertTrue(re.search(r"(?i)will not\s+raise it unprompted", self.body),
                        "the template does not say to prompt for the internal move")


class TheSuiteDoesNotClaimACount(unittest.TestCase):
    """A number in prose that nothing updates is a number that lies.

    The test count was written into README.md and CONTRIBUTING.md and was wrong
    in both -- 64 and 65, against a real figure past 300, with a third stale
    copy in BACKLOG.md. Nothing forces prose to move when code does. So the
    user-facing docs describe the suite's properties, which are stable, and not
    its size, which is not.

    BACKLOG.md is exempt: its counts are dated records of what a specific piece
    of work shipped with, not claims about the suite as it stands.
    """

    CLAIM = re.compile(r"\b\d+\s*(?:tests|checks)\b", re.I)

    def test_neither_readme_nor_contributing_states_a_test_count(self):
        for name in ("README.md", "CONTRIBUTING.md"):
            found = self.CLAIM.search(read(os.path.join(ROOT, name)))
            self.assertIsNone(
                found,
                f"{name} states a fixed test count ({found.group(0) if found else ''}) — "
                f"it will be wrong by the next commit. Describe the suite, not its size.")


class TheAggregatorRule(unittest.TestCase):
    """Two skills gave opposite instructions and the wrong one ran first.

    role-radar said "read the cached description, no refetch needed" and then
    "score properly". For an aggregator row that cache IS the truncated posting,
    and truncation is asymmetric: it strips qualifiers and alternatives, which
    are the parts that make a candidate MORE eligible. So the system
    systematically under-scored its user, invisibly.
    """

    def test_the_radar_skill_says_to_refetch_before_scoring(self):
        body = read(RADAR_SKILL)
        for pattern, what in [
                (r"(?i)employer'?s own posting before scoring", "refetch before scoring"),
                (r"(?i)aggregator'?s cached description is not the posting",
                 "the warning that the cache is not the posting")]:
            self.assertTrue(re.search(pattern, body), f"role-radar has lost: {what}")

    def test_it_says_which_sources_do_not_need_it(self):
        """Blanket "always refetch" would be ignored: board adapters already
        return the employer's own text, and a rule that is wrong half the time
        gets dropped entirely."""
        self.assertTrue(re.search(r"(?i)need no refetch", read(RADAR_SKILL)),
                        "role-radar no longer exempts employer-board sources")


if __name__ == "__main__":
    unittest.main()


class TheScaffoldListStaysComplete(unittest.TestCase):
    """🔴 A template nobody is told to copy is a template nobody copies.

    Found by walking career-init on a fresh clone: it told the agent to create
    `CV.md`, for which no template existed at all -- so the structure of the most
    important page in the vault was left to be invented each time. And once
    `Search Findings.md` was added as a template, nothing named it, so a new
    vault would never have got one.

    Both directions are checked, because both have now happened.
    """

    ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    SKILL = os.path.join(ROOT, ".claude", "skills", "career-init", "SKILL.md")
    TEMPLATES = os.path.join(ROOT, "templates")
    # Not wiki pages, so career-init has no reason to name them.
    NOT_SCAFFOLDED = {"vault-AGENTS.md", "OVERSIGHT.md", "sources-README.md"}

    def _skill(self):
        with open(self.SKILL, encoding="utf-8") as fh:
            return fh.read()

    def test_every_wiki_template_is_named_in_career_init(self):
        text = self._skill()
        for f in sorted(os.listdir(self.TEMPLATES)):
            if not f.endswith(".md") or f in self.NOT_SCAFFOLDED:
                continue
            self.assertIn(f, text,
                          f"templates/{f} exists but career-init never tells anyone to copy it, "
                          f"so a new vault will not have it")

    def test_every_page_career_init_names_has_a_template(self):
        text = self._skill()
        named = set(re.findall(r"`([A-Z][A-Za-z ]*\.md)`", text)) | {"index.md", "log.md"}
        for page in sorted(named):
            if page in ("SCHEMA.md", "AGENTS.md", "BACKLOG.md", "README.md", "CLAUDE.md"):
                continue
            self.assertTrue(os.path.exists(os.path.join(self.TEMPLATES, page)),
                            f"career-init tells the agent to create {page} and no template "
                            f"exists, so its structure gets invented every time")
