> **Part of [Career Wiki](README.md).** Getting it running, and the first hour after that.

# Installing it

**If you have never used a terminal, this section is for you.** About fifteen minutes.

### 1. Get an Anthropic account

Sign up at [claude.ai](https://claude.ai). A paid plan or API credit is needed — this is not free to run,
and a full init plus a few applications uses a meaningful amount of usage.

### 2. Install Claude Code

Claude Code is the agent that reads and writes the files. **There are two ways to run it, and the desktop
app is the easier one if you are not comfortable in a terminal.** Both use the same engine and both work
identically with this repo.

The authoritative instructions, which stay correct if anything below changes, are at
**[code.claude.com/docs](https://code.claude.com/docs)**.

#### Option A — the desktop app (recommended if you are not technical)

Download and install:

- **[macOS](https://claude.ai/api/desktop/darwin/universal/dmg/latest/redirect)** — universal build,
  Intel and Apple Silicon
- **[Windows](https://claude.ai/api/desktop/win32/x64/setup/latest/redirect)** — x64. **Install
  [Git for Windows](https://git-scm.com/downloads/win) first**, then restart the app
- **Linux** — apt or .deb, see [the Linux guide](https://code.claude.com/docs/en/desktop-linux)

Then launch Claude, sign in, and **click the `Code` tab**.

> 🔴 **The `Code` tab, not `Chat`.** The desktop app has three tabs — Chat, Cowork and Code. Only **Code**
> can read your files and run the tools this repo needs. If you are typing into the ordinary chat window,
> none of this will work.

#### Option B — the terminal

**macOS or Linux** — open Terminal (on a Mac: press Command+Space, type "Terminal", press Enter) and
paste:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows** — open PowerShell and paste:

```powershell
irm https://claude.ai/install.ps1 | iex
```

**You can use both**, on the same folder, at the same time. They keep separate conversation histories but
share the same `SCHEMA.md` and the same wiki. To move a terminal session into the desktop app, type
`/desktop`.

### 3. Check you have Python

The job-search tool needs Python 3. macOS and most Linux systems already have it:

```bash
python3 --version
```

If that prints a version number you are fine. If it says "command not found", install it from
[python.org/downloads](https://www.python.org/downloads/). **On Windows, tick "Add Python to PATH"** in
the installer — it is easy to miss and nothing works without it.

### 4. Get this repo

**If you use git:**

```bash
git clone <this-repo-url> career-wiki
cd career-wiki
```

**If you do not:** click the green **Code** button on the GitHub page, choose **Download ZIP**, unzip it
somewhere sensible such as your Documents folder, and rename the folder to `career-wiki`. Then, in your
terminal:

```bash
cd ~/Documents/career-wiki
```

### 5. Add your CV

Copy your CV into **`vault/sources/`** inside `career-wiki`. Dragging and dropping is fine.

**It does not need tidying up first.** A messy CV is more useful than a polished one, because the gaps are
informative. If you can also export your LinkedIn profile and drop that in, do — the two disagree
surprisingly often, and every disagreement is worth knowing about.

**If you have a pile of other material and no idea what is worth keeping**, put all of it in
`vault/migration/` instead and say so when you start. The agent reads it, files what it recognises, and
tells you what it could not place. You should not have to learn a folder structure before you can begin.

🔴 **`vault/` is the only folder that is yours, and none of it is ever uploaded or committed.** Everything
else in this repo is the system, which means an update can replace all of it without touching a word you
wrote. There is a `README.md` in each folder explaining what belongs there.

### 6. Start

**In the desktop app:** open the `Code` tab, and before typing anything set the two things that matter in
the prompt area:

| Setting | Choose |
|---|---|
| **Environment** | **Local** — it needs to reach files on your own machine |
| **Project folder** | the `career-wiki` folder you just downloaded |

Then type `/career-init` and press Enter — or **`/career-migrate` if you already have a wiki or an export
from another tool**, in which case put it in `vault/migration/` rather than `vault/sources/` first.
Typing `/` at any point lists every command in this repo — they are picked up automatically from the
project folder, with nothing to install.

**In the terminal:** navigate to the folder and run `claude`, then type:

```
/career-init
```

#### Running the job search

Once you get to `/role-radar`, **just ask** — "run the radar for the last week" — and the agent runs the
script itself. You never need to type a command.

If you would rather watch it run, the desktop app has a built-in terminal: **Views → Terminal**, or press
**Ctrl+`**. It opens in your project folder already, so this works directly:

```bash
python3 tools/radar/radar.py --days 7
```

Or, to sweep everything still open rather than only the last week:

```bash
python3 tools/radar/radar.py --all-open
```

### 7. Check it is all set up

```bash
python3 tools/doctor.py
```

**It reads your files and says what is ready, what is optional, and what needs doing.** Most of it is
optional and says so — an unconfigured thing has not been tried, which is different from broken.

🔴 **The one it is really for**: a config file you copied from the example and never filled in. That
**looks configured and matches nothing** — the search runs, finds no roles, and reports a quiet week that
never happened. A missing file would have been louder.

It makes no network calls, so it is instant and works offline. To find out whether the job sources
actually answer, run `python3 tools/radar/sources_check.py`.

### 8. Optional but recommended — read the wiki in Obsidian

[Obsidian](https://obsidian.md) is a free app for reading interlinked markdown files. Open the
`career-wiki` folder as a vault and you can click through the wiki as it is written, follow the links, and
see how it all connects. The agent writes; you browse.

---

## Your first hour

**Expect a lot of questions.** That is the product, not a delay before it.

Roughly:

1. It reads your CV and tells you what it noticed. **If that reads like a summary of your own document,
   push back** — it should tell you something you did not know about it.
2. It scaffolds the wiki.
3. First interview round: reporting lines, decision rights, what the product is, who uses it.
4. Career anchors, then your salary floor and what it is for.
5. It builds your scoring framework from your answers.
6. It tells you the three most interesting things it learned that were not in your CV, and what it still
   does not know.

**It will not offer to write you a CV at the end of this, and that is deliberate.** There is not enough in
the wiki yet, and a CV written after one interview round is a reformatted version of the document you
already had. Run `/interview` a few more times first.

---
