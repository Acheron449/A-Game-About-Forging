"""Gameplay hotbar keys 1–0 (invhotbar.txt)."""

from __future__ import annotations

from typing import Any, Callable, List, Optional

import pygame

from ..config.config import HOTBAR_KEY_OFFSET, HOTBAR_SLOT_COUNT
from .inventory_manager import InventorySlot


class InventoryHotbar:
    def __init__(
        self,
        slot_count: int = HOTBAR_SLOT_COUNT,
        on_equip_or_use: Optional[Callable[[Any], None]] = None,
    ):
        self.hotbar_slots: List[InventorySlot] = [
            InventorySlot() for _ in range(slot_count)
        ]
        self._on_equip_or_use = on_equip_or_use
        self._active_index: Optional[int] = None

    def handle_hotbar_keydown(self, key: int) -> Optional[Any]:
        """Select hotbar slot from a single KEYDOWN event."""
        for key_number in range(1, HOTBAR_SLOT_COUNT + 1):
            key_code = HOTBAR_KEY_OFFSET + (key_number - 1)
            if key_number == 10:
                key_code = pygame.K_0
            if key == key_code:
                return self.select_item_in_slot(key_number - 1)
        return None

    def handle_hotbar_input(self, keys_pressed) -> None:
        for key_number in range(1, HOTBAR_SLOT_COUNT + 1):
            key_code = HOTBAR_KEY_OFFSET + (key_number - 1)
            if key_number == 10:
                key_code = pygame.K_0
            if keys_pressed[key_code]:
                self.select_item_in_slot(key_number - 1)

    def select_item_in_slot(self, slot_index: int) -> Optional[Any]:
        if slot_index < 0 or slot_index >= len(self.hotbar_slots):
            return None
        self._active_index = slot_index
        active_item = self.hotbar_slots[slot_index].get_item()
        if active_item is not None:
            self.equip_or_use(active_item)
        return active_item

    def equip_or_use(self, active_item: Any) -> None:
        if self._on_equip_or_use:
            self._on_equip_or_use(active_item)

    def set_slot(self, slot_index: int, item: Any) -> bool:
        if slot_index < 0 or slot_index >= len(self.hotbar_slots):
            return False
        self.hotbar_slots[slot_index].set_item(item)
        return True
