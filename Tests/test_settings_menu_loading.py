import unittest

from Contents.Engine.game.pause_menu_manager import PauseMenuManager
from Contents.Engine.main.Title import MainMenuManager


class SettingsMenuLoadingTests(unittest.TestCase):
    def test_main_menu_opens_settings_via_callback(self):
        opened = []
        manager = MainMenuManager(on_open_settings=lambda: opened.append('opened'))

        manager.open_settings_screen()

        self.assertEqual(opened, ['opened'])
        self.assertTrue(manager.is_settings_menu_open)

    def test_pause_menu_opens_settings_via_callback(self):
        opened = []
        manager = PauseMenuManager(on_open_settings=lambda: opened.append('opened'))

        manager.open_settings_screen()

        self.assertEqual(opened, ['opened'])


if __name__ == '__main__':
    unittest.main()
