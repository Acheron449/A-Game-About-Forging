"""Gameplay hotbar keys 1–0 (invhotbar.txt)."""

from __future__ import annotations

from typing import Any, Callable, List, Optional

import pygame

from Contents.Engine.configuration.constants import config # import the hotbar key offset and slot count from the config
from .inventory_manager import InventorySlot # import the inventory slot from the inventory manager class


class InventoryHotbar: # define the inventory hotbar class
    def __init__(
        self,
        slot_count: int = config.HOTBAR_SLOT_COUNT, # set the slot count to the hotbar slot count from the config
        on_equip_or_use: Optional[Callable[[Any], None]] = None, # set the on equip or use function to None if no function is provided in the constructor
    ):
        self.hotbar_slots: List[InventorySlot] = [ # create a list of inventory slots and initialize each slot with an inventory slot object
            InventorySlot() for _ in range(slot_count) # initialize each slot with an inventory slot object
        ] # create a list of inventory slots and initialize each slot with an inventory slot object
        self._on_equip_or_use = on_equip_or_use # set the on equip or use function
        self._active_index: Optional[int] = None # set the active index to None if no index is provided in the constructor

    def handle_hotbar_keydown(self, key: int) -> Optional[Any]: # handle the hotbar keydown event
        """Select hotbar slot from a single KEYDOWN event."""
        for key_number in range(1, config.HOTBAR_SLOT_COUNT + 1): # loop through the hotbar slots
            key_code = config.HOTBAR_KEY_OFFSET + (key_number - 1) # calculate the key code
            if key_number == 10:
                key_code = pygame.K_0 # set the key code to 0 if the key number is 10
            if key == key_code:
                return self.select_item_in_slot(key_number - 1) # select the item in the slot
        return None # return None if the key is not found

    def handle_hotbar_input(self, keys_pressed) -> None: # handle the hotbar input event
        for key_number in range(1, config.HOTBAR_SLOT_COUNT + 1): # loop through the hotbar slots
            key_code = config.HOTBAR_KEY_OFFSET + (key_number - 1)
            if key_number == 10:
                key_code = pygame.K_0 # set the key code to 0 if the key number is 10
            if keys_pressed[key_code]:
                self.select_item_in_slot(key_number - 1) # select the item in the slot

    def select_item_in_slot(self, slot_index: int) -> Optional[Any]: # select the item in the slot
        if slot_index < 0 or slot_index >= len(self.hotbar_slots): # check if the slot index is out of bounds
            return None
        self._active_index = slot_index
        active_item = self.hotbar_slots[slot_index].get_item() # get the item in the slot       
        if active_item is not None:
            self.equip_or_use(active_item) # equip or use the item if it is not None
        return active_item

    def equip_or_use(self, active_item: Any) -> None: # equip or use the item
        if self._on_equip_or_use:
            self._on_equip_or_use(active_item) # call the on equip or use function if it is not None

    def set_slot(self, slot_index: int, item: Any) -> bool:
        if slot_index < 0 or slot_index >= len(self.hotbar_slots): # check if the slot index is out of bounds
            return False # return False if the slot index is out of bounds
        self.hotbar_slots[slot_index].set_item(item) # set the item in the slot if the slot index is not out of bounds
        return True # return True if the item is set in the slot
