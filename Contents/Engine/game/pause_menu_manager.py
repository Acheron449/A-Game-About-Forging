"""Pause menu save/settings/quit (pausemenumanager.txt)."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple

import pygame

from Contents.Engine.configuration.constants import get_game_font
from .save_manager import SaveManager
from .Settings.settings_ui_manager import SettingsUIManager


class PauseMenuManager:
    def __init__(
        self,
        save_manager: Optional[SaveManager] = None,
        active_save_id: Optional[str] = None,
        on_pause_time: Optional[Callable[[bool], None]] = None,
        on_render_pause_ui: Optional[Callable[[bool], None]] = None,
        on_capture_state: Optional[Callable[[], Dict[str, Any]]] = None,
        on_notification: Optional[Callable[[str], None]] = None,
        on_open_settings: Optional[Callable[[], None]] = None,
        on_return_main_menu: Optional[Callable[[], None]] = None,
        on_quit_game: Optional[Callable[[], None]] = None,
        on_prompt: Optional[Callable[[str, List[str]], str]] = None,
    ):
        self.is_paused = False
        self.save_manager = save_manager or SaveManager()
        self.current_save_file_id = active_save_id or ''
        self._on_pause_time = on_pause_time
        self._on_render_pause_ui = on_render_pause_ui
        self._on_capture_state = on_capture_state
        self._on_notification = on_notification
        self._on_open_settings = on_open_settings
        self._on_return_main_menu = on_return_main_menu
        self._on_quit_game = on_quit_game
        self._on_prompt = on_prompt

    def set_active_save_id(self, save_id: str) -> None:
        self.current_save_file_id = save_id

    def toggle_pause_menu(self) -> None:
        self.is_paused = not self.is_paused
        if self.is_paused:
            if self._on_pause_time:
                self._on_pause_time(True)
            if self._on_render_pause_ui:
                self._on_render_pause_ui(True)
        else:
            if self._on_pause_time:
                self._on_pause_time(False)
            if self._on_render_pause_ui:
                self._on_render_pause_ui(False)

    def handle_input(self, button_clicked: str) -> None:
        handlers = {
            'save': self.on_save_clicked,
            'save_as_new': self.on_save_as_new_clicked,
            'settings': self.on_settings_clicked,
            'quit': self.on_quit_clicked,
        }
        handler = handlers.get(button_clicked)
        if handler:
            handler()

    def on_save_clicked(self) -> None:
        if not self.current_save_file_id:
            return
        current_game_state = self._capture_state()
        self.save_manager.overwrite_save(self.current_save_file_id, current_game_state)
        self._notify('Game Saved Successfully.')

    def on_save_as_new_clicked(self) -> None:
        current_game_state = self._capture_state()
        new_save_id = self.save_manager.create_new_save(current_game_state)
        self.current_save_file_id = new_save_id
        self._notify('New Save Created.')

    def on_settings_clicked(self) -> None:
        if self._on_open_settings:
            self._on_open_settings()

    def on_quit_clicked(self) -> None:
        """Close the application, matching the title menu's Quit Game action."""
        if self._on_quit_game:
            self._on_quit_game()

    def _capture_state(self) -> Dict[str, Any]:
        if self._on_capture_state:
            return self._on_capture_state()
        return SaveManager.generate_default_starting_stats()

    def _notify(self, message: str) -> None:
        if self._on_notification:
            self._on_notification(message)

    def _get_prompt_response(self, message: str, options: List[str]) -> str:
        if self._on_prompt:
            return self._on_prompt(message, options)
        return 'Cancel'

    def _return_to_main_menu(self) -> None:
        if self._on_return_main_menu:
            self._on_return_main_menu()


