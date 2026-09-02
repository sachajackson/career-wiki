"""quotes: does a line an assessment quotes actually appear in the posting?

🔴 ADVISORY, and not wired into doctor or pipeline. Against the live vault it
reports 28 of 56 pages, which is too high to gate on. These tests pin the
behaviour that IS settled, so the remaining tuning cannot silently undo it.
"""
import importlib.util, os, re, shutil, tempfile, unittest

def words(text):
    """Tokenised exactly as the tool does. A test that splits differently is
    testing its own tokeniser, which is how these two first failed."""
    return re.findall(r"[a-z0-9']+", text.lower())


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("quotes", os.path.join(ROOT, "tools", "quotes.py"))
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)


class TheExtraction(unittest.TestCase):

    def test_a_blockquote_quotation_is_a_claim_about_the_employer(self):
        """🔴 The tier that gates. A blockquote is this vault's convention for
        THIS IS WHAT THE POSTING SAYS, so a miss there is a claim that fails."""
        page = '> *"a requirement the posting actually states here"*\n'
        self.assertEqual(q.quotations(page),
                         [("claimed", "a requirement the posting actually states here")])

    def test_an_inline_quotation_is_advisory_not_a_claim(self):
        """🔴 An emphasised quote is used for four different things and only one
        is the employer: "the ceiling is disciplinary" is a finding of ours and is
        correctly absent from every advert. Reported, never gated on."""
        page = 'The pattern here is *"the ceiling is disciplinary, not hierarchical"* across six roles.'
        self.assertEqual(q.quotations(page)[0][0], "inline")

    def test_prose_containing_a_wiki_link_is_not_a_quotation(self):
        page = '> *"The same tier as [[NMBI Head of Digitalisation|NMBI]], which was turned down"*'
        self.assertEqual(q.quotations(page), [])

    def test_the_users_own_words_are_not_checked_against_a_job_advert(self):
        """A role page quotes Sacha as well as the posting, and his words are
        correctly not in the advert."""
        page = '> **Sacha said:** *"getting quite hands-on with building AI but not there yet"*\n'
        self.assertEqual(q.quotations(page), [])

    def test_an_ellipsis_splits_one_quotation_into_two_checkable_halves(self):
        page = '> *"the first requirement here… and a separate sentence entirely"*'
        self.assertEqual(len(q.quotations(page)), 2)

    def test_an_editorial_insertion_does_not_break_the_match(self):
        """🔴 Quoting an employer's typo faithfully with [sic] is correct
        practice, and it made the check fail — so quoting properly was the thing
        that broke it."""
        self.assertEqual(q.flatten('Object Oriented Programing [sic] skills'),
                         "object oriented programing skills")


class TheClassification(unittest.TestCase):

    def test_a_verbatim_quote_passes(self):
        body = words("we expect you to set safe-ai standards for agentic systems in production")
        self.assertEqual(q._classify("set safe-ai standards for agentic systems", body), "elided")

    def test_a_tightened_quote_is_elided_not_absent(self):
        """🔴 THE COMMONEST FAULT, and a similarity ratio cannot see it. Dropping
        three words barely moves a ratio and changes the string entirely, so 49
        pages read as fabricating when almost none were."""
        body = words("set safe-ai standards for agentic systems: prompt injection defenses")
        self.assertEqual(q._classify("set safe-ai standards prompt injection defenses", body),
                         "elided")

    def test_a_sentence_that_is_not_there_is_absent(self):
        body = words("we are looking for a delivery leader with governance experience")
        self.assertEqual(q._classify("fifty percent of capacity to active coding", body), "absent")

    def test_word_order_matters(self):
        """Same words, wrong order, is not the same sentence."""
        body = words("governance of delivery across four countries")
        self.assertEqual(q._classify("countries four across delivery of governance", body), "absent")


