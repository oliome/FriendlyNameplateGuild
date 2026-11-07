# Compatibility automation

The workflows and updater are implemented as a foundation. They are **not active on a hosted repository yet**. No Blizzard webhook, authenticated GitHub connection, or trusted live Interface feed is provisioned in this workspace.

## What triggers a bump

The `## Interface` TOC field controls the client's out-of-date classification. The addon's semantic version is separate. A higher live Interface value stages both an Interface update and a patch-version bump. A new client build with the same Interface produces no update. Older values, another product/channel, malformed data, and a new client family fail closed.

The baseline `16001` / build `70862` is provisional, based on the research notes. Confirm it using the installed client before the first release. Do not derive Interface from the game's displayed patch version.

## Feed contract

Set the repository Actions variable `FOREVER_BUILD_FEED_URL` to a trusted HTTPS endpoint you control or have verified. It must serve a single JSON object such as:

```json
{
  "product": "wowf",
  "channel": "live",
  "interface": 16002,
  "build": 71000
}
```

These values are illustrative future values, not a claim that such a patch exists. The Interface must come from actual live client metadata, for example an independently collected fourth return value of `GetBuildInfo()`. A build/version mirror alone is insufficient. The feed producer must establish freshness, live-channel identity, and authenticity; this updater validates the schema and monotonic values, not the truth of a feed's contents. A stale feed cannot notify us about a patch it has not observed. Choosing/provisioning a trustworthy automatic producer is an outstanding integration task.

For an offline exercise, copy `compatibility.json` to a temporary observation JSON, edit its Interface/build values, and run `python tools/compatibility.py --observation <path>`. This command stages local metadata changes; it does not publish or modify the game install. Use a throwaway checkout for synthetic observations.

## Setup on GitHub

1. The owner supplied `https://github.com/oliome/BetterForeverNames.git`, which is configured as this checkout's `origin`. Hosting/pushing is deferred until the end. When ready, verify the hosted repository's default branch and existing history before pushing the local commits; do not create a duplicate repository or overwrite remote history.
2. Configure `FOREVER_BUILD_FEED_URL`. Enable GitHub Actions and run **Forever compatibility** manually to verify the integration. It polls every six hours; GitHub may delay scheduled jobs. Check Actions notifications for failures.
3. Complete milestones 1–4 in PLAN.md. Add the actual Lua/runtime/API contract checks to **both workflows**, replacing the current metadata-only test command with a shared full check command. Record in-game validation, then set `runtime_ready` to `true` in a reviewed commit. Publish the initial functional release separately.
4. Set the repository Actions variable `AUTO_RELEASE` to `true` to enable unattended metadata releases. The default is off while this is only a planning repository. Both this flag and runtime readiness are required. Ensure repository rules allow the Actions bot to push the default branch and tags; otherwise use a tested-candidate PR approach. Do not disable protection rules just to force a release.

## Release sequence

The scheduled workflow validates the baseline, fetches one observation, stages candidate TOC/state changes, and tests the candidate. It retains candidate files as an Actions artifact when there is an Interface change. After the release gates are enabled, a second job downloads those exact files on the original source commit, retests, builds a zip with a top-level `BetterForeverNames` folder, and atomically pushes the metadata commit and tag. It then publishes a GitHub Release with the zip.

No failing test run can reach the release job. Network/feed/schema errors abort the run. Concurrent default-branch edits cause a non-fast-forward push failure rather than overwriting work; rerun against the new default branch. Branch/tag permissions may also block publishing.

If the atomic Git push succeeded but GitHub Release creation failed, repair the release from its existing tag and rebuild/package that tag; do not bump the version again just to retry publication. Check out the tag, run all checks, package, then use `gh release create <tag> <zip> --verify-tag` (or upload the missing asset to the existing release).

API breaking changes need code fixes. The workflow does not automatically repair addon code. CI checks cannot prove combat restrictions or native world rendering still behave correctly; expand the contract tests whenever a client change exposes a gap, and perform renewed in-game validation for renderer/API changes.

## Distribution and rollback

GitHub publishing does not update players' installed files by itself. Players need an addon manager that supports this repository's releases, or must install the zip manually. CurseForge/Wago upload integration needs separate project IDs and credentials and is not configured here. Addons cannot download their own code inside WoW.

On regression, disable `AUTO_RELEASE`, mark the bad GitHub release, and direct players to the last known-good zip. Fix and publish a new version; avoid rewriting published tags. A failed run leaves the previous release intact.
