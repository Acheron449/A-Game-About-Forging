"""Mutable game settings struct (config.txt pseudocode)."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from ..config.config import (
    BIND_ATTACK_LABEL,
    BIND_BLOCK_LABEL,
    BIND_INTERACT_LABEL,
    DEFAULT_DIFFICULTY,
    DEFAULT_MASTER_VOLUME,
    DEFAULT_MOUSE_SENSITIVITY,
    DEFAULT_MUSIC_VOLUME,
    DEFAULT_RESOLUTION_LABEL,
    DEFAULT_SETTINGS_FPS_LIMIT,
    DEFAULT_SFX_VOLUME,
    GAME_SETTINGS_FILENAME,
    PROJECT_ROOT,
    SAVE_DIRECTORY,
    SETTINGS_CATEGORIES,
)


@dataclass
class GameConfiguration:
    """General, video, audio, directory, and keybind settings."""

    difficulty: str = DEFAULT_DIFFICULTY
    mouse_sensitivity: float = DEFAULT_MOUSE_SENSITIVITY
    fps_limit: int = DEFAULT_SETTINGS_FPS_LIMIT
    resolution: str = DEFAULT_RESOLUTION_LABEL
    master_volume: float = DEFAULT_MASTER_VOLUME
    music_volume: float = DEFAULT_MUSIC_VOLUME
    sfx_volume: float = DEFAULT_SFX_VOLUME
    save_file_location: str = field(default_factory=lambda: SAVE_DIRECTORY)
    game_directory: str = field(default_factory=lambda: PROJECT_ROOT)
    bind_attack: str = BIND_ATTACK_LABEL
    bind_block: str = BIND_BLOCK_LABEL
    bind_interact: str = BIND_INTERACT_LABEL
    extra_binds: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def load_from_file(cls, path: Optional[str] = None) -> 'GameConfiguration':
        path = path or os.path.join(PROJECT_ROOT, GAME_SETTINGS_FILENAME)
        if not os.path.isfile(path):
            return cls()
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)

    def save_to_file(self, path: Optional[str] = None) -> None:
        path = path or os.path.join(PROJECT_ROOT, GAME_SETTINGS_FILENAME)
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def apply_setting(self, setting_name: str, new_value: Any) -> None:
        key = setting_name.replace('Bind_', 'bind_').lower()
        if hasattr(self, key):
            setattr(self, key, new_value)
        elif setting_name.startswith('Bind_'):
            self.extra_binds[setting_name] = str(new_value)
        else:
            setattr(self, key, new_value)

    @staticmethod
    def setting_category(setting_name: str) -> str:
        lower = setting_name.lower()
        if 'volume' in lower or lower.startswith('bind_') or lower.startswith('bind '):
            if lower.startswith('bind'):
                return 'Keybinds'
            return 'Audio'
        if 'fps' in lower or 'resolution' in lower:
            return 'Video'
        if 'directory' in lower or 'location' in lower:
            return 'Directories'
        if 'difficulty' in lower or 'mouse' in lower or 'sensitivity' in lower:
            return 'General'
        return 'General'

    @staticmethod
    def categories() -> List[str]:
        return list(SETTINGS_CATEGORIES)
