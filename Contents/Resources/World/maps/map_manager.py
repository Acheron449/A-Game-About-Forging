"""Manages the current state of the map, including loading, camera position, and map data."""
import json

from .map_loader import load_tiled_map
from .map_loader import TiledMap
from typing import Optional
from .....Engine.config.config import config
from .....Engine.config.imports import imports

class MapManager:
    def __init__(self):
        self.current_map: Optional[TiledMap] = None
        self.camera_x = 0
        self.camera_y = 0
        self.map_loaded = False

    def load_map(self, json_filepath: str):
        """Loads a new map from a JSON file path."""
        print(f"Attempting to load map from: {json_filepath}")
        try:
            # This call handles all the heavy lifting of parsing and image loading
            tiled_map = load_tiled_map(json_filepath)
            self.current_map = tiled_map
            self.map_loaded = True
            # Reset camera to map origin upon successful load
            self.camera_x = 0
            self.camera_y = 0
            print("Map loaded successfully.")
        except Exception as e:
            print(f"Error loading map: {e}")
            self.current_map = None
            self.map_loaded = False

    @property
    def current_map_data(self) -> Optional[TiledMap]:
        """Provides the current map data to the renderer."""
        return self.current_map

    @property
    def camera_position(self) -> tuple[int, int]:
        """Returns the current camera offset."""
        return self.camera_x, self.camera_y

    def update_camera(self, dx: float, dy: float):
        """Updates the camera position based on movement/panning."""
        self.camera_x += dx
        self.camera_y += dy

    def get_render_offsets(self) -> tuple[int, int]:
        """Returns the current camera offsets needed by the renderer."""
        return self.camera_x, self.camera_y