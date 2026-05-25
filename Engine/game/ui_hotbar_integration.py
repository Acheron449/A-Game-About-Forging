"""Inventory panel hotbar rendering and drag (uihotbarint.txt)."""

from __future__ import annotations

from typing import Any, Callable, List, Optional, Tuple

from ..config.config import HOTBAR_SLOT_COUNT
from .inventory_hotbar import InventoryHotbar
from .inventory_manager import InventoryManager, InventorySlot


class UIHotbarIntegration:
    def __init__(
        self,
        hotbar: Optional[InventoryHotbar] = None,
        inventory_manager: Optional[InventoryManager] = None,
        on_draw_slot: Optional[Callable[[Optional[Any], int, int], None]] = None,
    ):
        self.hotbar = hotbar or InventoryHotbar()
        self.inventory_manager = inventory_manager
        self.hotbar_slots: List[InventorySlot] = self.hotbar.hotbar_slots
        self._on_draw_slot = on_draw_slot

    def render_hotbar_in_inventory(
        self,
        origin_x: int = 0,
        origin_y: int = 0,
        slot_spacing: int = 48,
    ) -> None:
        for index in range(HOTBAR_SLOT_COUNT):
            x_pos = origin_x + index * slot_spacing
            y_pos = origin_y
            item = self.hotbar_slots[index].get_item()
            self.draw_slot(item, x_pos, y_pos, index)

    def draw_slot(
        self,
        item: Optional[Any],
        x_pos: int,
        y_pos: int,
        index: int,
    ) -> None:
        if self._on_draw_slot:
            self._on_draw_slot(item, x_pos, y_pos)
        else:
            pass  # Rendering hook not wired

    def transfer_to_hotbar(
        self,
        inventory_item_slot: InventorySlot,
        hotbar_index: int,
    ) -> None:
        if hotbar_index < 0 or hotbar_index >= len(self.hotbar_slots):
            return
        target_slot = self.hotbar_slots[hotbar_index]
        if self.inventory_manager:
            self.inventory_manager.move_item(inventory_item_slot, target_slot)
        else:
            target_slot.set_item(inventory_item_slot.get_item())
            inventory_item_slot.clear()
