import os
import pygame
from typing import Dict, Sequence, NamedTuple, Tuple

# Configuration constants
CONFIGURATION = "CONFIGURATION"
ENGINE_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
PROJECT_ROOT = os.path.normpath(os.path.join(ENGINE_ROOT, '..'))
CONTENTS_PATH = PROJECT_ROOT
RESOURCES_PATH = os.path.join(ENGINE_ROOT, 'Resources')
RESOURCE_MANIFEST_FILE = os.path.join(RESOURCES_PATH, 'resource_paths.txt')

#Map constants
CAVE = 'Cave'
TUTORIAL_CAVE = 'Tutorial Cave'
OVERWORLD = 'Overworld'
DAEMIAS_ALTAR = 'Daemias Altar'



# Display / main loop
SCREEN_WIDTH = 1550 # redundant with config.SCREEN_WIDTH, but kept for backward compatibility
SCREEN_HEIGHT = 850 # redundant with config.SCREEN_HEIGHT, but kept for backward compatibility
WINDOW_TITLE = "A Game About Forging"
TARGET_FPS = 60
SCREEN_CLEAR_COLOR = (20, 20, 20)
QUIT_KEY = pygame.K_ESCAPE

# Maps and map imports, add more maps as required
CAVE_MAP_PATH = os.path.join(RESOURCES_PATH, 'World', 'maps', 'tmx', 'cave.tmx')
CAVE_TUTORIAL_MAP_PATH = os.path.join(RESOURCES_PATH, 'World', 'maps', 'tmx', 'tutorial_rubble.tmx')

#Font import path, if font is to be changed later, simply adjust as required

DEFAULT_FONT_PATH = os.path.join(
    RESOURCES_PATH,
    'Fonts',
    'Handjet',
    'static',
    'Handjet-Regular.ttf',
)

# Player & world tuning
PLAYER_HITBOX_WIDTH = 16
PLAYER_HITBOX_HEIGHT = 16
PLAYER_START_HEALTH = 100
PLAYER_START_MAX_HEALTH = 100
PLAYER_START_MANA = 50
PLAYER_START_MAX_MANA = 50
PLAYER_START_XP = 0
PLAYER_START_LEVEL = 1
PLAYER_START_GOLD = 0
PLAYER_START_STATS: Dict[str, int] = {'strength': 10, 'defense': 5, 'speed': 5}
XP_PER_LEVEL_MULTIPLIER = 100
LEVEL_UP_MAX_HEALTH_BONUS = 10
DEFAULT_PLAYER_APPEARANCE = 'default'
PICKAXE_NAME_KEY = 'pickaxe'
WORLD_DEFAULT_TILE_SIZE = 4
PLAYER_DEFAULT_SIZE = (32, 32)

MINING_SPOT_WIDTH = 16
MINING_SPOT_HEIGHT = 16
DEFAULT_MINING_ITEM_NAME = 'Stone Ore'
DEFAULT_MINING_ITEM_TYPE = 'ore'
DEFAULT_MINING_ITEM_VALUE = 1

UPGRADE_TREE_INITIAL_COUNTS: Dict[str, int] = {'strength': 0, 'defense': 0, 'speed': 0}

# Asset roots (under Contents/Engine/Resources)
PLAYER_RESOURCES_DIR = os.path.join(RESOURCES_PATH, 'Player')

# PlayerRenderer tuning
PLAYER_DEFAULT_FACING = 'S'
PLAYER_DEFAULT_STATE = 'idle'
PLAYER_IDLE_FALLBACK_KEY = 'idle_S'
PLAYER_IDLE_SUBDIRS = ['MC - static']
PLAYER_DIRECTION_KEYS = ['W', 'S', 'A', 'D', 'AW', 'AS', 'WD', 'SD']
PLAYER_MOVEMENT_DIRECTORY_MAP: Dict[str, str] = {
    'walk': 'MC - walk',
    'run': 'Run',
    'sprint': 'MC - Sprint',
    'dash': 'Dash',
    'jump': 'Jump',
    'roll': 'Roll',
    'crouch': 'Crouch',
}
PLAYER_WEAPON_ANIMATION_FOLDERS = {
    'greatsword': {
        'attack': 'Attack - Greatsword',
        'block': 'Block - Greatsword',
        'parry': 'Parry - Greatsword',
    },
    'sword': {
        'attack': 'Attack - Sword',
        'block': 'Block - Sword',
        'parry': 'Parry - Sword',
    },
    'pickaxe': {
        'attack': 'Attack - Pickaxe',
    },
}
ANIMATION_SPEED_WALK = 10
ANIMATION_SPEED_DASH = 25
IDLE_ANIMATION_SPEED = 18
SPRITE_SCALE = 1
MOVEMENT_MIN_HOLD_MS = 1

