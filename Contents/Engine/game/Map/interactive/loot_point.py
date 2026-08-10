"""Interactive loot point object for the game map. interactable with key E, opens a menu and allows the player to pick up loot from the loot point."""

"""
Interactive loot point system.

A LootPoint is created from a Tiled object with the class:

    loot_point

The loot point has its own inventory and can be opened by
the player when they are within interaction range.
"""

import pygame as pg


# ============================================================
# LOOT ITEM
# ============================================================

class LootItem:
    """
    Represents one item inside a loot point.

    Parameters
    ----------
    item_id:
        Unique identifier for the item.

    name:
        Display name.

    quantity:
        Number of copies of the item.

    max_stack:
        Maximum number of this item that can occupy one slot.
    """

    def __init__(
        self,
        item_id,
        name,
        quantity=1,
        max_stack=99,
    ):
        self.item_id = item_id
        self.name = name
        self.quantity = quantity
        self.max_stack = max_stack

    def copy(self):
        """Return a copy of the item."""

        return LootItem(
            item_id=self.item_id,
            name=self.name,
            quantity=self.quantity,
            max_stack=self.max_stack,
        )


# ============================================================
# LOOT POINT
# ============================================================

class LootPoint:
    """
    Represents a loot container placed in a Tiled map.

    Each LootPoint owns its own inventory.
    """

    def __init__(self, tmx_object):

        # ----------------------------------------------------
        # TMX INFORMATION
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # TMX PROPERTIES
        # ----------------------------------------------------

        properties = getattr(
            tmx_object,
            "properties",
            {},
        ) or {}

        # Number of inventory slots.
        self.capacity = int(
            properties.get(
                "capacity",
                6,
            )
        )

        # Distance at which the interaction prompt appears.
        self.interaction_distance = int(
            properties.get(
                "interaction_distance",
                40,
            )
        )

        # ----------------------------------------------------
        # INVENTORY
        # ----------------------------------------------------

        self.inventory = []

        # ----------------------------------------------------
        # INITIAL LOOT
        # ----------------------------------------------------

        self._load_initial_loot(properties)

    # ========================================================
    # INITIAL LOOT
    # ========================================================

    def _load_initial_loot(self, properties):
        """
        Load initial loot from Tiled properties.

        This expects properties such as:

            item_1_id = potion
            item_1_name = Health Potion
            item_1_quantity = 3

            item_2_id = iron
            item_2_name = Iron Ore
            item_2_quantity = 5
        """

        for index in range(1, self.capacity + 1):

            item_id = properties.get(
                f"item_{index}_id"
            )

            item_name = properties.get(
                f"item_{index}_name"
            )

            quantity = properties.get(
                f"item_{index}_quantity"
            )

            if (
                item_id is None
                or item_name is None
                or quantity is None
            ):
                continue

            try:
                quantity = int(quantity)
            except (TypeError, ValueError):
                continue

            if quantity <= 0:
                continue

            self.add_item(
                LootItem(
                    item_id=item_id,
                    name=item_name,
                    quantity=quantity,
                )
            )

    # ========================================================
    # COORDINATES
    # ========================================================

    def get_coordinates(self):
        """Return the loot point's world coordinates."""

        return self.coordinates

    # ========================================================
    # PROXIMITY
    # ========================================================

    def is_near(self, player_rect):
        """
        Determine whether the player is close enough
        to display the interaction prompt.
        """

        interaction_rect = self.rect.inflate(
            self.interaction_distance * 2,
            self.interaction_distance * 2,
        )

        return player_rect.colliderect(
            interaction_rect
        )

    # ========================================================
    # INTERACTION
    # ========================================================

    def can_interact(self, player_rect):
        """
        Determine whether the player is inside the
        actual loot point interaction area.
        """

        return player_rect.colliderect(
            self.rect
        )

    # ========================================================
    # INVENTORY
    # ========================================================

    def is_full(self):
        """Return True if all inventory slots are occupied."""

        return len(self.inventory) >= self.capacity

    def add_item(self, item):
        """
        Add an item to the loot point.

        Returns True if the item was added.
        """

        # ---------------------------------------------
        # Try to stack with an existing item
        # ---------------------------------------------

        for existing_item in self.inventory:

            if (
                existing_item.item_id
                == item.item_id
            ):

                available_space = (
                    existing_item.max_stack
                    - existing_item.quantity
                )

                if available_space <= 0:
                    continue

                amount_to_add = min(
                    item.quantity,
                    available_space,
                )

                existing_item.quantity += (
                    amount_to_add
                )

                item.quantity -= amount_to_add

                if item.quantity <= 0:
                    return True

        # ---------------------------------------------
        # Add as a new inventory slot
        # ---------------------------------------------

        if item.quantity > 0:

            if self.is_full():
                return False

            self.inventory.append(
                item
            )

            return True

        return True

    def remove_item(self, index):
        """
        Remove and return an item from an inventory slot.
        """

        if index < 0:
            return None

        if index >= len(self.inventory):
            return None

        return self.inventory.pop(index)

    # ========================================================
    # TRANSFER
    # ========================================================

    def transfer_item_to_player(
        self,
        index,
        player_inventory,
    ):
        """
        Transfer one inventory slot from this loot point
        into the player's inventory.

        The player inventory must provide:

            add_item(item)

        returning True if the item was successfully added.
        """

        if index < 0:
            return False

        if index >= len(self.inventory):
            return False

        item = self.inventory[index]

        # Make a copy so the loot inventory isn't
        # accidentally modified if the player's inventory
        # rejects the item.
        item_to_transfer = item.copy()

        success = player_inventory.add_item(
            item_to_transfer
        )

        if not success:
            return False

        self.inventory.pop(index)

        return True

    # ========================================================
    # DEBUG
    # ========================================================

    def draw_debug(
        self,
        screen,
        camera_x=0,
        camera_y=0,
    ):
        """Draw the loot point's interaction rectangle."""

        debug_rect = self.rect.move(
            -camera_x,
            -camera_y,
        )

        pg.draw.rect(
            screen,
            (255, 215, 0),
            debug_rect,
            2,
        )


