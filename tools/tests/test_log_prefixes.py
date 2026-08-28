"""The log prefixes exist to be grepped, and one was missing for weeks.

🔴 `SCHEMA.md` lists **Migrate** among its operations, and every operation there
ends "update index.md, append to log.md". There was no `migrate` prefix. The
entry got written as `ingest`, which is the closest fit and is wrong — an ingest
is one source being read into the wiki; a migration is a hundred files sorted,
three deleted and one retyped. **The one operation that reshapes the whole vault
was the one that could not be found.**

🔴 And it was not alone. Building this found `market standards` in the same
position, logging as `research` with no prefix documented — so the drift was not
a one-off, it was the absence of anything comparing the lists.

🔴 THE FALSE-POSITIVE CASE, AND IT IS THE WHOLE DESIGN. A user's own log will
carry prefixes this system never wrote — `tools`, `framework`, `correction` all
appear in a real one. **A check that policed THEIR log would fire on every
hand-written line and be switched off the same day.** So this compares the two
SHIPPED lists to each other and to the documented operations, and never reads a
vault at all.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCHEMA = os.path.join(ROOT, "SCHEMA.md")
TEMPLATE = os.path.join(ROOT, "templates", "log.md")
PREFIX_LINE = re.compile(r"\*Prefixes:(.+?)\*", re.S)
# `**Ingest.**` at the start of a paragraph in the Operations section.
OPERATION = re.compile(r"^(?:🔴 |🟢 |🟡 )?\*\*([A-Z][A-Za-z ]{2,24})\.\*\*", re.M)
# Operations whose log prefix is deliberately not their name.
ALIASES = {"market standards": "research"}


def _read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def prefixes(text):
    m = PREFIX_LINE.search(text)
    return set(re.findall(r"`([a-z]+)`", m.group(1))) if m else set()


def operations():
    s = _read(SCHEMA)
    i = s.index("## Operations")
    j = s.index("\n## ", i + 5)
    return [o.strip().lower() for o in OPERATION.findall(s[i:j])]


class TheTwoShippedListsMustAgree(unittest.TestCase):

    def test_both_files_carry_a_prefix_list(self):
        self.assertTrue(prefixes(_read(SCHEMA)), "SCHEMA.md has no prefix list")
        self.assertTrue(prefixes(_read(TEMPLATE)), "templates/log.md has no prefix list")

    def test_they_are_identical(self):
        """🔴 Two files carrying the same list and nothing comparing them is how
        this drifted in the first place."""
        a, b = prefixes(_read(SCHEMA)), prefixes(_read(TEMPLATE))
        self.assertEqual(a, b, f"the lists disagree — only in SCHEMA: {a - b}; "
                               f"only in the template: {b - a}")


class EveryOperationCanBeFound(unittest.TestCase):

    def test_each_documented_operation_has_a_prefix(self):
        have = prefixes(_read(SCHEMA))
        missing = [op for op in operations()
                   if ALIASES.get(op, op) not in have]
        self.assertEqual(missing, [], "an operation the schema documents has no log prefix, so it "
                                      "leaves no greppable trace: " + str(missing))

    def test_migrate_specifically(self):
        """The instance that started this. Kept named, so a later tidy cannot
        remove it without the reason surfacing."""
        self.assertIn("migrate", prefixes(_read(SCHEMA)))
        self.assertIn("migrate", prefixes(_read(TEMPLATE)))

    def test_an_alias_is_declared_rather_than_guessed(self):
        """🟡 Not every operation's prefix is its name — `market standards` logs
        as `research`. That is fine, and it has to be WRITTEN DOWN, or the next
        person adds a `marketstandards` prefix nobody uses."""
        for op, prefix in ALIASES.items():
            self.assertIn(op, operations(), f"{op} is aliased but no longer an operation")
            self.assertIn(prefix, prefixes(_read(SCHEMA)))


class ItNeverReadsAVault(unittest.TestCase):
    """🔴 The false-positive case. A real log carries `tools`, `framework` and
    `correction` — none of them system prefixes, all of them legitimate."""

    def test_it_reads_only_shipped_files(self):
        """🟢 Asserted on the constants rather than by scanning this file for the
        word 'vault' — the first version did that and matched its own assertion."""
        for path in (SCHEMA, TEMPLATE):
            rel = os.path.relpath(path, ROOT)
            self.assertFalse(rel.startswith("vault"), rel)
            self.assertTrue(os.path.exists(path), rel)

    def test_a_users_own_prefix_is_not_a_failure(self):
        """A real log carries `tools`, `framework` and `correction`. The shipped
        list does not, and must not grow to accommodate them — they are that
        user's words for that user's work."""
        have = prefixes(_read(SCHEMA))
        for theirs in ("tools", "framework", "correction"):
            self.assertNotIn(theirs, have, f"{theirs!r} is one user's prefix, not a system one")


if __name__ == "__main__":
    unittest.main(verbosity=2)
