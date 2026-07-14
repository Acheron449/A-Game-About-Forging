"""Equipped gear overlay preview (charpreview.txt)."""

from __future__ import annotations

from typing import Any, Callable, List, Optional, TYPE_CHECKING

from ..config.config import config

if TYPE_CHECKING:
    from .equipment_manager import EquipmentManager


class CharacterPreview:
    def __init__(
        self,
        equipment_manager: Optional['EquipmentManager'] = None,
        static_player_image: str = config.CHARACTER_PREVIEW_BASE_IMAGE,
        on_display: Optional[Callable[[str, List[str]], None]] = None,
    ):
        self.equipment_manager = equipment_manager
        self.static_player_image = static_player_image
        self.current_render = static_player_image
        self._overlay_assets: List[str] = []
        self._on_display = on_display

    def update_image(self) -> str:
        self.current_render = self.static_player_image
        self._overlay_assets = []
        if not self.equipment_manager:
            self.display()
            return self.current_render
        for slot in self.equipment_manager.get_all_slots():
            if slot.has_item():
                item = slot.get_item()
                asset = getattr(item, 'visual_asset', None) or getattr(item, 'sprite', None)
                if asset:
                    self._overlay_assets.append(str(asset))
        self.display()
        return self.current_render

    def display(self) -> None:
        if self._on_display:
            self._on_display(self.current_render, list(self._overlay_assets))

    @property
    def overlay_assets(self) -> List[str]:
        return list(self._overlay_assets)
