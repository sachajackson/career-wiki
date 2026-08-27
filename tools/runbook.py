#!/usr/bin/env python3
"""The ordered steps of every sequence in this system, in one place.

    python3 tools/runbook.py                 # list the sequences
    python3 tools/runbook.py radar           # the steps, in order

WHY THIS EXISTS

Skill files are prose, and prose has no order. `role-radar/SKILL.md` is 323 lines
across eighteen sections; its only sequence was a five-item list two thirds of the
way down. The `role-triage` delegation is named twice in that file and went unused
for the entire life of the repo, because an agent reading prose picks up whatever
it happens to land on.

🔴 A SEQUENCE IS NOT A LIST OF WARNINGS. Every step here carries a command and one
line on what goes wrong when it is skipped -- and every skipped step named below
was skipped for real, once, at a cost.

🔴 WHAT A RUNBOOK CANNOT DO, stated plainly rather than hoped away: it is still
READ, so it is a guide and not a sensor. Printing an order does not enforce one.

🟢 Two things do enforce it, and they are where the real guarantee lives:

  PRECONDITIONS   `batch.py --open` REFUSES on a stale corpus, because opening a
                  batch is step 3 and cannot precede step 1. A refusal is not a
                  warning -- a warning is a thing you scroll past.
  AFTER THE FACT  `pipeline.py` recomputes every stage from the vault, so a step
                  skipped in the moment still surfaces before the work is called
                  finished.

**Between them: the order is suggested, the preconditions are enforced, and the
outcome is verified. Only the middle step of a sequence can still be skipped
silently, and that is the honest limit.**
"""
import argparse
import sys

# (step, command or artefact, what goes wrong without it)
RADAR = [
    ("sources answer",
     "python3 tools/radar/sources_check.py",
     "A silent run and a quiet market look identical. '0 usable' means it cannot speak."),
    ("sweep or window",
     "python3 tools/radar/radar.py --all-open      (or --days 7)",
     "--all-open every 7 days for the backlog, --days 7 for freshness. Not the same run."),
    ("read the header, not the command you typed",
     "head -3 vault/state/shortlist.md",
     "Three wordings mean three different things; one says the window applied to nothing."),
    ("open a batch from the SHORTLIST",
     "python3 tools/batch.py --open <slug> --employer <name>",
     "🔴 Never from raw.json — that is the corpus BEFORE the location filter."),
    ("delegate the reading",
     "role-triage agent, several in parallel above ~8 roles",
     "🔴 Standing rule. Job adverts are the bulkiest thing that can enter a session."),
    ("employer's own posting before scoring an aggregator row",
     "python3 tools/radar/refresh.py <archived posting>",
     "Aggregators cut the qualifiers that make a candidate MORE eligible."),
    ("score, and file in the same turn",
     "page + scoring-table row + posting URL",
     "🔴 All three, or the radar re-surfaces it and the work is done twice."),
    ("archive the posting text",
     "vault/postings/<Employer> - <Title>.txt",
     "raw.json is overwritten every run. The archive is the only durable copy."),
    ("log it",
     "append to vault/wiki/log.md",
     "An assessment that exists only in a reply gets re-derived next week."),
    ("verify the batch came back",
     "python3 tools/batch.py --status <slug> && python3 tools/pipeline.py",
     "A delegation nobody verifies is the same failure one level up."),
]

APPLICATION = [
    ("confirm the posting is still open",
     "python3 tools/radar/refresh.py <archived posting>",
     "One role closed within 26 hours of being found. An evening spent on a dead req is gone."),
    ("read the employer's own posting, not the aggregator's",
     "the employer's careers page",
     "A truncation once created a capability gap that stood for three days and did not exist."),
    ("check the market standard for the artefact",
     "vault/wiki/CV Layout and ATS Standards.md",
     "Length, structure and file format change by country and level. Guessing is how a CV gets binned."),
    ("write the CV as HTML",
     "templates/cv.html",
     "Needs nothing installed and behaves identically everywhere."),
    ("produce the .docx as well",
     "python3 tools/cv_docx.py <the filled CV>.html",
     "🔴 .docx is the portal default and mandatory for an agency. PDF-only cannot serve one."),
    ("run the deterministic layer before anything leaves",
     "python3 tools/cv_lint.py … && python3 tools/verify.py … && python3 tools/known.py …",
     "🔴 Catches a fabricated figure and a real achievement attached to the wrong job."),
    ("record the submission WITH ITS DATE",
     "status cell: `Submitted YYYY-MM-DD`",
     "🔴 Without the date nothing can age it, so it is never chased however long it goes unanswered."),
    ("log it",
     "append to vault/wiki/log.md",
     "The record of what was sent, and when, is the only thing that survives."),
]

OUTCOME = [
    ("check what is owed",
     "python3 tools/outcomes.py",
     "Nothing in the system happens when an employer replies, or fails to."),
    ("use the closed vocabulary",
     "Submitted · Rejected by employer · Withdrew · Declined · Closed · Vetoed · Not applied",
     "🔴 'Rejected' meaning both directions makes the table unable to say who turned whom down."),
    ("record silence as an outcome after 21 days",
     "`no response`",
     "A blank field looks unasked rather than unanswered."),
    ("put the reason on the role page, not only in the table",
     "vault/roles/<role>.md",
     "A rejection with a reason is worth more than a silent success."),
    ("log it",
     "append to vault/wiki/log.md",
     "Patterns only appear across several outcomes, and only if each one was written down."),
]

