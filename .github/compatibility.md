# Forever update automation

The hourly `Forever compatibility` workflow reads Blizzard's **live `wowf` US region** directly:

https://us.version.battle.net/v2/products/wowf/versions

It can also run manually (optionally testing the current build) or receive a `repository_dispatch` event named `wow-updated`. Dispatch payloads are never trusted as version data; the job always rereads Blizzard.

## Behavior

1. No new live build: no mutation, test dependency install, release, or issue.
2. New build of a previously verified game patch: retain that patch's known Interface, stage an addon patch-version bump and build checkpoint, and run the complete Lua/Python test suite against those candidate files.
3. Tests pass: build a zip, update the permanent player download, atomically push the tested metadata commit and version tag, and create a GitHub release. Until `runtime_ready` is explicitly verified in-game, releases remain **prereleases**. Passing mocks never sets readiness automatically.
4. Tests fail: no candidate commit/tag/release. Open an issue containing the build, observation, test output, and workflow link. The same open issue is reused without duplicate tickets. Detection, dependency, packaging, and publishing failures also raise an issue.
5. Unfamiliar game patch: do not guess the Interface. Run the tests, block staging/publishing, and open an issue requesting a verified live value. Optionally configure `FOREVER_BUILD_FEED_URL` to an HTTPS JSON endpoint providing `{ "product": "wowf", "channel": "live", "interface": 16002, "build": 71000 }` (illustrative future values). Its build must exactly match the official live observation. After verifying in-game, the Interface can instead be updated in a reviewed commit along with `game_version`/`build` in `compatibility.json`.

The official version table does not include Interface. Retaining the existing Interface for the same patch is a maintenance policy based on the previous client observation, not a new live Interface measurement. API changes inside a patch can still evade mocks; CI does not launch WoW. GitHub schedules may be delayed or disabled after public-repository inactivity. Regional rollout is controlled by `region` in `compatibility.json`.

Tests and logs are maintained outside the three-file runtime addon. No updater code runs inside WoW. Branch/tag protection can prevent a push; that fails with an issue rather than bypassing protection. If the atomic push succeeds but release creation fails, rebuild from the existing tag, rerun checks, and create/upload the missing release without inventing another version.

## Sources considered

| Source | Finding |
| --- | --- |
| [Blizzard live versions](https://us.version.battle.net/v2/products/wowf/versions) | Direct live-region BuildId/VersionsName; selected primary detector. Live read on 2026-11-07 matched 70862 / 1.60.1.70862. |
| [Wago build API](https://wago.tools/api/builds) | Useful secondary build history, including background-download status; an index can lag the official region feed. |
| [Wago addon game metadata](https://addons.wago.io/api/data/game) | Explicit Forever patch support, but no actual client Interface field; not sufficient to verify a changed TOC. |
| [UI mirror version](https://github.com/Gethe/wow-ui-source/blob/forever/version.txt) | Useful for source/API review; unnecessary extra delay for basic build detection. |
| [GitHub triggers](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows) | Hourly polling needs no external service; repository dispatch can supplement it with an external watcher. |

Smoke check: `python tools/compatibility.py --detect --output candidate.json`. This writes only the ignored observation file, never commits or opens an issue. Unit tests exercise synthetic new builds and failure reporting without creating fake GitHub tickets.
