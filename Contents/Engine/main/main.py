"""main.py - """
 # Start the game, initialize runtime state, and run the main event loop.
import sys
from pathlib import Path
from types import SimpleNamespace

import pygame as pg

# PATH SETUP

current_file_path = Path(__file__).resolve()
project_root = current_file_path.parents[3]

if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# IMPORTS

from ..configuration.imports import *

from ..game.Inventory.inventory import (
    InventoryManager,
    InventoryScreen,
)

from ..game.Inventory.inventory_hotbar import (
    InventoryHotbar,
)

from ..game.Map.map_manager import (
    MapManager,
)

from ..game.pause_menu_manager import (
    PauseMenuManager,
    PauseScreen,
)

from ..game.Player.movement_controller import (
    PlayerController,
)

from ..game.Player.player_status import (
    PlayerStatus,
)

from ..game.Player.equipment_manager import (
    EquipmentManager,
)

from ..game.Player.character_attack import (
    CharacterAttack,
)

from ..game.Player.items.pickaxe import (
    Pickaxe,
)

from ..game.Settings.settings_modifier import (
    SettingsModifier,
)

from ..game.Settings.settings_ui_manager import (
    SettingsScreen,
    SettingsUIManager,
)

from ..game.ui_hotbar_integration import(
    UIHotbarIntegration,
)

from ..game.Map.interactive.loot_point import (
    LootWindow,
)

from ..game.Map.interactive.quest_point import (
    QuestPoint,
)

from ..game.Quest.quest_manager import (
    QuestEntry,
    QuestManager,
)

from ..game.Map.interactive.forge import ForgeWindow

from ..game.Quest.quest_menu import (
    QuestMenu,
)


from .Title import (
    Application,
    GameEngine,
    MainMenuManager,
    TitleScreen,
)

from .playerRenderer import (
    PlayerRenderer,
)

# PLAYER

class GameplayPlayerStub(SimpleNamespace):

    def equipped_weapon_type(self):
        return None

# PLAY STATE INITIALISATION

def initialize_play_state(
    screen_size,
    on_quit_game,
    settings_screen,
    map_manager,
):
    
    """
    Creates all systems that belong to the player/gameplay state.
    """

    # PLAYER STATUS

    player_status = PlayerStatus()

    player = GameplayPlayerStub(
        health=player_status.current_health,
        max_health=player_status.max_health,

        mana=player_status.current_mana,
        max_mana=player_status.max_mana,

        level=player_status.player_level,
        gold=player_status.gold,
    )

    # INVENTORY

    inventory_manager = InventoryManager()

    hotbar = InventoryHotbar()

    inventory_screen = InventoryScreen(
        inventory_manager=inventory_manager,
        hotbar=hotbar,
    )

    hotbar_ui = UIHotbarIntegration(
        hotbar=hotbar,
        inventory_manager=inventory_manager,
    )

    loot_window = LootWindow(
        inventory_manager=inventory_manager,
    )

    # FORGE WINDOW

    forge_window = ForgeWindow(
        inventory_manager=inventory_manager,
    )

    # QUEST SYSTEM

    quest_manager = QuestManager()
    quest_menu = QuestMenu(
        quest_manager=quest_manager
    )

    # EQUIPMENT

    equipment_manager = EquipmentManager(
        inventory_manager=inventory_manager,
        player_status=player_status,
    )

    # PLAYER RENDERER

    player_renderer = PlayerRenderer(
        player
    )

    # PICKAXE

    pickaxe = Pickaxe(
        player=player,
        player_renderer=player_renderer,
        inventory_manager=inventory_manager,
    )


    # MOVEMENT


    movement_controller = PlayerController(
        player=player,
        player_status=player_status,
    )

    movement_controller.equipment_manager = (
        equipment_manager
    )


    # CHARACTER ATTACK


    character_attack = CharacterAttack(
        player_controller=movement_controller,
    )

    movement_controller._on_attack = (
        character_attack.start_attack
    )


    # PAUSE MENU


    pause_menu = PauseMenuManager(
        on_quit_game=on_quit_game,

        on_open_settings=(
            lambda:
            settings_screen.open()
            if settings_screen
            else None
        ),
    )

    pause_screen = PauseScreen(
        pause_menu=pause_menu,
        screen_size=screen_size,
    )


    # RETURN STATE


    return {

        "player": player,

        "player_status": player_status,

        "player_renderer": player_renderer,

        "inventory_manager": inventory_manager,

        "hotbar": hotbar,

        "hotbar_ui": hotbar_ui,

        "inventory_screen": inventory_screen,

        "quest_manager": quest_manager,

        "quest_menu": quest_menu,

        "loot_window": loot_window,

        "forge_window": forge_window,

        "equipment_manager": equipment_manager,

        "pickaxe": pickaxe,

        "movement_controller": movement_controller,

        "character_attack": character_attack,

        "pause_menu": pause_menu,

        "pause_screen": pause_screen,

        "map_manager": map_manager,

    }



