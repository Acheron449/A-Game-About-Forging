"""Save/load backend (savemanagerbackend.txt + savemanageringamebackend.txt)."""

from __future__ import annotations

import json
import os
import time
import uuid
from typing import Any, Callable, Dict, List, Optional

from config.config import config


class SaveManager:
    def __init__(
        self,
        save_directory: str = None,
        serialize: Optional[Callable[[Dict[str, Any]], str]] = None,
        deserialize: Optional[Callable[[str], Dict[str, Any]]] = None,
    ):
        self.save_directory = save_directory or config.SAVE_DIRECTORY
        os.makedirs(self.save_directory, exist_ok=True)
        self._serialize = serialize or self._default_serialize
        self._deserialize = deserialize or self._default_deserialize
        self._id_to_filename: Dict[str, str] = {}

    @staticmethod
    def _default_serialize(data: Dict[str, Any]) -> str:
        return json.dumps(data, indent=2)

    @staticmethod
    def _default_deserialize(raw: str) -> Dict[str, Any]:
        return json.loads(raw)

    def check_for_existing_save(self) -> bool:
        return len(self._list_save_files()) > 0

    def _list_save_files(self) -> List[str]:
        if not os.path.isdir(self.save_directory):
            return []
        return [
            f for f in os.listdir(self.save_directory)
            if f.endswith(config.SAVE_FILE_EXTENSION)
        ]

    def _full_path(self, filename: str) -> str:
        return os.path.join(self.save_directory, filename)

    def retrieve_last_known_save(self) -> Dict[str, Any]:
        files = self._list_save_files()
        if not files:
            return self.generate_default_starting_stats()
        latest = max(
            files,
            key=lambda name: os.path.getmtime(self._full_path(name)),
        )
        return self.read_and_decode(self._full_path(latest))

    def read_and_decode(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, encoding='utf-8') as f:
            return self._deserialize(f.read())

    @staticmethod
    def generate_default_starting_stats() -> Dict[str, Any]:
        return {
            'health': config.PLAYER_START_HEALTH,
            'max_health': config.PLAYER_START_MAX_HEALTH,
            'mana': config.PLAYER_START_MANA,
            'max_mana': config.PLAYER_START_MAX_MANA,
            'level': config.PLAYER_START_LEVEL,
            'gold': config.PLAYER_START_GOLD,
            'scene': 'TutorialLevel',
        }

    def _generate_timestamp_filename(self) -> str:
        return f"{int(time.time())}_save{config.SAVE_FILE_EXTENSION}"

    def create_new_save_file(self) -> Dict[str, Any]:
        default_data = self.generate_default_starting_stats()
        new_file_name = self._generate_timestamp_filename()
        self._write_file(self._full_path(new_file_name), default_data)
        save_id = self.generate_id(new_file_name)
        self._id_to_filename[save_id] = new_file_name
        default_data['save_id'] = save_id
        default_data['filename'] = new_file_name
        return default_data

    def create_new_save(self, game_state_data: Dict[str, Any]) -> str:
        new_file_name = self._generate_timestamp_filename()
        file_path = self._full_path(new_file_name)
        self._write_file(file_path, game_state_data)
        save_id = self.generate_id(new_file_name)
        self._id_to_filename[save_id] = new_file_name
        return save_id

    def overwrite_save(self, file_id: str, game_state_data: Dict[str, Any]) -> None:
        file_name = self.get_file_name_by_id(file_id)
        file_path = self._full_path(file_name)
        self._write_file(file_path, game_state_data)

    def get_file_name_by_id(self, file_id: str) -> str:
        if file_id in self._id_to_filename:
            return self._id_to_filename[file_id]
        for name in self._list_save_files():
            if self.generate_id(name) == file_id:
                self._id_to_filename[file_id] = name
                return name
        raise FileNotFoundError(f"No save file for id {file_id!r}")

    @staticmethod
    def generate_id(file_name: str) -> str:
        return str(uuid.uuid5(uuid.NAMESPACE_URL, file_name))

    def _write_file(self, file_path: str, data: Dict[str, Any]) -> None:
        serialized = self._serialize(data)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(serialized)

    def is_recognized(self, save_data: Dict[str, Any]) -> bool:
        required = {'health', 'max_health', 'scene'}
        return required.issubset(save_data.keys())
