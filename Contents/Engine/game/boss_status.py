"""Boss health bar state (bossstat.txt)."""

 # Track boss health, defeat state, and callbacks used by combat UI.
from __future__ import annotations

from typing import Callable, Optional


class BossStatus:
    def __init__(
        self,
        boss_name: str = 'Boss Name',
        max_boss_health: float = 100.0,
        on_ui_update: Optional[Callable[[float, str], None]] = None,
    ):
        self.boss_name = boss_name
        self.max_boss_health = max_boss_health
        self.current_health = max_boss_health
        self._on_ui_update = on_ui_update

    def take_damage(self, damage_amount: float) -> None:
        self.current_health = max(0.0, self.current_health - damage_amount)
        self.update_boss_ui()

    def update_boss_ui(self) -> None:
        if self._on_ui_update:
            ratio = self.current_health / self.max_boss_health if self.max_boss_health else 0.0
            self._on_ui_update(ratio, self.boss_name)

    def display_bar(self, health_ratio: float) -> float:
        """Return clamped ratio for UI bar rendering."""
        return max(0.0, min(1.0, health_ratio))

    def display_name(self, name: Optional[str] = None) -> str:
        return name or self.boss_name

    @property
    def health_ratio(self) -> float:
        if self.max_boss_health <= 0:
            return 0.0
        return self.current_health / self.max_boss_health
