#!/usr/bin/env bash
# Copy tooling from this repo into a personal vault. One direction only.
#
#   tools/sync-to-vault.sh ~/Documents/my-career-wiki
#   tools/sync-to-vault.sh ~/Documents/my-career-wiki --dry-run
#
# WHY ONE DIRECTION
#
# The repo and the vault are deliberately different places. The repo is public
# and holds only scaffolding; the vault is private and holds a real person's
# history. Keeping them apart means personal material has no path to the public
# remote -- not "is ignored on the way", but has no path.
#
# The cost is that improvements have to be carried across, which is what this
# does. It copies the parts that are the tool and never the parts that are the
# person: it will not read, write, or look at sources/, wiki/ or oversight/.
#
# CLAUDE.md is NOT overwritten. A vault's schema gets customised -- other
# sections, house rules, the user's own writing standard -- and clobbering it
# would silently discard that. Differences are reported for you to merge.
set -euo pipefail

VAULT="${1:-}"
DRY=""
[ "${2:-}" = "--dry-run" ] && DRY="--dry-run"
[ -z "$VAULT" ] && { echo "usage: $0 <vault-directory> [--dry-run]"; exit 1; }
[ -d "$VAULT" ] || { echo "not a directory: $VAULT"; exit 1; }

REPO="$(cd "$(dirname "$0")/.." && pwd)"
[ "$(cd "$VAULT" && pwd)" = "$REPO" ] && { echo "refusing: that is this repo, not a vault"; exit 1; }

echo "  from: $REPO"
echo "  to:   $VAULT"
[ -n "$DRY" ] && echo "  (dry run -- nothing will be written)"
echo

for item in .claude/skills .claude/agents .claude/hooks .claude/settings.json \
            tools/verify.py tools/cv_lint.py tools/export_review.py tools/radar \
            templates oversight/OVERSIGHT.md; do
  src="$REPO/$item"
  [ -e "$src" ] || continue
  dst="$VAULT/$item"
  mkdir -p "$(dirname "$dst")"
  if [ -d "$src" ]; then
    rsync -a $DRY --itemize-changes --exclude '__pycache__' --exclude '*.pyc' \
          --exclude 'raw.json' --exclude 'seen.json' --exclude 'shortlist.md' \
          --exclude 'config.json' "$src/" "$dst/" | sed 's|^|  |'
  else
    rsync -a $DRY --itemize-changes "$src" "$dst" | sed 's|^|  |'
  fi
done

echo
if [ -f "$VAULT/CLAUDE.md" ]; then
  if diff -q "$REPO/CLAUDE.md" "$VAULT/CLAUDE.md" >/dev/null 2>&1; then
    echo "  CLAUDE.md: identical"
  else
    n=$(diff "$REPO/CLAUDE.md" "$VAULT/CLAUDE.md" | grep -c '^[<>]' || true)
    echo "  CLAUDE.md: $n differing lines -- NOT copied, review and merge by hand:"
    echo "      diff \"$REPO/CLAUDE.md\" \"$VAULT/CLAUDE.md\""
    echo "      Your vault's version is authoritative for anything you have customised."
  fi
else
  echo "  CLAUDE.md: none in the vault. Copy the repo's and adapt it:"
  echo "      cp \"$REPO/CLAUDE.md\" \"$VAULT/CLAUDE.md\""
fi

cat <<EOF

  Not touched, by design: sources/  wiki/  oversight/<application>/
  Those are yours. Nothing in this script reads them.
EOF