# ============================================================
# LOOT WINDOW
# ============================================================

class LootWindow:
    """
    Graphical interface for a LootPoint.

    Displays the loot point's inventory and allows
    the player to transfer items to their inventory.
    """

    def __init__(
        self,
        loot_point,
        player_inventory,
        screen_size,
    ):

        self.loot_point = loot_point
        self.player_inventory = player_inventory

        self.screen_width, self.screen_height = (
            screen_size
        )

        self.is_open = False

        # ----------------------------------------------------
        # UI
        # ----------------------------------------------------

        self.width = 700
        self.height = 450

        self.rect = pg.Rect(
            0,
            0,
            self.width,
            self.height,
        )

        self.rect.center = (
            self.screen_width // 2,
            self.screen_height // 2,
        )

        self.font = pg.font.Font(
            None,
            24,
        )

        self.small_font = pg.font.Font(
            None,
            18,
        )

        # Number of columns in each inventory.
        self.columns = 4

        self.slot_size = 70
        self.slot_gap = 10

    # ========================================================
    # OPEN / CLOSE
    # ========================================================

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False

    def toggle(self):
        self.is_open = not self.is_open

    # ========================================================
    # EVENTS
    # ========================================================

    def handle_event(self, event):

        if not self.is_open:
            return

        # ---------------------------------------------
        # Close with Escape
        # ---------------------------------------------

        if (
            event.type == pg.KEYDOWN
            and event.key == pg.K_ESCAPE
        ):
            self.close()
            return

        # ---------------------------------------------
        # Mouse click
        # ---------------------------------------------

        if (
            event.type == pg.MOUSEBUTTONDOWN
            and event.button == 1
        ):

            self.handle_click(
                event.pos
            )

    # ========================================================
    # CLICK
    # ========================================================

    def handle_click(self, mouse_position):

        loot_start_x = (
            self.rect.x
            + 40
        )

        loot_start_y = (
            self.rect.y
            + 80
        )

        for index in range(
            len(self.loot_point.inventory)
        ):

            row = index // self.columns
            column = index % self.columns

            slot_x = (
                loot_start_x
                + column
                * (
                    self.slot_size
                    + self.slot_gap
                )
            )

            slot_y = (
                loot_start_y
                + row
                * (
                    self.slot_size
                    + self.slot_gap
                )
            )

            slot_rect = pg.Rect(
                slot_x,
                slot_y,
                self.slot_size,
                self.slot_size,
            )

            if slot_rect.collidepoint(
                mouse_position
            ):

                self.loot_point.transfer_item_to_player(
                    index,
                    self.player_inventory,
                )

                return

    # ========================================================
    # DRAW
    # ========================================================

    def draw(self, screen):

        if not self.is_open:
            return

        # ----------------------------------------------------
        # WINDOW
        # ----------------------------------------------------

        pg.draw.rect(
            screen,
            (25, 25, 25),
            self.rect,
        )

        pg.draw.rect(
            screen,
            (180, 180, 180),
            self.rect,
            2,
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = self.font.render(
            "Loot",
            True,
            (255, 255, 255),
        )

        screen.blit(
            title,
            (
                self.rect.x + 40,
                self.rect.y + 25,
            ),
        )

        # ----------------------------------------------------
        # CAPACITY
        # ----------------------------------------------------

        capacity_text = self.small_font.render(
            f"{len(self.loot_point.inventory)}"
            f"/"
            f"{self.loot_point.capacity}",
            True,
            (200, 200, 200),
        )

        screen.blit(
            capacity_text,
            (
                self.rect.right - 70,
                self.rect.y + 30,
            ),
        )

        # ----------------------------------------------------
        # LOOT SLOTS
        # ----------------------------------------------------

        start_x = (
            self.rect.x + 40
        )

        start_y = (
            self.rect.y + 80
        )

        for index in range(
            self.loot_point.capacity
        ):

            row = index // self.columns
            column = index % self.columns

            x = (
                start_x
                + column
                * (
                    self.slot_size
                    + self.slot_gap
                )
            )

            y = (
                start_y
                + row
                * (
                    self.slot_size
                    + self.slot_gap
                )
            )

            slot_rect = pg.Rect(
                x,
                y,
                self.slot_size,
                self.slot_size,
            )

            pg.draw.rect(
                screen,
                (45, 45, 45),
                slot_rect,
            )

            pg.draw.rect(
                screen,
                (100, 100, 100),
                slot_rect,
                2,
            )

            # -----------------------------------------
            # ITEM
            # -----------------------------------------

            if index < len(
                self.loot_point.inventory
            ):

                item = (
                    self.loot_point
                    .inventory[index]
                )

                item_text = self.small_font.render(
                    item.name,
                    True,
                    (255, 255, 255),
                )

                screen.blit(
                    item_text,
                    (
                        x + 5,
                        y + 5,
                    ),
                )

                quantity_text = (
                    self.small_font.render(
                        str(item.quantity),
                        True,
                        (255, 255, 255),
                    )
                )

                screen.blit(
                    quantity_text,
                    (
                        x + 50,
                        y + 45,
                    ),
                )

        # ----------------------------------------------------
        # INSTRUCTIONS
        # ----------------------------------------------------

        instruction = self.small_font.render(
            "Click an item to transfer it",
            True,
            (180, 180, 180),
        )

        screen.blit(
            instruction,
            (
                self.rect.x + 40,
                self.rect.bottom - 40,
            ),
        )