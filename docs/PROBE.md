# Read-only overhead-name probe

This diagnostic addon reports the actual client Interface, relevant CVars, and whether the target has accessible Lua nameplate text. It does **not** change colors, enable nameplates, write settings, request rosters, collect names/GUIDs, or send data. Its report does not prove native world text is editable.

## Install and run

1. Build with `python tools/build_probe.py`, or use the provided `dist/BetterForeverNamesProbe-0.1.0.zip`.
2. Extract the `BetterForeverNamesProbe` folder into the **Forever** client's `Interface/AddOns` folder. Do not put it into Anniversary. The TOC and Lua file must be directly inside that folder, without an extra nested folder.
3. Restart the client or type `/reload` if the client detects the new addon. Enable **BetterForeverNames Probe** in the addon list. Its provisional Interface is 16001; if the client calls it out of date, report the actual Interface before changing the TOC.
4. In the open world, select a friendly player and type `/bfnprobe`. Copy the selected report using Ctrl+C. No name or player GUID appears in the report.
5. Record whether friendly nameplates were enabled and whether the visible name had a health bar. Repeat with friendly nameplates on and off using the game's own settings. Target a guild member, a friend, and an unrelated player to compare the native appearances visually.

If a field says `absent`, `unavailable`, `restricted`, or `forbidden`, do not infer that coloring is universally impossible: the target may not have a visible plate, an addon may replace it, or the context may restrict access. Record the context and repeat out of combat with other nameplate addons disabled. The probe never requests forbidden nameplates.

## Current finding

The source review found class-color controls on **Lua nameplates**, but no supported API for per-player native world-text color assignment. The FirstNames author explicitly describes native world text as engine-controlled and implements editable overhead names using friendly nameplates in name-only mode. This is evidence for that alternative, not a test performed on this computer. See RESEARCH.md for links.

Only an Anniversary installation was found at the default WoW location on 2026-11-07; its build metadata identifies `wow_anniversary`, version `2.5.6.69110`. The probe has not been installed or run in Forever here. No game files were changed.

Owner decision (2026-11-07): retain native world text only and stop if unsupported. Do not build the nameplate alternative. The owner is downloading Forever for the final client check. Native-only coloring remains blocked without a supported API. Keep `runtime_ready` false throughout this probe phase.
