#!/usr/bin/env python3
"""Turn a filled cv.html into an ATS-clean .docx.

    python3 tools/cv_docx.py path/to/CV.html            # writes CV.docx beside it
    python3 tools/cv_docx.py CV.html -o Somewhere.docx

WHY THIS EXISTS

`build-application` writes the CV as HTML and the user prints it to PDF. That is
the right default and is not being undone: it needs nothing installed and behaves
identically on every platform.

🔴 But the vault's own policy was REVERSED on 2026-08-26 -- "upload the .docx to
an employer portal; send the .pdf to a human" -- and the tooling still made PDF
only. Worse, the skill was telling the user the opposite of their own settled
decision: "a PDF parses more predictably in an ATS than a .docx built by a
library". **The tools were arguing with the vault.**

And an agency recruiter needs .docx unconditionally. They reformat a CV onto
their own letterhead and strip the direct contact details before forwarding it.
Handed a PDF they either retype it or send it on unchanged, and the second is
worse -- it hands the client a candidate's direct contact details, which is the
one thing the agency will not do, so it gets retyped badly instead.

🔴 NO DEPENDENCIES, BY DESIGN. The backlog entry that asked for this warned that
generating .docx "with a library or converting via an office suite is
platform-specific and fails on somebody else's machine". It is right. A .docx is
a ZIP of XML, so this writes one with `zipfile` and string templates from the
standard library and nothing else.

WHAT IT DELIBERATELY WILL NOT EMIT

Everything the ATS research says breaks parsing:

  - no tables, no text boxes, no columns
  - no headers or footers -- contact details go in the body or they are lost
  - no images, no graphics, no drawing objects
  - no fancy list numbering; bullets are paragraphs with a bullet style

🟡 The result looks plainer than the PDF. That is the point: the PDF is for a
human, this is for a parser.
"""
import argparse
import html as html_mod
import os
import re
import sys
import zipfile

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""

W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'

# 🔴 Real Word heading styles, not bold body text. An ATS uses the style name to
# find section boundaries; a visually-bold paragraph tells it nothing.
STYLES = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles {W}>
<w:style w:type="paragraph" w:styleId="Normal" w:default="1"><w:name w:val="Normal"/>
<w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="21"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/>
<w:pPr><w:spacing w:after="60"/></w:pPr>
<w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:sz w:val="34"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/>
<w:pPr><w:outlineLvl w:val="0"/><w:spacing w:before="220" w:after="60"/></w:pPr>
<w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:caps/><w:sz w:val="23"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/>
<w:pPr><w:outlineLvl w:val="1"/><w:spacing w:before="140" w:after="20"/></w:pPr>
<w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:sz w:val="21"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="ListParagraph"><w:name w:val="List Paragraph"/>
<w:pPr><w:ind w:left="360" w:hanging="180"/><w:spacing w:after="20"/></w:pPr></w:style>
</w:styles>"""


def esc(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def para(text, style=None):
    p = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    return f"<w:p>{p}<w:r><w:t xml:space=\"preserve\">{esc(text)}</w:t></w:r></w:p>"


def strip_tags(fragment):
    """Visible text of an HTML fragment, whitespace collapsed."""
    fragment = re.sub(r"<br\s*/?>", " ", fragment, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html_mod.unescape(text)).strip()


def convert(html):
    """cv.html -> a list of (text, style) paragraphs, in document order."""
    body = re.search(r"<body[^>]*>(.*)</body>", html, re.S | re.I)
    body = body.group(1) if body else html
    out = []
    # Everything the template can contain, matched in source order so the
    # document reads the way the page does.
    pattern = re.compile(
        r"<h1[^>]*>(?P<h1>.*?)</h1>"
        r"|<h2[^>]*>(?P<h2>.*?)</h2>"
        r"|<h3[^>]*>(?P<h3>.*?)</h3>"
        r"|<li[^>]*>(?P<li>.*?)</li>"
        r"|<div[^>]*class=\"[^\"]*\b(?P<cls>strap|contact|role|dates)\b[^\"]*\"[^>]*>(?P<div>.*?)</div>"
        r"|<p[^>]*>(?P<p>.*?)</p>", re.S | re.I)
    for m in pattern.finditer(body):
        if m.group("h1") is not None:
            out.append((strip_tags(m.group("h1")), "Title"))
        elif m.group("h2") is not None:
            out.append((strip_tags(m.group("h2")), "Heading1"))
        elif m.group("h3") is not None:
            out.append((strip_tags(m.group("h3")), "Heading2"))
        elif m.group("li") is not None:
            # 🔴 A literal bullet character, not Word list numbering. Numbering
            # lives in a separate part that some parsers drop entirely, taking
            # the text with it.
            out.append(("• " + strip_tags(m.group("li")), "ListParagraph"))
        elif m.group("div") is not None:
            cls = m.group("cls").lower()
            out.append((strip_tags(m.group("div")),
                        "Heading2" if cls == "role" else None))
        elif m.group("p") is not None:
            text = strip_tags(m.group("p"))
            if text:
                out.append((text, None))
    return [(t, s) for t, s in out if t]


def write_docx(paragraphs, path):
    body = "".join(para(t, s) for t, s in paragraphs)
    document = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f"<w:document {W}><w:body>{body}"
                f'<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
                f'<w:pgMar w:top="720" w:right="850" w:bottom="720" w:left="850"'
                f' w:header="0" w:footer="0" w:gutter="0"/></w:sectPr>'
                f"</w:body></w:document>")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/styles.xml", STYLES)
        z.writestr("word/document.xml", document)
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("html", help="a filled-in cv.html")
    ap.add_argument("-o", "--out", help="output path (default: alongside, .docx)")
    args = ap.parse_args()

    if not os.path.exists(args.html):
        print(f"  no such file: {args.html}")
        return 1
    with open(args.html, encoding="utf-8") as fh:
        paragraphs = convert(fh.read())
    if not paragraphs:
        print("  nothing to convert — is this a filled cv.html?")
        return 1
    out = args.out or os.path.splitext(args.html)[0] + ".docx"
    write_docx(paragraphs, out)
    words = sum(len(t.split()) for t, _ in paragraphs)
    print(f"  {out}\n  {len(paragraphs)} paragraph(s), {words} words. "
          f"No tables, headers, footers or images — parseable by design.\n"
          f"  🔴 Open it once before sending. This converts structure, not judgement.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
