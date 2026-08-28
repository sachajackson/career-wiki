"""employers: the two lists, and why they are two.

The watch list is complete coverage of an employer rather than whatever they
syndicate. The avoid list stops the assess-every-role-immediately rule spending
effort on questions settled months ago.

Three cases here are ones the design was corrected on. A preferred employer can
contain a division the user will not work in -- in real use roughly a third of
one employer's local postings belonged to one, so a company-level filter would
have surfaced every one of them, every run, forever. A watch entry with no route
is not being watched, and saying otherwise is a lie the user cannot see. And a
role declined over a commute is not a principled exclusion: it can come back,
so it annotates rather than filters.
"""
import datetime, importlib.util, os, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "radar"))
import employers as EMP                                          # noqa: E402


def role(company="<Employer A>", title="Head of Delivery", body=""):
    return {"company": company, "title": title, "body": body}


class Names(unittest.TestCase):
    def test_legal_suffixes_are_not_identity(self):
        """A user writing the short form must not silently miss the long one."""
        self.assertEqual(EMP.norm("Acme Group plc"), EMP.norm("Acme"))
        self.assertEqual(EMP.norm("Beta Holdings Ltd."), EMP.norm("beta"))

    def test_matching_works_in_both_directions(self):
        """Listings write an employer as itself, its parent, and a division."""
        self.assertTrue(EMP._names_match("Acme", "Acme Financial Services"))
        self.assertTrue(EMP._names_match("Acme Financial Services", "Acme"))

    def test_a_short_name_does_not_match_inside_unrelated_ones(self):
        """Below the floor this starts hitting words inside other companies."""
        self.assertFalse(EMP._names_match("BT", "Bright Consulting"))
        self.assertFalse(EMP._names_match("", "Acme"))


    def test_a_squashed_name_matches_a_spaced_one(self):
        """THE DEFECT. norm() collapses whitespace but keeps it, so a two-word
        name never matched its one-word form.

        It matters because adapters label rows with whatever the SOURCE calls
        the employer, and an ATS tenant slug has no spaces in it. A real avoid
        entry naming a two-word employer silently failed against rows the
        adapter had labelled with the tenant slug -- the exclusion was
        configured, reported as configured, and filtered nothing."""
        self.assertTrue(EMP._names_match("Acme Financial", "acmefinancial"))
        self.assertTrue(EMP._names_match("acmefinancial", "Acme Financial"))
        self.assertTrue(EMP._names_match("Acme Financial", "AcmeFinancial Group"))

    def test_squashing_does_not_make_unrelated_names_match(self):
        """THE FALSE-POSITIVE CASE. Removing spaces creates new adjacencies,
        so the floor and the direction still have to hold."""
        self.assertFalse(EMP._names_match("BT", "Brighttelecom"))
        self.assertFalse(EMP._names_match("Acme", "Widgetcorp"))
        self.assertFalse(EMP._names_match("", "acme"))

    def test_a_division_exclusion_fires_against_a_tenant_slug(self):
        """End to end: the shape that actually failed on a real run."""
        emp = {"avoid": [{"employer": "Acme Financial", "divisions": ["Beta Systems"]}]}
        row = {"company": "acmefinancial",
               "title": "Technical Delivery Manager, Beta Systems, Vice President"}
        self.assertIsNotNone(EMP.excluded(row, emp))
        keep = {"company": "acmefinancial", "title": "Custody Services Vice President"}
        self.assertIsNone(EMP.excluded(keep, emp))