# MAIN


def main():

    
    # PYGAME INITIALISATION
    

    pg.init()
    pg.font.init()

    screen = pg.display.set_mode(
        (1200, 800)
    )

    pg.display.set_caption(
        "A Game About Forging"
    )

    clock = pg.time.Clock()

    
    # MAP INITIALISATION
    

    base_dir = (
        Path(__file__).parent.parent.parent
    )

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

    map_manager.load_map("tutorial", spawn_id="default")

    print(
        "COLLISION OBJECT COUNT:",
        len(
            map_manager.current_map
            .collision_objects
        ),
    )

    
    # GLOBAL GAME STATE
    

    running = True

    game_state = "MENU"

    play_state = None

    player_speed = 4

    
    # RUNNING CONTROL
    

    def set_running(value):

        nonlocal running

        running = value

    
    # PLAYER INTERACTION
    

    def get_player_interaction():

        if play_state is None:
            return None

        player_rect = play_state[
            "player_rect"
        ]

        return (
            map_manager.current_map
            .get_interaction(
                player_rect
            )
        )

    
    # INTERACTION ACTIVATION
    

    def activate_interaction():

        if play_state is None:
            return

        interactive = (
            get_player_interaction()
        )

        if interactive is None:
            return

        print(
            "INTERACTION:",
            interactive.class_name,
        )

        
        # DOOR
        

        if interactive.class_name.lower() == "door":

            interactive.interact(
                play_state
            )

        
        # LOOT POINT
        

        elif (
            interactive.class_name.lower()
            == "loot_point"
        ):

            interactive.interact(
                play_state,
                screen.get_size(),
            )

        
        # MINING NODE
        

        elif (
            interactive.class_name.lower()
            in (
                "mining_node",
                "mining",
                "mine",
            )
        ):

            play_state["pickaxe"].mine(interactive)

        # QUEST POINT

        elif interactive.class_name.lower() == "quest_point":
            interactive.trigger(play_state)


        # FORGE 

        elif interactive.class_name.lower() == "forge":
            interactive.interact(
                play_state,
                screen.get_size(),
            )


    
    # INTERACTION PROMPT
    

    def draw_interaction_prompt(
        screen,
        text,
    ):

        font = pg.font.Font(
            None,
            28,
        )

        text_surface = font.render(
            text,
            True,
            (255, 255, 255),
        )

        padding = 10

        rect = text_surface.get_rect()

        rect.inflate_ip(
            padding * 2,
            padding * 2,
        )

        rect.center = (
            screen.get_width() // 2,
            screen.get_height() - 80,
        )

        pg.draw.rect(
            screen,
            (30, 30, 30),
            rect,
            border_radius=6,
        )

        pg.draw.rect(
            screen,
            (255, 255, 255),
            rect,
            2,
            border_radius=6,
        )

        screen.blit(
            text_surface,
            text_surface.get_rect(
                center=rect.center
            ),
        )

    
    # PLAYER MOVEMENT
    

    def update_player_position(
        keys_pressed
    ):

        if play_state is None:
            return

        player_rect = play_state[
            "player_rect"
        ]

        dx = 0
        dy = 0

        
        # INPUT
        

        if (
            keys_pressed[pg.K_w]
            or keys_pressed[pg.K_UP]
        ):
            dy -= player_speed

        if (
            keys_pressed[pg.K_s]
            or keys_pressed[pg.K_DOWN]
        ):
            dy += player_speed

        if (
            keys_pressed[pg.K_a]
            or keys_pressed[pg.K_LEFT]
        ):
            dx -= player_speed

        if (
            keys_pressed[pg.K_d]
            or keys_pressed[pg.K_RIGHT]
        ):
            dx += player_speed

        
        # NORMALISE
        

        if dx and dy:

            dx *= 0.7
            dy *= 0.7

        
        # HORIZONTAL COLLISION
        

        player_rect.x += int(dx)

        for blocker in (
            map_manager.current_map
            .collision_objects
        ):

            if blocker.collides_with_rect(
                player_rect
            ):

                if dx > 0:

                    player_rect.right = (
                        blocker.rect.left
                    )

                elif dx < 0:

                    player_rect.left = (
                        blocker.rect.right
                    )

        
        # VERTICAL COLLISION
        

        player_rect.y += int(dy)

        for blocker in (
            map_manager.current_map
            .collision_objects
        ):

            if blocker.collides_with_rect(
                player_rect
            ):

                if dy > 0:

                    player_rect.bottom = (
                        blocker.rect.top
                    )

                elif dy < 0:

                    player_rect.top = (
                        blocker.rect.bottom
                    )

        
        # POSITION
        

        play_state["world_position"] = [
            player_rect.x,
            player_rect.y,
        ]

        
        # CAMERA
        

        current_map = (
            map_manager.current_map
        )

        map_width = (
            current_map.pixels_width
        )

        map_height = (
            current_map.pixels_height
        )

        view_width, view_height = (
            screen.get_size()
        )

        max_camera_x = max(
            0,
            map_width - view_width,
        )

        max_camera_y = max(
            0,
            map_height - view_height,
        )

        camera_x = max(
            0,
            min(
                player_rect.centerx
                - view_width // 2,
                max_camera_x,
            ),
        )

        camera_y = max(
            0,
            min(
                player_rect.centery
                - view_height // 2,
                max_camera_y,
            ),
        )

        play_state["camera"] = [
            camera_x,
            camera_y,
        ]

    def process_pending_map_transition():

        if play_state is None:
            return

        transition = play_state.get(
            "pending_map_transition"
        )

        if transition is None:
            return

        # Prevent the same transition from
        # being processed every frame.
        play_state[
            "pending_map_transition"
        ] = None

        target_map = transition.get(
            "target_map"
        )

        spawn_id = transition.get(
            "spawn_id"
        )

        quest_point = transition.get(
            "quest_point"
        )

        print(
            f"[MAIN] Loading map: {target_map}, "
            f"spawn: {spawn_id}"
        )

        # LOAD TARGET MAP

        map_manager.load_map(
            target_map,
            spawn_id=spawn_id,
        )

        # GET NEW SPAWN POSITION

        spawn_x, spawn_y = (
            map_manager.spawn_position
        )

        # RESET PLAYER POSITION

        play_state[
            "player_rect"
        ] = pg.Rect(
            spawn_x,
            spawn_y,
            24,
            20,
        )

        play_state[
            "world_position"
        ] = [
            spawn_x,
            spawn_y,
        ]

        # RESET CAMERA

        view_width, view_height = (
            screen.get_size()
        )

        play_state[
            "camera"
        ] = [
            max(
                0,
                spawn_x - view_width // 2,
            ),
            max(
                0,
                spawn_y - view_height // 2,
            ),
        ]

        print(
            "[MAIN] Player moved to:",
            spawn_x,
            spawn_y,
        )

        # CONTINUE QUEST SEQUENCE

        if quest_point is not None:

            quest_point._step_complete(
                play_state
            )    


    
    # START PLAYING
    

    def trigger_play(
        scene_name=""
    ):

        nonlocal game_state
        nonlocal play_state

        print(
            f"Loading scene: {scene_name}"
        )

        if play_state is None:

            play_state = initialize_play_state(
                screen_size=screen.get_size(),

                on_quit_game=lambda:set_running(False),

                settings_screen=(settings_screen),

                map_manager=map_manager,
            )

            play_state["screen"] = screen
            play_state["map_manager"] = map_manager

            # PLAYER SPAWN
            

            spawn_x, spawn_y = map_manager.spawn_position
            

            play_state[
                "player_rect"
            ] = pg.Rect(
                spawn_x,
                spawn_y,
                24,
                20,
            )

            play_state[
                "world_position"
            ] = [
                spawn_x,
                spawn_y,
            ]

            
            # CAMERA
            

            view_width, view_height = (
                screen.get_size()
            )

            play_state[
                "camera"
            ] = [

                max(
                    0,
                    spawn_x
                    - view_width // 2,
                ),

                max(
                    0,
                    spawn_y
                    - view_height // 2,
                ),
            ]

            
            # MOVEMENT CALLBACK
            

            play_state[
                "movement_controller"
            ]._on_move = (
                update_player_position
            )

        game_state = "PLAYING"

    
    # SETTINGS
    

    settings_ui = SettingsUIManager()

    settings_modifier = SettingsModifier(
        current_config=(
            settings_ui.current_config
        ),
    )

    settings_screen = SettingsScreen(
        settings_ui=settings_ui,
        modifier=settings_modifier,
    )

    
    # MENU
    

    engine = GameEngine(
        on_load_scene=trigger_play,
    )

    app = Application(
        on_quit=set_running,
    )

    menu_manager = MainMenuManager(
        game_engine=engine,
        application=app,
        on_open_settings=(
            lambda:
            settings_screen.open()
        ),
    )

    title_screen = TitleScreen(
        title_menu=menu_manager,
        screen_size=(1200, 800),
    )

    
    # GAME LOOP
    

    while running:

        
        # EVENTS
        

        events = pg.event.get()

        for event in events:

            
            # QUIT
            

            if event.type == pg.QUIT:

                running = False
                continue

            
            # SETTINGS
            

            if settings_screen.is_open:

                settings_screen.handle_event(
                    event
                )

                continue

            
            # MENU
            

            if game_state == "MENU":

                title_screen.handle_event(
                    event
                )

                continue


            # GAMEPLAY EVENTS

            if (
                game_state == "PLAYING"
                and play_state is not None
            ):

                # LOOT WINDOW

                if play_state["loot_window"].is_open:

                    if play_state["loot_window"].handle_event(event):
                        continue


                # FORGE WINDOW

                if play_state["forge_window"].is_open:

                    if play_state["forge_window"].handle_event(event):
                        continue


                # ESCAPE

                if (
                    event.type == pg.KEYDOWN
                    and event.key == pg.K_ESCAPE
                ):

                    play_state[
                        "pause_menu"
                    ].toggle_pause_menu()

                    continue


                # HOTBAR SELECTION

                if event.type == pg.KEYDOWN:

                    if play_state[
                        "hotbar_ui"
                    ].handle_keydown(event.key):

                        selected_item = (
                            play_state[
                                "hotbar_ui"
                            ].get_selected_item()
                        )

                        print(
                            "Selected hotbar item:",
                            getattr(
                                selected_item,
                                "name",
                                None,
                            ),
                        )

                        continue


                # INVENTORY

                if (
                    event.type == pg.KEYDOWN
                    and event.key == pg.K_i
                ):

                    play_state[
                        "inventory_screen"
                    ].toggle()

                    continue


                if play_state[
                    "inventory_screen"
                ].is_open:

                    if play_state[
                        "inventory_screen"
                    ].handle_event(event):

                        continue


                # INTERACTION

                if (
                    event.type == pg.KEYDOWN
                    and event.key == pg.K_e
                ):

                    if not (
                        play_state[
                            "pause_menu"
                        ].is_paused
                    ):

                        activate_interaction()

                    continue
                
                # PAUSE MOUSE
                

                if (
                    event.type
                    == pg.MOUSEBUTTONDOWN
                    and event.button == 1
                    and play_state[
                        "pause_menu"
                    ].is_paused
                ):

                    play_state[
                        "pause_screen"
                    ].handle_event(
                        event
                    )

        
        # UPDATE
        

        if (
            game_state == "PLAYING"
            and play_state is not None
            # and not play_state["pause_menu"].is_paused
        ):

            keys_pressed = pg.key.get_pressed()

            mouse_buttons = (pg.mouse.get_pressed(3))

            # QUEST + MAP TRANSITIONS

            process_pending_map_transition()

            
            # MOVEMENT INPUT
            

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

            
            # MOVEMENT
            

            update_player_position(
                keys_pressed
            )

            
            # CONTROLLER
            

            play_state[
                "movement_controller"
            ].handle_input(
                keys_pressed,
                mouse_buttons=mouse_buttons,
            )

            
            # ATTACK UPDATE
            

            play_state[
                "character_attack"
            ].update()

            
            # PICKAXE UPDATE
            

            play_state[
                "pickaxe"
            ].update()

            
            # PLAYER ANIMATION
            

            play_state[
                "player_renderer"
            ].update(
                axis_scancodes_held,
                keys_pressed,
                mouse_buttons,
            )

        
        # DRAW
        

        screen.fill(
            (0, 0, 0)
        )

        
        # MENU
        

        if game_state == "MENU":

            title_screen.render(
                screen
            )

        
        # GAMEPLAY
        

        elif (
            game_state == "PLAYING"
            and play_state is not None
        ):

            camera_x, camera_y = (
                play_state.get(
                    "camera",
                    (0, 0),
                )
            )

            
            # MAP
            

            map_manager.current_map.render(
                screen,
                camera_x,
                camera_y,
            )

            
            # PLAYER
            

            screen_center = (
                screen.get_width() // 2,
                screen.get_height() // 2,
            )

            play_state[
                "player_renderer"
            ].draw_player(
                screen,
                screen_center,
            )

            # HOTBAR

            play_state[
                "hotbar_ui"
            ].draw(
                screen
            )
            
            # INTERACTION PROMPT
            
            interactive = (
                get_player_interaction()
            )

            if interactive is not None:

                prompt_text = (
                    f"E  "
                    f"{interactive.class_name}"
                )

                draw_interaction_prompt(
                    screen,
                    prompt_text,
                )

            
            # INVENTORY

            if play_state[
                "inventory_screen"
            ].is_open:

                play_state[
                    "inventory_screen"
                ].draw(
                    screen,
                    None,
                )


            # LOOT WINDOW

            if play_state[
                "loot_window"
            ].is_open:

                play_state[
                    "loot_window"
                ].draw(
                    screen
                )


            # FORGE WINDOW

            if play_state[
                "forge_window"
            ].is_open:

                play_state[
                    "forge_window"
                ].draw(
                    screen
                )

            
            # PAUSE
            

            if play_state["pause_menu"].is_paused:

                play_state["pause_screen"].render(screen)

        
        # SETTINGS
        

        if settings_screen.is_open:

            settings_screen.draw(
                screen
            )

        
        # DISPLAY
        

        pg.display.flip()

        clock.tick(60)

    
    # SHUTDOWN
    

    pg.quit()
    sys.exit()



# ENTRY POINT


if __name__ == "__main__":
    main()