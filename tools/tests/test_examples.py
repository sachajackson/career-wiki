"""examples/ ships, and that is correct -- but it has already been the user once.

WHY THIS FILE EXISTS

`examples/Worked Example.md` was written from the maintainer's own career. Same
profile, same seniority, same confirmed gap. It read as fictional because it was
never labelled as real, and it was caught by somebody reading it closely rather
than by anything mechanical.

That is the whole risk of this folder. It is system content -- it ships, it is
replaced by an update, and it is emphatically NOT under vault/, because a
gitignored example never reaches the person it exists to reassure. But it is the
one shipped folder whose content is a description of a person, which makes it
the one place a real person can be published without any rule appearing to break.
"""
import os, re, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXAMPLES = os.path.join(ROOT, "examples")
VAULT = os.path.join(ROOT, "vault")

FICTION = re.compile(r"\b(fiction|fictional|invented|not (a )?real)\b", re.I)
# Three digits or more, minus anything that is obviously a year. A shared figure
# is how the misattribution was found: the same number in two documents that
# should have had nothing in common.
FIGURE = re.compile(r"(?<![\d.,])\d[\d,]{2,}(?![\d.,])")
YEAR = re.compile(r"^(19|20)\d\d$")


def example_files():
    for base, _, files in os.walk(EXAMPLES):
        for f in files:
            if f.endswith(".md"):
                yield os.path.join(base, f)


def figures(text):
    return {m.group(0) for m in FIGURE.finditer(text) if not YEAR.match(m.group(0))}


class EveryExampleSaysItIsOne(unittest.TestCase):
    def test_each_file_declares_itself_fictional(self):
        """The label is what makes a close reader check. Without it, a real
        profile in this folder looks exactly like an invented one."""
        for path in example_files():
            with open(path, encoding="utf-8") as fh:
                head = fh.read(1500)
            self.assertTrue(FICTION.search(head),
                            f"{os.path.relpath(path, ROOT)} must say it is invented, near the top")

    def test_examples_are_not_hidden_in_the_vault(self):
        """Putting them under vault/ would look tidy and would mean they never
        ship -- an example nobody receives is an empty promise."""
        self.assertTrue(os.path.isdir(EXAMPLES))
        self.assertFalse(os.path.isdir(os.path.join(VAULT, "examples")))


class NoExampleOverlapsTheRealPerson(unittest.TestCase):
    """Cheap, and it catches the exact failure that happened. Skips on a clean
    clone, which is fine: the risk only exists on a machine that has a vault."""

    def setUp(self):
        if not os.path.isdir(os.path.join(VAULT, "wiki")):
            self.skipTest("no vault on this machine")
        self.vault_text = ""
        for base, _, files in os.walk(os.path.join(VAULT, "wiki")):
            for f in files:
                if f.endswith(".md"):
                    with open(os.path.join(base, f), encoding="utf-8", errors="ignore") as fh:
                        self.vault_text += fh.read()

    def test_no_figure_appears_in_both(self):
        shared = set()
        for path in example_files():
            with open(path, encoding="utf-8") as fh:
                shared |= {f for f in figures(fh.read()) if f in self.vault_text}
        self.assertEqual(sorted(shared), [],
                         f"a figure in examples/ also appears in the vault -- whose career is this? {shared}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
