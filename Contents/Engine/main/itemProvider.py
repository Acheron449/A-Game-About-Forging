"""Provide weighted random ore selections to the game-facing item API."""
from __future__ import annotations

import random
from typing import Callable, Optional, Protocol, Sequence

from ..configuration.imports import config, OreDrop


class SupportsAddItem(Protocol):
    def add_item(self, item) -> None: ...


def _choose_weighted(pool: Sequence[OreDrop], rng: random.Random) -> OreDrop:
    if not pool:
        raise ValueError("ORE_POOL must not be empty")

    total_weight = sum(max(0, ore.weight) for ore in pool)
    if total_weight <= 0:
        raise ValueError("ORE_POOL must contain at least one positive weight")

    # Inclusive 1..total_weight, matching the original pseudocode.
    roll = rng.randint(1, total_weight)
    cursor = 0
    for ore in pool:
        cursor += max(0, ore.weight)
        if roll <= cursor:
            return ore

    # Defensive fallback (should be unreachable)
    return pool[0]


def provide_random_ore(
    target_object,
    *,
    inventory: Optional[SupportsAddItem] = None,
    make_item: Optional[Callable[[str], object]] = None,
    rng: Optional[random.Random] = None,
    on_popup: Optional[Callable[[str], None]] = None,
    on_destroy: Optional[Callable[[object], None]] = None,
    on_sound: Optional[Callable[[str], None]] = None,
    damage: int = 1,
) -> str:
    """
    Choose a weighted random ore name and (optionally) award it to an inventory.

    This replaces the original pseudocode `ProvideRandomOres(targetObject)` while
    staying engine-agnostic: callers can plug in inventory/item creation, popup,
    destroy, and sound hooks.

    Returns the selected ore name.
    """
    rng = rng or random.Random()

    selected = _choose_weighted(config.ORE_POOL, rng).name

    if inventory is not None:
        if make_item is None:
            # If your game uses an Item class, pass `make_item` to construct it.
            inventory.add_item(selected)
        else:
            inventory.add_item(make_item(selected))

    if on_popup is not None:
        on_popup(f"+1 {selected}")

    # Optional: damage & destroy the target if it has a compatible attribute
    if target_object is not None and hasattr(target_object, "health"):
        try:
            target_object.health -= damage
        except Exception:
            pass

        try:
            if target_object.health <= 0:
                if on_destroy is not None:
                    on_destroy(target_object)
                if on_sound is not None:
                    on_sound(config.SOUND_ROCK_SHATTER)
        except Exception:
            pass

    return selected


# Backwards-compatible alias for older call sites (original pseudocode name).
ProvideRandomOres = provide_random_ore