import unittest
from pathlib import Path

from Engine.updater import collect_dependency_packages


class UpdaterTests(unittest.TestCase):
    def test_collect_dependency_packages_finds_common_game_dependencies(self):
        project_root = Path(__file__).resolve().parent
        packages = collect_dependency_packages(project_root)

        self.assertIn('pygame', packages)
        self.assertIn('numpy', packages)
        self.assertIn('arcade', packages)
        self.assertIn('pytmx', packages)


if __name__ == '__main__':
    unittest.main()
