"""Mutable game settings struct (config.txt pseudocode)."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from Contents.configuration.constants import config


@dataclass
class GameConfiguration:
    """General, video, audio, directory, and keybind settings."""

    difficulty: str = config.DEFAULT_DIFFICULTY
    mouse_sensitivity: float = config.DEFAULT_MOUSE_SENSITIVITY
    fps_limit: int = config.DEFAULT_SETTINGS_FPS_LIMIT
    resolution: str = config.DEFAULT_RESOLUTION_LABEL
    master_volume: float = config.DEFAULT_MASTER_VOLUME
    music_volume: float = config.DEFAULT_MUSIC_VOLUME
    sfx_volume: float = config.DEFAULT_SFX_VOLUME
    save_file_location: str = field(default_factory=lambda: config.SAVE_DIRECTORY)
    game_directory: str = field(default_factory=lambda: config.PROJECT_ROOT)
    bind_attack: str = config.BIND_ATTACK_LABEL
    bind_block: str = config.BIND_BLOCK_LABEL
    bind_interact: str = config.BIND_INTERACT_LABEL
    extra_binds: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def load_from_file(cls, path: Optional[str] = None) -> 'GameConfiguration':
        path = path or os.path.join(config.PROJECT_ROOT, config.GAME_SETTINGS_FILENAME)
        if not os.path.isfile(path):
            return cls()
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)

    def save_to_file(self, path: Optional[str] = None) -> None:
        path = path or os.path.join(config.PROJECT_ROOT, config.GAME_SETTINGS_FILENAME)
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
        return list(config.SETTINGS_CATEGORIES)
