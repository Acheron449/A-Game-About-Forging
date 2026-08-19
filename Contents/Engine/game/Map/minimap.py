"""manages and renders the minimap in the game, including zooming and panning functionality."""

 # Draw the player's reduced world-map view and map markers.
from ...configuration.constants import config
from ...configuration.imports import imports

class Minimap:
    def __init__(self, map_manager):
        self.map_manager = map_manager
        self.is_visible = True  # Minimap is visible by default
        self.zoom_level = 1.0   # Default zoom level
        self.pan_offset = (0, 0) # Default pan offset
        # Constants for Minimap display size and location (Top Right Corner)
        self.MINIMAP_WIDTH = 200
        self.MINIMAP_HEIGHT = 200
        # These coordinates define where the minimap window is drawn on the main screen buffer.
        self.TOP_RIGHT_X = config.SCREEN_WIDTH - self.MINIMAP_WIDTH - 10 # Offset from screen edge
        self.TOP_RIGHT_Y = 10 # Top edge offset

    def toggle_visibility(self):
        """Toggle the visibility of the minimap."""
        self.is_visible = not self.is_visible

    def zoom_in(self):
        """Zoom in on the minimap."""
        self.zoom_level *= 1.1  # Increase zoom level by 10%
    def zoom_out(self):
        """Zoom out on the minimap."""
        self.zoom_level /= 1.1  # Decrease zoom level by 10%

    def pan(self, dx, dy):
        """Pan the minimap by a given offset."""
        self.pan_offset = (self.pan_offset[0] + dx, self.pan_offset[1] + dy)

    def handle_event(self, event):
        """Handle user input events for the minimap."""
        if event.type == imports.pygame.KEYDOWN:
            if event.key == config.MINIMAP_ZOOM_IN_KEY:
                self.zoom_in() 
            elif event.key == config.MINIMAP_ZOOM_OUT_KEY:
                self.zoom_out()   # Decrease zoom level by 10%
            elif event.key == config.MINIMAP_PAN_UP_KEY:
                self.pan(0, -10)  # Pan up
            elif event.key == config.MINIMAP_PAN_DOWN_KEY:
                self.pan(0, 10)   # Pan down
            elif event.key == config.MINIMAP_PAN_LEFT_KEY:
                self.pan(-10, 0)  # Pan left
            elif event.key == config.MINIMAP_PAN_RIGHT_KEY:
                self.pan(10, 0)   # Pan right

    def render(self, screen):
        """Render the minimap on the given screen at the dedicated top-right position."""
        if not self.is_visible:
            return

        # Get the latest map data from the MapManager
        map_data_snapshot = self.map_manager.get_map_data_for_minimap()

        if map_data_snapshot is None:
            return

        # --- Rendering Logic ---
        # map_data_snapshot['map_data'] contains the full Tiled map object (including dimensions).
        # We use the map dimensions to calculate the required scale factor.
        map_object = map_data_snapshot['map_data']
        
        # Map dimensions from Tiled JSON
        map_width = map_object.get('imagewidth', 1615)
        map_height = map_object.get('imageheight', 1073)

        # Calculate scale factor based on desired minimap size vs map size
        # This scales the map content to fit the minimap window size.
        scale_x = self.MINIMAP_WIDTH / map_width
        scale_y = self.MINIMAP_HEIGHT / map_height
        
        # The effective scale is usually the smaller of the two to ensure the whole map fits initially.
        effective_scale = min(scale_x, scale_y) * self.zoom_level

        # In a full implementation, you would now use map_object and player_pos to render the scaled/panned view.
        # For demonstration, we confirm the data flow is correct.
        # print(f"Rendering minimap: Scale={effective_scale:.3f}, Pan={self.pan_offset}")
        pass
