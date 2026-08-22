 # Load and draw player sprites, equipment, bars, and related UI elements.
import os 
import json
import pygame

from ..configuration.constants import *
from ..configuration.imports import *
from .userStatusUi import UserStatusUI

class PlayerRenderer:
# moved player rendering to this file
        # Initialize map-specific variables here
        pass

class PlayerRenderer:
    """Handles loading and rendering directional player sprites."""
    
    def __init__(self, player):
        self.player = player
        self.player_resources_dir = config.PLAYER_RESOURCES_DIR

        self.action = None
        self.action_frame = 0
        self.action_finished = False

        
        self.facing_direction = config.PLAYER_DEFAULT_FACING
        self.current_state = config.PLAYER_DEFAULT_STATE
        self.animation_frame = 0
        self.animation_counter = 0
        self.animation_speed = config.ANIMATION_SPEED_WALK
        self.idle_animation_speed = config.IDLE_ANIMATION_SPEED
        self.sprite_scale = config.SPRITE_SCALE
        self.min_hold_time = config.MOVEMENT_MIN_HOLD_MS
        self.movement_press_start = None
        
        # Load sprite sheets
        self.idle_sprites = self._load_idle_sprites()
        self.movement_sprites = self._load_movement_sprites()
        self.weapon_action_sprites = self._load_weapon_action_sprites()
        self.mining_sprites = self._load_mining_sprites()

        print("[DEBUG] MINING SPRITES:", [x[0]for x in self.mining_sprites])

        self.current_sprite = None
        self.sprites_list = []
        
        # Set current sprite to idle 'S'
        idle_s_key = config.PLAYER_IDLE_FALLBACK_KEY
        if idle_s_key in self.idle_sprites and self.idle_sprites[idle_s_key]:
            self.current_sprite = self.idle_sprites[idle_s_key][0][1]  # First frame
 

    def _axis_held(self, axis_scancodes_held, axis):
        return bool(axis_scancodes_held[axis])

    def _any_movement_held(self, axis_scancodes_held):
        return any(axis_scancodes_held[ax] for ax in config.KEYBINDS)

    def start_action(self, action):

        if self.action is not None:
            return False

        # Mining uses its own animation list.
        # Direction is completely ignored.
        if action == "mine":
            sprites = self.mining_sprites
        else:
            sprites = self.get_sprite(
                action,
                self.facing_direction
            )

        if not sprites:
            print(
                f"[PlayerRenderer] No animation found for action '{action}'"
            )
            return False

        self.action = action
        self.action_frame = 0
        self.animation_counter = 0
        self.action_finished = False

        self.current_sprite = sprites[0][1]

        print(
            f"[PlayerRenderer] Started '{action}' "
            f"with {len(sprites)} frames"
        )

        return True

    
    def _load_idle_sprites(self):
        """Load idle sprites for all directions from Player/Idle folders.""" #TEST - Updated to load from all subfolders in Idle, not just 'Test - Static'
        idle_sprites = {}
        idle_paths = config.PLAYER_IDLE_SUBDIRS
        
        direction_keys = config.PLAYER_DIRECTION_KEYS
        for idle_type in idle_paths:
            idle_dir = os.path.join(self.player_resources_dir, "Idle", idle_type)
            if not os.path.isdir(idle_dir):
                continue
                
            for key in direction_keys:
                sprite_key = f'idle_{key}'
                loaded_images = self._load_direction_images(idle_dir, key) # Load sprites for this direction, e.g. 'idle_W' for walking north, 'idle_A' for walking west, etc.
                if loaded_images:
                    idle_sprites.setdefault(sprite_key, []).extend(loaded_images)
        
        return idle_sprites
    
    def _load_movement_sprites(self):
        """Load movement sprites for all directions from Player/Movement folders."""
        # The 'walk' state uses the Mc - Walk directory for animation sequences.
        movement_sprites = {}
        
        # --- Load Walk Animation Sequence (The requested feature) ---
        walk_dir = os.path.join(self.player_resources_dir, "Movement", "Mc - Walk")
        if os.path.isdir(walk_dir):
            direction_keys = config.PLAYER_DIRECTION_KEYS
            for dir_key in direction_keys:
                sprite_key = f'walk_{dir_key}'
                movement_sprites[sprite_key] = self._load_direction_images(walk_dir, dir_key)
        # --- End of Walk Sequence Loading ---

        # Load other states (run, dash, etc.) using the generic map for backward compatibility/future use
        movement_directories = config.PLAYER_MOVEMENT_DIRECTORY_MAP
        for state, move_type in movement_directories.items():
            if state == 'walk':
                continue # Already handled above
            
            move_dir = os.path.join(self.player_resources_dir, "Movement", move_type)
            if not os.path.isdir(move_dir):
                continue
            
            direction_keys = config.PLAYER_DIRECTION_KEYS
            for dir_key in direction_keys:
                sprite_key = f'{state}_{dir_key}'
                movement_sprites[sprite_key] = self._load_direction_images(move_dir, dir_key)
        
        return movement_sprites
    
    def _load_weapon_action_sprites(self):
        """Load weapon-specific action sprites from Player/Movement/Attack... folders."""
        weapon_sprites = {}
        action_map = getattr(config, 'PLAYER_WEAPON_ANIMATION_FOLDERS', {})
        direction_keys = config.PLAYER_DIRECTION_KEYS

        for weapon_type, actions in action_map.items():
            weapon_sprites[weapon_type] = {}
            for action_name, folder_name in actions.items():
                action_dir = os.path.join(self.player_resources_dir, 'Movement', folder_name)
                if not os.path.isdir(action_dir):
                    continue
                weapon_sprites[weapon_type][action_name] = {}
                for direction_key in direction_keys:
                    weapon_sprites[weapon_type][action_name][direction_key] = self._load_direction_images(action_dir, direction_key)
        return weapon_sprites

    def _load_mining_sprites(self):
        """Load pickaxe mining animation frames in numerical order.

        Direction is deliberately ignored.
        """

        mining_dir = os.path.join(
            self.player_resources_dir,
            "Movement",
            "Attack - Pickaxe"
        )

        if not os.path.isdir(mining_dir):
            print(
                f"[PlayerRenderer] Mining folder not found: "
                f"{mining_dir}"
            )
            return []

        frames = []

        for filename in os.listdir(mining_dir):

            if not filename.lower().endswith(
                (".png", ".jpg", ".jpeg")
            ):
                continue

            image_path = os.path.join(
                mining_dir,
                filename
            )

            try:
                image = pygame.image.load(
                    image_path
                ).convert_alpha()

                if self.sprite_scale != 1.0:
                    image = pygame.transform.rotozoom(
                        image,
                        0,
                        self.sprite_scale
                    )

                frames.append((filename, image))

            except Exception as e:
                print(
                    f"[PlayerRenderer] Failed to load "
                    f"mining frame {filename}: {e}"
                )

        # Sort using the number in the filename.
        def frame_number(frame):
            filename = frame[0]
            name = os.path.splitext(filename)[0]

            numbers = [
                int(part)
                for part in name.replace("-", "_").split("_")
                if part.isdigit()
            ]

            return numbers[-1] if numbers else 0

        frames.sort(key=frame_number)

        print(
            "[PlayerRenderer] Loaded mining frames:",
            [frame[0] for frame in frames]
        )

        return frames

    def _load_direction_images(self, base_dir, direction_key):
        """Load animation frames for a direction.

        If the requested direction does not exist, use D as the source
        and horizontally flip it for A.
        """

        images = []
        direction_key = direction_key.upper()

        # ---------------------------------------------------------
        # A = horizontally flipped version of D
        # ---------------------------------------------------------
        source_direction = "D" if direction_key == "A" else direction_key

        candidate_dir = os.path.join(base_dir, source_direction)

        # If a direction subfolder exists, use it.
        # Otherwise search the base folder.
        if os.path.isdir(candidate_dir):
            search_dir = candidate_dir
        else:
            search_dir = base_dir

        if not os.path.isdir(search_dir):
            return []

        files = []

        for filename in sorted(os.listdir(search_dir)):
            if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
                continue

            name_base = os.path.splitext(filename)[0].upper()

            # -----------------------------------------------------
            # If using a direction-specific folder, accept frames
            # in that folder without requiring the filename to end
            # in the direction.
            # -----------------------------------------------------
            if os.path.isdir(candidate_dir):
                files.append(filename)

            else:
                # Otherwise only accept files belonging to source D.
                parts = name_base.split("_")

                # Remove frame number
                if parts and parts[-1].isdigit():
                    parts = parts[:-1]

                suffix = "".join(parts)

                if suffix == source_direction:
                    files.append(filename)

        # ---------------------------------------------------------
        # Load the frames
        # ---------------------------------------------------------
        for filename in files:

            image_path = os.path.join(search_dir, filename)

            try:
                image = pygame.image.load(image_path)

                if pygame.display.get_surface() is not None:
                    image = image.convert_alpha()

                # -------------------------------------------------
                # Flip D -> A
                # -------------------------------------------------
                if direction_key == "A":
                    image = pygame.transform.flip(
                        image,
                        True,   # horizontal
                        False   # vertical
                    )

                # -------------------------------------------------
                # Scale
                # -------------------------------------------------
                if self.sprite_scale != 1.0:
                    image = pygame.transform.rotozoom(
                        image,
                        0,
                        self.sprite_scale
                    )

                images.append((filename, image))

            except Exception as e:
                print(
                    f"[PlayerRenderer] Failed to load "
                    f"{filename}: {e}"
                )

        return images


    def get_current_direction(self, axis_scancodes_held): # Determine player facing direction based on pressed keys.
        """Determine player facing direction based on pressed keys."""
        up = self._axis_held(axis_scancodes_held, 'up')
        down = self._axis_held(axis_scancodes_held, 'down')
        left = self._axis_held(axis_scancodes_held, 'left')
        right = self._axis_held(axis_scancodes_held, 'right')

        direction = self.facing_direction
        if up and left and not down and not right: # Diagonal up-left
            direction = 'AW'
        elif up and right and not down and not left: # Diagonal up-right
            direction = 'WD'
        elif down and left and not up and not right: # Diagonal down-left
            direction = 'AS'
        elif down and right and not up and not left: # Diagonal down-right
            direction = 'SD'
        elif up and not down: # Up takes priority over down if both are pressed
            direction = 'W'
        elif down and not up: # Down takes priority over up if both are pressed
            direction = 'S'
        elif left and not right: # Left takes priority over right if both are pressed
            direction = 'A'
        elif right and not left: # Right takes priority over left if both are pressed
            direction = 'D'

        self.facing_direction = direction # Set the facing direction.
        return self.facing_direction # Return the facing direction.
    
    def is_key_pressed(self, axis_scancodes_held): # Check if any movement key is being pressed.
        """Check if any movement key is being pressed."""
        return self._any_movement_held(axis_scancodes_held) # Return True if any movement key is being pressed, False otherwise.
    
    def get_current_state(self, axis_scancodes_held, keys_pressed): # Determine player movement state based on pressed keys.
        """Determine player movement state based on pressed keys."""
        up = self._axis_held(axis_scancodes_held, 'up')
        down = self._axis_held(axis_scancodes_held, 'down')
        left = self._axis_held(axis_scancodes_held, 'left')
        right = self._axis_held(axis_scancodes_held, 'right')

        if not (up or down or left or right):
            return 'idle' # Return 'idle' if no movement keys are being pressed.
        
        # Check for shift key (sprint)
        if keys_pressed[pygame.K_LSHIFT] or keys_pressed[pygame.K_RSHIFT]:
            return 'sprint' # Return 'sprint' if the shift key is being pressed.
        
        # Default to walk if moving
        return 'walk'
    

    def get_sprite(self, state, direction):

        sprite_key = f'{state}_{direction}'
        idle_key = f'idle_{direction}'

        # IDLE
        if state == 'idle':
            sprites = self.idle_sprites.get(idle_key, [])

            if sprites:
                return sprites

            return self.idle_sprites.get(
                config.PLAYER_IDLE_FALLBACK_KEY,
                []
            )

        # EQUIPPED WEAPON
        weapon_type = None

        if hasattr(self.player, 'equipped_weapon_type'):
            value = getattr(
                self.player,
                'equipped_weapon_type'
            )

            weapon_type = value() if callable(value) else value

        # NORMAL WEAPON ACTIONS
        if weapon_type and state in {
            'attack',
            'block',
            'parry',
        }:

            action_sprites = self.get_weapon_action_sprites(
                weapon_type,
                state,
                direction
            )

            if action_sprites:
                return action_sprites

        # MINING

        if state == 'mine':

            if self.mining_sprites:
                return self.mining_sprites

            print(
                "[PlayerRenderer] No pickaxe mining animation found."
            )

            return []

        # NORMAL MOVEMENT
        sprites = self.movement_sprites.get(sprite_key, [])

        if sprites:
            return sprites

        # WALK FALLBACK
        if state != 'walk':
            sprites = self.movement_sprites.get(
                f'walk_{direction}',
                []
            )

            if sprites:
                return sprites

        # IDLE FALLBACK
        return self.idle_sprites.get(idle_key, [])

    
    def update_action(self):

        if self.action is None:
            return False

        # Mining ignores direction.
        if self.action == "mine":
            sprites = self.mining_sprites
        else:
            sprites = self.get_sprite(
                self.action,
                self.facing_direction
            )

        if not sprites:
            self.action = None
            return False

        self.animation_counter += 1

        if self.animation_counter >= self.animation_speed:

            self.animation_counter = 0
            self.action_frame += 1

            if self.action_frame >= len(sprites):

                self.action = None
                self.action_frame = 0
                self.action_finished = True

                return True

        self.current_sprite = sprites[
            self.action_frame
        ][1]

        return False

    def update_animation(self, state, direction, axis_scancodes_held, previous_state=None, previous_direction=None):
        """Update the current animation frame for the given state and direction."""
        sprites = self.get_sprite(state, direction) # Get the sprites for this state and direction.
        
        if not sprites:
            self.current_sprite = None # Set the current sprite to None if no sprites are found.
            return # Return if no sprites are found.
        
        if previous_state is None:
            previous_state = self.current_state
        if previous_direction is None:
            previous_direction = self.facing_direction

        # Reset animation when state or direction changes
        if state != previous_state or direction != previous_direction:
            self.animation_frame = 0
            self.animation_counter = 0
        
        if state == 'idle':
            # Multi-frame idle: loop (last facing from update(); direction matches movement diagonals AW, WD, AS, SD)
            if len(sprites) > 1:
                self.animation_counter += 1 # Increment the animation counter.
                if self.animation_counter >= self.idle_animation_speed:
                    self.animation_counter = 0
                    self.animation_frame = (self.animation_frame + 1) % len(sprites) # Increment the animation frame.
            else:
                self.animation_frame = 0 # Set the animation frame to 0.
                self.animation_counter = 0 # Set the animation counter to 0.
            self.current_sprite = sprites[self.animation_frame][1]
        else:
            # Advance frames for all non-idle states, including weapon actions.
            advance_frames = self.is_key_pressed(axis_scancodes_held) or state in {'attack', 'block', 'parry', 'mine'}
            if advance_frames:
                self.animation_counter += 1
                if self.animation_counter >= self.animation_speed:
                    self.animation_counter = 0
                    self.animation_frame = (self.animation_frame + 1) % len(sprites)
            self.current_sprite = sprites[self.animation_frame][1]
    
    def draw_player(self, screen, position):
        """Draw the player sprite at the given position."""
        if self.current_sprite:
            sprite_rect = self.current_sprite.get_rect(center=position)
            screen.blit(self.current_sprite, sprite_rect)
    
    def update(self, axis_scancodes_held, keys_pressed, mouse_buttons=None):
        """Update player sprite: handle weapon actions, movement, and idle state based on input."""
        previous_state = self.current_state
        previous_direction = self.facing_direction

        if self.action is not None:
            self.update_action()
            return


        moving = self._any_movement_held(axis_scancodes_held)
        direction = self.facing_direction
        if moving:
            direction = self.get_current_direction(axis_scancodes_held)

        action_state = self._get_weapon_action_state(mouse_buttons, direction)
        if action_state:
            state = action_state
            self.movement_press_start = None
        elif moving:
            raw_state = self.get_current_state(axis_scancodes_held, keys_pressed)
            if self.movement_press_start is None:
                self.movement_press_start = pygame.time.get_ticks()
            if pygame.time.get_ticks() - self.movement_press_start >= self.min_hold_time:
                state = raw_state
            else:
                state = 'idle'
        else:
            self.movement_press_start = None
            state = 'idle'

        self.animation_speed = config.ANIMATION_SPEED_DASH if state == 'dash' else config.ANIMATION_SPEED_WALK
        self.update_animation(state, direction, axis_scancodes_held, previous_state, previous_direction)
        self.current_state = state

    def _get_weapon_action_state(self, mouse_buttons, direction):
        if not mouse_buttons or self.player is None:
            return None
        weapon_type = None
        if hasattr(self.player, 'equipped_weapon_type'):
            value = getattr(self.player, 'equipped_weapon_type')
            if callable(value):
                weapon_type = value()
            else:
                weapon_type = value
        if not weapon_type:
            return None

        if len(mouse_buttons) > config.MOUSE_BUTTON_ATTACK_INDEX and mouse_buttons[config.MOUSE_BUTTON_ATTACK_INDEX]:
            if self._has_weapon_action_sprite(weapon_type, 'attack', direction):
                return 'attack'
        if len(mouse_buttons) > config.MOUSE_BUTTON_BLOCK_INDEX and mouse_buttons[config.MOUSE_BUTTON_BLOCK_INDEX]:
            if self._has_weapon_action_sprite(weapon_type, 'block', direction):
                return 'block'
        return None

    def _has_weapon_action_sprite(self, weapon_type, action, direction):
        return bool(
            self.weapon_action_sprites
            .get(weapon_type, {})
            .get(action, {})
            .get(direction)
        )

    def get_weapon_action_sprites(self, weapon_type, action, direction):
        return (
            self.weapon_action_sprites
            .get(weapon_type, {})
            .get(action, {})
            .get(direction, [])
        )

class UIRenderer:
    def __init__(self, player):
        self.player = player
        self.elements = {}
        self.user_status = UserStatusUI(player)

    def draw_ui(self, screen):
        self.user_status.draw(screen)

    def update_ui(self):
        self.user_status.refresh_status()

    def configure_appearance(self, appearance):
        self.player.appearance = appearance
        os.makedirs(config.PLAYER_APPEARANCE_SAVE_DIR, exist_ok=True)
        config_path = os.path.join(config.PLAYER_APPEARANCE_SAVE_DIR, config.PLAYER_APPEARANCE_JSON_NAME)
        with open(config_path, 'w') as f:
            json.dump({"appearance": appearance}, f)






