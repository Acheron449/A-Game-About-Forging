"""Equipment slots and equip/unequip flow (equipmentmanager.txt)."""

 # Track equipped item slots and synchronize equipment changes.
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .character_preview import CharacterPreview
    from ..Inventory.inventory_manager import InventoryManager
    from .player_status import PlayerStatus


class EquipmentSlot:
    def __init__(self, name: str, allowed_types: List[str]):
        self.name = name
        self.allowed_types = allowed_types
        self.current_item: Optional[Any] = None

    def has_item(self) -> bool:
        return self.current_item is not None

    def set_item(self, item: Any) -> None:
        self.current_item = item

    def clear(self) -> None:
        self.current_item = None

    def get_item(self) -> Optional[Any]:
        return self.current_item

    def accepts(self, item: Any) -> bool:
        item_type = getattr(item, 'type', None) or getattr(item, 'slot_type', None)
        if item_type is None:
            return False
        return str(item_type).lower() in {t.lower() for t in self.allowed_types}


class EquipmentManager:
    """Armor (left) and weapon/tool (right) slots from pseudocode."""

    def __init__(
        self,
        inventory_manager: Optional['InventoryManager'] = None,
        player_status: Optional['PlayerStatus'] = None,
        character_preview: Optional['CharacterPreview'] = None,
        on_stats_apply: Optional[Callable[[Dict[str, int]], None]] = None,
        on_stats_remove: Optional[Callable[[Dict[str, int]], None]] = None,
    ):
        self.inventory_manager = inventory_manager
        self.player_status = player_status
        self.character_preview = character_preview
        self._on_stats_apply = on_stats_apply
        self._on_stats_remove = on_stats_remove

        self.head_slot = EquipmentSlot('head', ['head', 'helmet'])
        self.chest_slot = EquipmentSlot('chest', ['chest', 'armor'])
        self.leg_slot = EquipmentSlot('leg', ['leg', 'legs'])
        self.boot_slot = EquipmentSlot('boot', ['boot', 'boots'])
        self.accessory_slot = EquipmentSlot('accessory', ['accessory', 'backpack'])
        self.tool_slot = EquipmentSlot('tool', ['tool', 'weapon'])
        self.primary_weapon_slot = EquipmentSlot('primary_weapon', ['weapon', 'primary_weapon'])
        self.offhand_slot = EquipmentSlot('offhand', ['offhand', 'shield'])
        self.ranged_weapon_slot = EquipmentSlot('ranged_weapon', ['ranged', 'bow'])

    def get_all_slots(self) -> List[EquipmentSlot]:
        return [
            self.head_slot,
            self.chest_slot,
            self.leg_slot,
            self.boot_slot,
            self.accessory_slot,
            self.tool_slot,
            self.primary_weapon_slot,
            self.offhand_slot,
            self.ranged_weapon_slot,
        ]



    def slot_by_name(self, name: str) -> Optional[EquipmentSlot]:
        for slot in self.get_all_slots():
            if slot.name == name:
                return slot
        return None

    def _item_stats(self, item: Any) -> Dict[str, int]:
        return getattr(item, 'stats_bonus', None) or getattr(item, 'stats', {}) or {}

    def _apply_bonuses(self, item: Any) -> None:
        stats = self._item_stats(item)
        if self.player_status:
            self.player_status.apply_item_stats(stats)
        if self._on_stats_apply:
            self._on_stats_apply(stats)

    def _remove_bonuses(self, item: Any) -> None:
        stats = self._item_stats(item)
        if self.player_status:
            self.player_status.remove_item_stats(stats)
        if self._on_stats_remove:
            self._on_stats_remove(stats)

    def equip_item(self, item_to_equip: Any, target_slot: EquipmentSlot) -> bool:
        if not target_slot.accepts(item_to_equip):
            return False
        if target_slot.has_item():
            old = target_slot.get_item()
            if self.inventory_manager:
                self.inventory_manager.move_to_bag(old)
            else:
                self._remove_bonuses(old)
        target_slot.set_item(item_to_equip)
        self._apply_bonuses(item_to_equip)
        if self.character_preview:
            self.character_preview.update_image()
        return True

    def unequip_item(self, target_slot: EquipmentSlot) -> bool:
        if not target_slot.has_item():
            return False
        item = target_slot.get_item()
        if self.inventory_manager and not self.inventory_manager.has_empty_slot():
            return False
        if self.inventory_manager:
            self.inventory_manager.move_to_bag(item)
        self._remove_bonuses(item)
        target_slot.clear()
        if self.character_preview:
            self.character_preview.update_image()
        return True

    def get_equipped_item(self) -> Optional[Any]:
        """Return the item currently equipped for attacking."""

        # Primary weapon takes priority
        if self.primary_weapon_slot.has_item():
            return self.primary_weapon_slot.get_item()

        # Otherwise use the tool slot
        if self.tool_slot.has_item():
            return self.tool_slot.get_item()

        # Nothing usable is equipped
        return None

    def get_equipped_attack_type(self) -> Optional[str]:
        """Return the attack type of the currently equipped item."""

        item = self.get_equipped_item()

        if item is None:
            return None

        return getattr(item, "attack_type", None)

    def has_tool(self, tool_type: str) -> bool:
        for slot in self.get_all_slots():
            if not slot.has_item():
                continue

            item = slot.get_item()

            if getattr(item, "attack_type", None) == tool_type:
                return True

        return False

    def get_equipped_weapon(self):
        """Return the currently equipped primary weapon."""

        if self.primary_weapon_slot.has_item():
            return self.primary_weapon_slot.get_item()

        return None


    def get_tool(self, tool_type):
        """Return the required tool if it is equipped."""

        if not self.tool_slot.has_item():
            return None

        item = self.tool_slot.get_item()

        if getattr(item, "item_type", None) == tool_type:
            return item

        return None


