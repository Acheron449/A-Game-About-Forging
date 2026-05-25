"""Main menu flow (mainmenumanager.txt)."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from ..config.config import SCENE_MAIN_WORLD, SCENE_TUTORIAL, WINDOW_TITLE
from .save_manager import SaveManager


class MainMenuManager:
    def __init__(
        self,
        save_manager: Optional[SaveManager] = None,
        on_render_title: Optional[Callable[[str], None]] = None,
        on_enable_button: Optional[Callable[[str], None]] = None,
        on_disable_button: Optional[Callable[[str], None]] = None,
        on_display_prompt: Optional[Callable[[str], None]] = None,
        on_load_scene: Optional[Callable[[str], None]] = None,
        on_apply_save: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_initialize_new_game: Optional[Callable[[], None]] = None,
        on_toggle_settings: Optional[Callable[[bool], None]] = None,
        on_quit_application: Optional[Callable[[], None]] = None,
        user_confirms: Optional[Callable[[], bool]] = None,
    ):
        self.game_title = WINDOW_TITLE
        self.is_settings_menu_open = False
        self.save_manager = save_manager or SaveManager()
        self._on_render_title = on_render_title
        self._on_enable_button = on_enable_button
        self._on_disable_button = on_disable_button
        self._on_display_prompt = on_display_prompt
        self._on_load_scene = on_load_scene
        self._on_apply_save = on_apply_save
        self._on_initialize_new_game = on_initialize_new_game
        self._on_toggle_settings = on_toggle_settings
        self._on_quit_application = on_quit_application
        self._user_confirms = user_confirms or (lambda: True)

    def initialize_menu(self) -> None:
        if self._on_render_title:
            self._on_render_title(self.game_title)
        if self.save_manager.check_for_existing_save():
            if self._on_enable_button:
                self._on_enable_button('Continue')
        else:
            if self._on_disable_button:
                self._on_disable_button('Continue')

    def handle_input(self, button_clicked: str) -> None:
        handlers = {
            'Continue': self.on_continue_clicked,
            'NewGame': self.on_new_game_clicked,
            'Settings': self.on_settings_clicked,
            'Quit': self.on_quit_clicked,
        }
        handler = handlers.get(button_clicked)
        if handler:
            handler()

    def on_continue_clicked(self) -> None:
        save_file = self.save_manager.retrieve_last_known_save()
        if self.save_manager.is_recognized(save_file):
            if self._on_load_scene:
                self._on_load_scene(SCENE_MAIN_WORLD)
            if self._on_apply_save:
                self._on_apply_save(save_file)
        else:
            self._show_prompt('Save file corrupted or missing.')

    def on_new_game_clicked(self) -> None:
        self._show_prompt('Are you sure? This may overwrite previous auto-saves.')
        if self._user_confirms():
            new_save = self.save_manager.create_new_save_file()
            if self._on_initialize_new_game:
                self._on_initialize_new_game()
            if self._on_apply_save:
                self._on_apply_save(new_save)
            if self._on_load_scene:
                self._on_load_scene(SCENE_TUTORIAL)

    def on_settings_clicked(self) -> None:
        self.is_settings_menu_open = not self.is_settings_menu_open
        if self._on_toggle_settings:
            self._on_toggle_settings(self.is_settings_menu_open)

    def on_quit_clicked(self) -> None:
        self._show_prompt('Are you sure you want to quit?')
        if self._user_confirms() and self._on_quit_application:
            self._on_quit_application()

    def _show_prompt(self, message: str) -> None:
        if self._on_display_prompt:
            self._on_display_prompt(message)
