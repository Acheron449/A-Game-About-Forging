"""Pause menu save/settings/quit (pausemenumanager.txt)."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from .save_manager import SaveManager


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
            'Save': self.on_save_clicked,
            'SaveAsNew': self.on_save_as_new_clicked,
            'Settings': self.on_settings_clicked,
            'Quit': self.on_quit_clicked,
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
        response = self._get_prompt_response(
            'Do you want to save your progress before quitting?',
            ['Yes', 'No', 'Cancel'],
        )
        if response == 'Yes':
            self.on_save_clicked()
            self._return_to_main_menu()
        elif response == 'No':
            self._return_to_main_menu()
        elif response == 'Cancel':
            pass  # Stay on pause menu

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
