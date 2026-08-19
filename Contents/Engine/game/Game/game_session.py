"""Wires menu, save, inventory, equipment, and UI systems for the running game."""

 # Assemble player, inventory, equipment, and quest state for a game run.
from __future__ import annotations

from typing import Any, Dict, Optional

from .character_preview import CharacterPreview
from .equipment_manager import EquipmentManager
from .inventory_hotbar import InventoryHotbar
from .inventory_manager import InventoryManager
from ..main.Title import Application, GameEngine, MainMenuManager
from .movement_controller import PlayerController
from .pause_menu_manager import PauseMenuManager
from .player_skills import PlayerSkills
from .player_status import PlayerStatus
from .save_manager import SaveManager
from .settings_modifier import SettingsModifier
from .settings_ui_manager import SettingsUIManager
from .ui_hotbar_integration import UIHotbarIntegration
from .ui_manager import UIManager


class GameSession:
    """
    Central holder for pseudocode managers. Pass an ``agaf.Player`` (or None for menus only).
    """

    def __init__(self, player: Optional[Any] = None):
        self.player = player
        self.save_manager = SaveManager()
        self.player_status = PlayerStatus()
        if player is not None:
            self.player_status.sync_from_player(player)

        self.inventory_manager = InventoryManager(
            on_pause=lambda paused: self._set_paused(paused),
        )
        self.inventory_hotbar = InventoryHotbar()
        self.ui_hotbar = UIHotbarIntegration(
            hotbar=self.inventory_hotbar,
            inventory_manager=self.inventory_manager,
        )
        self.character_preview = CharacterPreview()
        self.equipment_manager = EquipmentManager(
            inventory_manager=self.inventory_manager,
            player_status=self.player_status,
            character_preview=self.character_preview,
        )
        self.character_preview.equipment_manager = self.equipment_manager

        self.ui_manager = UIManager(on_pause=lambda p: self._set_paused(p))
        self.settings_ui = SettingsUIManager()
        self.settings_modifier = SettingsModifier(
            current_config=self.settings_ui.current_config,
        )
        self.main_menu = MainMenuManager(
            save_manager=self.save_manager,
            ui_manager=self.ui_manager,
            game_engine=GameEngine(
                on_apply_save_data=self.apply_save_data,
            ),
        )
        self.pause_menu = PauseMenuManager(
            save_manager=self.save_manager,
            on_capture_state=self.capture_current_state,
            on_open_settings=lambda: self.ui_manager.toggle_settings_menu(True),
        )
        self.movement_controller = PlayerController(
            player=player,
            player_status=self.player_status,
        ) if player else None
        self.player_skills = PlayerSkills(self.player_status)
        self._paused = False

    def _set_paused(self, paused: bool) -> None:
        self._paused = paused
        self.pause_menu.is_paused = paused

    def capture_current_state(self) -> Dict[str, Any]:
        state = SaveManager.generate_default_starting_stats()
        if self.player:
            self.player_status.sync_from_player(self.player)
        state.update({
            'health': int(self.player_status.current_health),
            'max_health': int(self.player_status.max_health),
            'mana': int(self.player_status.current_mana),
            'max_mana': int(self.player_status.max_mana),
            'stamina': int(self.player_status.current_stamina),
            'level': self.player_status.player_level,
            'gold': self.player_status.gold,
        })
        return state

    def apply_save_data(self, save_data: Dict[str, Any]) -> None:
        self.player_status.current_health = save_data.get('health', self.player_status.current_health)
        self.player_status.max_health = save_data.get('max_health', self.player_status.max_health)
        self.player_status.current_mana = save_data.get('mana', self.player_status.current_mana)
        self.player_status.max_mana = save_data.get('max_mana', self.player_status.max_mana)
        self.player_status.player_level = save_data.get('level', self.player_status.player_level)
        self.player_status.gold = save_data.get('gold', self.player_status.gold)
        if 'save_id' in save_data:
            self.pause_menu.set_active_save_id(save_data['save_id'])
        if self.player:
            self.player_status.sync_to_player(self.player)

    def tick_idle_regen(self, is_idle: bool) -> None:
        self.player_status.update_status(is_idle)
        if self.player:
            self.player_status.sync_to_player(self.player)

    def handle_in_game_input(self, keys_pressed, mouse_buttons=None) -> None:
        if self._paused:
            return
        if self.movement_controller:
            self.movement_controller.handle_input(keys_pressed, mouse_buttons)
        self.player_skills.handle_skill_input(keys_pressed)
        self.inventory_hotbar.handle_hotbar_input(keys_pressed)
        self.ui_manager.handle_ui_input(keys_pressed)
