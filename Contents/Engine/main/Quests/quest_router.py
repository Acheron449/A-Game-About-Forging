"""Discover quests from folders and route them into the quest manager."""

 # Discover quest modules and route quest identifiers to implementations.
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import List, Optional

from ...game.quest_manager import QuestManager, QuestEntry


class QuestRouter:
    """Load quest modules from the quest folders and expose discoverable quest data."""

    def __init__(self, root_dir: Optional[Path] = None, quest_manager: Optional[QuestManager] = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parent)
        self.quest_manager = quest_manager or QuestManager()

    def discover_quests(self) -> List[QuestEntry]:
        quests: List[QuestEntry] = []
        if not self.root_dir.exists():
            return quests

        for folder in sorted(self.root_dir.iterdir()):
            if not folder.is_dir():
                continue
            for quest_file in sorted(folder.glob('*.py')):
                if quest_file.name.startswith('_'):
                    continue
                quest = self._load_quest_from_file(quest_file, folder.name)
                if quest is not None:
                    self.quest_manager.add_quest(
                        quest_id=quest.id,
                        title=quest.title,
                        description=quest.description,
                        folder=quest.folder,
                        data=quest.data,
                    )
                    quests.append(quest)
        return quests

    def _load_quest_from_file(self, quest_file: Path, folder_name: str) -> Optional[QuestEntry]:
        module_name = f'quest_{quest_file.stem.lower().replace(" ", "_")}'
        spec = importlib.util.spec_from_file_location(module_name, quest_file)
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        title = getattr(module, 'QUEST_TITLE', quest_file.stem)
        description = getattr(module, 'QUEST_DESCRIPTION', '')
        quest_id = getattr(module, 'QUEST_ID', f'{folder_name}:{quest_file.stem}')
        data = getattr(module, 'QUEST_DATA', {})
        if not isinstance(data, dict):
            data = {}
        return QuestEntry(id=quest_id, title=title, description=description, folder=folder_name, data=data)
