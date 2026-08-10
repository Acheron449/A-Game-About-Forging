"""
Interactive door object loaded from a Tiled TMX map.
"""

import pygame as pg


class InteractiveDoor:
    """
    Represents an interactive door defined as a Tiled object
    with the class name 'door'.
    """

    def __init__(self, tmx_object):
        # --------------------------------------------------
        # BASIC TMX INFORMATION
        # --------------------------------------------------

        self.object_id = tmx_object.id
        self.name = getattr(tmx_object, "name", "")

        # The rectangle assigned to the door in Tiled.
        self.rect = pg.Rect(
            int(tmx_object.x),
            int(tmx_object.y),
            int(tmx_object.width),
            int(tmx_object.height),
        )

        # Store the door's coordinates.
        self.coordinates = (
            self.rect.x,
            self.rect.y,
        )

        # --------------------------------------------------
        # TMX CUSTOM PROPERTIES
        # --------------------------------------------------

        properties = getattr(
            tmx_object,
            "properties",
            {}
        ) or {}

        self.destination_map = properties.get(
            "destination_map"
        )

        self.destination_x = properties.get(
            "destination_x"
        )

        self.destination_y = properties.get(
            "destination_y"
        )

        # --------------------------------------------------
        # INTERACTION SETTINGS
        # --------------------------------------------------

        # Distance around the door at which the
        # "E  door" prompt becomes visible.
        self.interaction_distance = 40

    # ======================================================
    # COORDINATES
    # ======================================================

    def get_coordinates(self):
        """Return the door's top-left world coordinates."""

        return self.coordinates

    # ======================================================
    # PROXIMITY
    # ======================================================

    def is_near(self, player_rect):
        """
        Return True when the player is close enough
        to the door for the interaction prompt.
        """

        interaction_rect = self.rect.inflate(
            self.interaction_distance * 2,
            self.interaction_distance * 2,
        )

        return player_rect.colliderect(
            interaction_rect
        )

    # ======================================================
    # INTERACTION
    # ======================================================

    def can_interact(self, player_rect):
        """
        Return True only when the player's collision
        rectangle overlaps the actual door area.
        """

        return player_rect.colliderect(
            self.rect
        )

    # ======================================================
    # DESTINATION
    # ======================================================

    def get_destination(self):
        """
        Return the map and spawn position associated
        with this door.

        Returns None if the door has not been configured
        correctly in Tiled.
        """

        if self.destination_map is None:
            return None

        if self.destination_x is None:
            return None

        if self.destination_y is None:
            return None

        return {
            "map": self.destination_map,
            "position": (
                int(self.destination_x),
                int(self.destination_y),
            ),
        }

    # ======================================================
    # INTERACT
    # ======================================================

    def interact(self, player_rect):
        """
        Attempt to interact with the door.

        Returns the destination information if the player
        is inside the door area.

        Returns None otherwise.
        """

        if not self.can_interact(player_rect):
            return None

        return self.get_destination()

    # ======================================================
    # DEBUG
    # ======================================================

    def draw_debug(
        self,
        screen,
        camera_x=0,
        camera_y=0,
    ):
        """
        Draw the door's interaction rectangle for debugging.
        """

        debug_rect = self.rect.move(
            -camera_x,
            -camera_y,
        )

        pg.draw.rect(
            screen,
            (0, 255, 255),
            debug_rect,
            2,
        )