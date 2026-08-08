"""
Map loader using pytmx library to handle Tiled TMX maps.
This class now encapsulates loading, parsing, and rendering logic.
"""
import pygame as pg
from pathlib import Path
import pytmx

# --- Helper Classes (Kept for logical separation of concerns) ---

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
        screen.blit(self.surface, (int(self.x - camera_x), int(self.y - camera_y)))


class TiledCollisionObject:
    """Handling of individual polygon data for walls/collisions."""
    def __init__(self, obj_data):
        self.id = obj_data.id
        # The base spawn point of the object
        self.x = obj_data.x
        self.y = obj_data.y

        # Convert Tiled relative points into absolute screen points
        self.points = []
        if hasattr(obj_data, 'polygon') and obj_data.polygon:
            for pt in obj_data.polygon:
                # pytmx polygon points are tuples of (x, y)
                abs_x = obj_data.x + pt[0] 
                abs_y = obj_data.y + pt[1]
                self.points.append((abs_x, abs_y))
                
    def draw_debug(self, screen, color=(255, 0, 0)):
        """Draws the polygon outlines for debugging."""
        if len(self.points) > 1:
            pg.draw.polygon(screen, color, self.points, 2)


class TiledMap:
    def __init__(self, tmx_data, base_path, scale=1.0): 
        self.tmx_data = tmx_data # Save the raw data for rendering tiles
        self.scale = scale
        self.tile_width = int(tmx_data.tilewidth * scale)
        self.tile_height = int(tmx_data.tileheight * scale)

        self.width_in_tiles = tmx_data.width
        self.height_in_tiles = tmx_data.height

        self.pixels_width = self.width_in_tiles * self.tile_width
        self.pixels_height = self.height_in_tiles * self.tile_height

        self.image_layers = []
        self.collision_objects = []
        self.tile_layers = [] # List to hold standard tile layers



        print("--- DEBUG: Starting layer parsing. ---")
        for layer in tmx_data.visible_layers:
            
            # 1. NEW: Handle Standard Grid Tile Layers
            if isinstance(layer, pytmx.TiledTileLayer):
                print(f"--- DEBUG: Found Tile Layer: {layer.name} ---")
                self.tile_layers.append(layer)
            
            # 2. Handle Image Layers
            elif isinstance(layer, pytmx.TiledImageLayer):
                print(f"--- DEBUG: Found Image Layer: {layer.name} ---")
                self.image_layers.append(TiledImageLayer(
                    name=layer.name,
                    image_path=layer.source, 
                    x=getattr(layer, 'offsetx', 0), 
                    y=getattr(layer, 'offsety', 0)
                ))
            
            # 3. Handle Object Groups 
            elif isinstance(layer, pytmx.TiledObjectGroup):
                print(f"--- DEBUG: Found Object Group: {layer.name} ---")
                for obj in layer:
                    if hasattr(obj, 'polygon') and obj.polygon:
                        self.collision_objects.append(TiledCollisionObject(obj))

        print("--- DEBUG: TiledMap initialization complete. ---")
        
    def render(self, screen, camera_x=0, camera_y=0):
        """Renders all parsed layers onto the screen surface."""
        
        # 1. Draw standard Tile Layers
        for layer in self.tile_layers:
            # pytmx allows us to loop through every tile's x, y, and image data
            for x, y, gid in layer:
                tile_surface = self.tmx_data.get_tile_image_by_gid(gid)
                if tile_surface:
                    # Scale the tile surface to match the desired tile size 
                    if self.scale != 1.0:
                        tile_surface = pg.transform.scale(tile_surface, (self.tile_width, self.tile_height))

                    # Calculate position and subtract camera offset
                    pos_x = (x * self.tile_width) - camera_x
                    pos_y = (y * self.tile_height) - camera_y
                    screen.blit(tile_surface, (pos_x, pos_y))

        # 2. Draw massive background Image Layers (if you have any)
        for layer in self.image_layers:
            layer.draw(screen, camera_x, camera_y)
        
# --- End of map_loader.py ---