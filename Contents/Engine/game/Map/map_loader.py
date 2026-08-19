"""
Map loader using pytmx library to handle Tiled TMX maps.

Handles:
    - Tile layers
    - Image layers
    - Collision objects
    - Interactive objects
        - doors
        - loot points
        - mining nodes
"""

 # Load Tiled map data, images, layers, and collision geometry.
from __future__ import annotations
from typing import Any, Optional

import pygame as pg
import pytmx

from ...configuration.constants import config
from typing import Optional, Any
from .interactive.door import Door
from .interactive.loot_point import LootPoint
from .interactive.mining_node import MiningNode
from .interactive.quest_point import QuestPoint
from .interactive.forge import Forge



# IMAGE LAYER


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



# COLLISION OBJECT


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

    def collides_with_rect(self, rect):

        return self.rect.colliderect(rect)




# TILED MAP


class TiledMap:

    def __init__(
        self,
        tmx_data,
        base_path,
        scale=1.0,
    ):

        self.tmx_data = tmx_data
        self.scale = scale

        # Map dimensions

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

        
        # Layers
        

        self.image_layers = []
        self.tile_layers = []

        
        # Collision

        self.collision_objects = []

        # Interactive objects
        
        self.interactive_objects = []

        self.doors = []
        self.loot_points = []
        self.mining_nodes = []
        self.forges = []

        # Spawn points

        self.spawn_points = {}

        # Quest Points
        self.quest_points = []
        
        # Parse Tiled
        

        print(
            "--- DEBUG: Starting layer parsing. ---"
        )

        for layer in tmx_data.visible_layers:

            # TILE LAYER

            if isinstance(
                layer,
                pytmx.TiledTileLayer,
            ):

                print(
                    f"--- Tile Layer: {layer.name} ---"
                )

                self.tile_layers.append(layer)

            # IMAGE LAYER

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

            # OBJECT GROUP

            elif isinstance(
                layer,
                pytmx.TiledObjectGroup,
            ):

                print(
                    f"--- Object Group: {layer.name} ---"
                )

                for obj in layer:

                    # COLLISION

                    if layer.name == "Collision":

                        if (
                            obj.width > 0
                            and obj.height > 0
                        ):

                            collision = (
                                TiledCollisionObject(obj)
                            )

                            self.collision_objects.append(
                                collision
                            )

                    # INTERACTIVE OBJECTS

                    elif layer.name in ("Objects", "MiningNodes"):

                        if (
                            obj.width <= 0
                            or obj.height <= 0
                        ):
                            continue

                        interactive = (
                            self._create_interactive_object(
                                obj
                            )
                        )

                        if interactive is not None:

                            self.interactive_objects.append(
                                interactive
                            )

                            # Store in the
                            # appropriate category.

                            if isinstance(
                                interactive,
                                Door,
                            ):

                                self.doors.append(
                                    interactive
                                )

                            elif isinstance(
                                interactive,
                                LootPoint,
                            ):

                                self.loot_points.append(
                                    interactive
                                )

                            elif isinstance(
                                interactive,
                                MiningNode,
                            ):

                                self.mining_nodes.append(
                                    interactive
                                )

                            elif isinstance(
                                interactive,
                                Forge,
                            ):

                                self.forges.append(
                                    interactive
                                )

                    # SPAWN POINTS

                    elif layer.name == "SpawnPoints":

                        for obj in layer:

                            spawn_id = obj.name or "default"

                            position = (
                                int(obj.x + obj.width / 2),
                                int(obj.y + obj.height / 2),
                            )

                            self.spawn_points[spawn_id] = position

                            print(
                                f"Spawn point: "
                                f"{spawn_id}, {position}"
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

    # SPAWN LOOKUP
    def get_spawn_position(self, spawn_id="default"):

        spawn_point = self.spawn_points.get(spawn_id)

        if spawn_point is None:

            print("--- SPAWN POINTS FOUND ---")

            for spawn_id, position in self.spawn_points.items():

                print(f"  {spawn_id}: {position}")

            print("--------------------------")

            print(
                f"WARNING: Spawn point "
                f"'{spawn_id}' not found."
            )

            # Fallback
            default_spawn = self.spawn_points.get("default")

            if default_spawn is not None:
                return default_spawn

            return (0, 0)

        return spawn_point


    
    # CREATE INTERACTIVE OBJECT
    

    def _create_interactive_object(self, obj_data):

        """
        Converts a Tiled object into the appropriate
        Python interactive object.
        """

        
        # Get Tiled class
        

        class_name = getattr(
            obj_data,
            "class_",
            "",
        )

        # Fallback for older pytmx versions
        if not class_name:

            class_name = getattr(
                obj_data,
                "type",
                "",
            )

        class_name = getattr(obj_data,"class_",None,)

        if not class_name: # if initial class name detection fails, should search for a seperate property "type"
            class_name = getattr(obj_data,"type",None,)

        if class_name is None:

            class_name = ""

        class_name = str(class_name).lower().strip()

        
        # Rectangle
        

        rect = pg.Rect(
            int(obj_data.x),
            int(obj_data.y),
            int(obj_data.width),
            int(obj_data.height),
        )

        
        # Tiled custom properties
        

        properties = (
            getattr(
                obj_data,
                "properties",
                {},
            )
            or {}
        )


        # DOOR


        if class_name == "door":

            print("\n========== DOOR LOADED ==========")
            print("Name:", obj_data.name)
            print("Class:", class_name)
            print("Properties:", properties)
            print("target_map:", properties.get("target_map"))
            print("spawn_id:", properties.get("spawn_id"))
            print("=================================\n")


            return Door(
                rect=rect,

                name=obj_data.name,
  
                target_map=properties.get(
                    "target_map"
                    
                ),

                spawn_id=properties.get(
                    "spawn_id",
                    "default",
                ),
            )

        # LOOT POINT

        if class_name == "loot_point":

            return LootPoint(
                rect=rect,
                name=properties.get("name", "Loot"),
                loot_id=properties.get("loot_id"),
                capacity=properties.get("capacity", 10),
                loot_type=properties.get("loot_type", "fixed"),
                loot_pool=properties.get("loot_pool"),
            ) 


        # MINING NODE

        if class_name in (
            "mining_node",
            "mining",
            "mine",
        ):

            return MiningNode(
                rect=rect,
                possible_resources=properties.get(
                    "possible_resources",
                    ["Stone"],
                ),
                health=properties.get(
                    "health",
                    3,
                ),
            )

        # FORGE

        if class_name == "forge":

            return Forge(
                rect=rect,
                name=properties.get(
                    "name",
                    obj_data.name or "Forge",
                ),
            )

        # map_loader.py — add before “UNKNOWN CLASS”
        if class_name == "quest_point":
            return QuestPoint(
                x=rect.x,
                y=rect.y,
                width=rect.width,
                height=rect.height,
                properties=properties,
            )


        # UNKNOWN CLASS


        print(
            f"--- DEBUG: Unknown interactive class: "
            f"{class_name} ---"
        )

        return None

    
    # FIND INTERACTIVE OBJECT
    

    def get_interaction(
        self,
        player_rect,
    ):

        """
        Returns the first interactive object
        currently being touched by the player.
        """

        for obj in self.interactive_objects:

            if obj.can_interact(player_rect):

                return obj

        return None

    
    # UPDATE INTERACTIVE OBJECTS
    

    def update(
        self,
        dt,
    ):

        """
        Updates interactive objects such as
        mining-node respawn timers.
        """

        for obj in self.interactive_objects:

            update_method = getattr(
                obj,
                "update",
                None,
            )

            if update_method is not None:

                update_method(dt)

    
    # DEBUG INTERACTIVE OBJECTS
    

    def draw_interactive_debug(
        self,
        screen,
        camera_x=0,
        camera_y=0,
    ):

        for obj in self.interactive_objects:

            draw_method = getattr(
                obj,
                "draw_debug",
                None,
            )

            if draw_method is not None:

                draw_method(
                    screen,
                    camera_x,
                    camera_y,
                )

    
    # RENDER
    

    def render(
        self,
        screen,
        camera_x=0,
        camera_y=0,
    ):

        
        # Tile layers
        

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

        
        # Image layers
        

        for layer in self.image_layers:

            layer.draw(
                screen,
                camera_x,
                camera_y,
            )