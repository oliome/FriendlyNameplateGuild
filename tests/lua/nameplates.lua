SlashCmdList = {}
SystemFont_NamePlate = "MockLocaleFontFamily"
visible = {}
guilds = {}
players = {}
friends = {}
labels = {}
messages = {}
combat = false
instance = false
namespace = {}

function print(message) messages[#messages + 1] = message end
function InCombatLockdown() return combat end
function IsInInstance() return instance, "none" end
function UnitIsPlayer(unit) return players[unit] end
function UnitIsFriend(_, unit) return friends[unit] end
function GetGuildInfo(unit) return guilds[unit] end
C_NamePlate = {GetNamePlates = function() return visible end}
C_CVar = {SetCVar = function() error("CVar mutation is forbidden in this fixture") end}
function UnitName() error("Player-name reads are not needed") end
function UnitGUID() error("GUID reads are not needed") end
function hooksecurefunc() error("Blizzard hooks are not needed") end

function MakePlate(unit, guild, friendly, isPlayer)
    guilds[unit] = guild
    players[unit] = isPlayer == nil or isPlayer
    friends[unit] = friendly == nil or friendly
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
        function label:Hide() self.shown = false end
        labels[#labels + 1] = label
        return label
    end
    local plate = {UnitFrame = frame, unit = unit}
    function plate:IsForbidden() return false end
    function plate:GetUnit() return self.unit end
    return plate
end

function CreateFrame()
    driver = {scripts = {}, events = {}}
    function driver:SetScript(event, callback) self.scripts[event] = callback end
    function driver:RegisterEvent(event) self.events[event] = true end
    return driver
end
