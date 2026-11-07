#!/usr/bin/env bash
set -euo pipefail
repo=$(pwd -P)
work="$repo/.tooling/update-test.$$"
mkdir -p "$work/.github"
cp .github/wow-version.json "$work/.github/wow-version.json"
cp FriendlyNameplateGuild.toc "$work/FriendlyNameplateGuild.toc"
build=$(jq -r '.build' .github/wow-version.json)
patch=$(jq -r '.game_version' .github/wow-version.json)
interface=$(jq -r '.interface' .github/wow-version.json)
version=$(jq -r '.addon_version' .github/wow-version.json)
fixture="$work/versions.txt"
fixture() { printf 'Region!STRING:0|BuildId!DEC:4|VersionsName!String:0\n## seqn = 1\n%s\n' "$1" > "$fixture"; }
detect() { (cd "$work"; FNG_VERSION_FILE="$fixture" GITHUB_OUTPUT="$work/outputs" bash "$repo/.github/check-wow.sh" detect) > "$work/detect.log" 2>&1; }
stage() { (cd "$work"; GITHUB_OUTPUT="$work/outputs" bash "$repo/.github/check-wow.sh" stage) > "$work/stage.log" 2>&1; }
fixture "us|$build|$patch.$build"
detect
grep -q '^changed=false$' "$work/outputs"
cmp .github/wow-version.json "$work/.github/wow-version.json"
fixture "us|$((build+1))|$patch.$((build+1))"
detect; stage
jq -e --arg version "$version" --argjson build "$((build+1))" --argjson interface "$interface" '.addon_version!=$version and .build==$build and .interface==$interface' "$work/.github/wow-version.json" >/dev/null
cp "$work/.github/wow-version.json" "$work/checkpoint.json"
stage
cmp "$work/checkpoint.json" "$work/.github/wow-version.json"
cp .github/wow-version.json "$work/.github/wow-version.json"
fixture "us|$((build+1))|1.60.99.$((build+1))"
detect
if stage; then echo 'Unverified Interface was accepted' >&2; exit 1; fi
cmp .github/wow-version.json "$work/.github/wow-version.json"
for row in "us|$build|12.1.5.$build" "us|$build|$patch.999999" "eu|$build|$patch.$build" "us|$((build-1))|$patch.$((build-1))"; do
  fixture "$row"
  if detect; then echo "Invalid live row was accepted: $row" >&2; exit 1; fi
done
# Exercise failure-ticket output without creating a real GitHub issue.
mkdir -p "$work/bin"
cat > "$work/bin/gh" <<'MOCK'
#!/usr/bin/env bash
if [[ $1 == issue && $2 == list ]]; then printf '%s\n' "${FNG_FAKE_ISSUES:-[]}"; exit 0; fi
if [[ $1 == issue && $2 == create ]]; then
  while [[ $# -gt 0 ]]; do if [[ $1 == --body-file ]]; then cp "$2" "$FNG_CAPTURE"; break; fi; shift; done
  echo create >> "$FNG_CAPTURE.calls"
  exit 0
fi
exit 1
MOCK
chmod +x "$work/bin/gh"
printf 'FAIL: guild label test\n' > "$work/test-results.txt"
(cd "$work"; PATH="$work/bin:$PATH" RUNNER_TEMP="$work" FNG_BUILD="$build" FNG_CAPTURE="$work/issue.md" GITHUB_REPOSITORY=oliome/FriendlyNameplateGuild GITHUB_RUN_ID=123 bash "$repo/.github/report-failure.sh")
grep -q 'FAIL: guild label test' "$work/issue.md"
grep -q '/actions/runs/123' "$work/issue.md"
issues=$(jq -n --arg title "Forever build $build: addon checks failed" '[{title:$title,url:"https://github.com/example/issues/1"}]')
(cd "$work"; PATH="$work/bin:$PATH" RUNNER_TEMP="$work" FNG_BUILD="$build" FNG_CAPTURE="$work/issue.md" FNG_FAKE_ISSUES="$issues" bash "$repo/.github/report-failure.sh")
[[ $(wc -l < "$work/issue.md.calls") == 1 ]]
echo 'Update detection, staged version/idempotence, Interface guard, invalid feeds, and failure-ticket deduplication passed'
