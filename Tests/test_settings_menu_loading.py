"""Verify settings defaults and menu loading behavior."""
 # Verify that the settings menu can initialize its configured controls.
import unittest

from Contents.Engine.game.pause_menu_manager import PauseMenuManager
from Contents.Engine.main.Title import MainMenuManager


class SettingsMenuLoadingTests(unittest.TestCase):
    # Verify that the title menu delegates settings opening to its callback.
    def test_main_menu_opens_settings_via_callback(self):
        # Collect callback invocations without opening a real settings window.
        opened = []
        # Configure the menu with an observable settings callback.
        manager = MainMenuManager(on_open_settings=lambda: opened.append('opened'))

        # Trigger the menu action under test.
        manager.open_settings_screen()

        # Confirm the callback ran once with the expected marker.
        self.assertEqual(opened, ['opened'])
        # Confirm the menu records that its settings view is open.
        self.assertTrue(manager.is_settings_menu_open)

    # Verify that the pause menu delegates settings opening similarly.
    def test_pause_menu_opens_settings_via_callback(self):
        # Collect callback invocations without opening a real settings window.
        opened = []
        # Configure the pause menu with an observable settings callback.
        manager = PauseMenuManager(on_open_settings=lambda: opened.append('opened'))

        # Trigger the pause-menu action under test.
        manager.open_settings_screen()

        # Confirm the callback ran once with the expected marker.
        self.assertEqual(opened, ['opened'])


if __name__ == '__main__':
    unittest.main()