class TheFalseTruncationCaveat(unittest.TestCase):
    """🔴 Found on FIVE pages at once, every one of them false — including the two
    highest-scoring roles in the vault, where it is why LIFE, PAY and REQS were
    all left unanswered for a week. The posting stated every one of them, salary
    band included.

    An assessment that believes its source was cut STOPS LOOKING, and nothing
    ever revisits the caveat. That makes it worse than a misquote: a misquote is
    one wrong sentence, this suppresses whole dimensions.
    """

    PAGE = ("# A role\n\nIngested from https://www.linkedin.com/jobs/view/4456261092/\n\n"
            "🔴 **Scored from cached aggregator text** — aggregators truncate.\n")
    WHOLE = ("Source https://www.linkedin.com/jobs/view/4456261092/\n\nBody of the advert. "
             "Salary Range: 130 000,00 € - 230 000,00 €\nView our EEO Policy Statement.\n")
    CUT = ("Source https://www.linkedin.com/jobs/view/4456261092/\n\nBody of the advert, "
           "stopping mid-sen\n")

    def _postings(self, body):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        saved = q.paths.VAULT
        self.addCleanup(q.paths.use, saved)
        os.makedirs(os.path.join(d, "postings"))
        with open(os.path.join(d, "postings", "Northwind - A role.txt"), "w", encoding="utf-8") as fh:
            fh.write(body)
        q.paths.use(d)
        return q.load_postings()

    def test_a_claim_of_truncation_over_a_complete_archive_is_caught(self):
        self.assertTrue(q.false_truncation(self.PAGE, self._postings(self.WHOLE)))

    def test_a_genuinely_cut_archive_is_not_reported(self):
        """🟡 The caveat is right far more often than it is wrong. Reporting the
        true ones would bury the false ones."""
        self.assertFalse(q.false_truncation(self.PAGE, self._postings(self.CUT)))

    def test_a_page_that_says_nothing_about_its_source_is_not_reported(self):
        """Silence is the normal case. Flagging it would list every assessment."""
        self.assertFalse(q.false_truncation(
            "# A role\n\nhttps://www.linkedin.com/jobs/view/4456261092/\n",
            self._postings(self.WHOLE)))

    def test_the_check_does_not_fire_on_its_own_correction(self):
        """🔴 IT DID. Correcting a page means writing the word "truncated" on it —
        "the truncation caveat that stood here was wrong" — so all five pages
        still reported after three had been repaired. A check that cannot tell a
        claim from its retraction reports its own successes as failures."""
        fixed = ("# A role\n\nhttps://www.linkedin.com/jobs/view/4456261092/\n\n"
                 "🟢 **Checked 2026-08-27: the archived text is COMPLETE, not truncated.**\n")
        self.assertFalse(q.false_truncation(fixed, self._postings(self.WHOLE)))

    def test_a_retraction_that_wraps_across_lines_still_counts(self):
        """🔴 THE SECOND VERSION'S BUG. Markdown here wraps at ~100 characters, so
        the claim and its retraction land on different lines. Line-by-line, the
        first half fires and the second half is never seen. Paragraphs, not lines."""
        wrapped = ("# A role\n\nhttps://www.linkedin.com/jobs/view/4456261092/\n\n"
                   "🔴 **The truncation caveat that stood here was simply\nwrong.**\n")
        self.assertFalse(q.false_truncation(wrapped, self._postings(self.WHOLE)))


