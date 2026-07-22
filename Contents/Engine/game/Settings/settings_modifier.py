"""Apply settings and rebind keys (settingmodifier.txt)."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

import pygame

from ..Game.game_configuration import GameConfiguration


class SettingsModifier:
    def __init__(
        self,
        current_config: Optional[GameConfiguration] = None,
        on_audio_update: Optional[Callable[[str, float], None]] = None,
        on_overlay: Optional[Callable[[str], None]] = None,
        on_close_overlay: Optional[Callable[[], None]] = None,
        on_warning: Optional[Callable[[str], None]] = None,
        on_refresh_panel: Optional[Callable[[], None]] = None,
        get_next_input: Optional[Callable[[], Optional[str]]] = None,
    ):
        self.current_config = current_config or GameConfiguration()
        self.is_listening_for_input = False
        self._pending_action: Optional[str] = None
        self._on_audio_update = on_audio_update
        self._on_overlay = on_overlay
        self._on_close_overlay = on_close_overlay
        self._on_warning = on_warning
        self._on_refresh_panel = on_refresh_panel
        self._get_next_input = get_next_input

    def handle_setting_change(self, setting_name: str, new_value: Any) -> None:
        self.current_config.apply_setting(setting_name, new_value)
        if GameConfiguration.setting_category(setting_name) == 'Audio':
            if self._on_audio_update:
                self._on_audio_update(setting_name, float(new_value))

    def initiate_keybind_change(self, action_to_bind: str) -> None:
        self.is_listening_for_input = True
        self._pending_action = action_to_bind
        message = (
            f"Press any key to bind to {action_to_bind}... "
            "(Press ESC to cancel)"
        )
        if self._on_overlay:
            self._on_overlay(message)

    def poll_keybind_capture(self, event) -> bool:
        """Process one pygame event while listening; returns True when done."""
        if not self.is_listening_for_input or self._pending_action is None:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._finish_listen(cancelled=True)
                return True
            captured = pygame.key.name(event.key)
            if self.check_for_bind_conflict(captured):
                if self._on_warning:
                    self._on_warning('Key already in use!')
            else:
                bind_key = f"Bind_{self._pending_action}"
                self.current_config.apply_setting(bind_key, captured)
                self._finish_listen(cancelled=False)
            return True
        if event.type == pygame.MOUSEBUTTONDOWN:
            captured = f"Mouse Button {event.button}"
            if self.check_for_bind_conflict(captured):
                if self._on_warning:
                    self._on_warning('Key already in use!')
            else:
                bind_key = f"Bind_{self._pending_action}"
                self.current_config.apply_setting(bind_key, captured)
                self._finish_listen(cancelled=False)
            return True
        return False

    def _finish_listen(self, cancelled: bool) -> None:
        self.is_listening_for_input = False
        self._pending_action = None
        if self._on_close_overlay:
            self._on_close_overlay()
        if not cancelled and self._on_refresh_panel:
            self._on_refresh_panel()

    def check_for_bind_conflict(self, captured_input: str) -> bool:
        binds = {
            self.current_config.bind_attack,
            self.current_config.bind_block,
            self.current_config.bind_interact,
            *self.current_config.extra_binds.values(),
        }
        return captured_input in binds

    def run_listen_loop_blocking(self) -> None:
        """Optional loop when ``get_next_input`` is provided (non-pygame tests)."""
        if not self._get_next_input or not self._pending_action:
            return
        while self.is_listening_for_input:
            captured = self._get_next_input()
            if captured == 'ESC':
                self._finish_listen(cancelled=True)
            elif captured:
                if self.check_for_bind_conflict(captured):
                    if self._on_warning:
                        self._on_warning('Key already in use!')
                else:
                    self.current_config.apply_setting(
                        f"Bind_{self._pending_action}",
                        captured,
                    )
                    self._finish_listen(cancelled=False)
