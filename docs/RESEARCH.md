# Research notes — 2026-11-07

These are source observations, not local in-game verification.

- The [Forever UI source mirror version](https://raw.githubusercontent.com/Gethe/wow-ui-source/forever/version.txt) reports `1.60.1.70862`. It is a community mirror of Blizzard UI code, not an official build notification service. Its `version.txt` contains no explicit Interface value and must not be used to infer one automatically.
- The [Forever NamePlateUnitFrame implementation](https://github.com/Gethe/wow-ui-source/blob/forever/Interface/AddOns/Blizzard_NamePlates/Blizzard_NamePlateUnitFrame.lua) exposes nameplate text and class-color updates. This demonstrates Lua nameplate code, not arbitrary control of native overhead world names.
- The [Forever nameplate TOC](https://github.com/Gethe/wow-ui-source/blob/forever/Interface/AddOns/Blizzard_NamePlates/Blizzard_NamePlates.toc) selects Camelot-specific files. Start with the Forever branch, not Classic Era assumptions.
- [ForeverPlusPlus's first-hand client notes](https://github.com/xIGBClutchIx/ForeverPlusPlus/blob/main/docs/forever-api.md) report Interface `16001`, live product `wowf`, `_forever_`, and first-name/surname behavior in `UnitName`. Treat these as a provisional baseline until verified on the user's installed client.
- [GitHub's workflow documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule) explains scheduled checks. They run from the default branch, may be delayed, and public-repository schedules can be disabled after inactivity. This is polling, not a Blizzard push webhook.

Open questions: native overhead per-player color API; identity lookup and surname handling; availability of social data and writable rendering in combat/instances; authoritative machine-readable live Interface feed. Resolve these before claiming support or unattended in-game compatibility.

## Follow-up feasibility review — 2026-11-07

The [generated Forever NamePlate API](https://github.com/Gethe/wow-ui-source/blob/forever/Interface/AddOns/Blizzard_APIDocumentationGenerated/NamePlateDocumentation.lua) exposes plate lookup/size controls, and the nameplate implementation above exposes Lua name text. Neither establishes a native-world-text color setter. No supported per-player native color setter was identified in the reviewed Unit/NamePlate documentation. Absence in this subset is not proof about every undocumented client facility.

The [FirstNames author's description](https://www.curseforge.com/wow/addons/firstnames) explicitly says native 3D world names are engine-controlled and implements editable overhead names through name-only friendly nameplates. This is a first-hand addon implementation report supporting the limitation; it is not our own client validation.

Practical conclusion: native per-player coloring appears unsupported; do not implement the rejected nameplate workaround. The remaining client check records the actual build/CVars and accessible Lua plate state, without claiming that nameplate access proves native access. The owner is downloading Forever. Only an Anniversary client was found locally at the default location.
