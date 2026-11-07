local _, Addon = ...
local window, syncing

local function text(parent, value, x, y, font)
    local label = parent:CreateFontString(nil, "OVERLAY", font or "GameFontNormal")
    label:SetPoint("TOPLEFT", x, y)
    label:SetText(value)
    return label
end

local function rgb(hex)
    return tonumber(hex:sub(1, 2), 16) / 255, tonumber(hex:sub(3, 4), 16) / 255, tonumber(hex:sub(5, 6), 16) / 255
end

local function slider(parent, key, title, y, low, high)
    local caption = text(parent, title, 22, y)
    local control = CreateFrame("Slider", "FriendlyNameplateGuild_" .. key, parent, "OptionsSliderTemplate")
    control:SetPoint("TOPLEFT", 24, y - 24)
    control:SetWidth(350)
    control:SetMinMaxValues(low, high)
    control:SetValueStep(1)
    control:SetObeyStepOnDrag(true)
    control:SetScript("OnValueChanged", function(_, value)
        if not syncing then Addon.SetSetting(key, math.floor(value + 0.5)) end
    end)
    return control, caption
end

function Addon.UpdateSettings()
    if not window then return end
    syncing = true
    local db = FriendlyNameplateGuildDB
    window.enabled:SetChecked(db.enabled)
    window.hideEnemyLevels:SetChecked(db.hideEnemyLevels)
    local nameOnly = Addon.NameOnly()
    window.nameOnly:SetChecked(nameOnly == true)
    window.nameOnly:SetEnabled(nameOnly ~= nil)
    window.size:SetValue(db.fontSize)
    window.gap:SetValue(db.gap)
    window.sizeText:SetText("Font size: " .. db.fontSize)
    window.gapText:SetText("Space below name: " .. db.gap)
    window.color:SetText("|cff" .. db.color .. "Choose guild color|r")
    window.preview:SetFontHeight(db.fontSize)
    window.preview:SetTextColor(rgb(db.color))
    window.preview:ClearAllPoints()
    window.preview:SetPoint("TOP", window.sample, "BOTTOM", 0, -db.gap)
    local _, status = Addon.Compatibility()
    window.status:SetText(status)
    syncing = false
end

local function chooseColor()
    if not ColorPickerFrame and C_AddOns and C_AddOns.LoadAddOn then
        C_AddOns.LoadAddOn("Blizzard_ColorPickerFrame")
    end
    if not ColorPickerFrame or not ColorPickerFrame.SetupColorPickerAndShow then
        print("FriendlyNameplateGuild: color picker unavailable; use /fng color RRGGBB.")
        return
    end
    local original = FriendlyNameplateGuildDB.color
    local r, g, b = rgb(original)
    ColorPickerFrame:SetupColorPickerAndShow({r = r, g = g, b = b, hasOpacity = false,
        swatchFunc = function()
            local red, green, blue = ColorPickerFrame:GetColorRGB()
            Addon.SetSetting("color", string.format("%02x%02x%02x", math.floor(red * 255 + 0.5),
                math.floor(green * 255 + 0.5), math.floor(blue * 255 + 0.5)))
        end,
        cancelFunc = function() Addon.SetSetting("color", original) end,
    })
end

function Addon.ShowSettings()
    -- Build the entire UI only when requested; use Blizzard widgets, no libraries.
    if not window then
        window = CreateFrame("Frame", "FriendlyNameplateGuildSettings", UIParent, "BasicFrameTemplateWithInset")
        Addon.SettingsWindow = window
        window:SetSize(410, 508)
        window:SetPoint("CENTER")
        window:SetFrameStrata("DIALOG")
        window.TitleText:SetText("FriendlyNameplateGuild")
        if UISpecialFrames then table.insert(UISpecialFrames, "FriendlyNameplateGuildSettings") end
        window.enabled = CreateFrame("CheckButton", nil, window, "UICheckButtonTemplate")
        window.enabled:SetPoint("TOPLEFT", 16, -35)
        text(window, "Show guild names", 52, -44)
        window.enabled:SetScript("OnClick", function(self) Addon.SetSetting("enabled", self:GetChecked()) end)
        window.nameOnly = CreateFrame("CheckButton", nil, window, "UICheckButtonTemplate")
        window.nameOnly:SetPoint("TOPLEFT", 16, -68)
        text(window, "Show names only (hide friendly health bars)", 52, -77)
        window.nameOnly:SetScript("OnClick", function(self)
            Addon.SetNameOnly(self:GetChecked())
            Addon.UpdateSettings()
        end)
        window.hideEnemyLevels = CreateFrame("CheckButton", nil, window, "UICheckButtonTemplate")
        window.hideEnemyLevels:SetPoint("TOPLEFT", 16, -101)
        text(window, "Hide enemy level badges", 52, -110)
        window.hideEnemyLevels:SetScript("OnClick", function(self) Addon.SetSetting("hideEnemyLevels", self:GetChecked()) end)
        window.size, window.sizeText = slider(window, "fontSize", "Font size", -154, 8, 24)
        window.gap, window.gapText = slider(window, "gap", "Space below name", -219, 0, 20)
        window.color = CreateFrame("Button", nil, window, "UIPanelButtonTemplate")
        window.color:SetSize(190, 26)
        window.color:SetPoint("TOPLEFT", 20, -283)
        window.color:SetScript("OnClick", chooseColor)
        text(window, "Preview", 22, -328)
        window.sample = text(window, "Friendly Player", 150, -348, "GameFontHighlight")
        window.preview = window:CreateFontString(nil, "OVERLAY")
        window.preview:SetFontObject(SystemFont_NamePlate)
        window.preview:SetText("<Your Guild>")
        window.status = text(window, "", 22, -404, "GameFontHighlightSmall")
        window.status:SetWidth(365)
        window.status:SetHeight(44)
        window.status:SetJustifyH("LEFT")
        local note = text(window, "Guild labels require friendly player nameplates.\nGuild labels pause in combat and instances; restricted plates are skipped.", 22, -456, "GameFontDisableSmall")
        note:SetWidth(365)
        note:SetJustifyH("LEFT")
        window.reset = CreateFrame("Button", nil, window, "UIPanelButtonTemplate")
        window.reset:SetSize(100, 24)
        window.reset:SetPoint("TOPRIGHT", -20, -283)
        window.reset:SetText("Reset")
        window.reset:SetScript("OnClick", Addon.Reset)
    end
    Addon.UpdateSettings()
    window:Show()
end
