# Current implementation plan

## Accepted scope — 2026-11-07

The owner approved guild names underneath friendly player nameplates as an alternative after the native-overhead investigation. This supersedes the earlier native-only stop decision **for guild labels**. Native name recoloring remains unsupported in our research; do not replace native text or imply that guild labels solve native recoloring.

## Implemented preview: 0.2.0

- A separate guild FontString beneath the existing friendly player name.
- One shared guild-text color; configurable size, vertical spacing, on/off, and reset through `/bfn`.
- SavedVariables with validation and defaults.
- Skip NPCs, hostile players, missing guild data, hidden name text, and forbidden/restricted frames.
- Hide in combat and instances for this initial preview; recover when the supported context returns.
- Refresh visible plates once per second and on relevant events, hide on removal, and reuse owned text safely with pooled Blizzard frames.
- Leave native names, existing nameplate name colors, CVars, social data, and Blizzard frame functions unchanged.
- Execute the actual production Lua in tests, including delayed data, stale labels, pooling, restricted inputs, settings, and context changes.

## Next: in-game validation

Install the preview ZIP in Forever build 70862 / Interface 16001, enable friendly player nameplates, and approach a guilded friendly player in the open world. Check a visible label, an unguilded player, hostile players/NPCs, target changes, range transitions, delayed guild data, off/on, font/color/gap controls, `/reload`, and full logout/login. Confirm labels hide in combat/instances and return afterward. Check Lua errors and interactions with other nameplate addons.

Record results and screenshots in IN_GAME_VALIDATION.md. A working nameplate from the earlier diagnostic probe does not prove the new guild-label renderer works. Confirm `GetGuildInfo(nameplateUnit)` returns readable guild data on this client. If an API or anchor fails, fix the preview and retest before promotion.

## Then: release/update automation

The production release gate stays closed (`runtime_ready: false`) until these checks pass in-game. `--package --preview` only creates a clearly named desktop test ZIP and does not modify readiness. Provision a trustworthy live Interface feed and validate it independently. The existing scheduled pipeline tests candidate metadata before packaging/publishing; API changes still require code fixes and validation. See AUTOMATION.md.

Additional friend/class color rules and broader contexts are future scope; do not silently extend this guild-label preview to those features.
