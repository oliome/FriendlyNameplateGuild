#!/usr/bin/env bash
set -euo pipefail
build=${FNG_BUILD:-unknown}
[[ $build =~ ^[1-9][0-9]*$ ]] || build=unknown
title="Forever build $build: addon checks failed"
existing=$(gh issue list --state open --limit 100 --search "$title in:title" --json title,url | jq -r --arg title "$title" '.[] | select(.title==$title) | .url' | head -n 1)
if [[ -n $existing ]]; then echo "Already tracked: $existing"; exit 0; fi
body=$(mktemp "${RUNNER_TEMP:-/tmp}/fng-issue.XXXXXX")
trap 'rm -f "$body"' EXIT
{
  echo 'Addon checks or update/release automation failed. Failed checks block publication.'
  echo
  echo "Workflow: ${GITHUB_SERVER_URL:-https://github.com}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}"
  if [[ -f candidate.json ]]; then echo; echo 'Live build observation:'; echo; sed 's/^/    /' candidate.json; fi
  echo; echo 'Test output (see workflow logs for lint, detection, or publishing errors):'; echo
  if [[ -f test-results.txt ]]; then tail -c 12000 test-results.txt | sed 's/^/    /'; else echo '    Tests were not reached.'; fi
  echo; echo 'Fix the error and rerun the workflow. For an unfamiliar patch, verify the live Interface instead of guessing it. A release upload can fail after a passing commit/tag was pushed; inspect the run before retrying.'
} > "$body"
gh issue create --title "$title" --body-file "$body"