class TheArchiveThatWins(unittest.TestCase):
    """🔴 TWO ARCHIVES ROUTINELY SHARE ONE POSTING ID — the radar's clean capture
    and a raw page scrape of the same URL. load_postings keyed a dict by id with a
    plain assignment, so whichever glob returned LAST won, unsorted.

    For one role that was a scrape ending at LinkedIn's sign-in wall, which beat a
    complete capture ending at the employer's own footer. Everything downstream —
    quotation checking, truncation claims — then ran against the worse text.
    """

    def test_the_longer_body_wins_whatever_the_filename(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        saved = q.paths.VAULT
        self.addCleanup(q.paths.use, saved)
        os.makedirs(os.path.join(d, "postings"))
        src = "Source https://www.linkedin.com/jobs/view/4457340972/\n"
        # 'Zzz' sorts last and would win under a plain assignment.
        for name, body in [("Aaa - full capture.txt", src + "The whole advert. " * 40),
                           ("Zzz raw scrape.txt", src + "Sign in to view.")]:
            with open(os.path.join(d, "postings", name), "w", encoding="utf-8") as fh:
                fh.write(body)
        q.paths.use(d)
        (filename, body), = q.load_postings().values()
        self.assertEqual(filename, "Aaa - full capture.txt",
                         "the raw scrape won; the longer body must")
        self.assertGreater(len(body), 100)


class TheCompletenessMarkers(unittest.TestCase):
    """🔴 Widened twice, and both misses were real pages. A posting's end matter is
    legal boilerplate and every employer picks a different clause, so the pattern
    has to match the CATEGORY rather than the two footers that happened to be in
    front of me when it was written."""

    def test_the_footers_that_were_missed_are_matched_now(self):
        for tail in ["An employer who violates this law shall be subject to criminal penalties",
                     "please review our candidate AI-use guidelines",   # not a marker on its own
                     "employment without regard to race, colour or religion",
                     "if you need a reasonable accommodation",
                     "status as a protected veteran",
                     "our Total Rewards package"]:
            with self.subTest(tail=tail):
                hit = bool(q.COMPLETE.search(tail))
                if "AI-use guidelines" in tail:
                    self.assertFalse(hit, "this one is NOT end matter and must not match")
                else:
                    self.assertTrue(hit, f"end matter not recognised: {tail!r}")

    def test_mid_advert_prose_is_not_mistaken_for_an_ending(self):
        """🟡 The false-positive direction. If ordinary body text matched, every
        genuinely truncated archive would be reported as complete and the check
        would invert."""
        for body in ["You will lead a team of engineers building payment systems.",
                     "Requirements: 10 years of delivery leadership in financial services."]:
            self.assertIsNone(q.COMPLETE.search(body), body)


class APostingIdIsPerATS(unittest.TestCase):
    """🔴 `/job/` FOLLOWED BY ANYTHING PAIRED PAGES TO THE WRONG ARCHIVES.

    Oracle puts the requisition straight after /job/. Workday puts the LOCATION
    there, then the title, then the id:

        .../job/Ireland---Dublin/AI-Builder--Emerging-Talent-Senior-Manager_JR354003

    So every Workday URL yielded `Ireland---Dublin` as its posting id. A
    Salesforce AI role was compared against a Salesforce COMPLIANCE role and its
    quotations reported as misquotes — the quote was fine and the pairing was
    broken.

    🔴 And the damage was the opposite of what it looked like. The check reported
    **55 assessments checked** on those collisions; with correct ids it dropped to
    12, because most role pages carry no URL at all. **A gate reporting inflated
    coverage is worse than one reporting none** — the number is what stops anyone
    looking.
    """

    CASES = {
        "https://www.linkedin.com/jobs/view/4458039835/": "4458039835",
        "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/210773432": "210773432",
        "https://salesforce.wd12.myworkdayjobs.com/External_Career_Site/job/Ireland---Dublin/"
        "AI-Builder--Emerging-Talent-Senior-Manager_JR354003": "JR354003",
        "https://citi.wd5.myworkdayjobs.com/2/job/Dublin--Ireland/Director--Services-Ops_26987524": "26987524",
        "https://boards.greenhouse.io/acme?gh_jid=8094855": "8094855",
    }

    def test_each_ats_yields_its_own_requisition(self):
        for url, want in self.CASES.items():
            with self.subTest(url=url[:48]):
                self.assertEqual(q.ids_in(url), {want})

    def test_an_oracle_site_slug_is_not_mistaken_for_a_workday_id(self):
        """🔴 The second attempt at this fix matched `CX_1001` inside an Oracle
        URL and returned `1001`, because a single alternation picks the leftmost
        match and cannot see which host it is looking at. Hence per-host rules."""
        url = ("https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/"
               "CX_1001/job/210773432")
        self.assertNotIn("1001", q.ids_in(url))

    def test_a_location_segment_is_never_an_id(self):
        """The original bug, named so a later edit cannot reintroduce it."""
        url = ("https://salesforce.wd12.myworkdayjobs.com/External_Career_Site/job/"
               "Ireland---Dublin/Some-Role_JR111111")
        self.assertNotIn("Ireland---Dublin", q.ids_in(url))

    def test_a_repost_suffix_survives(self):
        """🟡 `_JR358522-1` is a repost. Requiring the id to end at the digits
        dropped it, and that archive then had no id at all."""
        url = ("https://salesforce.wd12.myworkdayjobs.com/External_Career_Site/job/"
               "Ireland---Dublin/Compliance-Delivery_JR358522-1")
        self.assertEqual(q.ids_in(url), {"JR358522-1"})

    def test_two_workday_roles_in_one_city_do_not_collide(self):
        """🔴 The consequence that did the damage: same city, different jobs."""
        a = "https://x.myworkdayjobs.com/s/job/Ireland---Dublin/Role-A_JR100001"
        b = "https://x.myworkdayjobs.com/s/job/Ireland---Dublin/Role-B_JR100002"
        self.assertNotEqual(q.ids_in(a), q.ids_in(b))