# UIRenderer tuning — User Status composite bar (HP / MP / Stamina)
USER_STATUS_SPRITE_PATH = os.path.join(RESOURCES_PATH, 'UI', 'Bars', 'User Status', '0.png')
USER_STATUS_POSITION: Tuple[int, int] = (8, 8)
USER_STATUS_SCALE = 1.0
# Fill slots within the sprite (x, y, height, max_fill_width) at native resolution
USER_STATUS_HP_SLOT: Tuple[int, int, int, int] = (50, 14, 16, 248)
USER_STATUS_MP_SLOT: Tuple[int, int, int, int] = (75, 34, 14, 194)
USER_STATUS_STAMINA_SLOT: Tuple[int, int, int, int] = (50, 54, 14, 185)
USER_STATUS_HP_COLOR: Tuple[int, int, int] = (200, 45, 45)
USER_STATUS_MP_COLOR: Tuple[int, int, int] = (45, 130, 220)
USER_STATUS_STAMINA_COLOR: Tuple[int, int, int] = (220, 185, 45)

# Save / appearance
SAVE_DIRECTORY = os.path.join(PROJECT_ROOT, 'Saves')
SAVE_FILE_EXTENSION = '.dat'
PLAYER_APPEARANCE_SAVE_DIR = 'Saves/player config'
PLAYER_APPEARANCE_JSON_NAME = 'appearance.json'
GAME_SETTINGS_FILENAME = 'game_settings.json'

# Inventory & hotbar
HOTBAR_SLOT_COUNT = 10
HOTBAR_HEIGHT = 128
INVENTORY_BAG_SLOT_COUNT = 50
INVENTORY_BAG_COLUMNS = 10


def get_game_font(size: int, bold: bool = False, italic: bool = False):
    """Load the in-game font from the bundled Handjet asset when available."""
    pygame.font.init()
    if os.path.exists(DEFAULT_FONT_PATH):
        try:
            return pygame.font.Font(DEFAULT_FONT_PATH, size)
        except pygame.error:
            pass
    return pygame.font.SysFont('serif', size, bold=bold, italic=italic)

# Player stamina & skills (pseudocode defaults)
PLAYER_START_STAMINA = 100
PLAYER_START_MAX_STAMINA = 100
PLAYER_STATUS_DEFAULT_LEVEL = 1
PLAYER_STATUS_DEFAULT_GOLD = 50
DASH_STAMINA_COST = 25
SKILL_ULT_MANA_COST = 30
SKILL_1_MANA_COST = 15
SKILL_2_MANA_COST = 15
STAMINA_REGEN_BASE = 2.0
HEALTH_REGEN_IDLE_BASE = 1.0
MANA_REGEN_IDLE_BASE = 1.5

# UI toggles (keyboard)
UI_QUEST_TOGGLE_KEY = pygame.K_j
UI_MINIMAP_TOGGLE_KEY = pygame.K_m
HOTBAR_KEY_OFFSET = pygame.K_1  # keys 1–0 map to slots 0–9

# Action binds (display labels; runtime uses pygame keys where applicable)
BIND_ATTACK_LABEL = 'Left Mouse Button'
BIND_BLOCK_LABEL = 'Right Mouse Button'
BIND_INTERACT_LABEL = 'E'
BIND_INTERACT_KEYS = [pygame.K_e]
BIND_DASH_LABEL = 'Shift'
BIND_DASH_KEYS = [pygame.K_LSHIFT, pygame.K_RSHIFT]
MOUSE_BUTTON_ATTACK_INDEX = 0
MOUSE_BUTTON_BLOCK_INDEX = 1
SKILL_ULT_KEYS = [pygame.K_q]
SKILL_1_KEYS = [pygame.K_e]
SKILL_2_KEYS = [pygame.K_c]

# Settings UI
SETTINGS_CATEGORIES = ['General', 'Video', 'Audio', 'Directories', 'Keybinds']
DEFAULT_DIFFICULTY = 'Normal'
DEFAULT_MOUSE_SENSITIVITY = 0.5
DEFAULT_SETTINGS_FPS_LIMIT = 30
DEFAULT_RESOLUTION_LABEL = '1920 x 1080'
DEFAULT_MASTER_VOLUME = 0.50
DEFAULT_MUSIC_VOLUME = 1.00
DEFAULT_SFX_VOLUME = 1.00

