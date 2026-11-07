local addonName, Addon = ...
local initialized = false
local widgets = setmetatable({}, {__mode = "k"})
local defaults = {enabled = true, hideEnemyLevels = false, fontSize = 11, gap = 2, color = "66ff99"}
local state = "waiting for login"
local displayed = 0
local ticker
local hiddenLevels = setmetatable({}, {__mode = "k"})
local levelHooked = false

local function polling(wanted)
    if not wanted and ticker then ticker:Cancel(); ticker = nil end
    if wanted and not ticker and C_Timer and C_Timer.NewTicker then
        ticker = C_Timer.NewTicker(1, function() Addon.Refresh() end)
    end
end

local function accessible(value)
    if type(issecretvalue) == "function" and issecretvalue(value) then return false end
    if type(canaccessvalue) == "function" and not canaccessvalue(value) then return false end
    return true
end

local function numberInRange(value, low, high)
    return type(value) == "number" and value == value and value >= low and value <= high
end

local function validColor(value)
    return type(value) == "string" and value:match("^%x%x%x%x%x%x$") ~= nil
end

local function hideAll()
    displayed = 0
    for _, label in pairs(widgets) do
        -- Only our own text is touched; a recycled Blizzard name is never changed.
        pcall(label.Hide, label)
    end
end

local function safeFrame(frame)
    if not accessible(frame) or frame == nil then return false end
    if type(frame.IsForbidden) ~= "function" then return false end
    local forbidden = frame:IsForbidden()
    return accessible(forbidden) and not forbidden
end

local function restoreLevel(level)
    local original = hiddenLevels[level]
    if original ~= nil and safeFrame(level) then
        level:SetAlpha(original)
        hiddenLevels[level] = nil
    end
end

local function updateEnemyLevel(frame)
    if not safeFrame(frame) or type(frame.GetNamePlateFrame) ~= "function" then return end
    local level = frame.PlayerLevelDiffFrame
    if not safeFrame(level) or type(level.GetAlpha) ~= "function" or type(level.SetAlpha) ~= "function" then return end
    -- Restore first: Blizzard reuses these frames for friendly and enemy units.
    restoreLevel(level)
    if not FriendlyNameplateGuildDB.hideEnemyLevels then return end
    local plate = frame:GetNamePlateFrame()
    if not safeFrame(plate) or type(plate.GetUnit) ~= "function" then return end
    local unit = plate:GetUnit()
    if not accessible(unit) or type(unit) ~= "string" or type(UnitCanAttack) ~= "function" then return end
    local enemy = UnitCanAttack("player", unit)
    if not accessible(enemy) or not enemy then return end
    local alpha = level:GetAlpha()
    if not accessible(alpha) or type(alpha) ~= "number" then return end
    hiddenLevels[level] = alpha
    level:SetAlpha(0)
end

function Addon.UpdateEnemyLevels()
    if not initialized then return end
    for level in pairs(hiddenLevels) do pcall(restoreLevel, level) end
    if not FriendlyNameplateGuildDB.hideEnemyLevels then return end
    if not levelHooked and type(hooksecurefunc) == "function" and type(CompactUnitFrame_UpdatePlayerLevelDiff) == "function" then
        hooksecurefunc("CompactUnitFrame_UpdatePlayerLevelDiff", function(frame)
            if FriendlyNameplateGuildDB.hideEnemyLevels then pcall(updateEnemyLevel, frame) end
        end)
        levelHooked = true
    end
    if not C_NamePlate or type(C_NamePlate.GetNamePlates) ~= "function" then return end
    local ok, plates = pcall(C_NamePlate.GetNamePlates)
    if not ok or not accessible(plates) or type(plates) ~= "table"
        or (type(issecrettable) == "function" and issecrettable(plates)) then return end
    for _, plate in ipairs(plates) do
        pcall(function() if safeFrame(plate) then updateEnemyLevel(plate.UnitFrame) end end)
    end
end

