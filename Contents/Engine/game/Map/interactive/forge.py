"""Tiled forge interaction and its in-game forge window."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import pygame

from ...forge_system import ForgeInterface, ForgeSystem


class Forge:
    """A rectangular Tiled interaction object that opens the forge window."""

    def __init__(self, rect: pygame.Rect, name: str = "Forge") -> None:
        self.rect = pygame.Rect(rect)
        self.name = name
        self.class_name = "forge"

    def can_interact(self, player_rect: pygame.Rect) -> bool:
        return self.rect.colliderect(player_rect)

    def interact(self, play_state: Dict[str, Any], screen_size: Tuple[int, int]) -> bool:
        forge_window = play_state.get("forge_window")
        if forge_window is None:
            return False
        forge_window.open(self, screen_size)
        return True


class ForgeWindow:
    """Click + / - to choose ores, then click Forge Weapon."""

    PANEL = (53, 45, 39)
    PANEL_BORDER = (202, 151, 82)
    TEXT = (245, 236, 211)
    MUTED = (185, 170, 145)
    BUTTON = (101, 75, 53)
    BUTTON_HOVER = (137, 100, 66)
    SUCCESS = (133, 203, 112)
    ERROR = (230, 115, 100)

    def __init__(self, inventory_manager: Any) -> None:
        self.inventory_manager = inventory_manager
        self.forge_system = ForgeSystem()
        self.interface = ForgeInterface(self.forge_system, inventory_manager)
        self.is_open = False
        self.forge: Forge | None = None
        self.message = "Choose ores to forge a weapon."
        self.message_success = True
        self.window_rect = pygame.Rect(0, 0, 520, 500)
        self._ore_buttons: List[Tuple[str, pygame.Rect, pygame.Rect]] = []
        self._forge_button = pygame.Rect(0, 0, 200, 42)
        self._close_button = pygame.Rect(0, 0, 90, 34)
        self.title_font = pygame.font.Font(None, 34)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 19)

    def open(self, forge: Forge, screen_size: Tuple[int, int]) -> None:
        self.forge = forge
        self.interface = ForgeInterface(self.forge_system, self.inventory_manager)
        self.is_open = True
        self.message = "Choose ores to forge a weapon."
        self.message_success = True
        self.window_rect.center = (screen_size[0] // 2, screen_size[1] // 2)

    def close(self) -> None:
        self.is_open = False
        self.forge = None

    def _button(self, screen: pygame.Surface, rect: pygame.Rect, label: str) -> None:
        colour = self.BUTTON_HOVER if rect.collidepoint(pygame.mouse.get_pos()) else self.BUTTON
        pygame.draw.rect(screen, colour, rect, border_radius=6)
        pygame.draw.rect(screen, self.PANEL_BORDER, rect, 2, border_radius=6)
        text = self.font.render(label, True, self.TEXT)
        screen.blit(text, text.get_rect(center=rect.center))

    def _layout_controls(self) -> Dict[str, int]:
        ores = self.interface.available_ores()
        self._ore_buttons.clear()
        y = self.window_rect.top + 105
        for ore_name in sorted(ores):
            minus = pygame.Rect(self.window_rect.right - 155, y, 32, 30)
            plus = pygame.Rect(self.window_rect.right - 42, y, 32, 30)
            self._ore_buttons.append((ore_name, minus, plus))
            y += 38
        self._forge_button.center = (self.window_rect.centerx, self.window_rect.bottom - 52)
        self._close_button.topright = (self.window_rect.right - 14, self.window_rect.top + 14)
        return ores

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.is_open:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close()
            return True
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False

        ores = self._layout_controls()
        if self._close_button.collidepoint(event.pos):
            self.close()
            return True
        if self._forge_button.collidepoint(event.pos):
            result = self.interface.forge()
            self.message = result.message
            self.message_success = result.success
            return True
        for ore_name, minus, plus in self._ore_buttons:
            current = self.interface.ore_mix.get(ore_name, 0)
            if minus.collidepoint(event.pos):
                self.interface.set_ore_amount(ore_name, current - 1)
                return True
            if plus.collidepoint(event.pos):
                self.interface.set_ore_amount(ore_name, min(current + 1, ores[ore_name]))
                return True
        return self.window_rect.collidepoint(event.pos)

    def draw(self, screen: pygame.Surface) -> None:
        if not self.is_open:
            return
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, self.PANEL, self.window_rect, border_radius=12)
        pygame.draw.rect(screen, self.PANEL_BORDER, self.window_rect, 4, border_radius=12)

        title = self.title_font.render("FORGE", True, self.TEXT)
        screen.blit(title, (self.window_rect.left + 20, self.window_rect.top + 18))
        self._button(screen, self._close_button, "Close")

        ores = self._layout_controls()
        if not ores:
            text = self.font.render("No forgeable ores in your inventory.", True, self.MUTED)
            screen.blit(text, (self.window_rect.left + 20, self.window_rect.top + 105))
        for ore_name, minus, plus in self._ore_buttons:
            y = minus.top
            selected = self.interface.ore_mix.get(ore_name, 0)
            label = self.font.render(f"{ore_name}: {selected}/{ores[ore_name]}", True, self.TEXT)
            screen.blit(label, (self.window_rect.left + 22, y + 4))
            self._button(screen, minus, "-")
            self._button(screen, plus, "+")

        bonus = self.interface.rarity_preview_bonus()
        preview = self.small_font.render(f"Mixed-ore rarity bonus: +{bonus:.1f}%", True, self.MUTED)
        screen.blit(preview, (self.window_rect.left + 22, self.window_rect.bottom - 115))
        message_colour = self.SUCCESS if self.message_success else self.ERROR
        message = self.small_font.render(self.message, True, message_colour)
        screen.blit(message, (self.window_rect.left + 22, self.window_rect.bottom - 88))
        self._button(screen, self._forge_button, "Forge Weapon")
