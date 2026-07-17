from dataclasses import dataclass
from typing import Any

from ..config.config import config

@dataclass
class SwordController:
    player: Any

    def attack(self) -> bool:
        """Perform a sword attack action."""
        return True

    def block(self) -> bool:
        """Perform a sword block action."""
        return True

    def parry(self) -> bool:
        """Perform a sword parry action if supported."""
        return True

    def get_animation_type(self) -> str:
        return 'sword'


def get_sword_controller(player: Any) -> SwordController:
    return SwordController(player=player)
