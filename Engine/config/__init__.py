"""Compatibility package for older imports that expected Engine.config.config."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Contents.Engine.configuration.constants import config, get_game_font

__all__ = ["config", "get_game_font"]
