# FriendlyNameplateGuild

A small World of Warcraft: Forever addon that shows guild names beneath friendly player nameplates. Open **`/fng`** (or `/friendlynameplateguild`) for its settings window: enable/disable, font size, spacing, color picker, preview, and Reset. Changes apply immediately and are saved.

## Install

[Download 0.4.0 preview](downloads/FriendlyNameplateGuild-0.4.0-preview.zip?raw=true). Extract `FriendlyNameplateGuild` into `_forever_/Interface/AddOns`, restart WoW, and enable the addon. Enable friendly **player** nameplates in the game's own settings. You can use name-only mode to hide health bars.

When upgrading from the previous addon name, remove the previous addon folder before installing this one to avoid duplicate labels. The renamed addon starts with fresh settings.

Guilded friendly players get a separate guild line. Existing player names/colors are left alone. Labels pause in combat and instances, and restricted/replaced plates are skipped. Version 0.4.0 is awaiting live-client testing; automated tests use mocked WoW APIs. If a label is missing, run `/fng status` and check for Lua errors.

## Lightweight runtime

The installed addon contains only the TOC and two Lua files. No libraries, textures, probe, research files, network requests, or roster scans. Settings controls are created only when opened. A one-second timer checks visible nameplates and retries missing guild data; it stops while disabled, with no plates, or in unsupported contexts. There is no every-frame update handler.

The repository also keeps addon tests and its small packaging/update tooling; none of those are included in the install ZIP. Older research and diagnostic artifacts have been removed from the current tree; they remain recoverable in Git history.

## WoW update detection

- **In game:** the addon compares `GetBuildInfo()`'s Interface value with its TOC metadata. A higher client Interface produces a warning and appears in the settings window. WoW itself also marks old TOCs out of date; if it refuses to load the addon, the addon's warning cannot run. It cannot rewrite its own installed files.
- **On GitHub:** the compatibility workflow polls the Forever UI source mirror's `version.txt` every six hours. A newer build opens one GitHub issue for verification; repeated observations of the same build do not create duplicates. This is a community mirror, can lag Blizzard, and is not a Blizzard webhook. Follow repository issues/Actions for results. A new build does not by itself mean the Interface changed.
- **Automatic bump/release:** this still requires a trusted HTTPS JSON feed configured as the repository variable `FOREVER_BUILD_FEED_URL`. It must supply actual live-client metadata: `{"product":"wowf","channel":"live","interface":16002,"build":71000}` (illustrative values). We do not infer Interface from patch/build numbers. When a higher verified Interface arrives, the workflow stages a TOC/patch-version bump, runs tests, packages, and publishes only when `runtime_ready` in `compatibility.json` and the repository variable `AUTO_RELEASE` are both true. They remain off pending in-game validation. No feed has been provisioned yet, so unattended version bumps are **not currently active**.

Scheduled jobs may be delayed or disabled by GitHub's inactivity policy. A passing mock suite cannot detect every WoW API/rendering change; API-breaking updates need a code fix and client test. A published GitHub release also needs an addon manager or manual download to reach players' installations.

## Development

Python 3.11+; Lupa is a test-only dependency and executes the real Lua under Lua 5.1.

```powershell
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python tools/compatibility.py --package --preview
```

`python tools/compatibility.py --watch` checks the build mirror without modifying versions. `--observation <json-file>` stages a verified local observation for testing. Preview packaging does not enable production releases. Keep `runtime_ready` false until live appearance, frame reuse, settings persistence, disable/restore, combat/instance transitions, and errors have been checked.

Source references: [Forever build metadata API](https://github.com/Gethe/wow-ui-source/blob/forever/Interface/AddOns/Blizzard_APIDocumentationGenerated/BuildDocumentation.lua), [UI build mirror](https://github.com/Gethe/wow-ui-source/blob/forever/version.txt), [GitHub scheduling](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).
