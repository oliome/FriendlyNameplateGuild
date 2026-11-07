-- Read-only diagnostics. No roster requests, identity logging, hooks or CVar writes.
local _, Probe = ...
local cvars = {
    "UnitNameFriendlyPlayerName",
    "UnitNameOwn",
    "nameplateShowFriends",
    "nameplateShowFriendlyPlayers",
    "nameplateShowOnlyNameForFriendlyPlayerUnits",
    "nameplateUseClassColorForFriendlyPlayerUnitNames",
    "nameplateShowFriendlyClassColor",
}

local function readable(value)
    -- Never stringify or branch on an inaccessible value.
    if type(issecretvalue) == "function" and issecretvalue(value) then
        return false
    end
    if type(canaccessvalue) == "function" and not canaccessvalue(value) then
        return false
    end
    return true
end

local function display(value)
    if not readable(value) then return "restricted" end
    local kind = type(value)
    if kind == "nil" then return "unavailable" end
    if kind == "string" or kind == "number" or kind == "boolean" then
        return tostring(value)
    end
    return "unavailable"
end

local function readCall(fn, ...)
    if type(fn) ~= "function" then return "unavailable" end
    local ok, result = pcall(fn, ...)
    if not ok then return "unavailable" end
    return display(result)
end

function Probe.Collect()
    local lines = {"BetterForeverNames Probe 0.1.0 (read-only)"}
    local function add(key, value)
        lines[#lines + 1] = key .. "=" .. value
    end

    local ok, version, build, date, interface = false
    if type(GetBuildInfo) == "function" then
        ok, version, build, date, interface = pcall(GetBuildInfo)
    end
    if ok then
        add("client.version", display(version))
        add("client.build", display(build))
        add("client.date", display(date))
        add("client.interface", display(interface))
    else
        add("client", "unavailable")
    end
    -- Interface is reported, never inferred from the patch string or project ID.
    add("client.projectID", display(WOW_PROJECT_ID))

    for _, key in ipairs(cvars) do
        add("cvar." .. key, readCall(C_CVar and C_CVar.GetCVar, key))
    end
    add("api.nameplates", type(C_NamePlate) == "table" and
        type(C_NamePlate.GetNamePlateForUnit) == "function" and "present" or "unavailable")

    -- Only probe accessible Lua nameplates, never request forbidden plates.
    local status = "unavailable"
    if C_NamePlate and type(C_NamePlate.GetNamePlateForUnit) == "function" then
        local queried, result = pcall(function()
            local plate = C_NamePlate.GetNamePlateForUnit("target", false)
            if not readable(plate) then return "restricted" end
            if plate == nil then return "absent" end
            -- Fail closed if the client's forbidden-frame predicate is missing.
            if type(plate.IsForbidden) ~= "function" then return "unavailable" end
            local forbidden = plate:IsForbidden()
            if not readable(forbidden) then return "restricted" end
            if forbidden then return "forbidden" end
            local frame = plate.UnitFrame
            if not readable(frame) then return "restricted" end
            if frame == nil then return "no-unit-frame" end
            if type(frame.IsForbidden) ~= "function" then return "unavailable" end
            local frameForbidden = frame:IsForbidden()
            if not readable(frameForbidden) then return "restricted" end
            if frameForbidden then return "forbidden" end
            local name = frame.name
            if not readable(name) then return "restricted" end
            if name == nil then return "no-name-text" end
            -- Presence only: never read the target's name or set its text/color.
            return "lua-name-text-present"
        end)
        if queried then status = result end
    end
    add("target.nameplate", status)
    add("native.per-player-color", "no-supported-api-identified-in-source-review")
    lines[#lines + 1] = "A Lua nameplate is not proof that native world text is editable."
    return table.concat(lines, "\n")
end

local panel
local function showReport()
    if not panel then
        panel = CreateFrame("Frame", "BetterForeverNamesProbeReport", UIParent, "BasicFrameTemplateWithInset")
        panel:SetSize(660, 490)
        panel:SetPoint("CENTER")
        panel.TitleText:SetText("BetterForeverNames — read-only probe")
        local scroll = CreateFrame("ScrollFrame", nil, panel, "UIPanelScrollFrameTemplate")
        scroll:SetPoint("TOPLEFT", 14, -34)
        scroll:SetPoint("BOTTOMRIGHT", -32, 14)
        local edit = CreateFrame("EditBox", nil, scroll)
        edit:SetMultiLine(true)
        edit:SetFontObject(ChatFontNormal)
        edit:SetWidth(600)
        edit:SetAutoFocus(false)
        edit:SetScript("OnEscapePressed", function() panel:Hide() end)
        scroll:SetScrollChild(edit)
        panel.edit = edit
    end
    panel.edit:SetText(Probe.Collect())
    panel:Show()
    panel.edit:SetFocus()
    panel.edit:HighlightText()
end

SLASH_BETTERFOREVERNAMESPROBE1 = "/bfnprobe"
SlashCmdList.BETTERFOREVERNAMESPROBE = function(message)
    local ok = pcall(showReport)
    if not ok then
        print("BetterForeverNames: report window unavailable; printing read-only diagnostics.")
        print(Probe.Collect())
    end
end
