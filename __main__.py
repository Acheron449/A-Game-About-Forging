"""Entry point for the game."""

 # Launch the package entry point when the repository is run as a module.
import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from Contents.Engine.updater import ensure_runtime_dependencies

    project_root = Path(__file__).resolve().parent
    ensure_runtime_dependencies(project_root, install_missing=True)

    from Contents.Engine.main.main import main as game_main
    game_main()
    
