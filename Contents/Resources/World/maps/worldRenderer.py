"""handles rendering of the world map using the TiledMap structure"""

# We only need pygame here, not the map loader dependencies yet.
import pygame 

class WorldRenderer:
    """Handles rendering of the world map using the TiledMap structure."""
    def __init__(self, screen):
        self.screen = screen
        self.tiled_map = None # Map object will be assigned later when loaded.

    def set_map(self, tiled_map):
        # This method is called when the map has successfully loaded.
        self.tiled_map = tiled_map

    def render(self, cam_x, cam_y):
        if not self.tiled_map:
            # If the map hasn't loaded yet, we do nothing.
            return

        # --- START: Using the TiledMap structure for rendering ---
        # Draw all background images first (Image Layers)
        for layer in self.tiled_map.image_layers:
            # Note: We are ignoring cam_x/cam_y here for simplicity, assuming the layer's X/Y is the anchor.
            layer.draw(self.screen)

        # If you want to draw collision outlines for debugging:
        # for col_obj in self.tiled_map.collision_objects:
        #     col_obj.draw_debug(self.screen)
        # --- END: Using the TiledMap structure for rendering ---
