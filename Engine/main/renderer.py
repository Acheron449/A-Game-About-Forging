import os
import json
import pygame
import builtins

from ..config.config import *
from ..config.imports import *

class WorldRenderer:
    def __init__(self):
        pass

    def render_world(self, world, screen):
        # Render map and entities
        # Placeholder for rendering logic
        pass

class PlayerRenderer:
    """Handles loading and rendering directional player sprites."""
    
    def __init__(self, player):
        self.player = player
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) # Go up three levels to reach project root
        self.player_resources_dir = os.path.join(self.root_dir, "Contents", "Resources", "Player")
        
        self.facing_direction = 'S'  # Default facing direction (S for south/down)
        self.current_state = 'idle'  # Current state (idle, walk, run, sprint, etc.)
        self.animation_frame = 0
        self.animation_counter = 0
        self.animation_speed = 10  # Update every 10 frames while moving
        self.sprite_scale = 0.45  # Scale sprites to 45% of original size
        self.min_hold_time = 1  # Minimum hold time in ms for key to register
        self.down_press_start = None
        
        # Load sprite sheets
        self.idle_sprites = self._load_idle_sprites()
        self.movement_sprites = self._load_movement_sprites()
        self.current_sprite = None
        self.sprites_list = []
        
        # Set current sprite to idle 'S'
        idle_s_key = 'idle_S'
        if idle_s_key in self.idle_sprites and self.idle_sprites[idle_s_key]:
            self.current_sprite = self.idle_sprites[idle_s_key][0][1]  # First frame

        # Map WASD/arrows to SDL scancodes (stable; matches event.scancode on KEYDOWN/KEYUP)
        _to_sc = getattr(pygame.key, 'key_to_scancode', None)
        if _to_sc:
            self._axis_scancodes = {
                axis: frozenset(_to_sc(k) for k in keys) for axis, keys in KEYBINDS.items()
            }
            self._all_movement_scancodes = frozenset().union(*self._axis_scancodes.values())
        else:
            self._axis_scancodes = None
            self._all_movement_scancodes = frozenset()

    def _axis_held(self, movement_scancodes_held, axis):
        if self._axis_scancodes is None:
            return False
        return bool(movement_scancodes_held & self._axis_scancodes[axis])

    def _any_movement_held(self, movement_scancodes_held):
        if self._axis_scancodes is None:
            return False
        return bool(movement_scancodes_held & self._all_movement_scancodes)
        
    def _load_idle_sprites(self):
        """Load idle sprites for all directions from Player/Idle folders.""" #TEST - Updated to load from all subfolders in Idle, not just 'Test - Static'
        idle_sprites = {}
        idle_paths = ['Test - Static', 'Static', 'Armed']  # Updated to match actual directory names
        
        direction_keys = ['W', 'S', 'A', 'D', 'AW', 'AS', 'WD', 'SD']
        for idle_type in idle_paths:
            idle_dir = os.path.join(self.player_resources_dir, "Idle", idle_type)
            if not os.path.isdir(idle_dir):
                continue
                
            for key in direction_keys:
                sprite_key = f'idle_{key}'
                loaded_images = self._load_direction_images(idle_dir, key)
                if loaded_images:
                    idle_sprites.setdefault(sprite_key, []).extend(loaded_images)
        
        return idle_sprites
    
    def _load_movement_sprites(self):
        """Load movement sprites for all directions from Player/Movement folders."""
        movement_sprites = {}
        movement_directories = {
            'walk': 'test - walk',
            'run': 'Run',
            'sprint': 'Sprint',
            'dash': 'Dash',
            'jump': 'Jump',
            'roll': 'Roll',
            'crouch': 'Crouch',
        }
        
        direction_keys = ['W', 'S', 'A', 'D', 'AW', 'AS', 'WD', 'SD']
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
    
    def get_current_direction(self, movement_scancodes_held):
        """Determine player facing direction based on pressed keys."""
        up = self._axis_held(movement_scancodes_held, 'up')
        down = self._axis_held(movement_scancodes_held, 'down')
        left = self._axis_held(movement_scancodes_held, 'left')
        right = self._axis_held(movement_scancodes_held, 'right')

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

        self.facing_direction = direction
        return self.facing_direction
    
    def is_key_pressed(self, movement_scancodes_held):
        """Check if any movement key is being pressed."""
        return self._any_movement_held(movement_scancodes_held)
    
    def get_current_state(self, movement_scancodes_held, keys_pressed):
        """Determine player movement state based on pressed keys."""
        up = self._axis_held(movement_scancodes_held, 'up')
        down = self._axis_held(movement_scancodes_held, 'down')
        left = self._axis_held(movement_scancodes_held, 'left')
        right = self._axis_held(movement_scancodes_held, 'right')

        if not (up or down or left or right):
            return 'idle'
        
        # Check for shift key (sprint)
        if keys_pressed[pygame.K_LSHIFT] or keys_pressed[pygame.K_RSHIFT]:
            return 'sprint'
        
        # Default to walk if moving
        return 'walk'
    
    def get_sprite(self, state, direction):
        """Get the current sprite image based on state and direction."""
        sprite_key = f'{state}_{direction}'
        
        # Try movement sprites first, then idle
        if sprite_key in self.movement_sprites and self.movement_sprites[sprite_key]:
            return self.movement_sprites[sprite_key]
        elif sprite_key in self.idle_sprites and self.idle_sprites[sprite_key]:
            return self.idle_sprites[sprite_key]
        
        return []
    
    def update_animation(self, state, direction, movement_scancodes_held, previous_state=None, previous_direction=None):
        """Update the current animation frame for the given state and direction."""
        sprites = self.get_sprite(state, direction)
        
        if not sprites:
            self.current_sprite = None
            return
        
        if previous_state is None:
            previous_state = self.current_state
        if previous_direction is None:
            previous_direction = self.facing_direction

        # Reset animation when state or direction changes
        if state != previous_state or direction != previous_direction:
            self.animation_frame = 0
            self.animation_counter = 0
        
        if state == 'idle':
            # For idle, show the first frame and do not animate
            self.animation_frame = 0
            self.current_sprite = sprites[0][1]
            self.animation_counter = 0
        else:
            # Only advance frames when movement keys are pressed
            if self.is_key_pressed(movement_scancodes_held):
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
    
    def update(self, movement_scancodes_held):
        """Update player sprite based on input."""
        previous_state = self.current_state
        previous_direction = self.facing_direction
        
        # Default to idle
        state = 'idle'
        direction = 'S'
        
        # Down (S / arrow down): scancode set + KEYUP discard (see main loop)
        down_pressed = self._axis_held(movement_scancodes_held, 'down')
        
        if down_pressed:
            if self.down_press_start is None:
                self.down_press_start = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.down_press_start >= self.min_hold_time:
                state = 'walk'
        else:
            self.down_press_start = None
        
        self.facing_direction = direction
        self.update_animation(state, direction, movement_scancodes_held, previous_state, previous_direction)
        self.current_state = state

