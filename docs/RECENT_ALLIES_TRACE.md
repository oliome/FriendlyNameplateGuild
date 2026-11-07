# Recent Allies color investigation — 2026-11-07

Subsequent scope change: the owner approved separate guild labels under friendly player nameplates. That feature is implemented in the 0.2.0 preview; the findings below still apply to native overhead recoloring.

## Result

Recent Allies has built-in client support that does not expose an equivalent per-player native-name-color setter to addons. The source review supports an **inference** that its native overhead tint is chosen inside the client, rather than by a Lua hook an addon can reuse. The engine renderer itself has not been traced or modified, and no in-game recoloring experiment has been performed.

The owner's second probe, with friendly player nameplates enabled, found `target.nameplate=lua-name-text-present`. That confirms the editable Lua surface exists in that configuration. It does not establish access to native world text. Native-only remains the requirement.

## What was inspected

- Local installation: `C:/Program Files (x86)/World of Warcraft/_forever_`; `.flavor.info` identifies `wowf`. No game files were changed and no game process was running on this computer during the initial installation inspection. The owner supplied live probe results from their desktop separately.
- A read-only checkout of the Forever UI source mirror, version `1.60.1.70862`, commit `9dc84f0d3bbae1768ac3405b3716000bd93eda06`, matching the owner's reported build.
- [Machine-readable review results](validation/2026-11-07-recent-allies-source-review.json), including the API function list and literal color-symbol search. The checkout itself is ignored by Git under `.research/`.

## Trace through the exposed UI

1. [SharedXMLBase/Color.lua](https://github.com/Gethe/wow-ui-source/blob/9dc84f0d3bbae1768ac3405b3716000bd93eda06/Interface/AddOns/Blizzard_SharedXMLBase/Color.lua#L80) calls `C_UIColor.GetColors()`. For each exported database color, it creates a Lua color object from RGBA components and publishes it under its base tag. This is a copy of exported color data, not a demonstrated write-through interface to the client's color database. Changing a Lua global or ColorMixin cannot be assumed to change the native renderer.
2. The full snapshot contains no literal `RECENT_ALLY_FONT_COLOR` reference in Lua/XML. That does not exclude dynamically constructed references or native code. Earlier first-hand addon notes report a database color with that tag, approximately RGB `(0.325, 0.788, 1)`, but we have not read the installed client's GlobalColor record or verified its live value ourselves. The loader above explains how such a database color would become a Lua global.
3. [RecentAlliesDocumentation.lua](https://github.com/Gethe/wow-ui-source/blob/9dc84f0d3bbae1768ac3405b3716000bd93eda06/Interface/AddOns/Blizzard_APIDocumentationGenerated/RecentAlliesDocumentation.lua) exposes membership queries, cached data/search, system status, notes, pins, and a restricted data request. It exposes no native name-color setter and no function to add an arbitrary guild member or friend to Recent Allies. Note/pin setters do not establish color control.
4. [CompactUnitFrame_UpdateName](https://github.com/Gethe/wow-ui-source/blob/9dc84f0d3bbae1768ac3405b3716000bd93eda06/Interface/AddOns/Blizzard_UnitFrame/Shared/CompactUnitFrame.lua#L826) handles Lua frame names. It prioritizes enabled class colors ahead of the selection-color branch, which obtains its RGB from the engine's `UnitSelectionColor()`. This function is a getter; the Lua code does not specify a Recent Allies color itself. Other branches handle mouseover, tap/death, and default white.
5. [NamePlateUnitFrameMixin:UpdateNameClassColor](https://github.com/Gethe/wow-ui-source/blob/9dc84f0d3bbae1768ac3405b3716000bd93eda06/Interface/AddOns/Blizzard_NamePlates/Blizzard_NamePlateUnitFrame.lua#L614) enables the class-color path for friendly players based on the relevant CVar. The owner's second report has that CVar enabled. Its target nameplate therefore is not a clean experiment for native Recent Allies tinting, and may use class color instead of selection color.

## Implication for BetterForeverNames

Blizzard can apply a native color based on internal relationship state even when addon Lua has no setter for that state or rendering color. Hooking `C_RecentAllies.IsRecentAllyByGUID`, replacing `RECENT_ALLY_FONT_COLOR`, or changing a Lua nameplate does not demonstrate control of that internal behavior. Do not ship such an approach as native overhead support without an actual supported API and reproducible evidence.

There is currently no supported route identified to assign separate native overhead colors to friends, guild members, and classes. Keep runtime development stopped under the owner's native-only choice. The earlier probe was too narrow to reach a strong conclusion on its own; this targeted source investigation supplies the Recent Allies-specific evidence while leaving the internal renderer explicitly unverified.