class Routing(unittest.TestCase):
    def test_each_route_lands_in_the_adapter_that_serves_it(self):
        cfg = {"queries": ["delivery"]}
        emp = {"watch": [
            {"employer": "A", "workday": {"host": "h", "tenant": "t", "site": "s"}},
            {"employer": "B2", "oracle": {"host": "h2", "site": "s2"}},
            {"employer": "B", "greenhouse": "btoken"},
            {"employer": "C", "lever": "cslug"},
            {"employer": "D", "query": "\"D\" delivery"}]}
        routed, unrouted = EMP.route(emp, cfg)
        self.assertEqual(routed, ["A", "B2", "B", "C", "D"])
        self.assertEqual(unrouted, [])
        self.assertEqual(cfg["workday"]["employers"], [{"host": "h", "tenant": "t", "site": "s"}])
        self.assertEqual(cfg["workday"]["names"], {"t": "A"})
        self.assertEqual(cfg["oracle"]["employers"], [{"host": "h2", "site": "s2"}])
        self.assertEqual(cfg["oracle"]["names"], {"s2": "B2"})
        self.assertEqual(cfg["greenhouse"]["boards"], ["btoken"])
        self.assertEqual(cfg["lever"]["companies"], ["cslug"])
        self.assertIn('"D" delivery', cfg["queries"])

    def test_an_entry_with_no_route_is_not_being_watched(self):
        """The failure this prevents is silent: the employer never appears."""
        cfg = {}
        routed, unrouted = EMP.route({"watch": [{"employer": "A", "why": "..."}]}, cfg)
        self.assertEqual((routed, unrouted), ([], ["A"]))

    def test_a_partial_oracle_entry_is_not_a_route(self):
        """host and site or nothing. One of two reaches nobody."""
        cfg = {}
        _, unrouted = EMP.route(
            {"watch": [{"employer": "A", "oracle": {"host": "h"}}]}, cfg)
        self.assertEqual(unrouted, ["A"])

    def test_a_partial_workday_entry_is_not_a_route(self):
        """host, tenant and site or nothing -- two of three fetches nothing."""
        cfg = {}
        _, unrouted = EMP.route(
            {"watch": [{"employer": "A", "workday": {"host": "h", "tenant": "t"}}]}, cfg)
        self.assertEqual(unrouted, ["A"])

    def test_an_employer_on_both_lists_is_reported(self):
        """Whichever list wins would be an accident of ordering."""
        emp = {"watch": [{"employer": "Acme Group"}], "avoid": [{"employer": "Acme"}]}
        self.assertEqual(EMP.contradictions(emp), ["Acme Group"])


class Avoiding(unittest.TestCase):
    def test_a_whole_employer_is_dropped_with_a_reason(self):
        emp = {"avoid": [{"employer": "<Employer A>", "reason": "r", "basis": "published"}]}
        why = EMP.excluded(role(), emp)
        self.assertIn("<Employer A>", why)
        self.assertIn("avoid list", why)

    def test_a_division_exclusion_spares_the_rest_of_the_employer(self):
        """A whole employer can be fine and one division inside it not."""
        emp = {"avoid": [{"employer": "<Employer A>", "divisions": ["<Division X>"]}]}
        self.assertIsNone(EMP.excluded(role(title="Head of Delivery"), emp))
        why = EMP.excluded(role(title="Head of Delivery, <Division X>, VP"), emp)
        self.assertIn("<Division X> division", why)

    def test_a_watched_employer_can_still_have_a_division_excluded(self):
        """The case that prompted this: a preferred employer, one bad division."""
        emp = {"watch": [{"employer": "<Employer A>", "avoid_divisions": ["<Division X>"]}]}
        self.assertIsNone(EMP.excluded(role(), emp))
        self.assertIn("<Division X>",
                      EMP.excluded(role(title="Engineer, <Division X>, VP"), emp))

    def test_an_unlisted_employer_passes(self):
        self.assertIsNone(EMP.excluded(role(company="<Employer Z>"),
                                       {"avoid": [{"employer": "<Employer A>"}]}))


