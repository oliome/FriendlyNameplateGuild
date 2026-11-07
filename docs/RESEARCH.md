# Research notes — 2026-11-07

These are source observations, not local in-game verification.

- The [Forever UI source mirror version](https://raw.githubusercontent.com/Gethe/wow-ui-source/forever/version.txt) reports `1.60.1.70862`. It is a community mirror of Blizzard UI code, not an official build notification service. Its `version.txt` contains no explicit Interface value and must not be used to infer one automatically.
- The [Forever NamePlateUnitFrame implementation](https://github.com/Gethe/wow-ui-source/blob/forever/Interface/AddOns/Blizzard_NamePlates/Blizzard_NamePlateUnitFrame.lua) exposes nameplate text and class-color updates. This demonstrates Lua nameplate code, not arbitrary control of native overhead world names.
- The [Forever nameplate TOC](https://github.com/Gethe/wow-ui-source/blob/forever/Interface/AddOns/Blizzard_NamePlates/Blizzard_NamePlates.toc) selects Camelot-specific files. Start with the Forever branch, not Classic Era assumptions.
- [ForeverPlusPlus's first-hand client notes](https://github.com/xIGBClutchIx/ForeverPlusPlus/blob/main/docs/forever-api.md) report Interface `16001`, live product `wowf`, `_forever_`, and first-name/surname behavior in `UnitName`. Treat these as a provisional baseline until verified on the user's installed client.
- [GitHub's workflow documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule) explains scheduled checks. They run from the default branch, may be delayed, and public-repository schedules can be disabled after inactivity. This is polling, not a Blizzard push webhook.

Open questions: native overhead per-player color API; identity lookup and surname handling; availability of social data and writable rendering in combat/instances; authoritative machine-readable live Interface feed. Resolve these before claiming support or unattended in-game compatibility.
