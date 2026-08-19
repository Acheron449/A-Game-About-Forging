 # Represent a map door and the collision or transition behavior it controls.
import pygame as pg


class Door:

    def __init__(
        self,
        rect,
        target_map,
        spawn_id ="default",
        name="Door",
    ):

        self.rect = pg.Rect(rect)

        self.class_name = "door"
        self.name = name

        self.target_map = target_map
        self.spawn_id = spawn_id


    # --------------------------------------------------
    # INTERACTION
    # --------------------------------------------------

    def can_interact(self, player_rect):

        return self.rect.colliderect(player_rect)

    def interact(self, play_state):

        map_manager = play_state["map_manager"]
        # updated to load based on Tiled file information and the requested spawn point from tiled.
        
        ##DEBUG :(
        print()
        print("========== DOOR DEBUG ==========")
        print("Door:", self.name)
        print("Target map:", repr(self.target_map))
        print("Spawn ID:", repr(self.spawn_id))
        print("================================")



        map_manager.load_map(
            self.target_map,
            spawn_id=self.spawn_id,
        )
        # move player to the spawn point
        spawn_x, spawn_y = map_manager.spawn_position

        play_state["player_rect"].topleft = (
            spawn_x,
            spawn_y,
        )

        print(
            f"Entered {self.target_map}"
            f"at spawn '{self.spawn_id}'"
        )