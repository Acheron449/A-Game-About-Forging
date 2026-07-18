"""opens upon interaction with M key or the minimap"""
"""Allows interaction with the map, including zooming, panning, and selecting locations."""

from ..config import config
from ..config import imports

class MapMenu:
    def __init__(self):
        self.is_open = False
        self.zoom_level = 1.0  # Default zoom level
        self.pan_offset = (0, 0)  # Default pan offset

    def toggle(self):
        """Toggle the map menu open or closed."""
        self.is_open = not self.is_open

    def zoom_in(self):
        """Zoom in on the map."""
        self.zoom_level *= 1.1  # Increase zoom level by 10%

    def zoom_out(self):
        """Zoom out on the map."""
        self.zoom_level /= 1.1  # Decrease zoom level by 10%

    def pan(self, dx, dy):
        """Pan the map by a given offset."""
        x_offset, y_offset = self.pan_offset
        self.pan_offset = (x_offset + dx, y_offset + dy)

    def handle_event(self, event):
        """Handle user input events for the map menu."""
        if event.type == imports.pygame.KEYDOWN:
            if event.key == config.MAP_ZOOM_IN_KEY:
                self.zoom_in()
            elif event.key == config.MAP_ZOOM_OUT_KEY:
                self.zoom_out()
            elif event.key == config.MAP_PAN_UP_KEY:
                self.pan(0, -10)  # Pan up
            elif event.key == config.MAP_PAN_DOWN_KEY:
                self.pan(0, 10)   # Pan down
            elif event.key == config.MAP_PAN_LEFT_KEY:
                self.pan(-10, 0)  # Pan left
            elif event.key == config.MAP_PAN_RIGHT_KEY:
                self.pan(10, 0)   # Pan right

    def render(self, screen):
        """Render the map menu on the given screen."""
        if not self.is_open:
            return

        # Render the map background and elements here
        # Apply zoom and pan transformations based on self.zoom_level and self.pan_offset
    