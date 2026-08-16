"""Interactive loot points and loot window."""

from __future__ import annotations

from typing import Any, Optional

import pygame

from ...Inventory.item_identifier import create_item
from ...Loot.loot_generator import roll_loot


class LootPoint:

    def __init__(
        self,
        rect: pygame.Rect,
        name: str = "Loot",
        loot_id: Optional[str] = None,
        loot_pool: Optional[str] = None,
        loot_type: str = "fixed",
        capacity: int = 1,
    ):
        self.rect = rect
        self.name = name
        self.class_name = "loot_point"

        self.loot_id = loot_id
        self.loot_pool = loot_pool
        self.loot_type = loot_type
        self.capacity = capacity

        self.item: Optional[Any] = None
        self.opened = False

        self._generate_loot()

    def _generate_loot(self) -> None:

        if self.loot_id:
            self.item = create_item(self.loot_id)
            return

        if self.loot_pool:
            self.item = self._generate_from_pool()

    def _generate_from_pool(self):

        item_id = roll_loot(self.loot_pool)

        if item_id is None:
            return None

        return create_item(item_id)

    def can_interact(self, player_rect=None) -> bool:

        if self.opened or self.item is None:
            return False

        if player_rect is None:
            return True

        return self.rect.colliderect(player_rect)

    

    def interact(
        self,
        game_state=None,
        *args,
        **kwargs,
    ):
        """Open the in-game loot window."""

        if self.opened or self.item is None:
            return False

        if not isinstance(game_state, dict):
            return False

        loot_window = game_state.get(
            "loot_window"
        )

        if loot_window is None:
            return False

        screen = game_state.get("screen")

        if screen is None:
            return False

        loot_window.open(
            self,
            screen.get_size(),
        )

        return True

    def take_item(self):
        """Remove and return the item held by this loot point."""

        if self.opened or self.item is None:
            return None

        item = self.item

        self.item = None
        self.opened = True

        return item


