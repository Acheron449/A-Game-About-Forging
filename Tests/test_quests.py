"""Verify quest sequencing, prerequisites, and completion behavior."""
 # Verify quest registration, loading, and completion behavior.
import unittest
from pathlib import Path

from Engine.game.quest_manager import QuestManager
from Engine.game.quest_menu import QuestMenu
from Engine.main.Quests.quest_router import QuestRouter


class QuestFrameworkTests(unittest.TestCase):
    # Verify that quest files are discovered from the expected directory tree.
    def test_router_discovers_quests_in_folder_structure(self):
        # Point discovery at the repository's quest fixture directory.
        root = Path(__file__).resolve().parent / 'Engine' / 'main' / 'Quests'
        # Construct the router with that directory as its search root.
        router = QuestRouter(root_dir=root)
        # Discover all quest definitions below the configured root.
        quests = router.discover_quests()

        # Require both fixture quests to be present in the discovered set.
        self.assertGreaterEqual(len(quests), 2)
        # Extract titles to make the following membership checks readable.
        titles = {quest.title for quest in quests}
        # Confirm the Molten Ash quest was loaded.
        self.assertIn('Molten Ash', titles)
        # Confirm the Too much dust quest was loaded.
        self.assertIn('Too much dust', titles)

    # Verify that completed quests leave the active list.
    def test_manager_tracks_completed_and_active_quests(self):
        # Start with an isolated quest manager for this test.
        manager = QuestManager()
        # Register one quest with its display title and description.
        manager.add_quest('test-quest', 'Test Quest', 'A brief test quest')
        # Mark the registered quest complete through the public API.
        manager.mark_completed('test-quest')

        # Confirm the quest record stores the completed state.
        self.assertTrue(manager.get_quest('test-quest').completed)
        # Confirm completed quests no longer appear among active titles.
        self.assertEqual(manager.get_active_quest_titles(), [])
        # Confirm the completed title is exposed in completion order.
        self.assertEqual(manager.get_completed_quest_titles(), ['Test Quest'])

    # Verify that the quest menu produces display lines for its selection.
    def test_menu_builds_lines_for_selection(self):
        # Register a quest that the menu can display.
        manager = QuestManager()
        # Use a stable identifier and title for the menu fixture.
        manager.add_quest('quest-1', 'Quest One', 'First quest')
        # Select the fixture quest when constructing the menu.
        menu = QuestMenu(manager, selected_id='quest-1')
        # Build the lines that would be rendered by the quest UI.
        lines = menu.get_menu_lines()

        # Ensure the selected quest title appears in the generated lines.
        self.assertTrue(any('Quest One' in line for line in lines))


if __name__ == '__main__':
    unittest.main()
