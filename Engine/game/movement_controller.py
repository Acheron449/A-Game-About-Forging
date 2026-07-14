"""Player movement, dash, attack, block input (Mvmtctrl.txt)."""

from __future__ import annotations

from typing import Any, Callable, Optional

import pygame

from ..config.config import config
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

    def _movement_pressed(self, keys_pressed) -> bool:
        for axis in config.KEYBINDS:
            for key in config.KEYBINDS[axis]:
                if keys_pressed[key]:
                    return True
        return False

    def handle_input(
        self,
        keys_pressed,
        mouse_buttons: Optional[tuple] = None,
    ) -> None:
        mouse_buttons = mouse_buttons or (0, 0, 0)
        if self._movement_pressed(keys_pressed):
            self.move_player()
        if keys_pressed[pygame.K_LSHIFT] or keys_pressed[pygame.K_RSHIFT]:
            if self.player_status and self.player_status.current_stamina >= config.DASH_STAMINA_COST:
                self.execute_dash()
                self.player_status.use_stamina(config.DASH_STAMINA_COST)
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
