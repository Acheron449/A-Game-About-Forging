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
from ..game.pause_menu_manager import PauseMenuManager, PauseScreen
from ..game.Player.movement_controller import PlayerController
from ..game.Player.player_status import PlayerStatus
from .Title import Application, GameEngine, MainMenuManager, TitleScreen
from .playerRenderer import PlayerRenderer


class GameplayPlayerStub(SimpleNamespace):
    def equipped_weapon_type(self):
        return None


def initialize_play_state(screen_size=(900, 700), on_quit_game=None): # Initialize the play state with all necessary gameplay systems
    """Create the gameplay systems once the player enters the play state."""
    player_status = PlayerStatus()
    player = GameplayPlayerStub(
        health=player_status.current_health,
        max_health=player_status.max_health,
        mana=player_status.current_mana,
        max_mana=player_status.max_mana,
        level=player_status.player_level,
        gold=player_status.gold,
    )



    player_renderer = PlayerRenderer(player)
    inventory_manager = InventoryManager()
    hotbar = InventoryHotbar()
    inventory_screen = InventoryScreen(inventory_manager=inventory_manager, hotbar=hotbar)
    pause_menu = PauseMenuManager(on_quit_game=on_quit_game)
    pause_screen = PauseScreen(pause_menu=pause_menu, screen_size=screen_size)
    movement_controller = PlayerController(player=player, player_status=player_status)

    return {
        "player": player,
        "player_status": player_status,
        "player_renderer": player_renderer,
        "inventory_manager": inventory_manager,
        "hotbar": hotbar,
        "inventory_screen": inventory_screen,
        "pause_menu": pause_menu,
        "pause_screen": pause_screen,
        "movement_controller": movement_controller,
    }


def main():
    pg.init()
    pg.font.init()

    screen = pg.display.set_mode((900, 700))
    pg.display.set_caption("A Game About Forging")

    try:
        base_dir = Path(__file__).parent.parent.parent
        map_json_path = base_dir / "Engine" / "Resources" / "World" / "maps" / "tmx" / "cave.tmx"
        tmx_data = pytmx.load_pygame(str(map_json_path), pixelalpha=True)
        game_map = TiledMap(tmx_data, map_json_path.parent)
    except Exception as exc:
        print(f"CRITICAL ERROR DURING MAP INITIALIZATION: {exc}")
        return

    game_state = "MENU"
    running = True
    play_state = None
    player_speed = 4

    def set_running(value: bool) -> None:
        nonlocal running
        running = value

    def trigger_play(scene_name=""):
        nonlocal game_state, play_state
        print(f"Loading scene: {scene_name}. Switching to PLAYING state!")
        if play_state is None:
            play_state = initialize_play_state(
                screen_size=screen.get_size(),
                on_quit_game=lambda: set_running(False),
            )
            play_state["world_position"] = [300, 300]
            play_state["camera"] = [0, 0]
            play_state["movement_controller"] = PlayerController(
                player=play_state["player"],
                player_status=play_state["player_status"],
                on_move=lambda keys_pressed: update_player_position(keys_pressed),
            )
            print("Gameplay systems initialized for the active scene.")
        game_state = "PLAYING"

    def trigger_quit():
        set_running(False)
        print("Quit button pressed. Closing game...")

    engine = GameEngine(on_load_scene=trigger_play)
    app = Application(on_quit=trigger_quit)

    menu_manager = MainMenuManager(game_engine=engine, application=app)
    title_screen = TitleScreen(title_menu=menu_manager, screen_size=(900, 700))

    def update_player_position(keys_pressed):
        if play_state is None:
            return
        dx = 0
        dy = 0
        if keys_pressed is None:
            keys_pressed = pg.key.get_pressed()

        if keys_pressed[pg.K_w] or keys_pressed[pg.K_UP]:
            dy -= player_speed
        if keys_pressed[pg.K_s] or keys_pressed[pg.K_DOWN]:
            dy += player_speed
        if keys_pressed[pg.K_a] or keys_pressed[pg.K_LEFT]:
            dx -= player_speed
        if keys_pressed[pg.K_d] or keys_pressed[pg.K_RIGHT]:
            dx += player_speed

        if dx and dy:
            dx *= 0.7
            dy *= 0.7

        world_x, world_y = play_state["world_position"]
        play_state["world_position"] = [world_x + dx, world_y + dy]

        map_width = game_map.tmx_data.width * game_map.tmx_data.tilewidth
        map_height = game_map.tmx_data.height * game_map.tmx_data.tileheight
        view_width, view_height = screen.get_size()
        max_camera_x = max(0, map_width - view_width)
        max_camera_y = max(0, map_height - view_height)
        player_x, player_y = play_state["world_position"]
        play_state["camera"] = [
            max(0, min(player_x - view_width // 2, max_camera_x)),
            max(0, min(player_y - view_height // 2, max_camera_y)),
        ]

    clock = pg.time.Clock()

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                continue

            if game_state == "MENU":
                title_screen.handle_event(event)
            elif game_state == "PLAYING" and play_state is not None:
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    play_state["pause_menu"].toggle_pause_menu()
                elif event.type == pg.KEYDOWN and event.key == pg.K_i:
                    play_state["inventory_screen"].toggle()

        screen.fill((0, 0, 0))

        if game_state == "MENU":
            title_screen.render(screen)
        elif game_state == "PLAYING" and play_state is not None:
            camera_x, camera_y = play_state.get("camera", (0, 0))
            game_map.render(screen, camera_x, camera_y)
            screen_center_x, screen_center_y = screen.get_size()[0] // 2, screen.get_size()[1] // 2
            play_state["player_renderer"].draw_player(screen, (screen_center_x, screen_center_y))
            if play_state["inventory_screen"].is_open:
                play_state["inventory_screen"].draw(screen, None)
            if play_state["pause_menu"].is_paused:
                play_state["pause_screen"].render(screen)

            keys_pressed = pg.key.get_pressed()
            mouse_buttons = pg.mouse.get_pressed(3)
            if not play_state["pause_menu"].is_paused:
                axis_scancodes_held = {
                    "up": keys_pressed[pg.K_w] or keys_pressed[pg.K_UP],
                    "down": keys_pressed[pg.K_s] or keys_pressed[pg.K_DOWN],
                    "left": keys_pressed[pg.K_a] or keys_pressed[pg.K_LEFT],
                    "right": keys_pressed[pg.K_d] or keys_pressed[pg.K_RIGHT],
                }
                play_state["movement_controller"].handle_input(keys_pressed, mouse_buttons=mouse_buttons)
                play_state["player_renderer"].update(axis_scancodes_held, keys_pressed, mouse_buttons)

        pg.display.flip()
        clock.tick(60)

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()