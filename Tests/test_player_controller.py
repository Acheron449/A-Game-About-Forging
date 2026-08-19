 # Exercise player-controller movement behavior with a small test double.
import unittest

import pygame

from Engine.config.config import config
from Engine.game.movement_controller import PlayerController
from Engine.game.player_status import PlayerStatus


class DummyPlayer:
    # Supply only the player state needed to observe dash callbacks.
    def __init__(self):
        # Count dash events so the input edge behavior can be asserted.
        self.dash_count = 0


class PlayerControllerTests(unittest.TestCase):
    # Create a fresh pygame-backed controller for each test case.
    def setUp(self):
        # Initialize pygame services required by the controller under test.
        pygame.init()
        # Provide a minimal player object for the controller dependency.
        self.player = DummyPlayer()
        # Give the test player a full stamina pool before input is handled.
        self.player_status = PlayerStatus(max_stamina=100)
        # Set the current stamina explicitly to avoid relying on defaults.
        self.player_status.current_stamina = 100
        # Connect dash events to the observable test callback.
        self.controller = PlayerController(
            self.player,
            self.player_status,
            on_dash=self._record_dash,
        )

    def _record_dash(self):
        # Record each accepted dash request from the controller.
        self.player.dash_count += 1

    def _make_keys(self, *pressed_keys):
        # Start with every configured key released.
        keys = {key: False for axis in config.KEYBINDS.values() for key in axis}
        # Mark only the keys supplied by the test as pressed.
        for key in pressed_keys:
            # Set this binding true so the controller sees the simulated press.
            keys[key] = True
        # Return the complete key-state mapping expected by the controller.
        return keys

    def test_dash_triggers_once_per_press(self):
        # Establish the released state before simulating the key press.
        self.controller.handle_input(self._make_keys(), (0, 0, 0))
        # Send the first pressed frame that should trigger one dash.
        self.controller.handle_input(self._make_keys(*config.BIND_DASH_KEYS), (0, 0, 0))
        # Hold the same press to verify it is not retriggered continuously.
        self.controller.handle_input(self._make_keys(*config.BIND_DASH_KEYS), (0, 0, 0))

        # Confirm that one physical press produced exactly one dash event.
        self.assertEqual(self.player.dash_count, 1)


if __name__ == '__main__':
    # Run this module directly through unittest's standard test runner.
    unittest.main()
