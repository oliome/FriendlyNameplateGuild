# BetterForeverNames

Planning repository for a World of Warcraft: Forever addon that colors **overhead player names** for guild members, friends, and player classes.

**Status:** design and compatibility-update foundation. This is not yet a working name-coloring addon. The first milestone must prove that Forever exposes the requested overhead text to addons. No in-game behavior has been verified.

## Planned behavior

- Independently enable guild, friend, and class coloring.
- Pick custom guild/friend colors and reorder priority. Default: friend > guild > class > Blizzard's original color.
- Preserve the original Recent Allies appearance when no enabled rule matches.
- Apply to friendly players initially; preserve hostile/PvP identification.
- Restore Blizzard's original behavior when disabled. Save settings between sessions.

See [the implementation plan](docs/PLAN.md), [research and uncertainties](docs/RESEARCH.md), and [automatic updates](docs/AUTOMATION.md).

## Repository contents

`addon/BetterForeverNames/BetterForeverNames.toc` is a metadata template, not an installable release. `tools/compatibility.py` validates a build observation and stages a metadata-only patch. GitHub Actions tests the proposed files before committing or releasing anything. Publishing stays disabled until the addon exists and the initial in-game checks are recorded.

Run the current checks with Python 3.11 or newer (no third-party dependencies):

```powershell
python -m unittest discover -s tests -v
```

This folder already contains a local Git repository. A hosted GitHub repository, feed, and release settings still need to be connected; see the automation setup guide. Passing the current tests validates update logic, not the future addon or Blizzard's client.
