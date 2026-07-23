"""Player movement, dash, attack, block input (Mvmtctrl.txt)."""

from __future__ import annotations

from typing import Any, Callable, Optional

import pygame

from Contents.configuration.constants import config
from .player_status import PlayerStatus


class PlayerController:
    def __init__(
        self,
        player: Any,
        player_status: Optional[PlayerStatus] = None,
        on_move: Optional[Callable[[], None]] = None,
        on_dash: Optional[Callable[[], None]] = None,
        on_attack: Optional[Callable[[], None]] = None,
        on_block: Optional[Callable[[], None]] = None,
    ):
        self.player = player
        self.player_status = player_status
        self._on_move = on_move
        self._on_dash = on_dash
        self._on_attack = on_attack
        self._on_block = on_block
        self._dash_is_held = False

    def _is_key_pressed(self, keys_pressed, key: int) -> bool:
        if isinstance(keys_pressed, dict):
            return bool(keys_pressed.get(key, False))
        try:
            return bool(keys_pressed[key])
        except (KeyError, IndexError, TypeError):
            return False

    def _movement_pressed(self, keys_pressed) -> bool:
        for axis in config.KEYBINDS:
            for key in config.KEYBINDS[axis]:
                if self._is_key_pressed(keys_pressed, key):
                    return True
        return False

    def _dash_pressed(self, keys_pressed) -> bool:
        return any(self._is_key_pressed(keys_pressed, key) for key in config.BIND_DASH_KEYS)

    def handle_input(
        self,
        keys_pressed,
        mouse_buttons: Optional[tuple] = None,
    ) -> None:
        mouse_buttons = mouse_buttons or (0, 0, 0)
        if self._movement_pressed(keys_pressed):
            self.move_player()

        dash_pressed = self._dash_pressed(keys_pressed)
        if dash_pressed and not self._dash_is_held:
            if self.player_status and self.player_status.current_stamina >= config.DASH_STAMINA_COST:
                self.execute_dash()
                self.player_status.use_stamina(config.DASH_STAMINA_COST)
        self._dash_is_held = dash_pressed

        if mouse_buttons[0]:
            self.execute_attack()
        if len(mouse_buttons) > 1 and mouse_buttons[1]:
            self.execute_block()

    def move_player(self) -> None:
        if self._on_move:
            self._on_move()

    def execute_dash(self) -> None:
        if self._on_dash:
            self._on_dash()

    def execute_attack(self) -> None:
        if self._on_attack:
            self._on_attack()

    def execute_block(self) -> None:
        if self._on_block:
            self._on_block()
