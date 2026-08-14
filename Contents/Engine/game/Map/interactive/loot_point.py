import pygame as pg


class LootPoint:

    def __init__(
        self,
        rect,
        name="Loot",
        capacity=10,
    ):

        self.rect = pg.Rect(rect)

        self.class_name = "loot_point"
        self.name = name

        self.capacity = capacity

        # Each loot point gets its OWN inventory
        self.inventory = []

        self.is_open = False

    # --------------------------------------------------
    # INTERACTION
    # --------------------------------------------------

    def can_interact(self, player_rect):

        return self.rect.colliderect(player_rect)

    def interact(self, play_state):

        self.is_open = not self.is_open

        if self.is_open:

            print(
                f"Opened loot point: {self.name}"
            )

            # Eventually:
            #
            # play_state["loot_screen"].open(self)

        else:

            print(
                f"Closed loot point: {self.name}"
            )

    # --------------------------------------------------
    # INVENTORY
    # --------------------------------------------------

    def add_item(self, item):

        if len(self.inventory) >= self.capacity:
            return False

        self.inventory.append(item)

        return True

    def remove_item(self, index):

        if 0 <= index < len(self.inventory):

            return self.inventory.pop(index)

        return None