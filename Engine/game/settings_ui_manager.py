"""Settings menu layout and apply (uimanagersettings.txt)."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from ..config.config import SETTINGS_CATEGORIES
from .game_configuration import GameConfiguration


class SettingsUIManager:
    def __init__(
        self,
        config: Optional[GameConfiguration] = None,
        on_draw_category: Optional[Callable[[str], None]] = None,
        on_draw_panel: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        on_apply_engine: Optional[Callable[[GameConfiguration], None]] = None,
    ):
        self.current_config = config or GameConfiguration.load_from_file()
        self.active_category = 'General'
        self.categories: List[str] = list(SETTINGS_CATEGORIES)
        self._on_draw_category = on_draw_category
        self._on_draw_panel = on_draw_panel
        self._on_apply_engine = on_apply_engine

    def render_menu(self) -> None:
        for category in self.categories:
            if self._on_draw_category:
                self._on_draw_category(category)
        self.draw_settings_panel(self.active_category, self.current_config.to_dict())

    def draw_settings_panel(self, category: str, config_data: Dict[str, Any]) -> None:
        if self._on_draw_panel:
            self._on_draw_panel(category, config_data)

    def on_category_button_clicked(self, clicked_category: str) -> None:
        self.active_category = clicked_category
        self.refresh_settings_panel()

    def refresh_settings_panel(self) -> None:
        self.draw_settings_panel(self.active_category, self.current_config.to_dict())

    def on_apply_changes(self) -> None:
        self.current_config.save_to_file()
        if self._on_apply_engine:
            self._on_apply_engine(self.current_config)

    def load_configuration_from_file(self) -> GameConfiguration:
        self.current_config = GameConfiguration.load_from_file()
        return self.current_config
