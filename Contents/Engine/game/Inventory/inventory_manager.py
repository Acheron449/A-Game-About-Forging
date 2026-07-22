"""Bag inventory and drag-move (invmanager.txt)."""

from __future__ import annotations

from typing import Any, Callable, List, Optional

from config.config import config


class InventorySlot:
    def __init__(self):
        self._item: Optional[Any] = None

    def is_empty(self) -> bool:
        return self._item is None

    def get_item(self) -> Optional[Any]:
        return self._item

    def set_item(self, item: Any) -> None:
        self._item = item

    def clear(self) -> None:
        self._item = None


class InventoryManager:
    def __init__(
        self,
        total_bag_slots: int = config.INVENTORY_BAG_SLOT_COUNT,
        on_open: Optional[Callable[[], None]] = None,
        on_close: Optional[Callable[[], None]] = None,
        on_render: Optional[Callable[[], None]] = None,
        on_pause: Optional[Callable[[bool], None]] = None,
    ):
        self.is_inventory_open = False
        self.total_bag_slots = total_bag_slots
        self.bag_slots: List[InventorySlot] = [InventorySlot() for _ in range(total_bag_slots)]
        self._on_open = on_open
        self._on_close = on_close
        self._on_render = on_render
        self._on_pause = on_pause

    def has_empty_slot(self) -> bool:
        return any(slot.is_empty() for slot in self.bag_slots)

    def first_empty_slot(self) -> Optional[InventorySlot]:
        for slot in self.bag_slots:
            if slot.is_empty():
                return slot
        return None

    def move_to_bag(self, item: Any) -> bool:
        empty = self.first_empty_slot()
        if empty is None:
            return False
        empty.set_item(item)
        return True

    def toggle_inventory_ui(self) -> None:
        self.is_inventory_open = not self.is_inventory_open
        if self.is_inventory_open:
            if self._on_pause:
                self._on_pause(True)
            if self._on_open:
                self._on_open()
            if self._on_render:
                self._on_render()
        else:
            if self._on_pause:
                self._on_pause(False)
            if self._on_close:
                self._on_close()

    def move_item(self, source_slot: InventorySlot, destination_slot: InventorySlot) -> None:
        if destination_slot.is_empty():
            destination_slot.set_item(source_slot.get_item())
            source_slot.clear()
        else:
            temp_item = destination_slot.get_item()
            destination_slot.set_item(source_slot.get_item())
            source_slot.set_item(temp_item)

    def close_inventory_screen(self) -> None:
        if self.is_inventory_open:
            self.toggle_inventory_ui()