UPDATE = [
    ("pull",
     "git pull",
     "The vault is gitignored, so an update replaces the system and cannot touch it."),
    ("what the system now reads that this vault has not got",
     "python3 tools/settings_drift.py",
     "🔴 An update can require a settings file it has no way to deliver, and the failure is silent."),
    ("what the page templates gained",
     "python3 tools/template_drift.py",
     "The tool moves on and the vault does not."),
    ("what is configured and what will quietly do nothing",
     "python3 tools/doctor.py",
     "🔴 PLACEHOLDER is the verdict that matters: an unedited example looks configured."),
    ("run the suite",
     "python3 tools/tests/run.py",
     "If these fail, do not ship a document."),
]

INIT = [
    ("stop if the vault already has pages",
     "ls vault/wiki/",
     "🔴 This skill scaffolds over whatever is there. On a populated vault, run /career-migrate instead."),
    ("read the sources, then say what you found — BEFORE writing anything",
     "vault/sources/",
     "🔴 And FILE the findings. Five assessments once existed only in a reply and were re-derived weeks later."),
    ("place vault/AGENTS.md first, unedited",
     "cp templates/vault-AGENTS.md vault/AGENTS.md",
     "It is the user's own file and an update never touches it. Do not fill it in from the sources."),
    ("scaffold the wiki from templates/",
     "index · log · Career · Operating Model · CV · Standing Answers · Role Scoring Framework · Search Findings",
     "A template nobody is told to copy is a template nobody copies."),
    ("interview round 1, then file the answers",
     "/interview",
     "Do not stack rounds. Unfiled answers are answers you will ask for twice."),
    ("elicit the anchors, and pressure-test them",
     "Schein's career anchors, then 'what would you have said three years ago?'",
     "Everything downstream depends on this and none of it can be inferred from a CV."),
    ("capture the baseline",
     "days in an office now · commute · notice · unvested equity · service · exposure",
     "🔴 Every score is measured against it. Without it the framework reports 'best found' as 'best available'."),
    ("build the scoring framework from what they just said",
     "templates/Role Scoring Framework.md",
     "Their anchors become the two lifestyle/security dimensions; their floor becomes PAY."),
    ("configure what the tools read — ASK, never invent",
     "search.json · signal.json · profile.json · employers.json · review.json",
     "🔴 Every one fails silently. A radar that finds nothing looks exactly like a quiet market."),
    ("start the standing answers",
     "right to work · notice period · why are you leaving",
     "Knockout questions on every form; a careless answer is a rejection nobody reviews."),
    ("close the loop, then run doctor",
     "python3 tools/doctor.py",
     "🔴 PLACEHOLDER is the verdict that matters. OPTIONAL is not a fault."),
]

MIGRATE = [
    ("ask what else is in that folder",
     "before anything is copied",
     "The first real migration carried 118 files of an unrelated project into the drop zone."),
    ("report, do not apply",
     "python3 tools/migrate.py",
     "They know what their files are and you do not. A wrong guess is cheap to correct here only."),
    ("apply, then repair links — in that order",
     "python3 tools/migrate.py --apply && python3 tools/wikilinks.py --fix",
     "Links to refused files resolve to nothing until they are repointed."),
    ("name every leftover",
     "whatever is still in migration/",
     "🔴 A file quietly removed from a drop zone looks exactly like a file that was dealt with."),
    ("split any old instruction file",
     "conventions → SCHEMA.md · anything about the person → vault/AGENTS.md",
     "🔴 The highest-value step in the whole migration, and the easiest to skip."),
    ("reconcile the frontmatter",
     "check vault/roles/ is not empty",
     "In the first migration every role page was typed 'source' and forty assessments landed in wiki/."),
    ("give them a log and an index if they did not bring one",
     "templates/log.md · templates/index.md",
     "Every operation ends 'update index, append to log'. Without them the record is silently not kept."),
    ("extract settings, never invent them",
     "vault/settings/",
     "🔴 An invented geography produces a filter that matches nothing and reports a quiet week."),
    ("close with doctor, then stop",
     "python3 tools/doctor.py",
     "🔴 Do not offer to write a CV. The right next step is /career-lint."),
]

BOOKS = {"radar": ("A radar run", RADAR),
         "init": ("Setting up a new vault", INIT),
         "migrate": ("Migrating an existing vault", MIGRATE),
         "application": ("Building and sending an application", APPLICATION),
         "outcome": ("Recording what came back", OUTCOME),
         "update": ("Taking an update", UPDATE)}


def render(name):
    title, steps = BOOKS[name]
    out = ["", f"  {title}, in order", ""]
    for i, (step, cmd, why) in enumerate(steps):
        out += [f"  {i}  {step}", f"      $ {cmd}", f"      {why}", ""]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("book", nargs="?", choices=sorted(BOOKS))
    args = ap.parse_args()
    if not args.book:
        print("\n  Sequences in this system:\n")
        for k, (title, steps) in sorted(BOOKS.items()):
            print(f"    {k:14} {len(steps):2d} steps   {title}")
        print("\n  python3 tools/runbook.py <name>\n")
        return 0
    print(render(args.book))
    return 0


if __name__ == "__main__":
    sys.exit(main())