local function draw(plate)
    if not safeFrame(plate) then return end
    if type(plate.GetUnit) ~= "function" then return end
    local unit = plate:GetUnit()
    if not accessible(unit) or type(unit) ~= "string" then return end
    local isPlayer = UnitIsPlayer(unit)
    if not accessible(isPlayer) or not isPlayer then return end
    local friendly = UnitIsFriend("player", unit)
    if not accessible(friendly) or not friendly then return end

    local frame = plate.UnitFrame
    if not safeFrame(frame) then return end
    local name = frame.name
    if not safeFrame(name) then return end
    local shown = name:IsShown()
    if not accessible(shown) or not shown then return end

    local guild = GetGuildInfo(unit)
    if not accessible(guild) or type(guild) ~= "string" or guild == "" then return end

    local label = widgets[frame]
    if not label then
        label = frame:CreateFontString(nil, "OVERLAY")
        widgets[frame] = label
        label:SetFontObject(SystemFont_NamePlate)
        label:SetJustifyH("CENTER")
        label:SetWordWrap(false)
    end
    local settings = FriendlyNameplateGuildDB
    -- Font height preserves the client's locale-specific font family.
    label:SetFontHeight(settings.fontSize)
    label:ClearAllPoints()
    label:SetPoint("TOP", name, "BOTTOM", 0, -settings.gap)
    label:SetTextColor(tonumber(settings.color:sub(1, 2), 16) / 255,
        tonumber(settings.color:sub(3, 4), 16) / 255,
        tonumber(settings.color:sub(5, 6), 16) / 255)
    label:SetText("<" .. guild:gsub("|", "||") .. ">")
    label:Show()
    displayed = displayed + 1
end

