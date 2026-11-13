local _, Addon = ...
local window, syncing, category
local panelTitle = "FriendlyNameplateGuild"

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
    window.showInInstances:SetChecked(db.showInInstances)
    window.hideEnemyLevels:SetChecked(db.hideEnemyLevels)
    local nameOnly = Addon.NameOnly()
    window.nameOnly:SetChecked(nameOnly == true)
    window.nameOnly:SetEnabled(nameOnly ~= nil)
    window.size:SetValue(db.fontSize)
    window.gap:SetValue(db.gap)
    window.retry:SetValue(db.retryMs)
    window.sizeText:SetText("Font size: " .. db.fontSize)
    window.gapText:SetText("Space below name: " .. db.gap)
    window.retryText:SetText("Guild label retry interval: " .. db.retryMs .. " ms")
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

local function buildSettings(embedded)
    if not window then
        local template
        if not embedded then template = "BasicFrameTemplateWithInset" end
        window = CreateFrame("Frame", "FriendlyNameplateGuildSettings", UIParent, template)
        Addon.SettingsWindow = window
        window:Hide()
        if not embedded then
            window:SetSize(410, 530)
            window:SetPoint("CENTER")
            window:SetFrameStrata("DIALOG")
            window.TitleText:SetText(panelTitle)
            if UISpecialFrames then table.insert(UISpecialFrames, "FriendlyNameplateGuildSettings") end
        end
        window:SetScript("OnShow", Addon.UpdateSettings)
        window.enabled = CreateFrame("CheckButton", nil, window, "UICheckButtonTemplate")
        window.enabled:SetPoint("TOPLEFT", 16, -35)
        text(window, "Show guild names", 52, -44)
        window.enabled:SetScript("OnClick", function(self) Addon.SetSetting("enabled", self:GetChecked()) end)
        window.showInInstances = CreateFrame("CheckButton", nil, window, "UICheckButtonTemplate")
        window.showInInstances:SetPoint("TOPLEFT", 16, -68)
        text(window, "Show guild names in instances", 52, -77)
        window.showInInstances:SetScript("OnClick", function(self)
            Addon.SetSetting("showInInstances", self:GetChecked())
        end)
        window.nameOnly = CreateFrame("CheckButton", nil, window, "UICheckButtonTemplate")
        window.nameOnly:SetPoint("TOPLEFT", 16, -101)
        text(window, "Show names only (hide friendly health bars)", 52, -110)
        window.nameOnly:SetScript("OnClick", function(self)
            Addon.SetNameOnly(self:GetChecked())
            Addon.UpdateSettings()
        end)
        window.hideEnemyLevels = CreateFrame("CheckButton", nil, window, "UICheckButtonTemplate")
        window.hideEnemyLevels:SetPoint("TOPLEFT", 16, -134)
        text(window, "Hide enemy level badges", 52, -143)
        window.hideEnemyLevels:SetScript("OnClick", function(self) Addon.SetSetting("hideEnemyLevels", self:GetChecked()) end)
        window.size, window.sizeText = slider(window, "fontSize", "Font size", -178, 8, 24)
        window.gap, window.gapText = slider(window, "gap", "Space below name", -233, 0, 20)
        window.retry, window.retryText = slider(window, "retryMs", "Guild label retry interval",
            -288, Addon.retryRange.min, Addon.retryRange.max)
        window.color = CreateFrame("Button", nil, window, "UIPanelButtonTemplate")
        window.color:SetSize(190, 26)
        window.color:SetPoint("TOPLEFT", 20, -344)
        window.color:SetScript("OnClick", chooseColor)
        text(window, "Preview", 22, -385)
        window.sample = text(window, "Friendly Player", 150, -399, "GameFontHighlight")
        window.preview = window:CreateFontString(nil, "OVERLAY")
        window.preview:SetFontObject(SystemFont_NamePlate_Outlined or SystemFont_NamePlate)
        window.preview:SetShadowColor(0, 0, 0, 1)
        window.preview:SetShadowOffset(1, -1)
        window.preview:SetText("<Your Guild>")
        window.status = text(window, "", 22, -455, "GameFontHighlightSmall")
        window.status:SetWidth(365)
        window.status:SetJustifyH("LEFT")
        local note = text(window, "Guild labels require accessible friendly player nameplates.", 22, -490, "GameFontDisableSmall")
        note:SetWidth(365)
        note:SetJustifyH("LEFT")
        window.reset = CreateFrame("Button", nil, window, "UIPanelButtonTemplate")
        window.reset:SetSize(100, 24)
        window.reset:SetPoint("TOPLEFT", 290, -344)
        window.reset:SetText("Reset")
        window.reset:SetScript("OnClick", Addon.Reset)
    end
end

function Addon.RegisterSettings()
    if window or not Settings or not Settings.RegisterCanvasLayoutCategory
        or not Settings.RegisterAddOnCategory or not Settings.OpenToCategory then return end
    buildSettings(true)
    category = Settings.RegisterCanvasLayoutCategory(window, panelTitle)
    Settings.RegisterAddOnCategory(category)
end

function Addon.ShowSettings()
    Addon.RegisterSettings()
    if category then
        Settings.OpenToCategory(category:GetID())
    else
        buildSettings(false)
        Addon.UpdateSettings()
        window:Show()
    end
end
