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

    def test_a_blockquote_prefix_does_not_leak_into_the_quotation(self):
        """🔴 It did, and every multi-line quote failed: 69 of 71 pages."""
        page = '> *"the first line of a requirement\n> and the second line of it"*\n'
        self.assertEqual(q.quotations(page), ["the first line of a requirement and the second line of it"])

    def test_prose_containing_a_wiki_link_is_not_a_quotation(self):
        page = 'The same tier as "[[NMBI Head of Digitalisation|NMBI]]", which was turned down'
        self.assertEqual(q.quotations(page), [])

    def test_the_users_own_words_are_not_checked_against_a_job_advert(self):
        """A role page quotes Sacha as well as the posting, and his words are
        correctly not in the advert."""
        page = 'Sacha said he is "getting quite hands-on with building AI but not there yet"\n'
        self.assertEqual(q.quotations(page), [])

    def test_an_ellipsis_splits_one_quotation_into_two_checkable_halves(self):
        page = '*"the first requirement here… and a separate sentence entirely"*'
        self.assertEqual(len(q.quotations(page)), 2)


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
