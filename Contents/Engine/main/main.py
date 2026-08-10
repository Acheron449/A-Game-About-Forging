import sys
from pathlib import Path
from types import SimpleNamespace

import pygame as pg
import pytmx

# --- Path Setup ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parents[3]
sys.path.append(str(project_root))

from ..configuration.constants import config
from ..game.Inventory.inventory import InventoryManager, InventoryScreen
from ..game.Inventory.inventory_hotbar import InventoryHotbar
from ..game.Map.map_loader import TiledMap
from ..game.Map.map_manager import MapManager
from ..game.pause_menu_manager import PauseMenuManager, PauseScreen

from ..game.Player.movement_controller import PlayerController
from ..game.Player.player_status import PlayerStatus
from ..game.Player.equipment_manager import EquipmentManager
from ..game.Player.character_attack import CharacterAttack

from ..game.Settings.settings_modifier import SettingsModifier
from ..game.Settings.settings_ui_manager import (
    SettingsScreen,
    SettingsUIManager,
)

from .Title import (
    Application,
    GameEngine,
    MainMenuManager,
    TitleScreen,
)
from .playerRenderer import PlayerRenderer


class GameplayPlayerStub(SimpleNamespace):

    def equipped_weapon_type(self):
        return None


# ============================================================
# PLAY STATE INITIALISATION
# ============================================================

