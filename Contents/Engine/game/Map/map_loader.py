"""
Map loader using pytmx library to handle Tiled TMX maps.
Handles:
    - Tile layers
    - Image layers
    - Collision objects
    - Interactive objects
        - doors
        - loot_point
        - mining_node
"""

import pygame as pg
from pathlib import Path
import pytmx


# ============================================================
# IMAGE LAYER
# ============================================================

class TiledImageLayer:

    def __init__(self, name, image_path, x, y):

        self.name = name
        self.x = x
        self.y = y

        self.surface = pg.image.load(
            str(image_path)
        ).convert_alpha()

        self.width = self.surface.get_width()
        self.height = self.surface.get_height()

    def draw(self, screen, camera_x=0, camera_y=0):

        screen.blit(
            self.surface,
            (
                int(self.x - camera_x),
                int(self.y - camera_y),
            ),
        )


# ============================================================
# COLLISION OBJECT
# ============================================================

class TiledCollisionObject:

    def __init__(self, obj_data):

        self.id = obj_data.id
        self.name = obj_data.name

        self.rect = pg.Rect(
            int(obj_data.x),
            int(obj_data.y),
            int(obj_data.width),
            int(obj_data.height),
        )

    def draw_debug(
        self,
        screen,
        camera_x=0,
        camera_y=0,
        color=(255, 0, 0),
    ):

        debug_rect = self.rect.move(
            -camera_x,
            -camera_y,
        )

        pg.draw.rect(
            screen,
            color,
            debug_rect,
            2,
        )


# ============================================================
# INTERACTIVE OBJECT
# ============================================================

class TiledInteractiveObject:

    def __init__(self, obj_data):

        self.id = obj_data.id
        self.name = obj_data.name

        # Tiled class name
        self.class_name = getattr(
            obj_data,
            "class_",
            "",
        )

        # Fallback for older pytmx versions
        if not self.class_name:
            self.class_name = getattr(
                obj_data,
                "type",
                "",
            )

        self.rect = pg.Rect(
            int(obj_data.x),
            int(obj_data.y),
            int(obj_data.width),
            int(obj_data.height),
        )

        # Store the actual world-space coordinates
        self.coordinates = (
            self.rect.x,
            self.rect.y,
        )

        # Store the centre as well
        self.center = self.rect.center

        # ----------------------------------------------------
        # Read custom Tiled properties
        # ----------------------------------------------------

        properties = getattr(
            obj_data,
            "properties",
            {}
        ) or {}

        self.properties = properties

        # Door properties
        self.target_map = properties.get(
            "target_map"
        )

        self.target_x = properties.get(
            "target_x"
        )

        self.target_y = properties.get(
            "target_y"
        )

        # Loot properties
        self.capacity = properties.get(
            "capacity",
            10,
        )

        # Mining properties
        self.resource = properties.get(
            "resource",
            "ore",
        )

        self.health = properties.get(
            "health",
            3,
        )

        self.respawn_time = properties.get(
            "respawn_time",
            0,
        )

    def is_player_inside(self, player_rect):

        return self.rect.colliderect(player_rect)

    def is_player_near(
        self,
        player_rect,
        distance=50,
    ):

        expanded_rect = self.rect.inflate(
            distance * 2,
            distance * 2,
        )

        return expanded_rect.colliderect(
            player_rect
        )

    def draw_debug(
        self,
        screen,
        camera_x=0,
        camera_y=0,
        color=(0, 255, 255),
    ):

        debug_rect = self.rect.move(
            -camera_x,
            -camera_y,
        )

        pg.draw.rect(
            screen,
            color,
            debug_rect,
            2,
        )


# ============================================================
# TILED MAP
# ============================================================

