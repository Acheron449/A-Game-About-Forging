"""interface for the minimap in the game."""

from ..config import config
from ..config import imports

class Minimap:
    def __init__(self):
        self.is_visible = True  # Minimap is visible by default
        self.zoom_level = 1.0   # Default zoom level
        self.pan_offset = (0, 0) # Default pan offset

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
        x_offset, y_offset = self.pan_offset
        self.pan_offset = (x_offset + dx, y_offset + dy)

    def handle_event(self, event):
        """Handle user input events for the minimap."""
        if event.type == imports.pygame.KEYDOWN:
            if event.key == config.MINIMAP_ZOOM_IN_KEY:
                self.zoom_in()
            elif event.key == config.MINIMAP_ZOOM_OUT_KEY:
                self.zoom_out()
            elif event.key == config.MINIMAP_PAN_UP_KEY:
                self.pan(0, -10)  # Pan up
            elif event.key == config.MINIMAP_PAN_DOWN_KEY:
                self.pan(0, 10)   # Pan down
            elif event.key == config.MINIMAP_PAN_LEFT_KEY:
                self.pan(-10, 0)  # Pan left
            elif event.key == config.MINIMAP_PAN_RIGHT_KEY:
                self.pan(10, 0)   # Pan right

    def render(self, screen):
        """Render the minimap on the given screen."""
        if not self.is_visible:
            return

        # Render the minimap background and elements here
        # Apply zoom and pan transformations based on self.zoom_level and self.pan_offset