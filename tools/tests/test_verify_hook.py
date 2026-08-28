"""verify-artefact.sh: the only control here that gates everything and was checked
by nothing.

🔴 IT FIRES ON EVERY WRITE AND EDIT, and its whole design is that "the agent does
not get to decide whether to check its own work". `install-guard.sh`, sitting
beside it, had three behavioural tests. This had one assertion that the file
exists.

🔴 SO THE FIRST THING WRITING THESE FOUND WAS THAT IT HAD BEEN BROKEN FOR DAYS.
It passed `--wiki "$root/wiki"`, and that folder moved to `vault/wiki`. verify.py
printed `no wiki at ...` and exited 1, so the hook announced DETERMINISTIC LAYER
FAILED on every artefact write **while running no check at all** — 0 pages
indexed where there are 31, 0 figures where there are 399.

🔴 A control that fails for a reason unrelated to the document is worse than an
absent one: it trains whoever reads it to ignore the output. And the repo already
had the rule it broke — *paths come from `tools/lib/paths.py`, never from a string
literal*. The one place that broke it was a shell script nothing ran.
"""
import json
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOOK = os.path.join(ROOT, ".claude", "hooks", "verify-artefact.sh")

PAGE = """---
type: topic
section: career
verified: 2026-08-01
---

# Delivery

At **Acme** he ran **5 major releases a year**.
"""


class Hook:
    """A vault, an artefact and the hook, wired the way a session wires them."""

    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        self.vault = os.path.join(self.dir, "vault")
        os.makedirs(os.path.join(self.vault, "wiki"))
        self.write("vault/wiki/Delivery.md", PAGE)
        return self

    def write(self, rel, body):
        p = os.path.join(self.dir, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(body)
        return p

    def run(self, path, vault=True):
        env = dict(os.environ, CLAUDE_PROJECT_DIR=ROOT)
        if vault:
            env["CAREER_VAULT"] = self.vault
        payload = json.dumps({"tool_input": {"file_path": path}}) if path else "{}"
        return subprocess.run(["bash", HOOK], input=payload, env=env,
                              capture_output=True, text=True, timeout=120)

    def __exit__(self, *a):
        shutil.rmtree(self.dir, ignore_errors=True)


class ItSkipsWhatIsNotItsJob(unittest.TestCase):

    def test_no_file_path_at_all_exits_clean(self):
        with Hook() as h:
            self.assertEqual(h.run(None).returncode, 0)

    def test_an_ordinary_text_file_is_not_an_artefact(self):
        with Hook() as h:
            p = h.write("notes.txt", "just some notes\n")
            self.assertEqual(h.run(p).returncode, 0)

    def test_a_binary_artefact_is_left_to_the_pre_submit_gate(self):
        """DOCX and PDF are checked from extracted text at /pre-submit instead."""
        with Hook() as h:
            p = h.write("CV.docx", "not really a docx\n")
            self.assertEqual(h.run(p).returncode, 0)


class ItChecksLinksInAWikiPage(unittest.TestCase):
    """🔴 A link split across two lines renders as literal text and resolves to
    nothing. The rule against wrapping them failed three times in one session."""

    def test_a_wrapped_link_is_reported(self):
        with Hook() as h:
            p = h.write("vault/wiki/Note.md",
                        "# Note\n\nsee [[Delivery|the\ndelivery page]] for detail\n")
            r = h.run(p)
            self.assertEqual(r.returncode, 2)
            self.assertIn("BROKEN LINKS", r.stderr)

    def test_a_clean_page_passes(self):
        with Hook() as h:
            p = h.write("vault/wiki/Note.md", "# Note\n\nsee [[Delivery]] for detail\n")
            self.assertEqual(h.run(p).returncode, 0)


class ItRunsTheDeterministicLayer(unittest.TestCase):

    CLEAN = ("<html><body><p>Sacha — sacha@example.com</p>"
             "<p>At Acme he ran 5 major releases a year.</p></body></html>")

    def _app(self, h, artefact):
        h.write("app/application.json",
                json.dumps({"employer": "Acme", "past_employers": ["Acme"], "posting": "p.txt"}))
        return h.write(f"app/{artefact}", self.CLEAN)

    def test_an_artefact_with_no_application_json_says_so(self):
        with Hook() as h:
            p = h.write("loose/CV.html", self.CLEAN)
            r = h.run(p)
            self.assertEqual(r.returncode, 2)
            self.assertIn("no application.json", r.stderr)

    def test_a_fabricated_figure_is_caught(self):
        """🔴 The whole point of the layer: a number in the document and nowhere
        in the wiki."""
        with Hook() as h:
            self._app(h, "CV.html")
            p = h.write("app/CV.html", self.CLEAN.replace("5 major releases",
                                                          "9,412 major releases"))
            r = h.run(p)
            self.assertEqual(r.returncode, 2)
            self.assertIn("DETERMINISTIC LAYER FAILED", r.stderr)
            self.assertIn("9,412", r.stderr)


class TheWikiItReadsIsTheRealOne(unittest.TestCase):
    """🔴 THE REGRESSION. Asserted on BEHAVIOUR, not by grepping the script for a
    string: the hook must index the vault it is actually pointed at."""

    def test_it_indexes_the_vault_in_the_environment(self):
        with Hook() as h:
            h.write("app/application.json",
                    json.dumps({"employer": "Acme", "past_employers": ["Acme"],
                                "posting": "p.txt"}))
            p = h.write("app/CV.html", "<html><body><p>At Acme, 5 major releases a year.</p>"
                                       "</body></html>")
            out = h.run(p).stderr
            self.assertNotIn("no wiki at", out,
                             "the hook is pointed at a wiki folder that does not exist")
            self.assertNotIn("against 0 wiki pages", out,
                             "the hook indexed nothing, so no check actually ran")

    def test_it_does_not_hardcode_a_wiki_path(self):
        """🟡 Belt and braces on the specific literal, because the behavioural
        test above would still pass if a future edit hardcoded the CORRECT path —
        and it would break again the next time the vault moves."""
        with open(HOOK, encoding="utf-8") as fh:
            body = "\n".join(l for l in fh if not l.lstrip().startswith("#"))
        self.assertNotIn("--wiki", body,
                         "verify.py defaults --wiki to paths.WIKI; passing one re-hardcodes it")


if __name__ == "__main__":
    unittest.main(verbosity=2)
