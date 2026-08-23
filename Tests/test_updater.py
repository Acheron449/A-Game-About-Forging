"""Verify dependency inspection and import-update helper behavior."""
 # Verify dependency discovery and import-update behavior in the updater.
import unittest
from pathlib import Path

from Engine.updater import collect_dependency_packages


class UpdaterTests(unittest.TestCase):
    # Verify that source imports are mapped to installable package names.
    def test_collect_dependency_packages_finds_common_game_dependencies(self):
        # Resolve the repository root used as the dependency-scan input.
        project_root = Path(__file__).resolve().parent
        # Collect third-party packages referenced by the project sources.
        packages = collect_dependency_packages(project_root)

        # Confirm the scanner recognizes pygame imports.
        self.assertIn('pygame', packages)
        # Confirm the scanner recognizes numpy imports.
        self.assertIn('numpy', packages)
        # Confirm the scanner recognizes arcade imports.
        self.assertIn('arcade', packages)
        # Confirm the scanner recognizes pytmx imports.
        self.assertIn('pytmx', packages)


if __name__ == '__main__':
    unittest.main()