function Addon.Refresh()
    hideAll()
    if not initialized then return end
    Addon.UpdateEnemyLevels()
    if not FriendlyNameplateGuildDB.enabled then state = "disabled"; polling(false); return end
    if type(InCombatLockdown) ~= "function" or type(IsInInstance) ~= "function" then
        state = "required context API unavailable"; polling(false); return
    end
    local combat = InCombatLockdown()
    if not accessible(combat) or combat then state = "paused in combat"; polling(false); return end
    local instance = IsInInstance()
    if not accessible(instance) or instance then state = "paused in instances"; polling(false); return end
    if not C_NamePlate or type(C_NamePlate.GetNamePlates) ~= "function"
        or type(GetGuildInfo) ~= "function" or type(UnitIsPlayer) ~= "function"
        or type(UnitIsFriend) ~= "function" or not SystemFont_NamePlate then
        state = "required nameplate or guild API unavailable"; polling(false); return
    end
    local ok, plates = pcall(C_NamePlate.GetNamePlates)
    if not ok or not accessible(plates) or type(plates) ~= "table"
        or (type(issecrettable) == "function" and issecrettable(plates)) then
        state = "nameplates unavailable"; polling(false); return
    end
    state = "active"
    for _, plate in ipairs(plates) do
        -- Unsupported/replaced frames fail locally, without an error flood.
        local drawn = pcall(draw, plate)
        if not drawn then state = "active; some nameplates unavailable" end
    end
    polling(#plates > 0)
end

function Addon.Compatibility()
    local metadata = C_AddOns and C_AddOns.GetAddOnMetadata
    local supported = type(metadata) == "function" and tonumber(metadata(addonName, "Interface"))
    if type(GetBuildInfo) ~= "function" or not supported then return false, "Compatibility unavailable" end
    local _, _, _, current = GetBuildInfo()
    if type(current) ~= "number" then return false, "Compatibility unavailable" end
    if current > supported then
        return true, "New WoW Interface " .. current .. "; addon supports " .. supported .. ". Check for an update."
    end
    return false, "WoW Interface " .. current .. " / addon " .. supported
end

function Addon.SetSetting(key, value)
    if not initialized then return false end
    if not (((key == "enabled" or key == "hideEnemyLevels") and type(value) == "boolean")
        or (key == "fontSize" and numberInRange(value, 8, 24))
        or (key == "gap" and numberInRange(value, 0, 20))
        or (key == "color" and validColor(value))) then return false end
    FriendlyNameplateGuildDB[key] = value
    Addon.Refresh()
    if Addon.UpdateSettings then Addon.UpdateSettings() end
    return true
end

function Addon.NameOnly()
    if not C_CVar or type(C_CVar.GetCVar) ~= "function" then return nil end
    local ok, value = pcall(C_CVar.GetCVar, "nameplateShowOnlyNameForFriendlyPlayerUnits")
    if not ok or not accessible(value) then return nil end
    if value == "1" then return true end
    if value == "0" then return false end
    return nil
end

function Addon.SetNameOnly(enabled)
    -- This game setting is changed only by an explicit click, never at login.
    if type(enabled) ~= "boolean" or Addon.NameOnly() == nil then return false end
    if type(InCombatLockdown) ~= "function" then return false end
    local combat = InCombatLockdown()
    if not accessible(combat) or combat then
        print("FriendlyNameplateGuild: change name-only mode outside combat.")
        return false
    end
    if not C_CVar or type(C_CVar.SetCVar) ~= "function" then return false end
    local ok = pcall(C_CVar.SetCVar, "nameplateShowOnlyNameForFriendlyPlayerUnits", enabled and "1" or "0")
    ok = ok and Addon.NameOnly() == enabled
    if not ok then print("FriendlyNameplateGuild: WoW could not change name-only mode.") end
    Addon.Refresh()
    return ok
end

function Addon.Reset()
    for key, value in pairs(defaults) do FriendlyNameplateGuildDB[key] = value end
    Addon.Refresh()
    if Addon.UpdateSettings then Addon.UpdateSettings() end
end

function Addon.Initialize()
    if initialized then return end
    if type(FriendlyNameplateGuildDB) ~= "table" then FriendlyNameplateGuildDB = {} end
    local db = FriendlyNameplateGuildDB
    if type(db.enabled) ~= "boolean" then db.enabled = defaults.enabled end
    if type(db.hideEnemyLevels) ~= "boolean" then db.hideEnemyLevels = defaults.hideEnemyLevels end
    if not numberInRange(db.fontSize, 8, 24) then db.fontSize = defaults.fontSize end
    if not numberInRange(db.gap, 0, 20) then db.gap = defaults.gap end
    if not validColor(db.color) then db.color = defaults.color end
    initialized = true
    Addon.Refresh()
    local outdated, message = Addon.Compatibility()
    if outdated then print("FriendlyNameplateGuild: " .. message) end
end

local function say(message)
    print("FriendlyNameplateGuild: " .. message)
end

local help = "/fng (settings) | on | off | size 8-24 | gap 0-20 | color RRGGBB | status | reset"
function Addon.Command(message)
    if not initialized then say("waiting for addon settings to load"); return end
    local command, value = (message or ""):match("^%s*(%S*)%s*(.-)%s*$")
    command = command:lower()
    local db = FriendlyNameplateGuildDB
    if command == "" or command == "settings" then
        if Addon.ShowSettings then Addon.ShowSettings() end
        return
    elseif command == "on" then db.enabled = true
    elseif command == "off" then db.enabled = false
    elseif command == "size" and numberInRange(tonumber(value), 8, 24) then db.fontSize = tonumber(value)
    elseif command == "gap" and numberInRange(tonumber(value), 0, 20) then db.gap = tonumber(value)
    elseif command == "color" and validColor(value) then db.color = value:lower()
    elseif command == "reset" then
        for key, default in pairs(defaults) do db[key] = default end
    elseif command == "status" then
        Addon.Refresh()
        say(state .. "; visible guild labels=" .. displayed .. "; size=" .. db.fontSize .. "; gap=" .. db.gap .. "; color=#" .. db.color)
        say("Requires friendly player nameplates; first test build pauses in combat and instances.")
        return
    else say(help); return end
    Addon.Refresh()
    if Addon.UpdateSettings then Addon.UpdateSettings() end
    say(state .. ". " .. help)
end

local driver = CreateFrame("Frame")
driver:SetScript("OnEvent", function(_, event, arg)
    if event == "CVAR_UPDATE" then
        if not accessible(arg) or type(arg) ~= "string" then return end
        local key = arg:lower()
        if key ~= "nameplateshowonlynameforfriendlyplayerunits" and key ~= "nameplateshowfriendlyplayers" then return end
        Addon.Refresh()
        if Addon.UpdateSettings then Addon.UpdateSettings() end
    elseif event == "ADDON_LOADED" and arg == addonName then
        Addon.Initialize()
    elseif event == "PLAYER_LOGIN" then
        Addon.Initialize()
    elseif event == "NAME_PLATE_UNIT_REMOVED" then
        -- The Blizzard handler may not yet have released its pooled frame.
        hideAll()
    else
        Addon.Refresh()
    end
end)
-- No per-frame handler. Retry visible guild data at most once per second;
-- events restart polling when plates appear or the supported context returns.
for _, event in ipairs({"ADDON_LOADED", "PLAYER_LOGIN", "PLAYER_ENTERING_WORLD",
    "NAME_PLATE_UNIT_ADDED", "NAME_PLATE_UNIT_REMOVED", "UNIT_NAME_UPDATE", "UNIT_FACTION",
    "PLAYER_GUILD_UPDATE", "PLAYER_REGEN_DISABLED", "PLAYER_REGEN_ENABLED", "ZONE_CHANGED_NEW_AREA"}) do
    pcall(driver.RegisterEvent, driver, event)
end
pcall(driver.RegisterEvent, driver, "CVAR_UPDATE")
SLASH_FRIENDLYNAMEPLATEGUILD1 = "/fng"
SLASH_FRIENDLYNAMEPLATEGUILD2 = "/friendlynameplateguild"
SlashCmdList.FRIENDLYNAMEPLATEGUILD = Addon.Command