class Sectors(unittest.TestCase):
    def test_it_matches_the_description_not_just_the_name(self):
        """The point of a category is catching employers never heard of."""
        emp = {"avoid_sectors": [{"sector": "<sector>", "match": ["<keyword>"]}]}
        self.assertIsNone(EMP.excluded_by_sector(role(), emp))
        why = EMP.excluded_by_sector(role(body="we build <keyword> platforms"), emp)
        self.assertIn("<sector>", why)

    def test_a_keyword_edged_with_punctuation_still_matches(self):
        """Found by a placeholder. `\\b` needs a word character to sit against.

        Anchoring a keyword that starts or ends with punctuation asks for a
        boundary that cannot exist, so it never matches -- and the user believes
        the sector is filtered when it is not.
        """
        emp = {"avoid_sectors": [{"sector": "<s>", "match": ["(betting)"]}]}
        self.assertIsNotNone(EMP.excluded_by_sector(role(body="we do (betting)"), emp))

    def test_it_matches_whole_words_only(self):
        """A substring match here quietly excludes unrelated employers."""
        emp = {"avoid_sectors": [{"sector": "<sector>", "match": ["arms"]}]}
        self.assertIsNone(EMP.excluded_by_sector(role(body="pharmaceuticals"), emp))
        self.assertIsNone(EMP.excluded_by_sector(role(body="alarms and sensors"), emp))
        self.assertIsNotNone(EMP.excluded_by_sector(role(body="small arms"), emp))


class Declined(unittest.TestCase):
    def test_it_returns_a_note_carrying_the_reason_and_the_date(self):
        emp = {"declined": [{"employer": "<Employer A>", "reason": "commute",
                             "on": "2026-01-04"}]}
        n = EMP.declined_note(role(), emp)
        self.assertIn("commute", n)
        self.assertIn("2026-01-04", n)

    def test_it_is_not_the_avoid_list(self):
        """A principled exclusion is permanent; this one can come back."""
        emp = {"declined": [{"employer": "<Employer A>", "reason": "timing"}]}
        self.assertIsNone(EMP.excluded(role(), emp))


class Housekeeping(unittest.TestCase):
    def test_an_old_exclusion_is_raised_for_review(self):
        """Companies change ownership, policy and management."""
        today = datetime.date(2026, 8, 25)
        emp = {"avoid": [{"employer": "<Old>", "since": "2023-01-01"},
                         {"employer": "<Recent>", "since": "2026-06-01"}]}
        out = EMP.stale(emp, months=24, today=today)
        self.assertEqual(len(out), 1)
        self.assertIn("<Old>", out[0])

    def test_an_undated_entry_is_raised_too_because_it_cannot_be_aged(self):
        out = EMP.stale({"avoid": [{"employer": "<Undated>"}]})
        self.assertIn("undated", out[0])

    def test_an_unreadable_date_is_raised_rather_than_treated_as_fresh(self):
        out = EMP.stale({"avoid": [{"employer": "<Bad>", "since": "last year"}]})
        self.assertIn("<Bad>", out[0])

    def test_an_exclusion_without_a_basis_cannot_be_rejudged(self):
        """'Published policy' and 'someone told me' are different claims."""
        emp = {"avoid": [{"employer": "<A>", "reason": "r", "basis": "published"},
                         {"employer": "<B>", "reason": "r"},
                         {"employer": "<C>", "basis": "published"}]}
        self.assertEqual(sorted(EMP.basis_gaps(emp)), ["<B>", "<C>"])


class TheFileIsOptional(unittest.TestCase):
    def test_a_missing_file_is_not_an_error(self):
        """Most users will never write one, and the radar must still run."""
        self.assertEqual(EMP.load("/nonexistent/employers.json"), {})

    def test_every_check_tolerates_an_empty_config(self):
        for fn in (EMP.excluded, EMP.excluded_by_sector, EMP.declined_note):
            self.assertIsNone(fn(role(), {}))
        self.assertEqual(EMP.stale({}), [])
        self.assertEqual(EMP.basis_gaps({}), [])
        self.assertEqual(EMP.contradictions({}), [])


if __name__ == "__main__":
    unittest.main()