def initialize_play_state(
    screen_size=(1000, 800),
    on_quit_game=None,
    settings_screen=None,
):
    """Create all gameplay systems."""

    # --------------------------------------------------------
    # PLAYER STATUS
    # --------------------------------------------------------

    player_status = PlayerStatus()

    player = GameplayPlayerStub(
        health=player_status.current_health,
        max_health=player_status.max_health,
        mana=player_status.current_mana,
        max_mana=player_status.max_mana,
        level=player_status.player_level,
        gold=player_status.gold,
    )

    # --------------------------------------------------------
    # INVENTORY
    # --------------------------------------------------------

    inventory_manager = InventoryManager()
    hotbar = InventoryHotbar()

    inventory_screen = InventoryScreen(
        inventory_manager=inventory_manager,
        hotbar=hotbar,
    )

    # --------------------------------------------------------
    # EQUIPMENT
    # --------------------------------------------------------

    equipment_manager = EquipmentManager(
        inventory_manager=inventory_manager,
        player_status=player_status,
    )

    # --------------------------------------------------------
    # PLAYER RENDERER
    # --------------------------------------------------------

    player_renderer = PlayerRenderer(player)

    # --------------------------------------------------------
    # PAUSE MENU
    # --------------------------------------------------------

    pause_menu = PauseMenuManager(
        on_quit_game=on_quit_game,
        on_open_settings=(
            lambda: settings_screen.open()
            if settings_screen
            else None
        ),
    )

    pause_screen = PauseScreen(
        pause_menu=pause_menu,
        screen_size=screen_size,
    )

    # --------------------------------------------------------
    # ATTACK SYSTEM
    # --------------------------------------------------------

    # We create the controller first, then attach the attack
    # system to it.

    movement_controller = PlayerController(
        player=player,
        player_status=player_status,
    )

    # Give the controller access to equipment.
    movement_controller.equipment_manager = equipment_manager

    # CharacterAttack handles:
    #
    # - checking equipped item
    # - determining attack type
    # - cooldown
    # - animation
    #
    character_attack = CharacterAttack(
        player_controller=movement_controller
    )

    # Tell the controller what to do when the player attacks.
    movement_controller._on_attack = character_attack.start_attack

    # --------------------------------------------------------
    # RETURN GAMEPLAY SYSTEMS
    # --------------------------------------------------------

    return {
        "player": player,
        "player_status": player_status,

        "player_renderer": player_renderer,

        "inventory_manager": inventory_manager,
        "hotbar": hotbar,
        "inventory_screen": inventory_screen,

        "equipment_manager": equipment_manager,

        "character_attack": character_attack,

        "pause_menu": pause_menu,
        "pause_screen": pause_screen,

        "movement_controller": movement_controller,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    pg.init()
    pg.font.init()

    screen = pg.display.set_mode((1200, 800))
    pg.display.set_caption("A Game About Forging")

    # --------------------------------------------------------
    # MAP
    # --------------------------------------------------------

    base_dir = Path(__file__).parent.parent.parent

    maps_directory = (
        base_dir
        / "Engine"
        / "Resources"
        / "World"
        / "maps"
        / "tmx"
    )

    map_manager = MapManager(
        maps_directory,
        scale=1.0,
    )

    map_manager.load_map(
        "tutorial",
        spawn_position=(800, 600),
    )

    game_map = map_manager.current_map

    print(
        "COLLISION OBJECT COUNT:",
        len(game_map.collision_objects),
    )

    # --------------------------------------------------------
    # GAME STATE
    # --------------------------------------------------------

    game_state = "MENU"
    running = True
    play_state = None

    player_speed = 4

    # --------------------------------------------------------
    # QUIT
    # --------------------------------------------------------

    def set_running(value: bool) -> None:
        nonlocal running
        running = value

    # --------------------------------------------------------
    # PLAYER MOVEMENT
    # --------------------------------------------------------

    def update_player_position(keys_pressed):

        if play_state is None:
            return

        player_rect = play_state["player_rect"]

        dx = 0
        dy = 0

        # ----------------------------
        # Read movement input
        # ----------------------------

        if keys_pressed[pg.K_w] or keys_pressed[pg.K_UP]:
            dy -= player_speed

        if keys_pressed[pg.K_s] or keys_pressed[pg.K_DOWN]:
            dy += player_speed

        if keys_pressed[pg.K_a] or keys_pressed[pg.K_LEFT]:
            dx -= player_speed

        if keys_pressed[pg.K_d] or keys_pressed[pg.K_RIGHT]:
            dx += player_speed

        # ----------------------------
        # Normalize diagonal movement
        # ----------------------------

        if dx and dy:
            dx *= 0.7
            dy *= 0.7

        # ----------------------------
        # Horizontal movement
        # ----------------------------

        player_rect.x += int(dx)

        for blocker in map_manager.current_map.collision_objects:

            if blocker.collides_with_rect(player_rect):

                if dx > 0:
                    player_rect.right = blocker.rect.left

                elif dx < 0:
                    player_rect.left = blocker.rect.right

        # ----------------------------
        # Vertical movement
        # ----------------------------

        player_rect.y += int(dy)

        for blocker in map_manager.current_map.collision_objects:

            if blocker.collides_with_rect(player_rect):

                if dy > 0:
                    player_rect.bottom = blocker.rect.top

                elif dy < 0:
                    player_rect.top = blocker.rect.bottom

        # ----------------------------
        # Save position
        # ----------------------------

        play_state["world_position"] = [
            player_rect.x,
            player_rect.y,
        ]

        

        # ----------------------------
        # Camera
        # ----------------------------

        current_map = map_manager.current_map

        map_width = current_map.pixels_width
        map_height = current_map.pixels_height

        view_width, view_height = screen.get_size()

        max_camera_x = max(
            0,
            map_width - view_width,
        )

        max_camera_y = max(
            0,
            map_height - view_height,
        )

        play_state["camera"] = [
            max(
                0,
                min(
                    player_rect.centerx - view_width // 2,
                    max_camera_x,
                ),
            ),
            max(
                0,
                min(
                    player_rect.centery - view_height // 2,
                    max_camera_y,
                ),
            ),
        ]

    # --------------------------------------------------------
    # LOAD PLAY STATE
    # --------------------------------------------------------

    def trigger_play(scene_name=""):

        nonlocal game_state, play_state

        print(
            f"Loading scene: {scene_name}. "
            "Switching to PLAYING state!"
        )

        if play_state is None:

            play_state = initialize_play_state(
                screen_size=screen.get_size(),
                on_quit_game=lambda: set_running(False),
                settings_screen=settings_screen,
            )

            spawn_x, spawn_y = map_manager.spawn_position

            play_state["player_rect"] = pg.Rect(
                spawn_x,
                spawn_y,
                24,
                20,
            )

            play_state["world_position"] = [
                spawn_x,
                spawn_y,
            ]

            # ----------------------------
            # Initial camera
            # ----------------------------

            view_width, view_height = screen.get_size()

            play_state["camera"] = [
                max(
                    0,
                    spawn_x - view_width // 2,
                ),
                max(
                    0,
                    spawn_y - view_height // 2,
                ),
            ]

            # ----------------------------
            # Connect movement callback
            # ----------------------------

            movement_controller = play_state[
                "movement_controller"
            ]

            movement_controller._on_move = (
                update_player_position
            )

            print(
                "PLAYER POS:",
                play_state["player_rect"].topleft,
            )

        game_state = "PLAYING"

    # --------------------------------------------------------
    # QUIT
    # --------------------------------------------------------

    def trigger_quit():

        set_running(False)

        print(
            "Quit button pressed. Closing game..."
        )

    # --------------------------------------------------------
    # MENU / SETTINGS
    # --------------------------------------------------------

    engine = GameEngine(
        on_load_scene=trigger_play,
    )

    app = Application(
        on_quit=trigger_quit,
    )

    settings_ui = SettingsUIManager()

    settings_modifier = SettingsModifier(
        current_config=settings_ui.current_config,
    )

    settings_screen = SettingsScreen(
        settings_ui=settings_ui,
        modifier=settings_modifier,
    )

    menu_manager = MainMenuManager(
        game_engine=engine,
        application=app,
        on_open_settings=lambda: settings_screen.open(),
    )

    title_screen = TitleScreen(
        title_menu=menu_manager,
        screen_size=(1200, 800),
    )

    # ========================================================
    # GAME LOOP
    # ========================================================

    clock = pg.time.Clock()

    while running:

        # ----------------------------------------------------
        # EVENTS
        # ----------------------------------------------------

        events = pg.event.get()

        for event in events:

            if event.type == pg.QUIT:
                running = False
                continue

            # Settings
            if settings_screen.is_open:
                settings_screen.handle_event(event)
                continue

            # Menu
            if game_state == "MENU":

                title_screen.handle_event(event)

            # Gameplay
            elif (
                game_state == "PLAYING"
                and play_state is not None
            ):

                # Pause
                if (
                    event.type == pg.KEYDOWN
                    and event.key == pg.K_ESCAPE
                ):
                    play_state[
                        "pause_menu"
                    ].toggle_pause_menu()

                # Inventory
                elif (
                    event.type == pg.KEYDOWN
                    and event.key == pg.K_i
                ):
                    play_state[
                        "inventory_screen"
                    ].toggle()

                # Mouse input while paused
                if (
                    event.type == pg.MOUSEBUTTONDOWN
                    and event.button == 1
                    and play_state[
                        "pause_menu"
                    ].is_paused
                ):
                    play_state[
                        "pause_screen"
                    ].handle_event(event)

        # ----------------------------------------------------
        # CLEAR SCREEN
        # ----------------------------------------------------

        screen.fill((0, 0, 0))

        # ----------------------------------------------------
        # MENU
        # ----------------------------------------------------

        if game_state == "MENU":

            title_screen.render(screen)

        # ----------------------------------------------------
        # GAMEPLAY
        # ----------------------------------------------------

        elif (
            game_state == "PLAYING"
            and play_state is not None
        ):

            camera_x, camera_y = play_state.get(
                "camera",
                (0, 0),
            )

            # ----------------------------
            # Map
            # ----------------------------

            map_manager.current_map.render(
                screen,
                camera_x,
                camera_y,
            )

            # ----------------------------
            # Collision debug
            # ----------------------------

            for collision in (
                map_manager.current_map.collision_objects
            ):

                collision.draw_debug(
                    screen,
                    camera_x,
                    camera_y,
                )

            # ----------------------------
            # Player
            # ----------------------------

            screen_center_x = (
                screen.get_width() // 2
            )

            screen_center_y = (
                screen.get_height() // 2
            )

            play_state[
                "player_renderer"
            ].draw_player(
                screen,
                (
                    screen_center_x,
                    screen_center_y,
                ),
            )

            # ----------------------------
            # UI
            # ----------------------------

            if play_state[
                "inventory_screen"
            ].is_open:

                play_state[
                    "inventory_screen"
                ].draw(
                    screen,
                    None,
                )

            if play_state[
                "pause_menu"
            ].is_paused:

                play_state[
                    "pause_screen"
                ].render(screen)

            # ----------------------------
            # Input
            # ----------------------------

            if not play_state["pause_menu"].is_paused:

                keys_pressed = pg.key.get_pressed()

                mouse_buttons = pg.mouse.get_pressed(3)

                axis_scancodes_held = {
                    "up": (
                        keys_pressed[pg.K_w]
                        or keys_pressed[pg.K_UP]
                    ),

                    "down": (
                        keys_pressed[pg.K_s]
                        or keys_pressed[pg.K_DOWN]
                    ),

                    "left": (
                        keys_pressed[pg.K_a]
                        or keys_pressed[pg.K_LEFT]
                    ),

                    "right": (
                        keys_pressed[pg.K_d]
                        or keys_pressed[pg.K_RIGHT]
                    ),
                }

                print(
                    "RAW INPUT:",
                    "W =", keys_pressed[pg.K_w],
                    "A =", keys_pressed[pg.K_a],
                    "S =", keys_pressed[pg.K_s],
                    "D =", keys_pressed[pg.K_d],
                )

                update_player_position(keys_pressed)


                # ----------------------------
                # Movement + attack input
                # ----------------------------

                play_state[
                    "movement_controller"
                ].handle_input(
                    keys_pressed,
                    mouse_buttons=mouse_buttons,
                )

                # ----------------------------
                # Update attack animation
                # ----------------------------

                play_state[
                    "character_attack"
                ].update()

                # ----------------------------
                # Update player animation
                # ----------------------------

                play_state[
                    "player_renderer"
                ].update(
                    axis_scancodes_held,
                    keys_pressed,
                    mouse_buttons,
                )

        # ----------------------------------------------------
        # SETTINGS
        # ----------------------------------------------------

        if settings_screen.is_open:
            settings_screen.draw(screen)

        # ----------------------------------------------------
        # DISPLAY
        # ----------------------------------------------------

        pg.display.flip()

        clock.tick(60)

    # ========================================================
    # SHUTDOWN
    # ========================================================

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()