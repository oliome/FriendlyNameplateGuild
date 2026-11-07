std = "lua51"
max_line_length = false
exclude_files = { ".github/", ".release/", ".tooling/" }
ignore = { "211", "212", "213" }
read_globals = {
    "C_AddOns", "C_CVar", "C_NamePlate", "C_Timer", "ColorPickerFrame",
    "CreateFrame", "GetBuildInfo", "GetGuildInfo", "InCombatLockdown", "IsInInstance",
    "SystemFont_NamePlate", "UIParent", "UISpecialFrames", "UnitIsFriend", "UnitIsPlayer",
    "canaccessvalue", "issecrettable", "issecretvalue", "hooksecurefunc",
    "CompactUnitFrame_UpdatePlayerLevelDiff", "UnitCanAttack",
    "SystemFont_NamePlate_Outlined", "GetTime", "UnitGUID",
    "DEFAULT_CHAT_FRAME",
}
globals = { "FriendlyNameplateGuildDB", "SlashCmdList", "SLASH_FRIENDLYNAMEPLATEGUILD1", "SLASH_FRIENDLYNAMEPLATEGUILD2" }
