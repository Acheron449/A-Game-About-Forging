"""Shows quest menu and handles quest selection."""

from __future__ import annotations

from typing import List, Optional

from .quest_manager import QuestManager


class QuestMenu:
    """Render helper for the quest log UI."""

    def __init__(self, quest_manager: Optional[QuestManager] = None, selected_id: Optional[str] = None) -> None:
        self.quest_manager = quest_manager or QuestManager()
        self.selected_id = selected_id

    def get_menu_lines(self) -> List[str]:
        lines = ['Quests']
        for quest in self.quest_manager.get_all_quests():
            marker = '>' if quest.id == self.selected_id else ' '
            status = '✓' if quest.completed else '•'
            lines.append(f'{marker} {status} {quest.title}')
        return lines

    def get_selected_quest(self) -> Optional[object]:
        if self.selected_id is None:
            return None
        return self.quest_manager.get_quest(self.selected_id)