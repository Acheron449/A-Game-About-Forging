
"""Define stable item identifiers and metadata used by inventory systems."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


from ...configuration.constants import (
    ITEM_STONE,
    ITEM_COAL,
    ITEM_IRON,
    ITEM_SILVER,
    ITEM_GOLD,
    ITEM_PLATINUM,
    ITEM_DIAMOND,
    ITEM_MITHRIL,
    ITEM_KYBER,
    ITEM_METEORITE_FRAGMENT,
    ITEM_GOLD_COIN,
    ITEM_HEALTH_POTION,
    ITEM_ALTAR_KEY,

    WEAPON_OLD_SWORD,
    WEAPON_IRON_SWORD,
    WEAPON_GREAT_SWORD,

    PICKAXE_WOODEN,
    PICKAXE_STONE,
    PICKAXE_IRON,
    PICKAXE_GOLD,
    PICKAXE_DIAMOND,
    PICKAXE_MITHRIL,

    PLAYER_RESOURCES_DIR,
)


@dataclass
class Item:
    item_id: str
    name: str
    type: str
    quantity: int = 1
    sprite: Optional[str] = None
    stats_bonus: Optional[dict] = None
    animation_type: Optional[str] = None


ITEM_DEFINITIONS = {
    ITEM_STONE: {
        "name": "Stone",
        "type": "material",
    },

    ITEM_COAL: {
        "name": "Coal",
        "type": "material",
    },

    ITEM_IRON: {
        "name": "Iron",
        "type": "material",
    },

    ITEM_SILVER: {
        "name": "Silver",
        "type": "material",
    },

    ITEM_GOLD: {
        "name": "Gold",
        "type": "material",
    },

    ITEM_DIAMOND: {
        "name": "Diamond",
        "type": "material",
    },

    ITEM_GOLD_COIN: {
        "name": "Gold Coin",
        "type": "currency",
    },

    ITEM_HEALTH_POTION: {
        "name": "Health Potion",
        "type": "consumable",
    },

    ITEM_ALTAR_KEY: {
        "name": "Altar Key",
        "type": "quest",
    },

    WEAPON_OLD_SWORD: {
        "name": "Old Sword",
        "type": "weapon",
        "animation_type": "sword",
    },

    WEAPON_IRON_SWORD: {
        "name": "Iron Sword",
        "type": "weapon",
        "animation_type": "sword",
    },

    WEAPON_GREAT_SWORD: {
        "name": "Greatsword",
        "type": "weapon",
        "animation_type": "greatsword",
    },

    PICKAXE_WOODEN: {
        "name": "Wooden Pickaxe",
        "type": "pickaxe",
        "animation_type": "pickaxe",
    },

    PICKAXE_STONE: {
        "name": "Stone Pickaxe",
        "type": "pickaxe",
        "animation_type": "pickaxe",
    },

    PICKAXE_IRON: {
        "name": "Iron Pickaxe",
        "type": "pickaxe",
        "animation_type": "pickaxe",
    },

    PICKAXE_GOLD: {
        "name": "Gold Pickaxe",
        "type": "pickaxe",
        "animation_type": "pickaxe",
    },

    PICKAXE_DIAMOND: {
        "name": "Diamond Pickaxe",
        "type": "pickaxe",
        "animation_type": "pickaxe",
    },

    PICKAXE_MITHRIL: {
        "name": "Mithril Pickaxe",
        "type": "pickaxe",
        "animation_type": "pickaxe",
    },
}


def create_item(item_id: str, quantity: int = 1) -> Item | None:
    """Create a game item from its identifier."""

    definition = ITEM_DEFINITIONS.get(item_id)

    if definition is None:
        print(f"[ItemFactory] Unknown item ID: {item_id}")
        return None

    return Item(
        item_id=item_id,
        name=definition["name"],
        type=definition["type"],
        quantity=quantity,
        sprite=definition.get("sprite"),
        stats_bonus=definition.get("stats_bonus"),
        animation_type=definition.get("animation_type"),
    )