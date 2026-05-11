from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Protocol, Sequence


class SupportsMine(Protocol):
    def mine(self, world, mouse_buttons) -> object: ...


@dataclass
class PickaxeController:
    """
    Minimal controller that turns the pickaxe pseudocode into usable Python.

    It’s intentionally engine-agnostic:
    - `get_target()` can be any function that returns the thing you're mining
      (e.g. a raycast hit, nearby entity, collision target, etc.)
    - `mine_action()` can award drops / call `provide_random_ore` / etc.
    """

    is_mining: bool = False
    get_target: Optional[Callable[[], object]] = None
    mine_action: Optional[Callable[[object], None]] = None
    on_stop_effects: Optional[Callable[[], None]] = None
    on_effect: Optional[Callable[[str], None]] = None
    on_sound: Optional[Callable[[str], None]] = None

    def update(self, *, mouse_buttons: Sequence[bool] | None) -> None:
        left_down = bool(mouse_buttons and len(mouse_buttons) > 0 and mouse_buttons[0])

        if not left_down:
            self.is_mining = False
            if self.on_stop_effects is not None:
                self.on_stop_effects()
            return

        target = self.get_target() if self.get_target is not None else None
        if target is None:
            self.is_mining = False
            return

        # Loosely mirror the pseudocode: only mine "ore-like" targets if possible.
        target_type = getattr(target, "type", None) or getattr(target, "Type", None)
        if isinstance(target_type, str) and target_type.lower() not in {"ore", "miningspot"}:
            self.is_mining = False
            return

        self.start_mining(target)

    def start_mining(self, target: object) -> None:
        self.is_mining = True
        if self.on_effect is not None:
            self.on_effect("Sparkles at impact point")
        if self.on_sound is not None:
            self.on_sound("Clink_Metal_On_Stone")
        if self.mine_action is not None:
            self.mine_action(target)


def mine_with_equipped_pickaxe(player: SupportsMine, world, mouse_buttons) -> object:
    """
    Convenience wrapper that matches your current engine design in `agaf.py`:
    if the player has a `mine()` method, delegate to it.
    """
    return player.mine(world, mouse_buttons)