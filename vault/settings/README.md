# settings/ — what the tools read

**Empty until you run `/career-init`.** It writes three files here from `templates/settings/`, and you
edit them from then on.

| File | What it holds | How often you touch it |
|---|---|---|
| `search.json` | Titles to search for, locations, which employers' boards to call | **Weekly.** This is the tuning surface |
| `employers.json` | Employers to watch, and employers to skip | Occasionally |
| `review.json` | Which model reviews your documents, and how | Rarely |

**They are three files rather than one because they are edited on three different rhythms.** A single
`config.json` means opening the file that holds your API-key preferences to add a job title, and a
weekly edit sitting in the same file as a set-once decision is how set-once decisions get changed by
accident.

## 🔴 `employers.json` is more sensitive than it looks

It names companies you will not work for, and usually why — a bad interview, something a friend told
you, a reputation you have heard about but cannot evidence. **Some of it is second-hand and some of it
would be awkward if the company read it.**

It lives here, it never ships, and it should not go into an oversight export. If you are sending your
vault to anyone, this is the file to look at first after `secrets/`.

## What does not go here

**Anything about you.** Settings are how the tools behave, not what they know. Your history, your
achievements, what you want from a role — those are wiki pages, because they need explanation,
provenance and dates, and a JSON file has nowhere to put any of that.
