"""quotes: does a line an assessment quotes actually appear in the posting?

🔴 ADVISORY, and not wired into doctor or pipeline. Against the live vault it
reports 28 of 56 pages, which is too high to gate on. These tests pin the
behaviour that IS settled, so the remaining tuning cannot silently undo it.
"""
import importlib.util, os, re, unittest

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
