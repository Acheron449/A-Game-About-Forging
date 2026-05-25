"""Ultimate and skill hotkeys Q / E / C (skill.txt)."""

from __future__ import annotations

from typing import Callable, Optional

import pygame

from ..config.config import (
    SKILL_1_KEYS,
    SKILL_1_MANA_COST,
    SKILL_2_KEYS,
    SKILL_2_MANA_COST,
    SKILL_ULT_KEYS,
    SKILL_ULT_MANA_COST,
)
from .player_status import PlayerStatus


class PlayerSkills:
    def __init__(
        self,
        player_status: PlayerStatus,
        on_ultimate: Optional[Callable[[], None]] = None,
        on_skill1: Optional[Callable[[], None]] = None,
        on_skill2: Optional[Callable[[], None]] = None,
    ):
        self.player_status = player_status
        self.ult_cost = SKILL_ULT_MANA_COST
        self.skill1_cost = SKILL_1_MANA_COST
        self.skill2_cost = SKILL_2_MANA_COST
        self._on_ultimate = on_ultimate
        self._on_skill1 = on_skill1
        self._on_skill2 = on_skill2

    def _key_down(self, keys_pressed, key_list) -> bool:
        return any(keys_pressed[k] for k in key_list)

    def handle_skill_input(self, keys_pressed) -> None:
        if self._key_down(keys_pressed, SKILL_ULT_KEYS):
            if self.player_status.current_mana >= self.ult_cost:
                self.execute_ultimate()
                self.player_status.use_mana(self.ult_cost)
        if self._key_down(keys_pressed, SKILL_1_KEYS):
            if self.player_status.current_mana >= self.skill1_cost:
                self.execute_skill1()
                self.player_status.use_mana(self.skill1_cost)
        if self._key_down(keys_pressed, SKILL_2_KEYS):
            if self.player_status.current_mana >= self.skill2_cost:
                self.execute_skill2()
                self.player_status.use_mana(self.skill2_cost)

    def execute_ultimate(self) -> None:
        if self._on_ultimate:
            self._on_ultimate()

    def execute_skill1(self) -> None:
        if self._on_skill1:
            self._on_skill1()

    def execute_skill2(self) -> None:
        if self._on_skill2:
            self._on_skill2()
