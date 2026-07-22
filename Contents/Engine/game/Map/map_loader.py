# Engine/game/map_loader.py
"""
Map loader using pytmx library to handle Tiled TMX maps.
This replaces the previous custom JSON parsing structure.
"""
import pygame as pg
from pathlib import Path
import pytmx

# NOTE: The constants and paths defined in config.py are likely still needed for resources,
# but the map loading itself is now handled by pytmx.

class TiledImageLayer:
    """Handles Large single-image backgrounds loaded via pytmx."""
    def __init__(self, name, image_path, x, y):
        self.name = name
        self.x = x
        self.y = y
        
        # Load image directly using pygame
        self.surface = pg.image.load(str(image_path)).convert_alpha()
        
        # Automatically pull dimensions directly from the loaded surface
        self.width = self.surface.get_width()
        self.height = self.surface.get_height()

    def draw(self, screen, camera_x=0, camera_y=0):
        """Draws the layer, applying camera offsets."""
        # Draw at the anchor point relative to the camera view
        screen.blit(self.surface, (self.x - camera_x, self.y - camera_y))


class TiledCollisionObject:
    """Handling of individual polygon data for walls/collisions."""
    def __init__(self, obj_data):
        self.id = obj_data['id']
        # The base spawn point of the object
        self.x = obj_data['x']
        self.y = obj_data['y']

        # Convert Tiled relative points into absolute screen points
        self.points = []
        if 'polygon' in obj_data:
            for pt in obj_data['polygon']:
                abs_x = obj_data['x'] + pt['x'] 
                abs_y = obj_data['y'] + pt['y']
                self.points.append((abs_x, abs_y))
                
    def draw_debug(self, screen, color=(255, 0, 0)):
        """Draws the polygon outlines for debugging."""
        if len(self.points) > 1:
            pg.draw.polygon(screen, color, self.points, 2)


class TiledMap:
    """Parses the raw Tiled data (via pytmx) into usable Python objects."""
    def __init__(self, tmx_data, base_path): # tmx_data is the loaded pytmx object
        print("--- MAP LOADER: TiledMap initialized. Starting parsing. ---")
        self.tile_width = tmx_data.tilewidth
        self.tile_height = tmx_data.tileheight
        
        # Categorized lists for easier processing
        self.image_layers = []
        self.collision_objects = []
        self.tilesets = {}

        # 1. Parse Layers based on their unique types
        print("--- DEBUG: Starting layer parsing. ---")
        for layer in tmx_data.visibleLayers:
            
            # Handle Image Layers (like your "cave 1" background)
            if isinstance(layer, pytmx.TiledImageLayer):
                print("--- DEBUG: Found Image Layer: {name} ---")
                # IMPORTANT: You must ensure layer.image_path, layer.x, and layer.y 
                # correctly hold the data needed for TiledImageLayer.__init__
                self.image_layers.append(TiledImageLayer(
                    name=layer.name,
                    image_path=layer.image_path, # <<< This needs to be reliable from pytmx data
                    x=layer.x,
                    y=layer.y
                ))
            
            # Handle Object Groups (like your "wall_collisions" polygon data)
            elif isinstance(layer, pytmx.TiledObjectGroup):
                print("--- DEBUG: Found Object Group. ---")
                for obj in layer.objects:
                    # We only care about shapes that have actual boundary points
                    if 'polygon' in obj:
                        self.collision_objects.append(TiledCollisionObject(obj))

        # 2. (Optional) Load external tilesets if you use standard tiles later
        print("--- DEBUG: TiledMap initialization complete. ---")

# The function that drives loading must now use pytmx.load_pygame()
# Example signature for the function that replaces the old load_tiled_map:
# def load_tiled_map(tmx_filepath: str, base_resource_path: Path) -> TiledMap:
#     tm = pytmx.load_pygame(tmx_filepath, pixelalpha=True)
#     return TiledMap(tm, base_resource_path)