class TheDivisionThatPostsUnderItsOwnName(unittest.TestCase):
    """🔴 An exclusion verified against one adapter, silently failing on another.

    A parent employer is watched and one of its divisions is excluded. The note
    recorded with that entry said every role in that division "names it in the
    title, which is where this filter looks" -- and that was true, measured on
    the parent's own Workday board, where the company field carries the PARENT's
    name and the division appears in the title.

    🔴 An aggregator labels the same roles with the DIVISION's own name. The
    employer name is checked first, so matching the parent against a company
    field that reads "<Division> Analytics" fails, the division check never runs
    at all, and 16 rows reached a shortlist. One was "Technical Delivery
    Manager", which matched the user's query list exactly and was precisely the
    role the exclusion existed to stop.

    🔴 The exclusion looked like it was working because it WAS working, on the
    source it was tested against.
    """

    CFG = {"avoid": [{"employer": "First Bank", "divisions": ["Halfling"],
                      "reason": "a stated reason"}]}

    def test_the_division_named_in_the_title_is_still_excluded(self):
        """The case that already worked, kept so the fix cannot break it."""
        why = EMP.excluded(
            {"company": "First Bank",
             "title": "Technical Delivery Manager, Halfling Analytics"}, self.CFG)
        self.assertTrue(why)
        self.assertIn("Halfling", why)

    def test_the_division_posting_under_its_own_name_is_excluded(self):
        """🔴 The bug. Sixteen of these reached a live shortlist."""
        why = EMP.excluded(
            {"company": "Halfling Analytics", "title": "Technical Delivery Manager"},
            self.CFG)
        self.assertTrue(why, "a division posting under its own name escaped the exclusion")
        self.assertIn("Halfling", why)

    def test_the_parent_employer_is_still_watched(self):
        """🔴 The false positive, and it matters more than the bug.

        The user is happy to work for First Bank and not for this one division.
        An exclusion that swallowed the parent would remove a watched employer's
        entire board -- 628 rows in one corpus -- and nothing would say so.
        """
        self.assertFalse(EMP.excluded(
            {"company": "First Bank", "title": "Technical Project Manager, AVP"}, self.CFG))

    def test_an_unrelated_employer_is_untouched(self):
        self.assertFalse(EMP.excluded(
            {"company": "Second Bank", "title": "Technical Delivery Manager"}, self.CFG))

    def test_a_whole_employer_exclusion_still_takes_everything(self):
        emp = {"avoid": [{"employer": "Widget Retail", "divisions": []}]}
        self.assertTrue(EMP.excluded(
            {"company": "Widget Retail", "title": "Director of Engineering"}, emp))


