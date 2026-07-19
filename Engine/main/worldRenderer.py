# Engine/main/worldRenderer.py
"""handles rendering of the world map using the TiledMap structure"""

from ..game.map_loader import TiledMap
from ..config import config
from ..config import imports


class worldRenderer:
    def __init__(self, screen, tiled_map=None): # Accept the map object here
        self.screen = screen
        self.tiled_map = tiled_map # Store the map object

    def render(self, cam_x, cam_y):
        if not self.tiled_map:
            return

        # --- START: Using the new TiledMap structure for rendering ---
        # Draw all background images first (Image Layers)
        for layer in self.tiled_map.image_layers:
            # Note: We are ignoring cam_x/cam_y here for simplicity, assuming the layer's X/Y is the anchor.
            layer.draw(self.screen)

        # If you want to draw collision outlines for debugging:
        # for col_obj in self.tiled_map.collision_objects:
        #     col_obj.draw_debug(self.screen)
        # --- END: Using the new TiledMap structure for rendering ---
