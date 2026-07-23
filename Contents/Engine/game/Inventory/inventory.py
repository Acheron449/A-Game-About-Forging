"""Bag inventory data, presentation, and drag-and-drop interaction."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import pygame

from Contents.configuration.constants import config, get_game_font


class InventorySlot:
    """One persistent storage location in the bag or hotbar."""

    def __init__(self) -> None:
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
    """Owns the bag slots and moves item references between compatible grids."""

    def __init__(
        self,
        total_bag_slots: int = config.INVENTORY_BAG_SLOT_COUNT,
        on_open: Optional[Callable[[], None]] = None,
        on_close: Optional[Callable[[], None]] = None,
        on_render: Optional[Callable[[], None]] = None,
        on_pause: Optional[Callable[[bool], None]] = None,
    ) -> None:
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
        return next((slot for slot in self.bag_slots if slot.is_empty()), None)

    def move_to_bag(self, item: Any) -> bool:
        empty = self.first_empty_slot()
        if empty is None:
            return False
        empty.set_item(item)
        return True

    def toggle_inventory_ui(self) -> None:
        self.is_inventory_open = not self.is_inventory_open
        if self._on_pause:
            self._on_pause(self.is_inventory_open)
        if self.is_inventory_open:
            if self._on_open:
                self._on_open()
            if self._on_render:
                self._on_render()
        elif self._on_close:
            self._on_close()

    def move_item(self, source_slot: InventorySlot, destination_slot: InventorySlot) -> None:
        """Move into an empty slot or swap the two items when it is occupied."""
        if source_slot is destination_slot or source_slot.is_empty():
            return
        source_item = source_slot.get_item()
        destination_item = destination_slot.get_item()
        destination_slot.set_item(source_item)
        if destination_item is None:
            source_slot.clear()
        else:
            source_slot.set_item(destination_item)

    def close_inventory_screen(self) -> None:
        if self.is_inventory_open:
            self.toggle_inventory_ui()


@dataclass
class InventoryItem:
    """Renderer-friendly item data. Existing game items work without conversion."""

    name: str
    type: str = 'material'
    sprite: Optional[Any] = None
    quantity: int = 1
    stats_bonus: Optional[Dict[str, int]] = None
    animation_type: Optional[str] = None


class InventoryScreen:
    """The in-game inventory overlay shown with ``I``.

    It renders the 10 x 5 bag grid from the reference layout and the existing
    ten-slot hotbar. Dragging between any two slots moves or swaps item objects.
    """

    OVERLAY = (4, 18, 13, 190)
    PANEL = (210, 177, 128)
    PANEL_DARK = (48, 57, 49)
    PANEL_BORDER = (127, 77, 47)
    SLOT = (110, 113, 108)
    SLOT_HOVER = (150, 142, 104)
    SLOT_BORDER = (70, 69, 63)
    TEXT = (245, 236, 211)
    MUTED_TEXT = (80, 72, 58)

    def __init__(self, inventory_manager: InventoryManager, hotbar: Optional[Any] = None) -> None:
        self.inventory_manager = inventory_manager
        self.hotbar = hotbar
        self.title_font = get_game_font(33, bold=True)
        self.label_font = get_game_font(18, bold=True)
        self.small_font = get_game_font(15)
        self._slot_rects: List[Tuple[InventorySlot, pygame.Rect]] = []
        self._dragged_slot: Optional[InventorySlot] = None
        self._dragged_item: Optional[Any] = None
        self._drag_position = (0, 0)
        self._sprite_cache: Dict[str, pygame.Surface] = {}

    @property
    def is_open(self) -> bool:
        return self.inventory_manager.is_inventory_open

    def toggle(self) -> None:
        self.inventory_manager.toggle_inventory_ui()
        self._cancel_drag()

    def close(self) -> None:
        self.inventory_manager.close_inventory_screen()
        self._cancel_drag()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Consume mouse input while the inventory is visible."""
        if not self.is_open:
            return False
        if event.type == pygame.MOUSEMOTION:
            self._drag_position = event.pos
            return self._dragged_slot is not None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            slot = self._slot_at(event.pos)
            if slot is not None and not slot.is_empty():
                self._dragged_slot = slot
                self._dragged_item = slot.get_item()
                self._drag_position = event.pos
            return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            destination = self._slot_at(event.pos)
            if self._dragged_slot is not None and destination is not None:
                self.inventory_manager.move_item(self._dragged_slot, destination)
            self._cancel_drag()
            return True
        return False

    def draw(self, screen: pygame.Surface, player_sprite: Optional[pygame.Surface] = None) -> None:
        if not self.is_open:
            return
        width, height = screen.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill(self.OVERLAY)
        screen.blit(overlay, (0, 0))
        panel = pygame.Rect(0, 0, min(760, width - 44), min(650, height - 44))
        panel.center = (width // 2, height // 2)
        pygame.draw.rect(screen, self.PANEL, panel, border_radius=10)
        pygame.draw.rect(screen, self.PANEL_BORDER, panel, width=4, border_radius=10)
        self._slot_rects.clear()

        title = self.title_font.render('INVENTORY', True, self.PANEL_DARK)
        screen.blit(title, (panel.left + 28, panel.top + 20))
        help_text = self.small_font.render('Drag items to organise your bag or hotbar  •  I to close', True, self.MUTED_TEXT)
        screen.blit(help_text, (panel.left + 28, panel.top + 62))

        self._draw_character_preview(screen, pygame.Rect(panel.left + 28, panel.top + 102, 182, 305), player_sprite)
        grid_x, grid_y = panel.left + 238, panel.top + 110
        self._draw_grid(screen, grid_x, grid_y)
        self._draw_hotbar(screen, panel.left + 42, panel.bottom - 86)
        hint = self.small_font.render('BAG  50 SLOTS', True, self.PANEL_DARK)
        screen.blit(hint, (grid_x, grid_y - 25))

        if self._dragged_item is not None:
            self._draw_item(screen, self._dragged_item, pygame.Rect(0, 0, 48, 48), self._drag_position, ghost=True)

    def _draw_character_preview(self, screen: pygame.Surface, rect: pygame.Rect, player_sprite: Optional[pygame.Surface]) -> None:
        pygame.draw.rect(screen, (190, 157, 111), rect, border_radius=8)
        pygame.draw.rect(screen, self.PANEL_BORDER, rect, width=2, border_radius=8)
        label = self.label_font.render('EQUIPPED', True, self.PANEL_DARK)
        screen.blit(label, label.get_rect(midtop=(rect.centerx, rect.top + 10)))
        figure = pygame.Rect(0, 0, 54, 105)
        figure.center = (rect.centerx, rect.centery + 28)
        pygame.draw.circle(screen, (72, 87, 80), (figure.centerx, figure.top + 16), 15)
        pygame.draw.rect(screen, (72, 87, 80), (figure.left + 9, figure.top + 30, 36, 48), border_radius=10)
        pygame.draw.rect(screen, (72, 87, 80), (figure.left + 5, figure.top + 70, 18, 32), border_radius=6)
        pygame.draw.rect(screen, (72, 87, 80), (figure.right - 23, figure.top + 70, 18, 32), border_radius=6)
        if player_sprite:
            preview = pygame.transform.smoothscale(player_sprite, (70, 70))
            screen.blit(preview, preview.get_rect(center=(rect.centerx, rect.centery + 28)))
        for index, text in enumerate(('Head', 'Chest', 'Legs', 'Boots')):
            slot = pygame.Rect(rect.left + 9, rect.top + 48 + index * 51, 34, 34)
            pygame.draw.rect(screen, self.SLOT, slot, border_radius=5)
            pygame.draw.rect(screen, self.SLOT_BORDER, slot, width=2, border_radius=5)
            caption = self.small_font.render(text, True, self.MUTED_TEXT)
            screen.blit(caption, (slot.right + 4, slot.centery - caption.get_height() // 2))

    def _draw_grid(self, screen: pygame.Surface, x: int, y: int) -> None:
        size, gap = 43, 5
        for index, slot in enumerate(self.inventory_manager.bag_slots):
            rect = pygame.Rect(x + (index % 10) * (size + gap), y + (index // 10) * (size + gap), size, size)
            self._draw_slot(screen, slot, rect)

    def _draw_hotbar(self, screen: pygame.Surface, x: int, y: int) -> None:
        label = self.label_font.render('HOTBAR', True, self.PANEL_DARK)
        screen.blit(label, (x, y - 29))
        if self.hotbar is None:
            return
        size, gap = 51, 8
        for index, slot in enumerate(self.hotbar.hotbar_slots):
            self._draw_slot(screen, slot, pygame.Rect(x + index * (size + gap), y, size, size), str((index + 1) % 10))

    def _draw_slot(self, screen: pygame.Surface, slot: InventorySlot, rect: pygame.Rect, key_label: str = '') -> None:
        colour = self.SLOT_HOVER if rect.collidepoint(pygame.mouse.get_pos()) else self.SLOT
        pygame.draw.rect(screen, colour, rect, border_radius=6)
        pygame.draw.rect(screen, self.SLOT_BORDER, rect, width=3, border_radius=6)
        self._slot_rects.append((slot, rect))
        if key_label:
            label = self.small_font.render(key_label, True, self.MUTED_TEXT)
            screen.blit(label, (rect.left + 4, rect.top + 2))
        if slot is not self._dragged_slot and not slot.is_empty():
            self._draw_item(screen, slot.get_item(), rect, rect.center)

    def _draw_item(self, screen: pygame.Surface, item: Any, slot_rect: pygame.Rect, center: Tuple[int, int], ghost: bool = False) -> None:
        icon = self._item_sprite(item, slot_rect.size)
        if icon:
            if ghost:
                icon = icon.copy()
                icon.set_alpha(180)
            screen.blit(icon, icon.get_rect(center=center))
        else:
            colour = (190, 83, 58) if getattr(item, 'type', '') == 'weapon' else (72, 149, 168)
            fallback = pygame.Rect(0, 0, slot_rect.width - 14, slot_rect.height - 14)
            fallback.center = center
            pygame.draw.circle(screen, colour, fallback.center, fallback.width // 2)
            initial = self.label_font.render(str(getattr(item, 'name', '?'))[0].upper(), True, self.TEXT)
            screen.blit(initial, initial.get_rect(center=fallback.center))
        quantity = getattr(item, 'quantity', 1)
        if quantity and quantity > 1:
            amount = self.small_font.render(str(quantity), True, self.TEXT)
            screen.blit(amount, amount.get_rect(bottomright=(slot_rect.right - 3, slot_rect.bottom - 2)))

    def _item_sprite(self, item: Any, size: Tuple[int, int]) -> Optional[pygame.Surface]:
        source = getattr(item, 'sprite', None) or getattr(item, 'visual_asset', None)
        if isinstance(source, pygame.Surface):
            return pygame.transform.smoothscale(source, (size[0] - 8, size[1] - 8))
        if not isinstance(source, (str, Path)):
            return None
        path = str(source)
        if path not in self._sprite_cache:
            try:
                self._sprite_cache[path] = pygame.image.load(path).convert_alpha()
            except (pygame.error, FileNotFoundError):
                return None
        return pygame.transform.smoothscale(self._sprite_cache[path], (size[0] - 8, size[1] - 8))

    def _slot_at(self, position: Tuple[int, int]) -> Optional[InventorySlot]:
        return next((slot for slot, rect in self._slot_rects if rect.collidepoint(position)), None)

    def _cancel_drag(self) -> None:
        self._dragged_slot = None
        self._dragged_item = None
