from dataclasses import dataclass
from typing import Any

from ..config.config import config

@dataclass
class GreatswordController:
    player: Any

    def attack(self) -> bool:
        """Perform a greatsword attack action."""
        return True

    def block(self) -> bool:
        """Perform a greatsword block action."""
        return True

    def dash(self) -> bool:
        """Greatsword dash interaction; can be used for heavier forward movement."""
        return True

    def get_animation_type(self) -> str:
        return 'greatsword'


def get_greatsword_controller(player: Any) -> GreatswordController:
    return GreatswordController(player=player)
