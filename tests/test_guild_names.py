from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]


class GuildNamesTests(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute((ROOT / 'tests/lua/nameplates.lua').read_text(encoding='utf-8'))
        source = (ROOT / 'addon/FriendlyNameplateGuild/GuildNames.lua').read_text(encoding='utf-8')
        self.lua.execute('assert(loadstring(...))("FriendlyNameplateGuild", namespace)', source)
        settings = (ROOT / 'addon/FriendlyNameplateGuild/Settings.lua').read_text(encoding='utf-8')
        self.lua.execute('assert(loadstring(...))("FriendlyNameplateGuild", namespace)', settings)

    def run_lua(self, code):
        self.lua.execute(code)

    def value(self, code):
        return self.lua.eval(code)

    def start(self, setup="visible = {MakePlate('nameplate1', 'Azeroth Explorers')}"):
        self.run_lua(setup)
        self.run_lua("driver.scripts.OnEvent(driver, 'ADDON_LOADED', 'FriendlyNameplateGuild')")

    def test_friendly_player_guild_appears_below_existing_name(self):
        self.start()
        self.assertEqual(self.value('labels[1].text'), '<Azeroth Explorers>')
        self.assertTrue(self.value('labels[1].shown'))
        self.assertEqual(self.value('labels[1].anchor[1]'), 'TOP')
        self.assertEqual(self.value('labels[1].anchor[3]'), 'BOTTOM')
        self.assertEqual(self.value('labels[1].anchor[5]'), -2)
        self.assertTrue(self.value('labels[1].anchor[2] == visible[1].UnitFrame.name'))
        self.assertEqual(self.value('labels[1].font'), 'MockLocaleFontFamily')

    def test_unguilded_hostile_and_npc_have_no_label(self):
        self.start("visible = {MakePlate('a', nil), MakePlate('b', 'Hostile Guild', false), MakePlate('c', 'NPC Guild', true, false)}")
        self.assertEqual(self.value('#labels'), 0)

    def test_newly_cached_guild_is_retried_without_roster_scan(self):
        self.start("visible = {MakePlate('nameplate1', nil)}")
        self.run_lua("guilds.nameplate1 = 'Loaded Later'; timer.callback()")
        self.assertEqual(self.value('labels[1].text'), '<Loaded Later>')

    def test_guild_change_and_departure_clear_stale_text(self):
        self.start()
        self.run_lua("guilds.nameplate1 = 'New Guild'; namespace.Refresh()")
        self.assertEqual(self.value('labels[1].text'), '<New Guild>')
        self.run_lua('guilds.nameplate1 = nil; namespace.Refresh()')
        self.assertFalse(self.value('labels[1].shown'))

    def test_pooled_frame_reuse_does_not_keep_previous_guild(self):
        self.start()
        self.run_lua("driver.scripts.OnEvent(driver, 'NAME_PLATE_UNIT_REMOVED', 'nameplate1')")
        self.assertFalse(self.value('labels[1].shown'))
        self.run_lua("guilds.nameplate2 = 'Other Guild'; players.nameplate2 = true; friends.nameplate2 = true; visible[1].unit = 'nameplate2'; namespace.Refresh()")
        self.assertEqual(self.value('#labels'), 1)
        self.assertEqual(self.value('labels[1].text'), '<Other Guild>')

    def test_combat_and_instances_hide_and_restore_owned_labels(self):
        self.start()
        for flag in ('combat', 'instance'):
            self.run_lua(f'{flag} = true; namespace.Refresh()')
            self.assertFalse(self.value('labels[1].shown'))
            self.run_lua(f'{flag} = false; namespace.Refresh()')
            self.assertTrue(self.value('labels[1].shown'))

    def test_hidden_name_and_removed_plate_hide_guild_line(self):
        self.start()
        self.run_lua('visible[1].UnitFrame.name.shown = false; namespace.Refresh()')
        self.assertFalse(self.value('labels[1].shown'))
        self.run_lua('visible[1].UnitFrame.name.shown = true; namespace.Refresh(); visible = {}; namespace.Refresh()')
        self.assertFalse(self.value('labels[1].shown'))

    def test_forbidden_plate_is_not_read(self):
        self.start("visible = {setmetatable({IsForbidden = function() return true end}, {__index = function() error('forbidden frame read') end})}")
        self.assertEqual(self.value('#labels'), 0)

    def test_restricted_guild_value_is_not_used(self):
        self.run_lua("secret = setmetatable({}, {__tostring = function() error('secret used') end}); issecretvalue = function(v) return rawequal(v, secret) end")
        self.start("visible = {MakePlate('nameplate1', secret)}")
        self.assertEqual(self.value('#labels'), 0)

    def test_erroring_plate_does_not_block_other_players(self):
        self.start("visible = {setmetatable({}, {__index = function() error('replaced plate') end}), MakePlate('a', 'Readable')}")
        self.assertEqual(self.value('labels[1].text'), '<Readable>')

    def test_missing_required_api_hides_existing_labels(self):
        self.start()
        self.run_lua('GetGuildInfo = nil; namespace.Refresh()')
        self.assertFalse(self.value('labels[1].shown'))
        self.run_lua("namespace.Command('status')")
        self.assertIn('API unavailable', self.value('messages[#messages - 1]'))

    def test_commands_change_only_owned_labels(self):
        self.start()
        self.run_lua("namespace.Command('size 16'); namespace.Command('gap 5'); namespace.Command('color ff8000')")
        self.assertEqual(self.value('labels[1].size'), 16)
        self.assertEqual(self.value('labels[1].anchor[5]'), -5)
        self.assertEqual(self.value('labels[1].color[1]'), 1)
        self.assertAlmostEqual(self.value('labels[1].color[2]'), 128 / 255)
        self.run_lua("namespace.Command('off')")
        self.assertFalse(self.value('labels[1].shown'))
        self.run_lua("namespace.Command('on')")
        self.assertTrue(self.value('labels[1].shown'))

    def test_invalid_settings_commands_and_reset(self):
        self.run_lua("FriendlyNameplateGuildDB = {enabled = 'yes', fontSize = 100, gap = -5, color = 'oops'}")
        self.start()
        self.assertEqual(self.value('FriendlyNameplateGuildDB.fontSize'), 11)
        self.run_lua("namespace.Command('size nan'); namespace.Command('size 25'); namespace.Command('gap -1'); namespace.Command('color invalid')")
        self.assertEqual(self.value('FriendlyNameplateGuildDB.fontSize'), 11)
        self.assertEqual(self.value('FriendlyNameplateGuildDB.gap'), 2)
        self.assertEqual(self.value('FriendlyNameplateGuildDB.color'), '66ff99')
        self.run_lua("namespace.Command('off'); namespace.Command('size 15'); namespace.Command('reset')")
        self.assertTrue(self.value('FriendlyNameplateGuildDB.enabled'))
        self.assertEqual(self.value('FriendlyNameplateGuildDB.fontSize'), 11)

    def test_saved_settings_are_preserved_and_unrelated_addon_load_ignored(self):
        self.run_lua("FriendlyNameplateGuildDB = {enabled = false, fontSize = 14, gap = 4, color = 'aabbcc'}; driver.scripts.OnEvent(driver, 'ADDON_LOADED', 'OtherAddon')")
        self.assertEqual(self.value('#labels'), 0)
        self.start()
        self.assertEqual(self.value('FriendlyNameplateGuildDB.fontSize'), 14)
        self.assertFalse(self.value('FriendlyNameplateGuildDB.enabled'))
        self.assertEqual(self.value('#labels'), 0)

    def test_guild_text_cannot_inject_wow_color_markup(self):
        self.start("visible = {MakePlate('a', '|cffff0000Guild')}")
        self.assertEqual(self.value('labels[1].text'), '<||cffff0000Guild>')

    def test_settings_ui_is_lazy_and_controls_update_real_settings(self):
        self.start()
        self.assertIsNone(self.value('namespace.SettingsWindow'))
        self.run_lua("namespace.Command('')")
        self.assertTrue(self.value('namespace.SettingsWindow.shown'))
        self.run_lua('namespace.SettingsWindow.size:SetValue(15); namespace.SettingsWindow.gap:SetValue(4)')
        self.assertEqual(self.value('FriendlyNameplateGuildDB.fontSize'), 15)
        self.assertEqual(self.value('labels[1].size'), 15)
        self.assertEqual(self.value('labels[1].anchor[5]'), -4)
        self.run_lua('namespace.SettingsWindow.enabled:SetChecked(false); namespace.SettingsWindow.enabled.scripts.OnClick(namespace.SettingsWindow.enabled)')
        self.assertFalse(self.value('labels[1].shown'))
        self.run_lua('namespace.SettingsWindow.reset.scripts.OnClick()')
        self.assertEqual(self.value('namespace.SettingsWindow.size.value'), 11)
        self.assertTrue(self.value('labels[1].shown'))
        self.run_lua("namespace.Command('')")
        self.assertEqual(self.value('#UISpecialFrames'), 1)

    def test_color_picker_applies_and_cancel_restores_the_original(self):
        self.start()
        self.run_lua('''
            ColorPickerFrame = {
                SetupColorPickerAndShow = function(self, info) self.info = info end,
                GetColorRGB = function() return 1, 0, 0 end,
            }
            namespace.ShowSettings()
            namespace.SettingsWindow.color.scripts.OnClick()
            ColorPickerFrame.info.swatchFunc()
        ''')
        self.assertEqual(self.value('FriendlyNameplateGuildDB.color'), 'ff0000')
        self.assertEqual(self.value('namespace.SettingsWindow.preview.color[1]'), 1)
        self.run_lua('ColorPickerFrame.info.cancelFunc()')
        self.assertEqual(self.value('FriendlyNameplateGuildDB.color'), '66ff99')

    def test_runtime_interface_warning_uses_metadata_not_build_number(self):
        self.run_lua('''
            C_AddOns = {GetAddOnMetadata = function() return '16001' end}
            GetBuildInfo = function() return '1.60.2', '99999', 'date', 16002 end
        ''')
        self.start()
        self.assertIn('New WoW Interface 16002', self.value('messages[1]'))
        self.run_lua("GetBuildInfo = function() return '1.60.1', '99999', 'date', 16001 end")
        self.assertFalse(self.value('(namespace.Compatibility())'))

    def test_polling_has_no_per_frame_handler_and_stops_when_not_needed(self):
        self.start()
        self.assertIsNone(self.value('driver.scripts.OnUpdate'))
        self.run_lua('originalTimer = timer; namespace.Refresh()')
        self.assertTrue(self.value('timer == originalTimer'))
        self.assertFalse(self.value('timer.cancelled'))
        self.run_lua("namespace.Command('off')")
        self.assertTrue(self.value('timer.cancelled'))
        self.run_lua("namespace.Command('on')")
        self.assertFalse(self.value('timer.cancelled'))
        self.run_lua('visible = {}; namespace.Refresh()')
        self.assertTrue(self.value('timer.cancelled'))


if __name__ == '__main__':
    unittest.main()
