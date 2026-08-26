"""Where the user's things live. One file, so a move touches one file.

WHY THIS EXISTS

Before this, seven paths were pinned in doctor.py alone, four more in radar.py,
and others scattered through export_review.py and employers.py. Each computed a
path from its own location. Moving the user root meant finding all of them, and
the failure mode of missing one is silent: a tool that computes a path nobody
writes to reports "nothing here" rather than "I am looking in the wrong place".

THE BOUNDARY

  vault/    Everything about, belonging to, or specific to one person.
            Never shipped. Droppable: a user can zip it, carry it to another
            machine, and be running again.

  Everything else is the system, and can be replaced wholesale by an update.
            That is the whole point of the split -- an updater cannot exist
            while user data sits inside tools/.

FOUR KINDS INSIDE THE VAULT, AND THEY ARE NOT THE SAME

They all live under vault/ because they all belong to the user, but a tool that
bundles the vault has to know which is which:

  knowledge   wiki, roles, companies, postings, applications  -- carry always
  settings    what the code reads: search rules, employers, profile  -- carry
  secrets     an .env  -- NEVER put in a bundle, never commit, never email
  state       seen/raw/shortlist  -- regenerable, safe to delete, never carry

VAULT_ROOT can be overridden with the CAREER_VAULT environment variable, which
is how a user keeps their vault outside the repo entirely.
"""
import os

# tools/lib/paths.py -> tools/lib -> tools -> repo root
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VAULT = os.path.abspath(os.environ.get("CAREER_VAULT") or os.path.join(REPO, "vault"))


def _p(*parts):
    return os.path.join(VAULT, *parts)


# --- knowledge: carry it to another machine, or another tool entirely --------
SOURCES      = _p("sources")        # what the user drops in: CVs, exports, clippings
WIKI         = _p("wiki")           # about the user: CV, operating model, achievements
ROLES        = _p("roles")          # one page per assessed role
COMPANIES    = _p("companies")      # employer and division research
POSTINGS     = _p("postings")       # archived job descriptions -- the only durable copy
APPLICATIONS = _p("applications")   # one folder per application, including its interview pack
OVERSIGHT    = _p("oversight")      # export folders for the independent reviewer

# --- settings: what the code reads, split by who edits it and how often ------
SETTINGS   = _p("settings")
SEARCH     = os.path.join(SETTINGS, "search.json")     # queries, locations, adapters. Weekly
EMPLOYERS  = os.path.join(SETTINGS, "employers.json")  # watch and avoid. Occasional
PROFILE    = os.path.join(SETTINGS, "profile.json")    # floor, anchors, notice. Yearly
REVIEW     = os.path.join(SETTINGS, "review.json")     # which oversight provider. Rarely
SIGNAL     = os.path.join(SETTINGS, "signal.json")     # the tiering vocabulary. PERSONAL. Rarely

# --- secrets: an .env, and nothing else ------------------------------------
SECRETS = _p("secrets")
ENV     = os.path.join(SECRETS, ".env")

# --- state: regenerable. Deleting this directory must cost nothing ----------
STATE     = _p("state")
SEEN      = os.path.join(STATE, "seen.json")
RAW       = os.path.join(STATE, "raw.json")
SHORTLIST = os.path.join(STATE, "shortlist.md")

# --- migration: a drop zone, not a home -------------------------------------
MIGRATION = _p("migration")

# Directories the agent creates on demand. Not at init: ten empty folders is ten
# questions a new user has to answer for no reason.
LAZY = (SOURCES, WIKI, ROLES, COMPANIES, POSTINGS, APPLICATIONS, OVERSIGHT,
        SETTINGS, SECRETS, STATE, MIGRATION)

# What a bundle carries, and what it must not. Used by anything that exports,
# zips or syncs a vault.
CARRY    = (SOURCES, WIKI, ROLES, COMPANIES, POSTINGS, APPLICATIONS, SETTINGS)
NEVER    = (SECRETS, STATE)


def use(root):
    """Point every path at a different vault, and recompute.

    Module constants are read once at import, which makes them easy to read and
    impossible to relocate. This exists because the first thing that tried was a
    test, and a layout nothing can re-root is a layout nothing can test.
    """
    global VAULT, SOURCES, WIKI, ROLES, COMPANIES, POSTINGS, APPLICATIONS
    global OVERSIGHT, SETTINGS, SEARCH, EMPLOYERS, PROFILE, REVIEW, SIGNAL
    global SECRETS, ENV, STATE, SEEN, RAW, SHORTLIST, MIGRATION, LAZY, CARRY, NEVER
    VAULT = os.path.abspath(root)
    SOURCES, WIKI, ROLES = _p("sources"), _p("wiki"), _p("roles")
    COMPANIES, POSTINGS = _p("companies"), _p("postings")
    APPLICATIONS, OVERSIGHT = _p("applications"), _p("oversight")
    SETTINGS = _p("settings")
    SEARCH = os.path.join(SETTINGS, "search.json")
    EMPLOYERS = os.path.join(SETTINGS, "employers.json")
    PROFILE = os.path.join(SETTINGS, "profile.json")
    REVIEW = os.path.join(SETTINGS, "review.json")
    SIGNAL = os.path.join(SETTINGS, "signal.json")
    SECRETS = _p("secrets")
    ENV = os.path.join(SECRETS, ".env")
    STATE = _p("state")
    SEEN = os.path.join(STATE, "seen.json")
    RAW = os.path.join(STATE, "raw.json")
    SHORTLIST = os.path.join(STATE, "shortlist.md")
    MIGRATION = _p("migration")
    LAZY = (SOURCES, WIKI, ROLES, COMPANIES, POSTINGS, APPLICATIONS, OVERSIGHT,
            SETTINGS, SECRETS, STATE, MIGRATION)
    CARRY = (SOURCES, WIKI, ROLES, COMPANIES, POSTINGS, APPLICATIONS, SETTINGS)
    NEVER = (SECRETS, STATE)
    return VAULT


def ensure(path):
    """Create a vault directory when something first needs it."""
    os.makedirs(path, exist_ok=True)
    return path


def rel(path):
    """A path as the user would recognise it, for messages."""
    try:
        return os.path.relpath(path, REPO)
    except ValueError:
        return path


def load_env():
    """Read vault/secrets/.env into the environment, without overwriting.

    A key already in the environment wins: a user who exports it in their shell
    should not be silently overridden by a stale file.
    """
    if not os.path.exists(ENV):
        return 0
    n = 0
    with open(ENV, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip('"\'')
            if k and k not in os.environ:
                os.environ[k] = v
                n += 1
    return n
