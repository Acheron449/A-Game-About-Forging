"""Player health, mana, stamina, and regen (Playerstatus.txt)."""

from __future__ import annotations

from typing import Callable, Dict, Optional

from Contents.configuration.constants import config


class PlayerStatus:
    def __init__(
        self,
        *,
        max_health: int = config.PLAYER_START_MAX_HEALTH,
        max_mana: int = config.PLAYER_START_MAX_MANA,
        max_stamina: int = config.PLAYER_START_MAX_STAMINA,
        level: int = config.PLAYER_STATUS_DEFAULT_LEVEL,
        gold: int = config.PLAYER_STATUS_DEFAULT_GOLD,
        item_stats: Optional[Dict[str, int]] = None,
        on_health_ui_update: Optional[Callable[[], None]] = None,
        on_stamina_ui_update: Optional[Callable[[], None]] = None,
        on_mana_ui_update: Optional[Callable[[], None]] = None,
    ):
        self.max_health = max_health
        self.max_mana = max_mana
        self.max_stamina = max_stamina
        self.current_health = config.PLAYER_START_HEALTH if max_health == config.PLAYER_START_MAX_HEALTH else max_health
        self.current_mana = config.PLAYER_START_MANA if max_mana == config.PLAYER_START_MAX_MANA else max_mana
        self.current_stamina = config.PLAYER_START_STAMINA if max_stamina == config.PLAYER_START_MAX_STAMINA else max_stamina
        self.player_level = level
        self.gold = gold
        self.item_stats = item_stats or {}
        self._on_health_ui = on_health_ui_update
        self._on_stamina_ui = on_stamina_ui_update
        self._on_mana_ui = on_mana_ui_update
        self.refresh_regen_rates()

    def refresh_regen_rates(self) -> None:
        self.stamina_regen_rate = self.calculate_stamina_regen(self.player_level, self.item_stats)
        self.health_regen_rate = self.calculate_health_regen(self.item_stats)
        self.mana_regen_rate = self.calculate_mana_regen(self.item_stats)

    @staticmethod
    def calculate_stamina_regen(player_level: int, item_stats: Dict[str, int]) -> float:
        bonus = item_stats.get('stamina_regen', 0)
        return config.STAMINA_REGEN_BASE + player_level * 0.1 + bonus

    @staticmethod
    def calculate_health_regen(item_stats: Dict[str, int]) -> float:
        return config.HEALTH_REGEN_IDLE_BASE + item_stats.get('health_regen', 0)

    @staticmethod
    def calculate_mana_regen(item_stats: Dict[str, int]) -> float:
        return config.MANA_REGEN_IDLE_BASE + item_stats.get('mana_regen', 0)

    def apply_item_stats(self, item_stats: Dict[str, int]) -> None:
        for key, value in item_stats.items():
            self.item_stats[key] = self.item_stats.get(key, 0) + value
        self.refresh_regen_rates()

    def remove_item_stats(self, item_stats: Dict[str, int]) -> None:
        for key, value in item_stats.items():
            if key in self.item_stats:
                self.item_stats[key] = max(0, self.item_stats[key] - value)
        self.refresh_regen_rates()

    def update_status(self, is_idle: bool) -> None:
        if is_idle:
            self.current_health = min(
                self.current_health + self.health_regen_rate,
                self.max_health,
            )
            self.current_mana = min(
                self.current_mana + self.mana_regen_rate,
                self.max_mana,
            )
        self.current_stamina = min(
            self.current_stamina + self.stamina_regen_rate,
            self.max_stamina,
        )

    def take_damage(self, damage_amount: float) -> None:
        self.current_health = max(0, self.current_health - damage_amount)
        self.update_ui_health_bar()

    def use_stamina(self, amount: float) -> bool:
        if self.current_stamina < amount:
            return False
        self.current_stamina -= amount
        self.update_ui_stamina_bar()
        return True

    def use_mana(self, amount: float) -> bool:
        if self.current_mana < amount:
            return False
        self.current_mana -= amount
        if self._on_mana_ui:
            self._on_mana_ui()
        return True

    def update_ui_health_bar(self) -> None:
        if self._on_health_ui:
            self._on_health_ui()

    def update_ui_stamina_bar(self) -> None:
        if self._on_stamina_ui:
            self._on_stamina_ui()

    def sync_from_player(self, player) -> None:
        """Mirror fields from ``bridger.Player`` when both are used."""
        self.current_health = player.health
        self.max_health = player.max_health
        self.current_mana = player.mana
        self.max_mana = player.max_mana
        self.player_level = player.level
        self.gold = player.gold

    def sync_to_player(self, player) -> None:
        player.health = int(self.current_health)
        player.max_health = int(self.max_health)
        player.mana = int(self.current_mana)
        player.max_mana = int(self.max_mana)
        player.level = self.player_level
        player.gold = self.gold
