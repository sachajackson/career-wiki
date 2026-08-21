#!/usr/bin/env bash
# Runs the deterministic layer whenever a CV or cover letter is written or edited,
# and puts any findings straight into the agent's context.
#
# PostToolUse cannot block -- the write has already happened. What it can do is
# exit 2, which surfaces stderr to Claude. That is the whole mechanism: the agent
# does not get to decide whether to check its own work, and it cannot quietly
# skip the re-check after a fix, because the fix is itself a write that fires
# this again.
set -uo pipefail

input=$(cat)
path=$(printf '%s' "$input" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
[ -z "$path" ] && exit 0

# Only artefacts, and only text we can read. DOCX and PDF are checked from
# extracted text at the /pre-submit gate instead.
case "$path" in
  *applications/*|*Applications/*) ;;
  *) exit 0 ;;
esac
case "$path" in
  *.html|*.htm|*.md|*.txt) ;;
  *) exit 0 ;;
esac
case "$(basename "$path")" in
  *CV*|*cv*|*Cover*|*cover*|*Letter*|*letter*|*Resume*|*resume*) ;;
  *) exit 0 ;;
esac

root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
[ -f "$root/tools/verify.py" ] || exit 0

# Nearest application.json, walking up from the artefact.
cfg=""; dir=$(dirname "$path")
for _ in 1 2 3 4; do
  [ -f "$dir/application.json" ] && { cfg="$dir/application.json"; break; }
  dir=$(dirname "$dir")
done

if [ -z "$cfg" ]; then
  echo "verify: no application.json beside $(basename "$path"), so the deterministic layer could not" >&2
  echo "run. Create one (see templates/application.example.json) with the employer, the past-employer" >&2
  echo "list and the posting -- without it the attribution and coverage checks cannot run at all." >&2
  exit 2
fi

out=$(python3 "$root/tools/verify.py" "$path" --config "$cfg" --wiki "$root/wiki" --coverage 2>&1)
status=$?

# Refresh the reviewer's export on every write, so it can never be stale and
# nobody has to remember to build it. A non-technical user will not run a
# script before asking for a second opinion -- and if the export is missing
# they will point the other tool at the application folder instead, which sits
# inside the wiki. That is the failure this prevents.
appdir=$(dirname "$cfg")
python3 "$root/tools/export_review.py" "$appdir" >/dev/null 2>&1 || true

if [ $status -eq 0 ]; then
  printf '{"systemMessage":"verify: %s is clean on the deterministic checks. oversight/%s/ refreshed"}\n' \
    "$(basename "$path")" "$(basename "$appdir")"
  exit 0
fi

{
  echo "DETERMINISTIC LAYER FAILED on $(basename "$path"). Fix these before doing anything else."
  echo
  echo "$out"
  echo
  echo "Rules for fixing, in order:"
  echo " - UNSOURCED: the figure is in the document and nowhere in the wiki. REMOVE IT FROM THE"
  echo "   DOCUMENT, or ask the user to confirm it. Do NOT add it to the wiki to make this pass:"
  echo "   that launders a fabrication into a source and is worse than the original error."
  echo " - ATTRIBUTION: move the figure to the role the wiki attributes it to, or correct the wiki"
  echo "   if the wiki is wrong. Say which you did and why."
  echo " - UNVERIFIED: ask the user to confirm it before it goes in an external document."
  echo " - COVERAGE items are not errors. Decide, and say what you decided."
  echo
  echo "This hook re-runs on your next write, so the fix is re-checked automatically."
} >&2
exit 2
