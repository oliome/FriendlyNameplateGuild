# In-game validation

Status: **desktop diagnostic reports received; guild-label preview implemented, awaiting in-game validation**. Automatic public production releases are not ready.

## Guild-label pivot and preview — 2026-11-07

The owner approved showing guild names beneath friendly player nameplates. This supersedes the historical native-only stop for this feature. Version 0.2.0 implements guild labels, with saved controls and mocked Lua tests; the test ZIP is explicitly a preview. No live rendering result has been reported yet. `runtime_ready` remains false.

Validate: guilded/unguilded friendly players, hostile players/NPCs, delayed guild data, range changes, pooled frames, disable/restore, font/gap/color controls, full settings persistence, combat/instance hide-and-return, other nameplate addons, Lua errors, and appearance. The source-matched APIs are not a substitute for these checks.

## Desktop probe — 2026-11-07

The owner ran the read-only probe and supplied [this report](validation/2026-11-07-desktop-probe.txt). It reports version `1.60.1`, build `70862`, Interface `16001`, project ID `18`. This confirms the provisional Interface/build baseline for that client; do not assume Forever shares Mainline's project ID.

`nameplateShowFriendlyPlayers=0` reports friendly player nameplates disabled. `target.nameplate=absent` is consistent with that setting; it is not evidence that native text is writable or universally inaccessible. The two class-color CVars and name-only setting report `1`, but these settings do not demonstrate per-player native world-text control. `nameplateShowFriends` is unavailable on this client; do not rely on that older CVar.

The report's `native.per-player-color` line is a fixed description of the earlier source review, not a dynamic test for native coloring support. No color-setting experiment, native rendering hook, or screenshot was supplied. The report alone cannot prove that no API exists.

Decision: no supported native per-player coloring API has been identified. Keep coloring implementation stopped under the owner's native-only requirement, and keep `runtime_ready` false. No further nameplate tests are required for the rejected nameplate alternative. Reopen implementation only if a supported native API is found.

## Earlier preparation

Subsequent owner report: [friendly nameplates enabled](validation/2026-11-07-desktop-nameplates-enabled.txt), with accessible Lua name text. This confirms the Lua surface only; it does not change the native-only decision. A subsequent [Recent Allies-specific source trace](RECENT_ALLIES_TRACE.md) matches the reported client build and explains the distinction between exported color data, Lua nameplate rendering, and inferred internal native coloring. The local Forever installation is now present.

2026-11-07 source review: no supported native per-player overhead-color API identified. A read-only probe is ready for client diagnostics (PROBE.md). Only Anniversary was found in the default install; the owner is downloading Forever. The owner explicitly chose native text only and instructed us to stop coloring implementation if unsupported. No game installation was modified. A successful probe report still does not establish native text editability.

Record the following for the first release and any renderer/API change:

- Tester, date, full `GetBuildInfo()` result, live product/channel.
- Exact API/hook used for native overhead text and evidence it is not just nameplate text.
- Guild, friend, overlap, class, and original/Recent Allies fallback results.
- Combat, instance, PvP, nameplate on/off, frame reuse, relationship changes, disable/restore results.
- Saved settings across reload and full restart; script errors/taint; addon conflicts.
- Screenshots and reproducible steps; remaining limitations.

Do not replace this status with a passing CI badge. CI cannot launch or validate the WoW client.
