# Implementation plan

## 1. Prove overhead-name support (first, blocking milestone)

Owner decision (2026-11-07): native world text only. If unsupported, stop the coloring implementation; a name-only friendly nameplate alternative is not authorized. A separate read-only probe is available; see PROBE.md.

Test on the installed live Forever client and record `GetBuildInfo()` including its fourth return value (Interface). Start with an isolated probe addon and script errors enabled.

Distinguish native floating world names from Lua nameplate text. Verify whether a supported API can assign different colors to individual friendly players' native overhead names. Inspect Forever's own name/class/Recent Allies CVars and UI code; do not assume a FontString on a nameplate changes native world text. A global color change does not satisfy per-player rules.

Record the API, build, screenshots, and results in `docs/IN_GAME_VALIDATION.md`. Test names with friendly nameplates both on and off. Test guild-only, friend-only, friend + guild, unrelated, class-known, and class-unknown players. If native overhead names cannot be customized, document the limitation and stop runtime coloring work, per the owner's decision. Do not substitute nameplates, chat, or unit-frame coloring.

Acceptance: a supported, repeatable demonstration changes one friendly player's overhead name without changing unrelated players, combat behavior, or Recent Allies data. If unsupported, stop runtime implementation and present the evidence.

## 2. Implement identity and rule resolution

Separate relationship lookup, color selection, and rendering. Resolve friend/guild membership with supported APIs and events. Prefer stable player identity where exposed; validate Forever first-name/surname semantics before normalizing names. Do not treat a surname as a realm or collapse players with the same first name. Battle.net membership only counts when the API exposes a matching current WoW character; an unresolved/offline identity is not a positive match.

Default priority: friend, guild, class, original. Add independent switches, color pickers, priority controls, reset, and a preview using fictional names. Get class colors from Blizzard's class palette. Unknown class/relationship returns the original appearance. Preserve Recent Allies naturally through the original-color fallback; do not mutate that roster.

Acceptance tests: all overlaps and rule orderings; disabled rules; unknown/stale identities; offline friends; guild departure; cross-ruleset and surname collisions; invalid saved settings; default migration; custom colors; class palette changes.

## 3. Integrate the proven renderer

Use only hooks/APIs established by milestone 1. Capability-check required functions. Handle forbidden frames and secret/restricted values before inspecting or branching on them. Skip unsupported contexts safely. Do not replace protected functions, spoof client versions, read secret combat data, or alter Blizzard's social records.

Refresh on supported identity/roster/class changes and settings changes. Release stale references when frames are reused; restore original rendering on disable/removal. Avoid per-frame roster scans. Coexist with other nameplate addons by detecting ownership/conflicts and explaining unsupported combinations.

## 4. Validate the first playable release

Add Lua syntax checks, pure resolver tests, adapter contract tests against captured Forever API data, and mocked lifecycle tests. Test the actual production Lua, rather than a Python reimplementation. CI must run all these checks once runtime files exist.

Run the manual matrix: open world, combat transitions, target change, entering/leaving instances, PvP, friendly nameplates on/off, visibility/range transitions, pooled frame reuse, `/reload`, logout/login, relationship changes, settings reset, and another popular nameplate addon. Check errors, taint, color restoration, and idle performance.

Record the initial release evidence in `docs/IN_GAME_VALIDATION.md`. Replace `runtime_ready: false` only after the renderer and checks exist. The current metadata tests alone cannot qualify the addon for release.

## 5. Enable compatibility releases

Provision a trusted live-Forever build observation feed as described in AUTOMATION.md. Validate its Interface value against the actual client, not an inferred mapping from patch number. Enable automatic releases after the first working release.

On an Interface increase: stage a patch-version/TOC bump, run the full suite against that candidate, package exactly the tested files, commit/tag, and publish a GitHub Release. Failures halt the release and leave the last known release intact. An API change needs implementation and renewed validation; a passing mock suite does not establish in-game compatibility by itself.

## Later options

Additional surfaces (chat/unit frames), per-character profiles, optional relationship indicators alongside class colors, addon-manager distribution, and additional rule categories follow the overhead-name milestone. They are outside the first release.
