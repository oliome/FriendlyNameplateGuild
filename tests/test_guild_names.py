from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]


class GuildNamesTests(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute((ROOT / 'tests/lua/nameplates.lua').read_text(encoding='utf-8'))
        source = (ROOT / 'addon/BetterForeverNames/GuildNames.lua').read_text(encoding='utf-8')
        self.lua.execute('assert(loadstring(...))("BetterForeverNames", namespace)', source)

    def run_lua(self, code):
        self.lua.execute(code)

    def value(self, code):
        return self.lua.eval(code)

    def start(self, setup="visible = {MakePlate('nameplate1', 'Azeroth Explorers')}"):
        self.run_lua(setup)
        self.run_lua("driver.scripts.OnEvent(driver, 'ADDON_LOADED', 'BetterForeverNames')")

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
        self.run_lua("guilds.nameplate1 = 'Loaded Later'; driver.scripts.OnUpdate(driver, 1)")
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
        self.run_lua("BetterForeverNamesDB = {enabled = 'yes', fontSize = 100, gap = -5, color = 'oops'}")
        self.start()
        self.assertEqual(self.value('BetterForeverNamesDB.fontSize'), 11)
        self.run_lua("namespace.Command('size nan'); namespace.Command('size 25'); namespace.Command('gap -1'); namespace.Command('color invalid')")
        self.assertEqual(self.value('BetterForeverNamesDB.fontSize'), 11)
        self.assertEqual(self.value('BetterForeverNamesDB.gap'), 2)
        self.assertEqual(self.value('BetterForeverNamesDB.color'), '66ff99')
        self.run_lua("namespace.Command('off'); namespace.Command('size 15'); namespace.Command('reset')")
        self.assertTrue(self.value('BetterForeverNamesDB.enabled'))
        self.assertEqual(self.value('BetterForeverNamesDB.fontSize'), 11)

    def test_saved_settings_are_preserved_and_unrelated_addon_load_ignored(self):
        self.run_lua("BetterForeverNamesDB = {enabled = false, fontSize = 14, gap = 4, color = 'aabbcc'}; driver.scripts.OnEvent(driver, 'ADDON_LOADED', 'OtherAddon')")
        self.assertEqual(self.value('#labels'), 0)
        self.start()
        self.assertEqual(self.value('BetterForeverNamesDB.fontSize'), 14)
        self.assertFalse(self.value('BetterForeverNamesDB.enabled'))
        self.assertEqual(self.value('#labels'), 0)

    def test_guild_text_cannot_inject_wow_color_markup(self):
        self.start("visible = {MakePlate('a', '|cffff0000Guild')}")
        self.assertEqual(self.value('labels[1].text'), '<||cffff0000Guild>')


if __name__ == '__main__':
    unittest.main()
