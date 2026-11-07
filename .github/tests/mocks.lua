SlashCmdList = {}
SystemFont_NamePlate = "MockLocaleFontFamily"
SystemFont_NamePlate_Outlined = "MockOutlinedLocaleFontFamily"
visible = {}
guilds = {}
players = {}
friends = {}
enemies = {}
labels = {}
messages = {}
combat = false
instance = false
namespace = {}
clock = 0
guids = {}
UIParent = {}
UISpecialFrames = {}
C_Timer = {NewTicker = function(interval, callback)
    timer = {callback = callback, interval = interval, cancelled = false}
    function timer:Cancel() self.cancelled = true end
    return timer
end}

function print(message) messages[#messages + 1] = message end
DEFAULT_CHAT_FRAME = {AddMessage = function(_, message) messages[#messages + 1] = message end}
function InCombatLockdown() return combat end
function IsInInstance() return instance, "none" end
function UnitIsPlayer(unit) return players[unit] end
function UnitIsFriend(_, unit) return friends[unit] end
function UnitCanAttack(_, unit) return enemies[unit] end
function GetGuildInfo(unit) return guilds[unit] end
C_NamePlate = {GetNamePlates = function() return visible end}
C_CVar = {SetCVar = function() error("CVar mutation is forbidden in this fixture") end}
function UnitName() error("Player-name reads are not needed") end
function UnitGUID(unit) return guids[unit] or ("GUID-" .. unit) end
function GetTime() return clock end
function CompactUnitFrame_UpdatePlayerLevelDiff() end
function hooksecurefunc(name, callback)
    hookCalls = (hookCalls or 0) + 1
    local original = _G[name]
    _G[name] = function(...) original(...); callback(...) end
end

function MakePlate(unit, guild, friendly, isPlayer)
    guilds[unit] = guild
    players[unit] = isPlayer == nil or isPlayer
    friends[unit] = friendly == nil or friendly
    enemies[unit] = friendly == false
    local name = {shown = true}
    function name:IsForbidden() return false end
    function name:IsShown() return self.shown end
    function name:SetText() error("Blizzard name must remain unchanged") end
    function name:SetTextColor() error("Blizzard name color must remain unchanged") end
    local frame = {name = name}
    function frame:IsForbidden() return false end
    function frame:CreateFontString()
        local label = {shown = false, parent = self}
        function label:SetFontObject(font) self.font = font end
        function label:SetJustifyH(value) self.justify = value end
        function label:SetWordWrap(value) self.wrap = value end
        function label:SetFontHeight(size) self.size = size end
        function label:ClearAllPoints() self.anchor = nil end
        function label:SetPoint(point, relative, relativePoint, x, y)
            self.anchor = {point, relative, relativePoint, x, y}
        end
        function label:SetTextColor(r, g, b) self.color = {r, g, b} end
        function label:SetText(text) self.text = text end
        function label:Show() self.shown = true end
        function label:Hide() self.shown = false; self.hideCalls = (self.hideCalls or 0) + 1 end
        function label:SetShadowColor(...) self.shadowColor = {...} end
        function label:SetShadowOffset(...) self.shadowOffset = {...} end
        labels[#labels + 1] = label
        return label
    end
    local plate = {UnitFrame = frame, unit = unit}
    function frame:GetNamePlateFrame() return plate end
    frame.PlayerLevelDiffFrame = {alpha = 1}
    function frame.PlayerLevelDiffFrame:IsForbidden() return false end
    function frame.PlayerLevelDiffFrame:GetAlpha() return self.alpha end
    function frame.PlayerLevelDiffFrame:SetAlpha(value) self.alpha = value end
    function plate:IsForbidden() return false end
    function plate:GetUnit() return self.unit end
    return plate
end

local function Widget()
    local widget = {scripts = {}, events = {}}
    function widget:SetScript(event, callback) self.scripts[event] = callback end
    function widget:RegisterEvent(event) self.events[event] = true end
    function widget:SetPoint(...) self.anchor = {...} end
    function widget:ClearAllPoints() self.anchor = nil end
    function widget:SetText(value) self.text = value end
    function widget:SetSize(w, h) self.width = w; self.height = h end
    function widget:SetWidth(w) self.width = w end
    function widget:SetHeight(h) self.height = h end
    function widget:SetJustifyH(value) self.justify = value end
    function widget:SetFrameStrata(value) self.strata = value end
    function widget:SetMinMaxValues(low, high) self.low = low; self.high = high end
    function widget:SetValueStep(step) self.step = step end
    function widget:SetObeyStepOnDrag() end
    function widget:SetChecked(value) self.checked = value end
    function widget:SetEnabled(value) self.enabled = value end
    function widget:GetChecked() return self.checked end
    function widget:SetFontObject(value) self.font = value end
    function widget:SetFontHeight(value) self.size = value end
    function widget:SetTextColor(...) self.color = {...} end
    function widget:SetShadowColor(...) self.shadowColor = {...} end
    function widget:SetShadowOffset(...) self.shadowOffset = {...} end
    function widget:SetValue(value)
        self.value = value
        if self.scripts.OnValueChanged then self.scripts.OnValueChanged(self, value) end
    end
    function widget:Show() self.shown = true end
    function widget:Hide() self.shown = false end
    function widget:CreateFontString() return Widget() end
    return widget
end
function CreateFrame(kind, name)
    local widget = Widget()
    if kind == 'Frame' and name == nil then driver = widget end
    if name == 'FriendlyNameplateGuildSettings' then widget.TitleText = Widget() end
    return widget
end