class LootWindow:
    """In-game loot window rendered directly onto the main Pygame screen."""

    OVERLAY = (4, 18, 13, 120)

    PANEL = (210, 177, 128)
    PANEL_DARK = (48, 57, 49)
    PANEL_BORDER = (127, 77, 47)

    SLOT = (110, 113, 108)
    SLOT_HOVER = (150, 142, 104)
    SLOT_BORDER = (70, 69, 63)

    TEXT = (245, 236, 211)
    MUTED_TEXT = (80, 72, 58)

    def __init__(self, inventory_manager):
        self.inventory_manager = inventory_manager

        self.is_open = False
        self.loot_point = None

        self.window_rect = pygame.Rect(
            0,
            0,
            360,
            300,
        )

        self.item_rect = pygame.Rect(
            0,
            0,
            96,
            96,
        )

        self.title_font = pygame.font.Font(
            None,
            32,
        )

        self.label_font = pygame.font.Font(
            None,
            20,
        )

        self.small_font = pygame.font.Font(
            None,
            16,
        )

        self._sprite_cache = {}

    
    # OPEN / CLOSE
    

    def open(self, loot_point, screen_size):
        """Open the loot window in the centre of the game screen."""

        self.loot_point = loot_point
        self.is_open = True

        width, height = screen_size

        self.window_rect.center = (
            width // 2,
            height // 2,
        )

        self.item_rect.center = (
            self.window_rect.centerx,
            self.window_rect.centery + 15,
        )

    def close(self):
        self.is_open = False
        self.loot_point = None

    
    # EVENTS
    

    def handle_event(self, event):
        """Handle mouse/keyboard input while the loot window is open."""

        if not self.is_open:
            return False

        # ESC closes the loot window
        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE
        ):
            self.close()
            return True

        # Mouse click
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):

            # Clicked the loot item
            if self.item_rect.collidepoint(event.pos):

                self._take_item()

                return True

            # Clicked somewhere inside the window
            if self.window_rect.collidepoint(event.pos):
                return True

            # Clicked outside the window
            self.close()

            return True

        return False

    
    # TAKE ITEM
    

    def _take_item(self):

        if self.loot_point is None:
            return

        item = self.loot_point.item

        if item is None:
            return

        # Try to put the item into the player's inventory.
        success = self.inventory_manager.move_to_bag(
            item
        )

        if not success:
            return

        # Only remove the item from the loot point
        # after the inventory accepted it.
        self.loot_point.take_item()

        self.close()

    # DRAW

    def draw(self, screen):
        """Draw the loot window onto the existing game screen."""

        if not self.is_open:
            return

        width, height = screen.get_size()

        # DARKEN GAME BEHIND WINDOW

        overlay = pygame.Surface(
            (width, height),
            pygame.SRCALPHA,
        )

        overlay.fill(self.OVERLAY)

        screen.blit(
            overlay,
            (0, 0),
        )

        # PANEL

        pygame.draw.rect(
            screen,
            self.PANEL,
            self.window_rect,
            border_radius=10,
        )

        pygame.draw.rect(
            screen,
            self.PANEL_BORDER,
            self.window_rect,
            width=4,
            border_radius=10,
        )

        # TITLE

        title = self.title_font.render(
            "LOOT",
            True,
            self.PANEL_DARK,
        )

        screen.blit(
            title,
            (
                self.window_rect.left + 24,
                self.window_rect.top + 18,
            ),
        )

        # ITEM SLOT

        slot_colour = self.SLOT

        if self.item_rect.collidepoint(
            pygame.mouse.get_pos()
        ):
            slot_colour = self.SLOT_HOVER

        pygame.draw.rect(
            screen,
            slot_colour,
            self.item_rect,
            border_radius=8,
        )

        pygame.draw.rect(
            screen,
            self.SLOT_BORDER,
            self.item_rect,
            width=3,
            border_radius=8,
        )

        # ITEM

        if self.loot_point is not None:

            item = self.loot_point.item

            if item is not None:

                self._draw_item(
                    screen,
                    item,
                    self.item_rect,
                )

                # Item name
                item_name = self.label_font.render(
                    str(
                        getattr(
                            item,
                            "name",
                            "Unknown Item",
                        )
                    ),
                    True,
                    self.PANEL_DARK,
                )

                screen.blit(
                    item_name,
                    item_name.get_rect(
                        center=(
                            self.window_rect.centerx,
                            self.item_rect.bottom + 30,
                        )
                    ),
                )

        # INSTRUCTION

        instruction = self.small_font.render(
            "Click the item to take it",
            True,
            self.MUTED_TEXT,
        )

        screen.blit(
            instruction,
            instruction.get_rect(
                center=(
                    self.window_rect.centerx,
                    self.window_rect.bottom - 30,
                )
            ),
        )

    # ITEM RENDERING

    def _draw_item(
        self,
        screen,
        item,
        slot_rect,
    ):
        """Draw an item's sprite using the same logic as InventoryScreen."""

        source = (
            getattr(item, "sprite", None)
            or getattr(item, "visual_asset", None)
        )

        icon = None

        # Already-loaded pygame Surface
        if isinstance(
            source,
            pygame.Surface,
        ):
            icon = source

        # Sprite path
        elif isinstance(
            source,
            str,
        ):
            icon = self._load_sprite(source)

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
                    center=slot_rect.center,
                ),
            )

            return

        # FALLBACK ICON

        item_type = getattr(
            item,
            "type",
            "",
        )

        if item_type == "weapon":
            fallback_colour = (190, 83, 58)

        elif item_type == "pickaxe":
            fallback_colour = (170, 130, 80)

        elif item_type == "consumable":
            fallback_colour = (100, 170, 100)

        else:
            fallback_colour = (72, 149, 168)

        radius = min(
            slot_rect.width,
            slot_rect.height,
        ) // 3

        pygame.draw.circle(
            screen,
            fallback_colour,
            slot_rect.center,
            radius,
        )

        name = str(
            getattr(
                item,
                "name",
                "?",
            )
        )

        initial = self.label_font.render(
            name[0].upper(),
            True,
            self.TEXT,
        )

        screen.blit(
            initial,
            initial.get_rect(
                center=slot_rect.center,
            ),
        )

    # SPRITE LOADING

    def _load_sprite(self, path):

        if path in self._sprite_cache:
            return self._sprite_cache[path]

        try:

            sprite = pygame.image.load(
                path
            ).convert_alpha()

            self._sprite_cache[path] = sprite

            return sprite

        except (
            pygame.error,
            FileNotFoundError,
        ):

            return None