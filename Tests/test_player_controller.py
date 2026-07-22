import unittest

import pygame

from Engine.config.config import config
from Engine.game.movement_controller import PlayerController
from Engine.game.player_status import PlayerStatus


class DummyPlayer:
    def __init__(self):
        self.dash_count = 0


class PlayerControllerTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.player = DummyPlayer()
        self.player_status = PlayerStatus(max_stamina=100)
        self.player_status.current_stamina = 100
        self.controller = PlayerController(
            self.player,
            self.player_status,
            on_dash=self._record_dash,
        )

    def _record_dash(self):
        self.player.dash_count += 1

    def _make_keys(self, *pressed_keys):
        keys = {key: False for axis in config.KEYBINDS.values() for key in axis}
        for key in pressed_keys:
            keys[key] = True
        return keys

    def test_dash_triggers_once_per_press(self):
        self.controller.handle_input(self._make_keys(), (0, 0, 0))
        self.controller.handle_input(self._make_keys(*config.BIND_DASH_KEYS), (0, 0, 0))
        self.controller.handle_input(self._make_keys(*config.BIND_DASH_KEYS), (0, 0, 0))

        self.assertEqual(self.player.dash_count, 1)


if __name__ == '__main__':
    unittest.main()
