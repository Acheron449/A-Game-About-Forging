"""Inventory panel hotbar rendering and drag (uihotbarint.txt)."""

from __future__ import annotations

from typing import Any, Callable, List, Optional, Tuple

from Contents.Engine.configuration.constants import config
from .Inventory.inventory_hotbar import InventoryHotbar
from .Inventory.inventory_manager import InventoryManager, InventorySlot


class UIHotbarIntegration: 
    def __init__( # initialize the UIHotbarIntegration class
        self,
        hotbar: Optional[InventoryHotbar] = None, # the hotbar to integrate
        inventory_manager: Optional[InventoryManager] = None, # the inventory manager to integrate
        on_draw_slot: Optional[Callable[[Optional[Any], int, int], None]] = None, # the function to call when drawing a slot
    ):
        self.hotbar = hotbar or InventoryHotbar() # the hotbar to integrate or create a new one if none is provided
        self.inventory_manager = inventory_manager # the inventory manager to integrate
        self.hotbar_slots: List[InventorySlot] = self.hotbar.hotbar_slots
        self._on_draw_slot = on_draw_slot # the function to call when drawing a slot

    def render_hotbar_in_inventory( # render the hotbar in the inventory
        self,
        origin_x: int = 0, # the x position of the origin
        origin_y: int = 0, # the y position of the origin
        slot_spacing: int = 48, # the spacing between slots
    ) -> None: # return None
        for index in range(config.HOTBAR_SLOT_COUNT): # loop through the hotbar slots
            x_pos = origin_x + index * slot_spacing # calculate the x position of the slot
            y_pos = origin_y # calculate the y position of the slot
            item = self.hotbar_slots[index].get_item() # get the item in the slot
            self.draw_slot(item, x_pos, y_pos, index) # draw the slot

    def draw_slot( # draw a slot
        self,
        item: Optional[Any], # the item to draw
        x_pos: int, # the x position of the slot
        y_pos: int, # the y position of the slot
        index: int, # the index of the slot
    ) -> None: # return None
        if self._on_draw_slot: # if there is a function to call when drawing a slot
            self._on_draw_slot(item, x_pos, y_pos) # call the function to draw the slot
        else: # if there is no function to call when drawing a slot
            pass  # Rendering hook not wired

    def transfer_to_hotbar( # transfer an item to the hotbar    
        self,
        inventory_item_slot: InventorySlot, # the inventory item slot to transfer
        hotbar_index: int, # the index of the hotbar slot to transfer to
    ) -> None: # return None
        if hotbar_index < 0 or hotbar_index >= len(self.hotbar_slots): # if the hotbar index is out of bounds
            return # return None
        target_slot = self.hotbar_slots[hotbar_index] # get the target slot
        if self.inventory_manager: # if there is an inventory manager
            self.inventory_manager.move_item(inventory_item_slot, target_slot) # move the item to the target slot
        else: # if there is no inventory manager
            target_slot.set_item(inventory_item_slot.get_item()) # set the item in the target slot
            inventory_item_slot.clear() # clear the inventory item slot