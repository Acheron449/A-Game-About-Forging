import json

from ..config.config import *
from ..config.imports import *

class WorldRenderer:
    def __init__(self):
        pass

    def render_world(self, world, screen):
        # Render map and entities
        # Placeholder for rendering logic
        pass

class UIRenderer:
    def __init__(self, player):
        self.player = player
        self.elements = {}  # Health bar, stats display, etc.

    def draw_ui(self, screen):
        # Draw UI elements
        # Placeholder for UI drawing logic
        pass

    def update_ui(self):
        # Update UI based on player stats
        pass

    def configure_appearance(self, appearance):
        self.player.appearance = appearance
        config_dir = "Saves/player config"
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, "appearance.json")
        with open(config_path, 'w') as f:
            json.dump({"appearance": appearance}, f)
