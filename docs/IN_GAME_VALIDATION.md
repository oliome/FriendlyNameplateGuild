# In-game validation

Status: **not performed**. Runtime implementation and automatic public releases are not ready.

2026-11-07 source review: no supported native per-player overhead-color API identified. A read-only probe is ready for client diagnostics (PROBE.md). Only Anniversary was found in the default install; the owner is downloading Forever. The owner explicitly chose native text only and instructed us to stop coloring implementation if unsupported. No game installation was modified. A successful probe report still does not establish native text editability.

Record the following for the first release and any renderer/API change:

- Tester, date, full `GetBuildInfo()` result, live product/channel.
- Exact API/hook used for native overhead text and evidence it is not just nameplate text.
- Guild, friend, overlap, class, and original/Recent Allies fallback results.
- Combat, instance, PvP, nameplate on/off, frame reuse, relationship changes, disable/restore results.
- Saved settings across reload and full restart; script errors/taint; addon conflicts.
- Screenshots and reproducible steps; remaining limitations.

Do not replace this status with a passing CI badge. CI cannot launch or validate the WoW client.
