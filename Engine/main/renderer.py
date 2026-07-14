import os 
import json
import pygame

from ..config.config import config
from ..config.imports import * # for any additional imports needed for rendering, not used in this snippet but may be needed for future rendering features (e.g., loading fonts, additional sprite types, etc.)
from .user_status_ui import UserStatusUI

class WorldRenderer: # Placeholder for future world rendering logic (e.g., map, tiles, entities, etc.)
    def __init__(self): # Initialize any necessary variables for world rendering (e.g., tile size, camera position, etc.)
        pass

    def render_world(self, world, screen): # Render the world map, player, and entities to the screen. This will be called from World.render() and can be expanded with actual rendering logic as needed.
        # Render map and entities
        # Placeholder for rendering logic
        pass 

class PlayerRenderer:
    """Handles loading and rendering directional player sprites."""
    
    def __init__(self, player):
        self.player = player
        self.player_resources_dir = config.PLAYER_RESOURCES_DIR
        
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
        movement_sprites = {}
        movement_directories = config.PLAYER_MOVEMENT_DIRECTORY_MAP
        
        direction_keys = config.PLAYER_DIRECTION_KEYS
        for state, move_type in movement_directories.items():
            move_dir = os.path.join(self.player_resources_dir, "Movement", move_type)
            if not os.path.isdir(move_dir):
                continue
            
            for dir_key in direction_keys: # Generate keys like 'walk_W', 'run_A', etc.
                sprite_key = f'{state}_{dir_key}' # e.g. 'walk_W', 'run_A', etc.
                movement_sprites[sprite_key] = self._load_direction_images(move_dir, dir_key) # Load sprites for this state and direction, e.g. 'walk_W' for walking north, 'run_A' for running west, etc.
        
        return movement_sprites
    
    def _load_direction_images(self, base_dir, direction_key):
        """Load all images for a specific direction from a directory."""
        images = []
        direction_key = direction_key.upper()
        
        # Look for image files matching the direction code
        for filename in sorted(os.listdir(base_dir)):
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue
            name_base = os.path.splitext(filename)[0].upper()
            parts = name_base.split('_')
            if not parts:
                continue
            # For files with frame numbers (e.g., AS_0), remove the frame part
            if parts[-1].isdigit():
                parts = parts[:-1]
            suffix = ''.join(parts)
            if suffix != direction_key:
                continue

            try: 
                image_path = os.path.join(base_dir, filename) 
                image = pygame.image.load(image_path)
                if pygame.display.get_surface() is not None:
                    image = image.convert_alpha()
                if self.sprite_scale != 1.0:
                    image = pygame.transform.rotozoom(image, 0, self.sprite_scale)
                images.append((filename, image))
            except Exception as e:
                print(f"Failed to load image {filename}: {e}")
        
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
        """Get the current sprite image based on state and direction."""
        sprite_key = f'{state}_{direction}'
        idle_key = f'idle_{direction}'

        if state == 'idle':
            if idle_key in self.idle_sprites and self.idle_sprites[idle_key]:
                return self.idle_sprites[idle_key]
            if config.PLAYER_IDLE_FALLBACK_KEY in self.idle_sprites and self.idle_sprites[config.PLAYER_IDLE_FALLBACK_KEY]:
                return self.idle_sprites[config.PLAYER_IDLE_FALLBACK_KEY]
            return [] # Return an empty list if no idle sprites are found.

        if sprite_key in self.movement_sprites and self.movement_sprites[sprite_key]:
            return self.movement_sprites[sprite_key] # Return the movement sprites for this state and direction.
        # Missing sprint/run/etc.: try walk, then idle for this facing
        if state != 'walk':
            walk_key = f'walk_{direction}'
            if walk_key in self.movement_sprites and self.movement_sprites[walk_key]:
                return self.movement_sprites[walk_key] # Return the walk sprites for this direction.
        if idle_key in self.idle_sprites and self.idle_sprites[idle_key]:
            return self.idle_sprites[idle_key] # Return the idle sprites for this direction.
        return [] # Return an empty list if no sprites are found.
    
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
            # Only advance frames when movement keys are pressed
            if self.is_key_pressed(axis_scancodes_held):
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
    
    def update(self, axis_scancodes_held, keys_pressed): 
        """Update player sprite: walk/sprint for all facings (W, S, A, D, AW, WD, AS, SD); idle keeps last facing."""
        previous_state = self.current_state
        previous_direction = self.facing_direction

        moving = self._any_movement_held(axis_scancodes_held)

        if moving:
            direction = self.get_current_direction(axis_scancodes_held) 
            raw_state = self.get_current_state(axis_scancodes_held, keys_pressed)
            if self.movement_press_start is None:
                self.movement_press_start = pygame.time.get_ticks()
            if pygame.time.get_ticks() - self.movement_press_start >= self.min_hold_time:
                state = raw_state
            else:
                state = 'idle' # Start in idle until min hold time is reached, then switch to walk/sprint based on shift key. This prevents instant sprinting and allows for a more natural transition from idle to movement.
        else:
            self.movement_press_start = None # Reset movement press timer when no movement keys are held
            state = 'idle' # When no movement keys are held, switch to idle but keep last facing direction for idle animation (e.g., if player was moving diagonally AW, then releases keys, they should still face that direction in idle)
            direction = self.facing_direction # Keep last facing direction when idle (e.g., if player was moving diagonally AW, then releases keys, they should still face that direction in idle)

        self.update_animation(state, direction, axis_scancodes_held, previous_state, previous_direction)
        self.current_state = state

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