class PauseScreen:
    """Render a paused game overlay with save/settings/quit buttons."""

    PANEL_COLOR = (36, 36, 46)
    PANEL_BORDER_COLOR = (192, 160, 96)
    BUTTON_COLOR = (80, 74, 60)
    BUTTON_DISABLED_COLOR = (60, 60, 60)
    BUTTON_BORDER_COLOR = (210, 190, 130)
    TEXT_COLOR = (240, 236, 220)
    OVERLAY_COLOR = (8, 8, 12, 190)

    BUTTON_LABELS = {
        'save': 'Save',
        'save_as_new': 'Save as New',
        'settings': 'Settings',
        'quit': 'Quit Game',
    }

    def __init__(self, pause_menu: PauseMenuManager, screen_size: Tuple[int, int]):
        self.pause_menu = pause_menu
        self.screen_size = screen_size
        self.title_font = get_game_font(56)
        self.button_font = get_game_font(34)
        self.prompt_font = get_game_font(22)
        self.button_rects: List[tuple[str, pygame.Rect]] = []

    def render(self, screen: pygame.Surface) -> None:
        if not self.pause_menu.is_paused:
            return

        width, height = self.screen_size
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill(self.OVERLAY_COLOR)
        screen.blit(overlay, (0, 0))

        panel_width = 560
        panel_height = 420
        panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
        panel_rect.center = (width // 2, height // 2)

        pygame.draw.rect(screen, self.PANEL_COLOR, panel_rect, border_radius=22)
        pygame.draw.rect(screen, self.PANEL_BORDER_COLOR, panel_rect, width=3, border_radius=22)

        title_surface = self.title_font.render('Paused', True, self.TEXT_COLOR)
        title_rect = title_surface.get_rect(midtop=(panel_rect.centerx, panel_rect.top + 40))
        screen.blit(title_surface, title_rect)

        subtitle_surface = self.prompt_font.render('Press ESC again to resume or choose an action.', True, self.TEXT_COLOR)
        subtitle_rect = subtitle_surface.get_rect(midtop=(panel_rect.centerx, title_rect.bottom + 12))
        screen.blit(subtitle_surface, subtitle_rect)

        self.button_rects = self.layout_buttons(panel_rect)
        for button_id, rect in self.button_rects:
            enabled = button_id != 'save' or bool(self.pause_menu.current_save_file_id)
            button_color = self.BUTTON_COLOR if enabled else self.BUTTON_DISABLED_COLOR
            pygame.draw.rect(screen, button_color, rect, border_radius=18)
            pygame.draw.rect(screen, self.BUTTON_BORDER_COLOR, rect, width=2, border_radius=18)
            label = self.BUTTON_LABELS[button_id]
            label_surface = self.button_font.render(label, True, self.TEXT_COLOR if enabled else (180, 180, 180))
            label_rect = label_surface.get_rect(center=rect.center)
            screen.blit(label_surface, label_rect)

        if self.pause_menu.current_save_file_id:
            footer_text = 'Current save ready to overwrite.'
        else:
            footer_text = 'Save as New to create a save file first.'
        footer_surface = self.prompt_font.render(footer_text, True, self.TEXT_COLOR)
        footer_rect = footer_surface.get_rect(midtop=(panel_rect.centerx, panel_rect.bottom - 40))
        screen.blit(footer_surface, footer_rect)

    def layout_buttons(self, panel_rect: pygame.Rect) -> List[tuple[str, pygame.Rect]]:
        button_ids = ['save', 'save_as_new', 'settings', 'quit']
        button_width = 360
        button_height = 62
        spacing = 16
        total_height = len(button_ids) * button_height + (len(button_ids) - 1) * spacing
        top = panel_rect.centery - total_height // 2 + 20

        rects: List[tuple[str, pygame.Rect]] = []
        for index, button_id in enumerate(button_ids):
            rect = pygame.Rect(0, 0, button_width, button_height)
            rect.centerx = panel_rect.centerx
            rect.top = top + index * (button_height + spacing)
            rects.append((button_id, rect))
        return rects

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        for button_id, rect in self.button_rects:
            if rect.collidepoint(event.pos):
                if button_id == 'save' and not self.pause_menu.current_save_file_id:
                    return
                self.pause_menu.handle_input(button_id)
                break
