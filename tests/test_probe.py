from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute('''
            SlashCmdList = {}
            GetBuildInfo = function() return '1.60.1', '70862', 'Nov 7 2026', 16001 end
            WOW_PROJECT_ID = 1
            C_CVar = {GetCVar = function(key) return '0' end}
            C_NamePlate = {GetNamePlateForUnit = function(unit, includeForbidden)
                assert(unit == 'target')
                assert(includeForbidden == false)
                return nil
            end}
            -- All mutation APIs must remain untouched, even when available.
            C_CVar.SetCVar = function() error('CVar mutation forbidden') end
            hooksecurefunc = function() error('Hooks forbidden') end
            SendAddonMessage = function() error('Network sends forbidden') end
            UnitName = function() error('Identity access forbidden') end
            UnitGUID = function() error('Identity access forbidden') end
            namespace = {}
        ''')
        source = (ROOT / 'probes/BetterForeverNamesProbe/Probe.lua').read_text(encoding='utf-8')
        self.lua.execute('assert(loadstring(...))("BetterForeverNamesProbe", namespace)', source)

    def report(self):
        return self.lua.eval('namespace.Collect()')

    def test_reports_actual_interface_without_patch_inference(self):
        self.lua.execute("GetBuildInfo = function() return '99.99.99', '80000', 'date', 16003 end")
        report = self.report()
        self.assertIn('client.interface=16003', report)
        self.assertIn('client.version=99.99.99', report)

    def test_absent_plate_and_read_only_cvars(self):
        report = self.report()
        self.assertIn('target.nameplate=absent', report)
        self.assertIn('cvar.nameplateShowFriends=0', report)
        self.assertIn('not proof that native world text is editable', report)

    def test_missing_and_throwing_apis_do_not_crash(self):
        self.lua.execute('GetBuildInfo = nil; C_CVar = nil; C_NamePlate = nil')
        report = self.report()
        self.assertIn('client=unavailable', report)
        self.assertIn('target.nameplate=unavailable', report)
        self.lua.execute('C_NamePlate = {GetNamePlateForUnit = function() error("blocked") end}')
        self.assertIn('target.nameplate=unavailable', self.report())

    def test_forbidden_frame_is_not_inspected(self):
        self.lua.execute('''
            C_NamePlate.GetNamePlateForUnit = function()
                return setmetatable({IsForbidden = function() return true end},
                    {__index = function() error('Forbidden frame inspected') end})
            end
        ''')
        self.assertIn('target.nameplate=forbidden', self.report())

    def test_unknown_forbidden_status_fails_closed(self):
        self.lua.execute('C_NamePlate.GetNamePlateForUnit = function() return {} end')
        self.assertIn('target.nameplate=unavailable', self.report())

    def test_accessible_lua_text_is_distinguished_from_native_text(self):
        self.lua.execute('''
            C_NamePlate.GetNamePlateForUnit = function()
                return {IsForbidden = function() return false end,
                    UnitFrame = {IsForbidden = function() return false end, name = {}}}
            end
        ''')
        report = self.report()
        self.assertIn('target.nameplate=lua-name-text-present', report)
        self.assertIn('native.per-player-color=no-supported-api-identified', report)

    def test_secret_values_are_not_stringified(self):
        self.lua.execute('''
            secret = setmetatable({}, {__tostring = function() error('Secret stringified') end})
            issecretvalue = function(value) return rawequal(value, secret) end
            C_CVar.GetCVar = function() return secret end
        ''')
        self.assertIn('cvar.nameplateShowFriends=restricted', self.report())

    def test_inaccessible_plate_is_not_inspected(self):
        self.lua.execute('''
            secret = setmetatable({}, {__index = function() error('Secret inspected') end})
            canaccessvalue = function(value) return not rawequal(value, secret) end
            C_NamePlate.GetNamePlateForUnit = function() return secret end
        ''')
        self.assertIn('target.nameplate=restricted', self.report())

    def test_report_ui_failure_falls_back_to_text(self):
        self.lua.execute('''
            messages = {}
            print = function(text) messages[#messages + 1] = text end
            CreateFrame = function() error('Unavailable frame template') end
            SlashCmdList.BETTERFOREVERNAMESPROBE('')
        ''')
        self.assertIn('report window unavailable', self.lua.eval('messages[1]'))
        self.assertIn('client.interface=16001', self.lua.eval('messages[2]'))


if __name__ == '__main__':
    unittest.main()
