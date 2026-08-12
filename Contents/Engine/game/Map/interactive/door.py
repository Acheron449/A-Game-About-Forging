import pygame as pg


class Door:

    def __init__(
        self,
        rect,
        target_map,
        target_x=0,
        target_y=0,
        name="Door",
    ):

        self.rect = pg.Rect(rect)

        self.class_name = "door"
        self.name = name

        self.target_map = target_map
        self.target_x = target_x
        self.target_y = target_y

    # --------------------------------------------------
    # INTERACTION
    # --------------------------------------------------

    def can_interact(self, player_rect):

        return self.rect.colliderect(player_rect)

    def interact(self, play_state):

        map_manager = play_state["map_manager"]

        map_manager.load_map(
            self.target_map,
            spawn_position=(
                self.target_x,
                self.target_y,
            ),
        )

        spawn_x, spawn_y = (
            map_manager.spawn_position
        )

        play_state["player_rect"].topleft = (
            spawn_x,
            spawn_y,
        )

        print(
            f"Entered {self.target_map}"
        )