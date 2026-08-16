
from __future__ import annotations

import random

from ...configuration.constants import LOOT_POOLS

# RANDOM LOOT

def roll_loot(pool_id: str) -> str:

    pool = LOOT_POOLS.get(pool_id)

    if pool is None:
        raise KeyError(
            f"Unknown loot pool: '{pool_id}'"
        )

    total_weight = sum(
        drop.weight
        for drop in pool
    )

    roll = random.uniform(
        0,
        total_weight,
    )

    current_weight = 0

    for drop in pool:

        current_weight += drop.weight

        if roll < current_weight:
            return drop.item_id

    return pool[-1].item_id