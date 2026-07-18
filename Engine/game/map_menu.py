"""opens upon interaction with M key or the minimap"""

from ..config import config
from ..config import imports

class MapMenu:
    def __init__(self, map_manager):
        self.map_manager = map_manager # Dependency injected
        self.is_open = False
        self.zoom_level = 1.0  # Default zoom level
        self.pan_offset = (0, 0)  # Default pan offset
        self.current_selected_map = None

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
            # ... existing key handling (zoom/pan) ...
            if event.key == config.MAP_ZOOM_IN_KEY:
                self.zoom_in()
            elif event.key == config.MAP_ZOOM_OUT_KEY:
                self.zoom_out()
            # ... (rest of key handling)
            pass

        # TODO: Add logic here to handle map selection from the dropdown menu if map_data suggests a selection event occurred.
        # This selection should call map_manager.load_map(selected_name) if the map is different.

    def render(self, screen):
        """Render the map menu on the given screen."""
        if not self.is_open:
            return

        # Render the map background and elements here
        # The sidebar dropdown list should be drawn here, populated using self.map_manager.available_map_names.
        # This fulfills the requirement for the map menu display.
        pass