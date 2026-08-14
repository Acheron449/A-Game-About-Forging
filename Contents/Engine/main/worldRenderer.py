"""Handles rendering of the world map using the TiledMap structure."""

from ..game.Map.map_loader import TiledMap
from ..configuration.constants import *


class worldRenderer:
    def __init__(self, screen, tiled_map: TiledMap): # Accept the map object here
        self.screen = screen
        self.tiled_map = tiled_map # Store the map object

    def render(self, cam_x, cam_y):
        """Delegates rendering to the TiledMap object."""
        self.tiled_map.render(self.screen, cam_x, cam_y)
