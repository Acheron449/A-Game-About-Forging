import unittest
from pathlib import Path

from Engine.game.quest_manager import QuestManager
from Engine.game.quest_menu import QuestMenu
from Engine.main.Quests.quest_router import QuestRouter


class QuestFrameworkTests(unittest.TestCase):
    def test_router_discovers_quests_in_folder_structure(self):
        root = Path(__file__).resolve().parent / 'Engine' / 'main' / 'Quests'
        router = QuestRouter(root_dir=root)
        quests = router.discover_quests()

        self.assertGreaterEqual(len(quests), 2)
        titles = {quest.title for quest in quests}
        self.assertIn('Molten Ash', titles)
        self.assertIn('Too much dust', titles)

    def test_manager_tracks_completed_and_active_quests(self):
        manager = QuestManager()
        manager.add_quest('test-quest', 'Test Quest', 'A brief test quest')
        manager.mark_completed('test-quest')

        self.assertTrue(manager.get_quest('test-quest').completed)
        self.assertEqual(manager.get_active_quest_titles(), [])
        self.assertEqual(manager.get_completed_quest_titles(), ['Test Quest'])

    def test_menu_builds_lines_for_selection(self):
        manager = QuestManager()
        manager.add_quest('quest-1', 'Quest One', 'First quest')
        menu = QuestMenu(manager, selected_id='quest-1')
        lines = menu.get_menu_lines()

        self.assertTrue(any('Quest One' in line for line in lines))


if __name__ == '__main__':
    unittest.main()
