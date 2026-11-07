# BetterForeverNames

Adds a configurable **guild name beneath friendly player nameplates** in World of Warcraft: Forever.

**Status: experimental 0.2.0 preview.** The Lua implementation passes mocked tests, but has not yet been tested in the actual client. The owner approved using nameplates for guild labels after investigating the limitations of native overhead text. Automatic production releases remain disabled pending in-game validation.

## Download and install

[Download BetterForeverNames 0.2.0 preview](downloads/BetterForeverNames-0.2.0-preview.zip?raw=true).

1. Extract the `BetterForeverNames` folder into Forever's `_forever_/Interface/AddOns` folder. The TOC and `GuildNames.lua` must sit directly inside that folder.
2. Restart the client and enable **BetterForeverNames** in the AddOns menu.
3. Enable friendly **player** nameplates in the game settings. For names without health bars, select the game's name-only option. The addon does not change these settings itself.
4. In the open world, out of combat, approach a friendly player who belongs to a guild. A green `<Guild Name>` line should appear beneath their existing name. Guild data may take a moment to load.

The probe addon is separate and can be disabled. This addon leaves the existing player-name text/color untouched. Unguilded players, hostile players, and NPCs receive no guild label. This first preview hides its labels during combat and in instances. Replaced/restricted nameplates are skipped; other nameplate addons are not yet validated.

## Commands

| Command | Effect |
| --- | --- |
| `/bfn status` | Show current state and visible guild-label count |
| `/bfn on` / `/bfn off` | Show/hide the added guild lines |
| `/bfn size 12` | Font size, 8–24 |
| `/bfn gap 3` | Space below the player's name, 0–20 |
| `/bfn color 66ff99` | Guild text color as six hex digits |
| `/bfn reset` | Restore defaults |

Settings are saved across sessions. Missing guild data is retried once per second using visible plates only; no roster scan is performed. Please test `/bfn off`, changes of target/visible players, `/reload`, and settings across a full restart. Report `/bfn status` and any Lua error if labels do not appear.

## Development

Run with Python 3.11+:

```powershell
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python tools/compatibility.py --package --preview
```

Lupa runs the actual addon and probe code under Lua 5.1 with mocked WoW APIs. It is a development dependency and is never shipped in the addon. Tests cover rendering eligibility, frame reuse, missing/secret data, combat/instance transitions, saved settings, commands, and compatibility packaging. They do not establish live-client support.

See [the current plan](docs/PLAN.md), [validation record](docs/IN_GAME_VALIDATION.md), [Recent Allies investigation](docs/RECENT_ALLIES_TRACE.md), and [automatic updates](docs/AUTOMATION.md). The original [read-only probe](docs/PROBE.md) remains available for diagnostics.

Origin: `https://github.com/oliome/BetterForeverNames.git`. A trusted live Interface feed and first in-game validation are still required before enabling automated production releases. Preview packaging does not enable them.
