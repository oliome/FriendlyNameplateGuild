# BetterForeverNames

Planning repository for a World of Warcraft: Forever addon that colors **overhead player names** for guild members, friends, and player classes.

**Status:** design, compatibility-update foundation, and a separate [read-only diagnostic probe](docs/PROBE.md). This is not yet a working name-coloring addon. The first milestone must prove that Forever exposes the requested overhead text to addons. No in-game behavior has been verified. The owner requires native world text only; stop if unsupported rather than substituting nameplates.

## Planned behavior

- Independently enable guild, friend, and class coloring.
- Pick custom guild/friend colors and reorder priority. Default: friend > guild > class > Blizzard's original color.
- Preserve the original Recent Allies appearance when no enabled rule matches.
- Apply to friendly players initially; preserve hostile/PvP identification.
- Restore Blizzard's original behavior when disabled. Save settings between sessions.

See [the implementation plan](docs/PLAN.md), [research and uncertainties](docs/RESEARCH.md), and [automatic updates](docs/AUTOMATION.md).

## Repository contents

`addon/BetterForeverNames/BetterForeverNames.toc` is a metadata template, not an installable release. `tools/compatibility.py` validates a build observation and stages a metadata-only patch. GitHub Actions tests the proposed files before committing or releasing anything. Publishing stays disabled until the addon exists and the initial in-game checks are recorded.

Run the current checks with Python 3.11 or newer. Lupa executes the actual probe under Lua 5.1; it is a development dependency, never shipped in the addon:

```powershell
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

The local Git repository's origin is `https://github.com/oliome/BetterForeverNames.git`. Pushing/hosting is deferred at the owner's request. A live build feed and release settings still need to be connected; see the automation setup guide. Passing the current tests validates update logic and mocked probe behavior, not Blizzard's client.
