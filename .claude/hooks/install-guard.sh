#!/usr/bin/env bash
# Installs the pre-commit guard, every session, silently.
#
# The guard is what refuses personal material even against `git add -f`. It was
# a line in the setup instructions and a WARN in `doctor.py`, which means it was
# on for whoever read the instructions and off for everyone else -- and off is
# exactly when it matters, because the person who skipped setup is the person
# who does not know the vault boundary exists.
#
# Every instruction-shaped control in this repo has failed at least once. This
# one had not failed yet only because nobody but its author had run it.
#
# Idempotent, local to this clone, and silent unless it changes something.
set -euo pipefail
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
git rev-parse --git-dir >/dev/null 2>&1 || exit 0   # a ZIP download: nothing to guard
[ -d githooks ] || exit 0
[ "$(git config core.hooksPath || true)" = "githooks" ] && exit 0
git config core.hooksPath githooks
echo "Installed the pre-commit guard (githooks/). It refuses personal material even against git add -f." >&2
exit 0
