"""Handles player attack input, attack cooldowns, attack animations, and equipped weapon behaviour."""

 # Implement player attack timing, hit detection, and weapon behavior.
from ...configuration.imports import pg
from .movement_controller import PlayerController


class CharacterAttack:

    def __init__(self, player_controller: PlayerController):
        self.player_controller = player_controller

        self.is_attacking = False
        self.current_frame_index = 0

        self.attack_cooldown = 500  # milliseconds
        self.last_attack_time = 0

        # Animation settings
        self.animation_speed = 100  # milliseconds per frame
        self.last_animation_time = 0


    # EQUIPMENT


    def get_equipped_weapon(self):
        """
        Returns the currently equipped weapon
        if current_time - self.last_attack_time < self.attack_cooldown:
        Returns None if nothing is equipped.
        """

        #equipment_manager = self.player_controller.equipment_manager - commented out because it was unused and causing confusion

        equipment = self.player_controller.equipment_manager

        if equipment is None:
            return None

        return equipment.get_equipped_item()

    # ATTACK

    def start_attack(self):

        weapon = self.get_equipped_weapon()

        if weapon is None:
            return

        print(f"Attacking with {weapon.name}")

        self.start_animation(weapon)



    # USE TOOL

    def use_tool(self, tool_type):

        equipment = self.player_controller.equipment_manager

        tool = equipment.get_tool(tool_type)

        if tool is None:
            print(f"Player needs a {tool_type}")
            return False

        print(f"Using {tool.name}")

        self.start_animation(tool)

        return True

    # ANIMATION

    def start_animation(self, item):

        frames = getattr(item, "attack_animation_frames", [])

        if not frames:
            return

        current_time = pg.time.get_ticks()

        self.is_attacking = True
        self.current_frame_index = 0
        self.last_attack_time = current_time
        self.last_animation_time = current_time


    # UPDATE


    def update(self):

        if not self.is_attacking:
            return

        current_time = pg.time.get_ticks()

        weapon = self.get_equipped_weapon()

        if weapon is None:
            self.is_attacking = False
            return

        # Get animation frames from equipped item
        frames = getattr(weapon, "attack_animation_frames", [])

        if not frames:
            self.is_attacking = False
            return

        # Advance animation
        if current_time - self.last_animation_time >= self.animation_speed:

            self.current_frame_index += 1
            self.last_animation_time = current_time

            # Animation finished
            if self.current_frame_index >= len(frames):
                self.current_frame_index = 0
                self.is_attacking = False


    # CURRENT FRAME


    def get_current_frame(self):

        if not self.is_attacking:
            return None

        item = self.get_equipped_item()

        if item is None:
            return None

        frames = getattr(item, "attack_animation_frames", [])

        if not frames:
            return None

        if self.current_frame_index >= len(frames):
            return None

        return frames[self.current_frame_index]

class Pickaxe:

    name = "Pickaxe"
    item_type = "pickaxe"
    damage = 10

    def __init__(self, attack_animation_frames):
        self.attack_animation_frames = attack_animation_frames

class Guitar:

    name = "Guitar"
    item_type = "guitar"
    damage = 8

    def __init__(self, attack_animation_frames):
        self.attack_animation_frames = attack_animation_frames

class Gauntlets:

    name = "Gauntlets"
    item_type = "gauntlets"
    damage = 15

    def __init__(self, attack_animation_frames):
        self.attack_animation_frames = attack_animation_frames


    

