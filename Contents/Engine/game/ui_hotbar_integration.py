"""Always-visible in-game hotbar UI."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import pygame

from Contents.Engine.configuration.constants import config
from Contents.Engine.game.Inventory.inventory_hotbar import InventoryHotbar
from Contents.Engine.game.Inventory.inventory import (
    InventoryManager,
    InventorySlot,
)


class UIHotbarIntegration:

    # Colours
    PANEL = (35, 35, 35)
    PANEL_BORDER = (180, 180, 180)

    SLOT = (70, 70, 70)
    SLOT_BORDER = (110, 110, 110)

    SELECTED = (190, 150, 60)
    SELECTED_BORDER = (255, 220, 100)

    TEXT = (245, 236, 211)
    MUTED_TEXT = (180, 180, 180)

    def __init__(
        self,
        hotbar: Optional[InventoryHotbar] = None,
        inventory_manager: Optional[InventoryManager] = None,
        on_draw_slot: Optional[
            Callable[[Optional[Any], int, int], None]
        ] = None,
    ):

        self.hotbar = hotbar or InventoryHotbar()

        self.inventory_manager = inventory_manager

        self.hotbar_slots: List[
            InventorySlot
        ] = self.hotbar.hotbar_slots

        self._on_draw_slot = on_draw_slot

        # Currently selected hotbar slot.
        # 0 = key 1
        # 1 = key 2
        # ...
        # 8 = key 9
        # 9 = key 0
        self.selected_index = 0

        self.slot_size = 52
        self.slot_gap = 6
        self.bottom_margin = 18

        self._sprite_cache: Dict[
            str,
            pygame.Surface
        ] = {}

    
    # NUMBER KEY SELECTION
    

    def handle_keydown(self, key: int) -> bool:
        """
        Select a hotbar slot using 1-9 and 0.

        Returns True if the key was a hotbar key.
        """

        key_to_index = {
            pygame.K_1: 0,
            pygame.K_2: 1,
            pygame.K_3: 2,
            pygame.K_4: 3,
            pygame.K_5: 4,
            pygame.K_6: 5,
            pygame.K_7: 6,
            pygame.K_8: 7,
            pygame.K_9: 8,
            pygame.K_0: 9,
        }

        if key not in key_to_index:
            return False

        index = key_to_index[key]

        if index >= len(self.hotbar_slots):
            return False

        self.selected_index = index

        return True

    
    # SELECTED ITEM
    

    def get_selected_slot(self) -> Optional[InventorySlot]:

        if not self.hotbar_slots:
            return None

        if (
            self.selected_index < 0
            or self.selected_index >= len(self.hotbar_slots)
        ):
            return None

        return self.hotbar_slots[
            self.selected_index
        ]

    def get_selected_item(self) -> Optional[Any]:

        slot = self.get_selected_slot()

        if slot is None:
            return None

        return slot.get_item()

    
    # DRAW HOTBAR
    

    def draw(
        self,
        screen: pygame.Surface,
    ) -> None:
        """
        Draw the hotbar fixed to the bottom of the screen.
        """

        screen_width, screen_height = screen.get_size()

        slot_count = len(self.hotbar_slots)

        if slot_count == 0:
            return

        total_width = (
            slot_count * self.slot_size
            + (slot_count - 1) * self.slot_gap
        )

        panel_padding = 10

        panel_width = (
            total_width
            + panel_padding * 2
        )

        panel_height = (
            self.slot_size
            + panel_padding * 2
            + 8
        )

        panel = pygame.Rect(
            0,
            0,
            panel_width,
            panel_height,
        )

        panel.centerx = screen_width // 2

        panel.bottom = (
            screen_height
            - self.bottom_margin
        )

        
        # BACKGROUND
        

        pygame.draw.rect(
            screen,
            self.PANEL,
            panel,
            border_radius=8,
        )

        pygame.draw.rect(
            screen,
            self.PANEL_BORDER,
            panel,
            width=2,
            border_radius=8,
        )

        
        # SLOTS
        

        start_x = (
            panel.left
            + panel_padding
        )

        start_y = (
            panel.top
            + panel_padding
        )

        for index, slot in enumerate(
            self.hotbar_slots
        ):

            x = (
                start_x
                + index
                * (
                    self.slot_size
                    + self.slot_gap
                )
            )

            rect = pygame.Rect(
                x,
                start_y,
                self.slot_size,
                self.slot_size,
            )

            self._draw_slot(
                screen,
                slot,
                rect,
                index,
            )

    
    # DRAW SLOT
    

    def _draw_slot(
        self,
        screen: pygame.Surface,
        slot: InventorySlot,
        rect: pygame.Rect,
        index: int,
    ):

        is_selected = (
            index == self.selected_index
        )

        # Selected slot gets a different background.
        if is_selected:
            slot_colour = self.SELECTED
            border_colour = self.SELECTED_BORDER
            border_width = 4

        else:
            slot_colour = self.SLOT
            border_colour = self.SLOT_BORDER
            border_width = 2

        pygame.draw.rect(
            screen,
            slot_colour,
            rect,
            border_radius=6,
        )

        pygame.draw.rect(
            screen,
            border_colour,
            rect,
            width=border_width,
            border_radius=6,
        )

        
        # NUMBER
        

        number = (
            str(index + 1)
            if index < 9
            else "0"
        )

        font = pygame.font.Font(
            None,
            16,
        )

        number_surface = font.render(
            number,
            True,
            self.TEXT,
        )

        screen.blit(
            number_surface,
            (
                rect.left + 5,
                rect.top + 3,
            ),
        )

        
        # ITEM
        

        item = slot.get_item()

        if item is not None:

            self._draw_item(
                screen,
                item,
                rect,
            )

    
    # DRAW ITEM
    

    def _draw_item(
        self,
        screen: pygame.Surface,
        item: Any,
        slot_rect: pygame.Rect,
    ):

        source = (
            getattr(item, "sprite", None)
            or getattr(
                item,
                "visual_asset",
                None,
            )
        )

        
        # PYGAME SURFACE
        

        if isinstance(
            source,
            pygame.Surface,
        ):

            icon = pygame.transform.smoothscale(
                source,
                (
                    slot_rect.width - 12,
                    slot_rect.height - 12,
                ),
            )

            screen.blit(
                icon,
                icon.get_rect(
                    center=slot_rect.center
                ),
            )

        
        # FILE PATH
        

        elif isinstance(
            source,
            (str, Path),
        ):

            path = str(source)

            if path not in self._sprite_cache:

                try:

                    self._sprite_cache[path] = (
                        pygame.image.load(
                            path
                        ).convert_alpha()
                    )

                except (
                    pygame.error,
                    FileNotFoundError,
                ):

                    self._sprite_cache[path] = None

            icon = self._sprite_cache.get(
                path
            )

            if icon is not None:

                icon = pygame.transform.smoothscale(
                    icon,
                    (
                        slot_rect.width - 12,
                        slot_rect.height - 12,
                    ),
                )

                screen.blit(
                    icon,
                    icon.get_rect(
                        center=slot_rect.center
                    ),
                )

        
        # FALLBACK
        

        else:

            fallback = pygame.Rect(
                0,
                0,
                28,
                28,
            )

            fallback.center = (
                slot_rect.centerx,
                slot_rect.centery + 3,
            )

            pygame.draw.circle(
                screen,
                (72, 149, 168),
                fallback.center,
                14,
            )

            font = pygame.font.Font(
                None,
                18,
            )

            name = str(
                getattr(
                    item,
                    "name",
                    "?",
                )
            )

            initial = font.render(
                name[0].upper(),
                True,
                self.TEXT,
            )

            screen.blit(
                initial,
                initial.get_rect(
                    center=fallback.center
                ),
            )

        
        # QUANTITY
        

        quantity = getattr(
            item,
            "quantity",
            1,
        )

        if quantity > 1:

            font = pygame.font.Font(
                None,
                15,
            )

            quantity_surface = font.render(
                str(quantity),
                True,
                self.TEXT,
            )

            screen.blit(
                quantity_surface,
                quantity_surface.get_rect(
                    bottomright=(
                        slot_rect.right - 4,
                        slot_rect.bottom - 3,
                    )
                ),
            )

    
    # INVENTORY COMPATIBILITY
    

    def render_hotbar_in_inventory(
        self,
        origin_x: int = 0,
        origin_y: int = 0,
        slot_spacing: int = 48,
    ) -> None:

        for index in range(
            min(
                config.HOTBAR_SLOT_COUNT,
                len(self.hotbar_slots),
            )
        ):

            x_pos = (
                origin_x
                + index
                * slot_spacing
            )

            y_pos = origin_y

            item = (
                self.hotbar_slots[index]
                .get_item()
            )

            self.draw_slot(
                item,
                x_pos,
                y_pos,
                index,
            )

    def draw_slot(
        self,
        item: Optional[Any],
        x_pos: int,
        y_pos: int,
        index: int,
    ) -> None:

        if self._on_draw_slot:

            self._on_draw_slot(
                item,
                x_pos,
                y_pos,
            )

    
    # TRANSFER INVENTORY -> HOTBAR
    

    def transfer_to_hotbar(
        self,
        inventory_item_slot: InventorySlot,
        hotbar_index: int,
    ) -> None:

        if (
            hotbar_index < 0
            or hotbar_index >= len(
                self.hotbar_slots
            )
        ):
            return

        target_slot = (
            self.hotbar_slots[
                hotbar_index
            ]
        )

        if self.inventory_manager:

            self.inventory_manager.move_item(
                inventory_item_slot,
                target_slot,
            )

        else:

            target_slot.set_item(
                inventory_item_slot.get_item()
            )

            inventory_item_slot.clear()