# Character preview
CHARACTER_PREVIEW_BASE_IMAGE = 'BasePlayerModel.png'

# Scenes (logical names for menu/load flow)
SCENE_MAIN_WORLD = 'MainWorld'
SCENE_TUTORIAL = 'TutorialLevel'
SCENE_MAIN_MENU = 'MainMenu'

# Pickaxe / mining feedback (string hooks for audio/VFX)
SOUND_CLINK_METAL_ON_STONE = 'Clink_Metal_On_Stone'
SOUND_ROCK_SHATTER = 'Rock_Shatter'
EFFECT_SPARKLES_IMPACT = 'Sparkles at impact point'

# Keybinding Configuration
KEYBINDS = {
    'up': [pygame.K_w, pygame.K_UP],
    'down': [pygame.K_s, pygame.K_DOWN],
    'left': [pygame.K_a, pygame.K_LEFT],
    'right': [pygame.K_d, pygame.K_RIGHT],
}

# Direction mappings for sprite filenames
DIRECTION_MAP = {
    'up': 'W',
    'down': 'S',
    'left': 'A',
    'right': 'D',
}

class OreDrop(NamedTuple):
    name: str
    weight: int

# Ore types: rarity label plus slice of a 0–100 roll (half-open interval [low, high)).
# Draw roll in [0, 100); the first matching range wins. Ranges must partition 0–100.
ORE_RARITY_BY_PERCENT_RANGE = {
    'Stone': {'rarity': 'common', 'percent_range': (0, 42)},
    'Coal': {'rarity': 'common', 'percent_range': (42, 60)},
    'Iron': {'rarity': 'uncommon', 'percent_range': (60, 72)},
    'Silver': {'rarity': 'uncommon', 'percent_range': (72, 80)},
    'Gold': {'rarity': 'rare', 'percent_range': (80, 86)},
    'Platinum': {'rarity': 'rare', 'percent_range': (86, 91)},
    'Diamond': {'rarity': 'legendary', 'percent_range': (91, 95)},
    'Mithril': {'rarity': 'mythical', 'percent_range': (95, 97)},
    'Kyber': {'rarity': 'mythical', 'percent_range': (97, 99)},
    'Meteorite Fragment': {'rarity': 'mythical', 'percent_range': (99, 100)},
}

ORE_POOL: Sequence[OreDrop] = [
    OreDrop(name="Stone", weight=42),
    OreDrop(name="Coal", weight=18),
    OreDrop(name="Iron", weight=12),
    OreDrop(name="Silver", weight=8),
    OreDrop(name="Gold", weight=6),
    OreDrop(name="Platinum", weight=5),
    OreDrop(name="Diamond", weight=4),
    OreDrop(name="Mithril", weight=2),
    OreDrop(name="Kyber", weight=2),
    OreDrop(name="Meteorite Fragment", weight=1),
    OreDrop(name="Meteorite Fragment", weight=1),
]


# Gear spawn: when rolling rarity for a drop, use a 0–100 value and the half-open
# [low, high) interval for the gear category. Weapon vs armor use different tables.
GEAR_SPAWN_CHANCE_BY_RARITY = {
    'weapon': {
        'common': (0, 40),
        'uncommon': (40, 70),
        'rare': (70, 88),
        'epic': (88, 97),
        'legendary': (97, 100),
    },
    'armor': {
        'common': (0, 45),
        'uncommon': (45, 72),
        'rare': (72, 90),
        'epic': (90, 98),
        'legendary': (98, 100),
    },
}

def get_all_resources(base_path):
    """
    Recursively scans the base_path and returns a dictionary of relative paths to absolute paths.
    Keys are relative paths with forward slashes, values are absolute file paths.
    """
    resources = {}
    for root, dirs, files in os.walk(base_path):
        rel_root = os.path.relpath(root, base_path)
        if rel_root == '.':
            rel_root = ''
        for file in files:
            key = os.path.join(rel_root, file).replace(os.sep, '/')
            resources[key] = os.path.join(root, file)
    return resources

# Dictionary containing all resources with relative paths as keys
ALL_RESOURCES = get_all_resources(RESOURCES_PATH)

# Create a module-level `config` object for easier, centralized access and
# future runtime-config overrides. This preserves the uppercase constants
# for backward compatibility while offering `config.<NAME>` attribute access.
from types import SimpleNamespace

_config_values = {k: v for k, v in globals().items() if k.isupper()}
config = SimpleNamespace(**_config_values)
