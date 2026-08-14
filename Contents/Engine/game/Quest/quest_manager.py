"""Quest tracker and manager for the game."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class QuestEntry:
    """Represents a single quest in the quest log."""

    id: str
    title: str
    description: str = ''
    completed: bool = False
    folder: Optional[str] = None
    data: Dict[str, object] = field(default_factory=dict)


class QuestManager:
    """Stores and updates quest state for the quest menu and UI."""

    def __init__(self) -> None:
        self._quests: Dict[str, QuestEntry] = {}

    def add_quest(self, quest_id: str, title: str, description: str = '', *, folder: Optional[str] = None, data: Optional[Dict[str, object]] = None) -> QuestEntry:
        quest = QuestEntry(id=quest_id, title=title, description=description, folder=folder, data=data or {})
        self._quests[quest_id] = quest
        return quest

    def get_quest(self, quest_id: str) -> Optional[QuestEntry]:
        return self._quests.get(quest_id)

    def mark_completed(self, quest_id: str) -> Optional[QuestEntry]:
        quest = self.get_quest(quest_id)
        if quest is not None:
            quest.completed = True
        return quest

    def get_active_quest_titles(self) -> List[str]:
        return [quest.title for quest in self._quests.values() if not quest.completed]

    def get_completed_quest_titles(self) -> List[str]:
        return [quest.title for quest in self._quests.values() if quest.completed]

    def get_all_quests(self) -> List[QuestEntry]:
        return list(self._quests.values())

    def get_quest_lines(self) -> List[str]:
        lines: List[str] = []
        for quest in self._quests.values():
            status = '✓' if quest.completed else '•'
            lines.append(f'{status} {quest.title}')
        return lines