# engine/game/map_loader.py
"""map loader with structure in charge of handling Tiled JSON Exported maps with multi layer handling"""
import json
import pygame
from pathlib import Path
from ..config import config
from ..config import imports

class TiledImageLayer:
    """Handles Large single-image backgrounds"""
    def __init__(self, name, image_path, x, y):
        self.name = name
        self.x = x
        self.y = y
        
        # Load image directly
        self.surface = pygame.image.load(str(image_path)).convert_alpha()
        
        # Automatically pull dimensions directly from the loaded surface
        self.width = self.surface.get_width()
        self.height = self.surface.get_height()

    def draw(self, screen):
        screen.blit(self.surface, (self.x, self.y))


class TiledCollisionObject:
    """handling of individual polygon data for walls/collisions."""
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
            pygame.draw.polygon(screen, color, self.points, 2)


class TiledMap:
    """Parses the raw Tiled JSON data into usable Python objects."""
    def __init__(self, data, base_path):
        print("--- MAP LOADER: TiledMap initialized. Starting parsing. ---")
        self.tile_width = data['tilewidth']
        self.tile_height = data['tileheight']
        
        # Categorized lists for easier processing
        self.image_layers = []
        self.collision_objects = []
        self.tilesets = {} 

        # 1. Parse Layers based on their unique types
        print("--- DEBUG: Starting layer parsing. ---")
        for layer in data['layers']:
            
            # Handle Image Layers (like your "cave 1" background)
            if layer['type'] == 'imagelayer':
                print("--- DEBUG: Found Image Layer: {name} ---")
                # Fix Tiled escaped slashes (\/) and clean path
                clean_img_path = layer['image'].replace('\\', '/')
                full_image_path = Path(base_path) / clean_img_path
                
                self.image_layers.append(TiledImageLayer(
                    name=layer['name'],
                    image_path=full_image_path,
                    x=layer['x'],
                    y=layer['y']
                ))
            
            # Handle Object Groups (like your "wall_collisions" polygon data)
            elif layer['type'] == 'objectgroup':
                print("--- DEBUG: Found Object Group. ---")
                for obj in layer.get('objects', []):
                    # We only care about shapes that have actual boundary points
                    if 'polygon' in obj:
                        self.collision_objects.append(TiledCollisionObject(obj))

        # 2. (Optional) Load external tilesets if you use standard tiles later
        print("--- DEBUG: TiledMap initialization complete. ---")