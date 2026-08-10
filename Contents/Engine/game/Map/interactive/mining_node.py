"""
Interactive mining node system.

Tiled objects should use the class:

    mining_node

The player can interact with a mining node by pressing E while
their player rectangle is inside the node's rectangle.
"""

import pygame as pg


class MiningNode:
    """
    A resource node placed in a Tiled map.

    Each mining node has its own:
        - position
        - interaction rectangle
        - resource type
        - resource quantity
        - mining amount
        - depleted state
    """

    def __init__(self, tmx_object):

        # ====================================================
        # TMX OBJECT DATA
        # ====================================================

        self.object_id = tmx_object.id

        self.name = getattr(
            tmx_object,
            "name",
            "",
        )

        self.rect = pg.Rect(
            int(tmx_object.x),
            int(tmx_object.y),
            int(tmx_object.width),
            int(tmx_object.height),
        )

        self.coordinates = (
            self.rect.x,
            self.rect.y,
        )

        # ====================================================
        # TMX PROPERTIES
        # ====================================================

        properties = getattr(
            tmx_object,
            "properties",
            {},
        ) or {}

        # Item/resource produced by this node.
        self.resource_id = properties.get(
            "resource_id",
            "iron_ore",
        )

        self.resource_name = properties.get(
            "resource_name",
            "Iron Ore",
        )

        # Amount initially available.
        self.resource_quantity = int(
            properties.get(
                "resource_quantity",
                5,
            )
        )

        # Amount obtained each time E is pressed.
        self.mining_amount = int(
            properties.get(
                "mining_amount",
                1,
            )
        )

        # ====================================================
        # STATE
        # ====================================================

        self.depleted = (
            self.resource_quantity <= 0
        )

    # ========================================================
    # COORDINATES
    # ========================================================

    def get_coordinates(self):
        return self.coordinates

    # ========================================================
    # PLAYER INTERACTION
    # ========================================================

    def player_is_inside(self, player_rect):
        """
        Returns True when the player's rectangle overlaps
        the mining node's rectangle.
        """

        return player_rect.colliderect(
            self.rect
        )

    def can_mine(self, player_rect):
        """
        Determines whether the player can currently
        interact with this mining node.
        """

        if self.depleted:
            return False

        return self.player_is_inside(
            player_rect
        )

    # ========================================================
    # MINING
    # ========================================================

    def mine(self):
        """
        Mine the node.

        Returns a dictionary describing the resource
        obtained, or None if the node is depleted.
        """

        if self.depleted:
            return None

        amount = min(
            self.mining_amount,
            self.resource_quantity,
        )

        self.resource_quantity -= amount

        if self.resource_quantity <= 0:
            self.resource_quantity = 0
            self.depleted = True

        return {
            "item_id": self.resource_id,
            "item_name": self.resource_name,
            "quantity": amount,
        }

    # ========================================================
    # DEBUG
    # ========================================================

    def draw_debug(
        self,
        screen,
        camera_x=0,
        camera_y=0,
    ):
        """
        Draw the mining node's interaction rectangle.
        """

        debug_rect = self.rect.move(
            -camera_x,
            -camera_y,
        )

        if self.depleted:
            color = (100, 100, 100)
        else:
            color = (0, 200, 255)

        pg.draw.rect(
            screen,
            color,
            debug_rect,
            2,
        )