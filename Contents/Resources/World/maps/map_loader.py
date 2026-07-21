"""map loader with structure in charge of handling Tiled JSON Exported maps with multi layer handling"""
import json
import pygame
from pathlib import Path
from .....Engine.config.config import config
from .....Engine.config.imports import imports

class TiledImageLayer:
    """Handles Large single-image backgrounds"""
    def __init__(self, name, image_path, x, y):
        self.name = name
        self.x = x
        self.y = y
        
        print(f"[MapLoader DEBUG] TiledImageLayer '{name}' initialized. Path: {image_path}")
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
            print(f"[MapLoader DEBUG] Parsing collision object ID {self.id} with {len(obj_data['polygon'])} points.")
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
    def __init__(self, data, base_path, csv_data=None):
        print("==============================================================")
        print(f"[MapLoader DEBUG] TiledMap initialized. Starting parsing. Base Path: {base_path}")
        self.tile_width = data['tilewidth']
        self.tile_height = data['tileheight']
        
        # Categorized lists for easier processing
        self.image_layers = []
        self.collision_objects = []
        self.tilesets = {} 

        # --- CSV INTEGRATION POINT ---
        if csv_data:
            print("--- DEBUG: CSV data provided. Integrating supplementary data. ---")
            # TODO: Implement CSV parsing logic here.
            pass # For now, we just acknowledge it was passed.

        # 1. Parse Layers based on their unique types
        print("--- DEBUG: Starting layer parsing. ---")
        for layer in data['layers']:
            print(f"[MapLoader DEBUG] Processing Layer Type: {layer.get('type')}")
            
            # Handle Image Layers (like your "cave 1" background) - ***TEMPORARILY SKIPPED***
            if layer['type'] == 'imagelayer':
                pass
            # Handle Object Groups (like your "wall_collisions" polygon data)
            elif layer['type'] == 'objectgroup':
                print("--- DEBUG: Found Object Group. ---")
                for obj in layer.get('objects', []):
                    # We only care about shapes that have actual boundary points
                    if 'polygon' in obj:
                        self.collision_objects.append(TiledCollisionObject(obj))

        # 2. (Optional) Load external tilesets if you use standard tiles later
        print("--- DEBUG: TiledMap initialization complete. ---")