class TiledMap:

    def __init__(
        self,
        tmx_data,
        base_path,
        scale=1.0,
    ):

        self.tmx_data = tmx_data
        self.scale = scale

        self.tile_width = int(
            tmx_data.tilewidth * scale
        )

        self.tile_height = int(
            tmx_data.tileheight * scale
        )

        self.width_in_tiles = tmx_data.width
        self.height_in_tiles = tmx_data.height

        self.pixels_width = (
            self.width_in_tiles *
            self.tile_width
        )

        self.pixels_height = (
            self.height_in_tiles *
            self.tile_height
        )

        # ----------------------------------------------------
        # Layers
        # ----------------------------------------------------

        self.image_layers = []
        self.tile_layers = []

        # ----------------------------------------------------
        # Collision
        # ----------------------------------------------------

        self.collision_objects = []

        # ----------------------------------------------------
        # Interactive objects
        # ----------------------------------------------------

        self.interactive_objects = []

        self.doors = []
        self.loot_points = []
        self.mining_nodes = []

        # ----------------------------------------------------
        # Parse Tiled
        # ----------------------------------------------------

        print(
            "--- DEBUG: Starting layer parsing. ---"
        )

        for layer in tmx_data.visible_layers:

            # =================================================
            # TILE LAYER
            # =================================================

            if isinstance(
                layer,
                pytmx.TiledTileLayer,
            ):

                print(
                    f"--- Tile Layer: {layer.name} ---"
                )

                self.tile_layers.append(layer)

            # =================================================
            # IMAGE LAYER
            # =================================================

            elif isinstance(
                layer,
                pytmx.TiledImageLayer,
            ):

                print(
                    f"--- Image Layer: {layer.name} ---"
                )

                self.image_layers.append(
                    TiledImageLayer(
                        name=layer.name,
                        image_path=layer.source,
                        x=getattr(
                            layer,
                            "offsetx",
                            0,
                        ),
                        y=getattr(
                            layer,
                            "offsety",
                            0,
                        ),
                    )
                )

            # =================================================
            # OBJECT GROUP
            # =================================================

            elif isinstance(
                layer,
                pytmx.TiledObjectGroup,
            ):

                print(
                    f"--- Object Group: {layer.name} ---"
                )

                for obj in layer:

                    # -----------------------------------------
                    # COLLISION OBJECTS
                    # -----------------------------------------

                    if layer.name == "Collision":

                        if (
                            obj.width > 0
                            and obj.height > 0
                        ):

                            self.collision_objects.append(
                                TiledCollisionObject(obj)
                            )

                    # -----------------------------------------
                    # INTERACTIVE OBJECTS
                    # -----------------------------------------

                    elif layer.name == "Objects":

                        if (
                            obj.width <= 0
                            or obj.height <= 0
                        ):
                            continue

                        interactive = (
                            TiledInteractiveObject(obj)
                        )

                        self.interactive_objects.append(
                            interactive
                        )

                        class_name = (
                            interactive.class_name.lower()
                        )

                        # -------------------------------------
                        # DOOR
                        # -------------------------------------

                        if class_name == "door":

                            self.doors.append(
                                interactive
                            )

                        # -------------------------------------
                        # LOOT POINT
                        # -------------------------------------

                        elif class_name == "loot_point":

                            self.loot_points.append(
                                interactive
                            )

                        # -------------------------------------
                        # MINING NODE
                        # -------------------------------------

                        elif class_name in (
                            "mining_node",
                            "mining",
                            "mine",
                        ):

                            self.mining_nodes.append(
                                interactive
                            )

        print(
            "--- DEBUG: TiledMap initialization complete. ---"
        )

        print(
            "Doors:",
            len(self.doors),
        )

        print(
            "Loot points:",
            len(self.loot_points),
        )

        print(
            "Mining nodes:",
            len(self.mining_nodes),
        )

    # ========================================================
    # FIND INTERACTIVE OBJECT
    # ========================================================

    def get_interaction(
        self,
        player_rect,
    ):

        """
        Returns the first interactive object whose
        rectangle contains the player.

        Priority:
            door
            loot_point
            mining_node
        """

        for obj in self.doors:

            if obj.is_player_inside(player_rect):
                return obj

        for obj in self.loot_points:

            if obj.is_player_inside(player_rect):
                return obj

        for obj in self.mining_nodes:

            if obj.is_player_inside(player_rect):
                return obj

        return None

    # ========================================================
    # RENDER
    # ========================================================

    def render(
        self,
        screen,
        camera_x=0,
        camera_y=0,
    ):

        # ----------------------------------------------------
        # Tile layers
        # ----------------------------------------------------

        for layer in self.tile_layers:

            for x, y, gid in layer:

                tile_surface = (
                    self.tmx_data
                    .get_tile_image_by_gid(gid)
                )

                if tile_surface:

                    if self.scale != 1.0:

                        tile_surface = pg.transform.scale(
                            tile_surface,
                            (
                                self.tile_width,
                                self.tile_height,
                            ),
                        )

                    pos_x = (
                        x * self.tile_width
                        - camera_x
                    )

                    pos_y = (
                        y * self.tile_height
                        - camera_y
                    )

                    screen.blit(
                        tile_surface,
                        (
                            pos_x,
                            pos_y,
                        ),
                    )

        # ----------------------------------------------------
        # Image layers
        # ----------------------------------------------------

        for layer in self.image_layers:

            layer.draw(
                screen,
                camera_x,
                camera_y,
            )