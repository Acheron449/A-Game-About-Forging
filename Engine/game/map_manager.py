"""manages the loading, creation, and state of maps in the game."""

from ..config import config
from ..config import imports
from ..main import worldRenderer

class MapManager:
    def __init__(self):
        self.maps = {}
        self.available_map_names = []
        self.current_map_name = None

    def create_map(self, name, map_data_object):
        # map_data_object is now expected to be the parsed JSON map data object.
        self.maps[name] = map_data_object
        self.available_map_names.append(name)
        # Set the map as current upon successful creation/loading
        self.current_map_name = name

    def load_map(self, name):
        # Returns the map object if it exists and sets it as current
        if name in self.maps:
            self.current_map_name = name
            return self.maps[name]
        return None

    def get_map_data_for_minimap(self):
        # This method must return a simplified, renderable snapshot of the current map state.
        # This snapshot includes player dimensions, map dimensions, and necessary tile/layer info.
        if self.current_map_name and self.maps.get(self.current_map_name):
            # Pass the entire map object structure for the renderer to use for scaling/panning.
            return self.maps[self.current_map_name]
        return None
    def update_player_location(self, new_x, new_y):
        # This method is called by the game loop to keep track of player movement.
        # It must also handle collision/bounds checking against the loaded map data.
        if self.current_map_name and self.maps.get(self.current_map_name):
            # TODO: Check if (new_x, new_y) is within map bounds and collision layers.
            pass
        # If the player moves outside the map bounds, this is where you'd handle despawning or transition.

