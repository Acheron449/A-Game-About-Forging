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

    def __init__(self, obj_data, scale=1.0):

        self.id = obj_data.id
        self.name = obj_data.name

        # ----------------------------------------------------
        # Collision property
        # ----------------------------------------------------
        #
        # Objects on the Collision layer are solid by default.
        #
        # In Tiled, you can set:
        #
        # collision = false
        #
        # on things such as doors.
        #
        self.collision_enabled = obj_data.properties.get(
            "collision",
            True
        )

        # ----------------------------------------------------
        # Polygon collision object
        # ----------------------------------------------------

        polygon = getattr(obj_data, "polygon", None)

        if polygon:

            self.points = [
                (
                    (obj_data.x + point.x) * scale,
                    (obj_data.y + point.y) * scale
                )
                for point in polygon
            ]

        # ----------------------------------------------------
        # Normal rectangle collision object
        # ----------------------------------------------------

        else:

            x = obj_data.x * scale
            y = obj_data.y * scale
            width = obj_data.width * scale
            height = obj_data.height * scale

            self.points = [
                (x, y),
                (x + width, y),
                (x + width, y + height),
                (x, y + height),
            ]

        # ----------------------------------------------------
        # Bounding rectangle
        #
        # Used only for broad-phase collision checking
        # and compatibility/debugging.
        # ----------------------------------------------------

        xs = [point[0] for point in self.points]
        ys = [point[1] for point in self.points]

        self.rect = pg.Rect(
            int(min(xs)),
            int(min(ys)),
            int(max(xs) - min(xs)),
            int(max(ys) - min(ys)),
        )

    # ========================================================
    # COLLISION TEST
    # ========================================================

    def collides_with_rect(self, player_rect):

        if not self.collision_enabled:
            return False

        # ----------------------------------------------------
        # Broad-phase check
        #
        # Quickly reject objects that are nowhere near player.
        # ----------------------------------------------------

        if not self.rect.colliderect(player_rect):
            return False

        # ----------------------------------------------------
        # Convert player rectangle to polygon
        # ----------------------------------------------------

        player_points = [
            (player_rect.left, player_rect.top),
            (player_rect.right, player_rect.top),
            (player_rect.right, player_rect.bottom),
            (player_rect.left, player_rect.bottom),
        ]

        # ----------------------------------------------------
        # SAT collision test
        # ----------------------------------------------------

        polygons = [
            self.points,
            player_points,
        ]

        for polygon in polygons:

            for i in range(len(polygon)):

                p1 = polygon[i]
                p2 = polygon[(i + 1) % len(polygon)]

                # Edge vector
                edge_x = p2[0] - p1[0]
                edge_y = p2[1] - p1[1]

                # Perpendicular axis
                axis_x = -edge_y
                axis_y = edge_x

                # Normalize axis
                length = (axis_x ** 2 + axis_y ** 2) ** 0.5

                if length == 0:
                    continue

                axis_x /= length
                axis_y /= length

                # Project first polygon
                projections_a = [
                    point[0] * axis_x + point[1] * axis_y
                    for point in self.points
                ]

                min_a = min(projections_a)
                max_a = max(projections_a)

                # Project second polygon
                projections_b = [
                    point[0] * axis_x + point[1] * axis_y
                    for point in player_points
                ]

                min_b = min(projections_b)
                max_b = max(projections_b)

                # If there's a gap, polygons do not collide.
                if max_a < min_b or max_b < min_a:
                    return False

        return True

    # ========================================================
    # DEBUG DRAW
    # ========================================================

    def draw_debug(
        self,
        screen,
        camera_x=0,
        camera_y=0,
        color=(255, 255, 255),
    ):

        if not self.collision_enabled:
            return

        debug_points = [
            (
                int(x - camera_x),
                int(y - camera_y)
            )
            for x, y in self.points
        ]

        if len(debug_points) >= 3:

            pg.draw.polygon(
                screen,
                color,
                debug_points,
                2
            )

        else:

            debug_rect = self.rect.move(
                -camera_x,
                -camera_y
            )

            pg.draw.rect(
                screen,
                color,
                debug_rect,
                2
            )

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

                # Only objects on the Collision layer become barriers
                if layer.name == "Collision":

                    for obj in layer:

                        collision_object = TiledCollisionObject(
                            obj,
                            scale=self.scale
                        )

                        self.collision_objects.append(
                            collision_object
                        )

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