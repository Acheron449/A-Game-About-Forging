from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Protocol, Sequence

from ..config.config import ( # Import the config
    EFFECT_SPARKLES_IMPACT,
    SOUND_CLINK_METAL_ON_STONE,
)


class SupportsMine(Protocol):
    def mine(self, world, mouse_buttons) -> object: ... # Mine a nearby mining spot when left mouse is pressed


@dataclass
class PickaxeController:
    """
    Minimal controller that turns the pickaxe pseudocode into usable Python.

    It’s intentionally engine-agnostic:
    - `get_target()` can be any function that returns the thing you're mining
      (e.g. a raycast hit, nearby entity, collision target, etc.)
    - `mine_action()` can award drops / call `provide_random_ore` / etc.
    """

    is_mining: bool = False # Set the is mining to the is mining
    get_target: Optional[Callable[[], object]] = None # Set the get target to the get target
    mine_action: Optional[Callable[[object], None]] = None # Set the mine action to the mine action
    on_stop_effects: Optional[Callable[[], None]] = None # Set the on stop effects to the on stop effects
    on_effect: Optional[Callable[[str], None]] = None # Set the on effect to the on effect
    on_sound: Optional[Callable[[str], None]] = None # Set the on sound to the on sound

    def update(self, *, mouse_buttons: Sequence[bool] | None) -> None:
        left_down = bool(mouse_buttons and len(mouse_buttons) > 0 and mouse_buttons[0]) # Check if the left mouse button is pressed and the mouse buttons are not None and the mouse buttons are not empty and the first mouse button is pressed    

        if not left_down:
            self.is_mining = False # Set the is mining to the is mining
            if self.on_stop_effects is not None: # Check if the on stop effects is not None
                self.on_stop_effects() # Call the on stop effects
            return

        target = self.get_target() if self.get_target is not None else None # Get the target from the get target
        if target is None: # Check if the target is None
            self.is_mining = False # Set the is mining to the is mining
            return

        # Loosely mirror the pseudocode: only mine "ore-like" targets if possible.
        target_type = getattr(target, "type", None) or getattr(target, "Type", None) # Get the target type from the target
        if isinstance(target_type, str) and target_type.lower() not in {"ore", "miningspot"}:
            self.is_mining = False # Set the is mining to the is mining
            return

        self.start_mining(target) # Start mining the target

    def start_mining(self, target: object) -> None:
        self.is_mining = True # Set the is mining to the is mining
        if self.on_effect is not None: # Check if the on effect is not None
            self.on_effect(EFFECT_SPARKLES_IMPACT) # Call the on effect
        if self.on_sound is not None: # Check if the on sound is not None
            self.on_sound(SOUND_CLINK_METAL_ON_STONE) # Call the on sound
        if self.mine_action is not None: # Check if the mine action is not None
            self.mine_action(target) # Call the mine action


def mine_with_equipped_pickaxe(player: SupportsMine, world, mouse_buttons) -> object: # Mine with the equipped pickaxe
    """
    Convenience wrapper that matches your current engine design in `agaf.py`:
    if the player has a `mine()` method, delegate to it.
    """
    return player.mine(world, mouse_buttons) # Return the mined item