class TheWatchListHasTwoShapesAndBothMustWork(unittest.TestCase):
    """🔴 THE WATCH LIST WAS UNUSABLE IN BOTH DIRECTIONS AND NOBODY FOUND OUT,
    because it had always been empty.

        watch: ["Name"]        registry.py's own docstring, and the only shape
                               resolve() would read -- and it raised
                               AttributeError inside employers.excluded(),
                               which reads watch entries as dicts

        watch: [{...}]         the shape templates/settings/employers.example.json
                               ships, carrying the route and avoid_divisions --
                               and resolve() skipped every one of them, so the
                               config named employers and watched nobody

    🟢 Both are accepted now. The object is canonical because it is the only one
    that can carry a route and a division exclusion; a bare name is shorthand the
    registry fills in.
    """

    ROW = {"company": "First Bank", "title": "Technical Project Manager, AVP"}
    DIVISION = {"company": "First Bank", "title": "Delivery Manager, Halfling Analytics"}

    def test_a_bare_string_does_not_raise(self):
        self.assertIsNone(EMP.excluded(self.ROW, {"watch": ["First Bank"], "avoid": []}))

    def test_an_object_does_not_raise(self):
        self.assertIsNone(EMP.excluded(self.ROW, {"watch": [{"employer": "First Bank"}], "avoid": []}))

    def test_avoid_divisions_on_a_watch_entry_still_excludes(self):
        """🟢 The case this shape exists for: watch the parent, refuse one
        division. Putting the parent on the avoid list instead would report a
        contradiction and risk excluding the whole employer."""
        cfg = {"watch": [{"employer": "First Bank", "avoid_divisions": ["Halfling"]}], "avoid": []}
        self.assertIsNone(EMP.excluded(self.ROW, cfg))
        self.assertTrue(EMP.excluded(self.DIVISION, cfg))

    def test_a_comment_string_in_the_array_is_ignored(self):
        """People leave comments in JSON arrays. Neither reader may choke."""
        cfg = {"watch": ["_a note to self", "", "First Bank"], "avoid": []}
        self.assertIsNone(EMP.excluded(self.ROW, cfg))
        self.assertEqual([e["employer"] for e in EMP._watch_entries(cfg)], ["First Bank"])

    def test_contradictions_reads_both_shapes(self):
        """🔴 An employer on both lists means whichever won was an accident. That
        warning must not go quiet just because the entry is a string."""
        avoid = [{"employer": "First Bank", "divisions": []}]
        for watch in (["First Bank"], [{"employer": "First Bank"}]):
            self.assertEqual(EMP.contradictions({"watch": watch, "avoid": avoid}), ["First Bank"])


class ARouteCanComeFromTheRegistry(unittest.TestCase):
    """🔴 THE OUTPUT CONTRADICTED ITSELF, and the false half is the one the skill
    tells a reader to act on.

    `sources_check.py` printed, three lines apart:

        watchlist: 0 employer(s) routed, 2 with NO ROUTE: SS&C Technologies, State Street
        OK  workday  ... ssctech (343 open) ... statestreet (1384 open)

    Both were computed correctly and they disagree. `registry.resolve()` writes a
    route into the ADAPTER config and records the employer in that adapter's
    `names` map; it does not write it back into the watch entry, which is the
    only place `route()` looked. **The coverage was real and the warning false**
    — and `role-radar`'s own instruction is that "no route ... NOT watched" means
    say so and do not report coverage the run did not have.
    """

    ENTRY = {"employer": "First Bank"}

    def test_an_employer_resolved_by_the_registry_counts_as_routed(self):
        cfg = {"workday": {"employers": [{"host": "h", "tenant": "fb", "site": "s"}],
                           "names": {"fb": "First Bank"}}}
        routed, unrouted = EMP.route({"watch": [self.ENTRY]}, cfg)
        self.assertEqual((routed, unrouted), (["First Bank"], []))

    def test_an_inline_route_still_counts(self):
        """🟡 The original mechanism. Writing the route into employers.json must
        keep working — the registry is a convenience, not a replacement."""
        entry = {"employer": "First Bank", "workday": {"host": "h", "tenant": "fb", "site": "s"}}
        routed, unrouted = EMP.route({"watch": [entry]}, {})
        self.assertEqual((routed, unrouted), (["First Bank"], []))

    def test_an_employer_with_neither_is_still_reported(self):
        """🔴 The warning must survive. An employer on the list with no route
        anywhere is genuinely not being watched, and silence there would be the
        original failure this whole line exists to prevent."""
        routed, unrouted = EMP.route({"watch": [{"employer": "Nowhere Ltd"}]}, {})
        self.assertEqual((routed, unrouted), ([], ["Nowhere Ltd"]))

    def test_a_different_employers_registry_entry_does_not_count(self):
        """🟡 The false-positive direction: matching on presence in the names map
        must be by NAME, not by the map being non-empty."""
        cfg = {"workday": {"names": {"other": "Second Bank"}}}
        routed, unrouted = EMP.route({"watch": [self.ENTRY]}, cfg)
        self.assertEqual((routed, unrouted), ([], ["First Bank"]))
