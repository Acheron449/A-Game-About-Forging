"""Inventory-backed forging with mixed-ore rarity bonuses."""

 # Model ore drops, forging recipes, and the forge interaction workflow.
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Sequence

from ..configuration.constants import (
    GEAR_SPAWN_CHANCE_BY_RARITY,
    ORE_RARITY_BY_PERCENT_RANGE,
)
from .Inventory.inventory import InventoryItem, InventorySlot


@dataclass(frozen=True)
class OreDrop:
    ore_type: str
    weight: float


@dataclass
class ForgeResult:
    success: bool
    message: str
    weapon: Optional[InventoryItem] = None
    rarity: Optional[str] = None


class ForgeSystem:
    """Detect ore in inventory, consume a selected mix, and create a weapon."""

    RARITY_VALUE = {
        "common": 0,
        "uncommon": 1,
        "rare": 2,
        "legendary": 3,
        "mythical": 4,
    }

    def __init__(
        self,
        ore_drops: Optional[Sequence[OreDrop]] = None,
        *,
        rng: Optional[random.Random] = None,
    ) -> None:
        self.ore_drops = list(ore_drops or [])
        self.rng = rng or random.Random()

    @staticmethod
    def _normalise_ore_name(value: object) -> str:
        """Convert item IDs/names such as ``stone_ore`` to ``stone``."""
        name = str(value or "").lower().replace("_", " ").replace("-", " ")
        name = " ".join(name.split())
        if name.endswith(" ore"):
            name = name[:-4]
        return name

    def _ore_key(self, item: Any) -> Optional[str]:
        known_ores = {
            self._normalise_ore_name(name): name
            for name in ORE_RARITY_BY_PERCENT_RANGE
        }

        for value in (
            getattr(item, "item_id", None),
            getattr(item, "name", None),
        ):
            key = self._normalise_ore_name(value)
            if key in known_ores:
                return known_ores[key]

        return None

    @staticmethod
    def _quantity(item: Any) -> int:
        return max(1, int(getattr(item, "quantity", 1) or 1))

    def ore_storage(self, inventory_manager: Any) -> Dict[str, int]:
        """Return every recognised ore currently held in bag slots."""
        ores: Dict[str, int] = {}

        for slot in getattr(inventory_manager, "bag_slots", []):
            if slot.is_empty():
                continue

            item = slot.get_item()
            ore_name = self._ore_key(item)
            if ore_name is not None:
                ores[ore_name] = ores.get(ore_name, 0) + self._quantity(item)

        return ores

    def select_ore(self) -> Optional[OreDrop]:
        """Randomly select an ore drop by its configured weight."""
        total_weight = sum(max(0, ore.weight) for ore in self.ore_drops)
        if total_weight <= 0:
            return None

        roll = self.rng.uniform(0, total_weight)
        cursor = 0.0
        for ore in self.ore_drops:
            cursor += max(0, ore.weight)
            if roll < cursor:
                return ore
        return self.ore_drops[-1]

    def rarity_boost(self, ore_mix: Mapping[str, int]) -> float:
        """Higher-quality and more varied ore mixes shift the rarity roll up."""
        total = sum(max(0, amount) for amount in ore_mix.values())
        if total <= 0:
            return 0.0

        weighted_quality = 0.0
        unique_ores = 0
        for ore_name, amount in ore_mix.items():
            amount = max(0, amount)
            if amount == 0:
                continue

            data = ORE_RARITY_BY_PERCENT_RANGE.get(ore_name)
            if data is None:
                continue

            unique_ores += 1
            weighted_quality += self.RARITY_VALUE[data["rarity"]] * amount

        # Each quality tier adds 5 percentage points; each extra ore variety
        # adds 3, capped at +30. A single low-tier ore therefore has no bonus.
        return min(30.0, (weighted_quality / total) * 5 + max(0, unique_ores - 1) * 3)

    def roll_weapon_rarity(self, ore_mix: Mapping[str, int]) -> str:
        roll = min(99.999, self.rng.uniform(0, 100) + self.rarity_boost(ore_mix))
        for rarity, (low, high) in GEAR_SPAWN_CHANCE_BY_RARITY["weapon"].items():
            if low <= roll < high:
                return rarity
        return "legendary"

    def _consume_ores(
        self,
        inventory_manager: Any,
        ore_mix: Mapping[str, int],
    ) -> bool:
        requested = {
            name: int(amount)
            for name, amount in ore_mix.items()
            if int(amount) > 0
        }

        available = self.ore_storage(inventory_manager)
        if not requested or any(available.get(name, 0) < amount for name, amount in requested.items()):
            return False

        remaining = requested.copy()
        for slot in inventory_manager.bag_slots:
            if slot.is_empty():
                continue

            item = slot.get_item()
            ore_name = self._ore_key(item)
            needed = remaining.get(ore_name, 0)
            if not needed:
                continue

            used = min(needed, self._quantity(item))
            remaining[ore_name] -= used
            item.quantity = self._quantity(item) - used
            if item.quantity <= 0:
                slot.clear()

        return not any(remaining.values())

    def forge_weapon(
        self,
        inventory_manager: Any,
        ore_mix: Mapping[str, int],
        *,
        weapon_name: str = "Forged Weapon",
    ) -> ForgeResult:
        """Forge a weapon from the requested inventory ore mix."""
        if not self._consume_ores(inventory_manager, ore_mix):
            return ForgeResult(False, "The selected ore mix is not available.")

        rarity = self.roll_weapon_rarity(ore_mix)
        weapon = InventoryItem(
            item_id=f"forged_{rarity}_weapon",
            name=f"{rarity.title()} {weapon_name}",
            type="weapon",
        )
        weapon.rarity = rarity
        weapon.ore_mix = dict(ore_mix)

        destination: Optional[InventorySlot] = inventory_manager.first_empty_slot()
        if destination is None:
            return ForgeResult(False, "Weapon forged, but there is no empty inventory slot.")

        destination.set_item(weapon)
        return ForgeResult(True, f"Forged a {weapon.name}.", weapon, rarity)


class ForgeInterface:
    """Small UI-facing model for selecting a mixture before calling ``forge``."""

    def __init__(self, forge_system: ForgeSystem, inventory_manager: Any) -> None:
        self.forge_system = forge_system
        self.inventory_manager = inventory_manager
        self.ore_mix: Dict[str, int] = {}

    def available_ores(self) -> Dict[str, int]:
        return self.forge_system.ore_storage(self.inventory_manager)

    def set_ore_amount(self, ore_name: str, amount: int) -> None:
        available = self.available_ores().get(ore_name, 0)
        amount = max(0, min(int(amount), available))
        if amount:
            self.ore_mix[ore_name] = amount
        else:
            self.ore_mix.pop(ore_name, None)

    def rarity_preview_bonus(self) -> float:
        return self.forge_system.rarity_boost(self.ore_mix)

    def forge(self, weapon_name: str = "Forged Weapon") -> ForgeResult:
        result = self.forge_system.forge_weapon(
            self.inventory_manager,
            self.ore_mix,
            weapon_name=weapon_name,
        )
        if result.success:
            self.ore_mix.clear()
        return result
