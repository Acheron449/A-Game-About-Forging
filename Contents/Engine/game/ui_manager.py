"""In-game UI toggles: quests, minimap, settings (uimanager.txt)."""

from __future__ import annotations

from typing import Callable, List, Optional

import pygame

from config.config import config


class UIManager:
    def __init__(
        self,
        on_toggle_quest: Optional[Callable[[bool], None]] = None,
        on_toggle_minimap: Optional[Callable[[bool], None]] = None,
        on_toggle_settings: Optional[Callable[[bool], None]] = None,
        on_pause: Optional[Callable[[bool], None]] = None,
        on_render_quests: Optional[Callable[[List[str]], None]] = None,
    ):
        self.is_quest_list_open = False
        self.is_minimap_open = False
        self.is_settings_open = False
        self._on_toggle_quest = on_toggle_quest
        self._on_toggle_minimap = on_toggle_minimap
        self._on_toggle_settings = on_toggle_settings
        self._on_pause = on_pause
        self._on_render_quests = on_render_quests
        self._active_quests: List[str] = [
            'Oh brother this guy STINKS',
        ]

    def handle_ui_keydown(self, key: int) -> None:
        """Prefer this from the event loop (one toggle per key press)."""
        if key == config.UI_QUEST_TOGGLE_KEY:
            self.is_quest_list_open = not self.is_quest_list_open
            self.toggle_quest_ui(self.is_quest_list_open)
        elif key == config.UI_MINIMAP_TOGGLE_KEY:
            self.is_minimap_open = not self.is_minimap_open
            self.toggle_minimap_ui(self.is_minimap_open)
        elif key == config.QUIT_KEY:
            self.is_settings_open = not self.is_settings_open
            self.toggle_settings_menu(self.is_settings_open)
            self.pause_game(self.is_settings_open)

    def handle_ui_input(self, keys_pressed) -> None:
        """Held-key polling (may repeat while key is held)."""
        if keys_pressed[config.UI_QUEST_TOGGLE_KEY]:
            self.handle_ui_keydown(config.UI_QUEST_TOGGLE_KEY)
        if keys_pressed[config.UI_MINIMAP_TOGGLE_KEY]:
            self.handle_ui_keydown(config.UI_MINIMAP_TOGGLE_KEY)
        if keys_pressed[config.QUIT_KEY]:
            self.handle_ui_keydown(config.QUIT_KEY)

    def toggle_quest_ui(self, is_open: bool) -> None:
        if self._on_toggle_quest:
            self._on_toggle_quest(is_open)
        if is_open:
            self.update_quest_list()

    def toggle_minimap_ui(self, is_open: bool) -> None:
        if self._on_toggle_minimap:
            self._on_toggle_minimap(is_open)

    def toggle_settings_menu(self, is_open: bool) -> None:
        if self._on_toggle_settings:
            self._on_toggle_settings(is_open)

    def pause_game(self, paused: bool) -> None:
        if self._on_pause:
            self._on_pause(paused)

    def update_quest_list(self) -> None:
        lines = [f'Quests [{len(self._active_quests)}]']
        for quest in self._active_quests:
            lines.append(f'- {quest}')
        if self._on_render_quests:
            self._on_render_quests(lines)

    def set_active_quests(self, quests: List[str]) -> None:
        self._active_quests = list(quests)