class UIRenderer:
    def __init__(self, player):
        self.player = player
        self.elements = {}  # Health bar, stats display, etc.
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.hp_bar_root = os.path.join(self.root_dir, "Contents", "Resources", "UI", "Bars", "HP")
        self.mp_bar_root = os.path.join(self.root_dir, "Contents", "Resources", "UI", "Bars", "MP")
        self.hp_frames = self._load_hp_frames()
        self.mp_frames = self._load_mp_frames()
        self.hp_frame_index = 0
        self.mp_frame_index = 0
        self.hp_bar_pos = (240, 40)  # Moved 40px right, HP bar higher at y=40
        self.mp_bar_pos = (240, 150)  # Moved 40px right, kept at y=150
        self.bar_scale = 0.2  # Scale bars to 20% size
        self.animation_counter = 0  # Counter for slowing down animation
        self.animation_speed = 15  # Update animation every 15 frames (4 FPS)

    def _load_hp_frames(self):
        frames = {}
        for folder_index in range(0, 12):
            folder_path = os.path.join(self.hp_bar_root, str(folder_index))
            if not os.path.isdir(folder_path):
                continue
            frame_images = []
            for image_name in ("0.png", "1.png"):
                image_path = os.path.join(folder_path, image_name)
                if os.path.isfile(image_path):
                    try:
                        frame_images.append(pygame.image.load(image_path).convert_alpha())
                    except Exception:
                        frame_images.append(None)
                else:
                    frame_images.append(None)
            frames[folder_index] = frame_images
        return frames

    def _load_mp_frames(self):
        """Load mana bar frames, similar to HP frames."""
        frames = {}
        for folder_index in range(0, 12):
            folder_path = os.path.join(self.mp_bar_root, str(folder_index))
            if not os.path.isdir(folder_path):
                continue
            frame_images = []
            for image_name in ("0.png", "1.png"):
                image_path = os.path.join(folder_path, image_name)
                if os.path.isfile(image_path):
                    try:
                        frame_images.append(pygame.image.load(image_path).convert_alpha())
                    except Exception:
                        frame_images.append(None)
                else:
                    frame_images.append(None)
            frames[folder_index] = frame_images
        return frames

    def _hp_group_index(self):
        hp = builtins.max(0, builtins.min(self.player.health, self.player.max_health))
        if hp <= 0:
            return 0
        if hp >= self.player.max_health:
            return 11
        return builtins.min(10, ((hp - 1) // 10) + 1)

    def _mp_group_index(self):
        """Get mana bar group index (0-11)."""
        mp = builtins.max(0, builtins.min(self.player.mana, self.player.max_mana))
        if mp <= 0:
            return 0
        if mp >= self.player.max_mana:
            return 11
        return builtins.min(10, ((mp - 1) // 10) + 1)

    def _select_hp_image(self):
        group = self._hp_group_index()
        frames = self.hp_frames.get(group, [None, None])

        if group == 0:
            # 0 HP uses the static zero-health image from folder 0
            return frames[0] or frames[1]

        if group == 1:
            # below 10 HP alternates between folder 1 images
            return frames[self.hp_frame_index % 2] or frames[0] or frames[1]

        if group == 11:
            # full HP alternates between folder 11 images
            return frames[self.hp_frame_index % 2] or frames[0] or frames[1]

        # For all other 10-HP intervals, use the image in the matching folder
        return frames[0] or frames[1]

    def _select_mp_image(self):
        """Select mana bar image based on current mana."""
        group = self._mp_group_index()
        frames = self.mp_frames.get(group, [None, None])

        if group == 0:
            return frames[0] or frames[1]

        if group == 1:
            return frames[self.mp_frame_index % 2] or frames[0] or frames[1]

        if group == 11:
            return frames[self.mp_frame_index % 2] or frames[0] or frames[1]

        return frames[0] or frames[1]

    def _update_hp_frame(self):
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.hp_frame_index = (self.hp_frame_index + 1) % 2
            self.mp_frame_index = (self.mp_frame_index + 1) % 2
            self.animation_counter = 0

    def draw_ui(self, screen):
        hp_image = self._select_hp_image()
        if hp_image is not None:
            # Scale the HP bar
            scaled_hp = pygame.transform.scale(hp_image, 
                (int(hp_image.get_width() * self.bar_scale), 
                 int(hp_image.get_height() * self.bar_scale)))
            # Center the scaled bar at the intended position
            hp_x = self.hp_bar_pos[0] - scaled_hp.get_width() // 2
            hp_y = self.hp_bar_pos[1] - scaled_hp.get_height() // 2
            screen.blit(scaled_hp, (hp_x, hp_y))
        
        mp_image = self._select_mp_image()
        if mp_image is not None:
            # Scale the MP bar
            scaled_mp = pygame.transform.scale(mp_image, 
                (int(mp_image.get_width() * self.bar_scale), 
                 int(mp_image.get_height() * self.bar_scale)))
            # Center the scaled bar at the intended position
            mp_x = self.mp_bar_pos[0] - scaled_mp.get_width() // 2
            mp_y = self.mp_bar_pos[1] - scaled_mp.get_height() // 2
            screen.blit(scaled_mp, (mp_x, mp_y))

    def update_ui(self):
        self._update_hp_frame()

    def configure_appearance(self, appearance):
        self.player.appearance = appearance
        config_dir = "Saves/player config"
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, "appearance.json")
        with open(config_path, 'w') as f:
            json.dump({"appearance": appearance}, f)
