"""cv_docx: the .docx route the vault's own policy requires.

🔴 THE GAP THIS CLOSES. `Application Mechanics` was REVERSED on 2026-08-26 to
"upload the .docx to an employer portal; send the .pdf to a human", and the
tooling made PDF only. The build-application skill was still telling the user the
opposite of their own settled decision -- "a PDF parses more predictably in an
ATS than a .docx built by a library". The tools were arguing with the vault.

And an agency recruiter needs .docx unconditionally: they reformat onto their own
letterhead and strip the direct contact details before forwarding.

🔴 NO DEPENDENCIES. The backlog entry asking for this warned that generating
.docx with a library is platform-specific and fails on somebody else's machine.
It was right, so this writes the ZIP-of-XML directly from the standard library.
"""
import importlib.util
import os
import re
import sys
import tempfile
import unittest
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("cv_docx", os.path.join(ROOT, "tools", "cv_docx.py"))
cv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cv)

TEMPLATE = os.path.join(ROOT, "templates", "cv.html")


def text_of(path):
    with zipfile.ZipFile(path) as z:
        doc = z.read("word/document.xml").decode()
    # unescaped, because that is what a parser sees -- "SS&amp;C" in the XML
    # is a correctly encoded "SS&C" on the page.
    import html
    raw = " ".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", doc))
    return html.unescape(raw), doc


class TheShippedTemplateConverts(unittest.TestCase):
    """The strongest version: the real template, not a fixture."""

    def setUp(self):
        with open(TEMPLATE, encoding="utf-8") as fh:
            self.paras = cv.convert(fh.read())
        self.tmp = tempfile.mkdtemp()
        self.out = cv.write_docx(self.paras, os.path.join(self.tmp, "cv.docx"))

    def test_every_section_of_the_template_survives(self):
        text, _ = text_of(self.out)
        for section in ("Profile", "Skills", "Experience", "Education"):
            self.assertIn(section, text, f"{section} was lost in conversion")

    def test_it_is_a_readable_zip_with_the_parts_word_requires(self):
        with zipfile.ZipFile(self.out) as z:
            names = z.namelist()
            self.assertIsNone(z.testzip(), "the archive is corrupt")
        for part in ("[Content_Types].xml", "_rels/.rels",
                     "word/document.xml", "word/styles.xml",
                     "word/_rels/document.xml.rels"):
            self.assertIn(part, names, f"{part} missing — Word will refuse the file")

    def test_none_of_the_things_that_break_ats_parsing_are_emitted(self):
        """🔴 The whole reason for writing this by hand rather than reaching for
        a library. Tables, text boxes and headers are what the ATS research says
        destroys parsing, and a library will happily produce all three."""
        _, doc = text_of(self.out)
        for bad, label in (("<w:tbl", "a table"), ("<w:drawing", "an image"),
                           ("<w:txbxContent", "a text box"), ("<w:pict", "a picture"),
                           ("w:hdrReference", "a header"), ("w:ftrReference", "a footer")):
            self.assertNotIn(bad, doc, f"emitted {label}")

    def test_contact_details_are_in_the_body(self):
        """🔴 Not in a header. A header is where contact details go to be lost --
        several ATS parsers drop that part entirely, and a CV that parses without
        an email address is a CV nobody can reply to."""
        text, _ = text_of(self.out)
        self.assertIn("email@example.com", text)

    def test_reading_order_matches_the_page(self):
        """A parser reads top to bottom. If the name arrives after the job
        history the document is scored as somebody else's."""
        text, _ = text_of(self.out)
        self.assertLess(text.index("FULL NAME"), text.index("Profile"))
        self.assertLess(text.index("Profile"), text.index("Experience"))
        self.assertLess(text.index("Experience"), text.index("Education"))

    def test_headings_use_real_word_styles(self):
        """An ATS finds section boundaries by style name. Bold body text tells it
        nothing at all."""
        _, doc = text_of(self.out)
        self.assertIn('w:val="Heading1"', doc)
        self.assertIn('w:val="Title"', doc)

    def test_bullets_are_literal_characters_not_word_numbering(self):
        """Numbering lives in a separate part that some parsers drop, taking the
        bullet text with it."""
        text, doc = text_of(self.out)
        self.assertIn("•", text)
        self.assertNotIn("<w:numPr", doc)


class TheConverter(unittest.TestCase):

    def test_markup_inside_a_bullet_is_flattened_not_dropped(self):
        paras = cv.convert("<body><ul><li>Cut <strong>40%</strong> of <em>toil</em></li></ul></body>")
        self.assertEqual(paras, [("• Cut 40% of toil", "ListParagraph")])

    def test_xml_special_characters_survive(self):
        """🔴 An ampersand in an employer name is common and an unescaped one
        makes the file unopenable. "SS&C" and "Johnson & Johnson" both occur."""
        out = os.path.join(tempfile.mkdtemp(), "x.docx")
        cv.write_docx([("SS&C Technologies <Europe>", None)], out)
        text, _ = text_of(out)
        self.assertIn("SS&C Technologies <Europe>", text)

    def test_empty_paragraphs_are_dropped(self):
        self.assertEqual(cv.convert("<body><p></p><p>  </p><p>Real</p></body>"),
                         [("Real", None)])

    def test_a_file_with_no_cv_in_it_converts_to_nothing(self):
        self.assertEqual(cv.convert("<html><body><div>x</div></body></html>"), [])

    def test_html_entities_are_decoded(self):
        self.assertEqual(cv.convert("<body><p>Risk &amp; Controls</p></body>"),
                         [("Risk & Controls", None)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
