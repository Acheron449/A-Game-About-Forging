import pygame as pg
import sys
from pathlib import Path
import pytmx

# --- Path Setup ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parents[3] 
sys.path.append(str(project_root)) 

# Game Dependencies
from ..game.Settings.settings_ui_manager import SettingsScreen, SettingsUIManager
from .Title import Application, GameEngine, MainMenuManager, TitleScreen
from .renderer import PlayerRenderer, UIRenderer
from .worldRenderer import worldRenderer
from ..game.Map.map_loader import TiledMap


def main(): 
    pg.init()
    pg.font.init()
    
    screen = pg.display.set_mode((800, 600))
    pg.display.set_caption("A Game About Forging")

    # 1. --- Pre-load the Map --- 
    try:
        base_dir = Path(__file__).parent.parent.parent 
        map_json_path = base_dir / 'Engine' / 'Resources' / 'World' /'maps'/ 'tmx' / 'cave.tmx'
        tmx_data = pytmx.load_pygame(str(map_json_path), pixelalpha=True) 
        game_map = TiledMap(tmx_data, map_json_path.parent)
    except Exception as e:
        print(f"CRITICAL ERROR DURING MAP INITIALIZATION: {e}")
        return 

    # 2. --- State Setup and Menu Callbacks ---
    game_state = "MENU" 
    running = True

    # These functions allow the menu to talk to our main loop!
    def trigger_play(scene_name=""):
        nonlocal game_state # This tells Python to modify the game_state variable above
        print(f"Loading scene: {scene_name}. Switching to PLAYING state!")
        game_state = "PLAYING"

    def trigger_quit():
        nonlocal running
        print("Quit button pressed. Closing game...")
        running = False

    # 3. --- Initialize Your UI/Menu Managers ---
    # We pass our custom functions into your engines
    engine = GameEngine(on_load_scene=trigger_play)
    app = Application(on_quit=trigger_quit)
    
    # Initialize the menu and title screen
    menu_manager = MainMenuManager(game_engine=engine, application=app)
    title_screen = TitleScreen(title_menu=menu_manager, screen_size=(800, 600))

    # --- THE GAME LOOP ---
    clock = pg.time.Clock()
    
    while running:
        # --- PROCESS EVENTS (Input) ---
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            
            # Feed mouse clicks directly to the Title Screen!
            if game_state == "MENU":
                title_screen.handle_event(event)

        # --- RENDER GRAPHICS ---
        screen.fill((0, 0, 0)) 
        
        if game_state == "MENU":
            # Draw your main menu UI
            title_screen.render(screen)
            
        elif game_state == "PLAYING":
            # Render the game map
            game_map.render(screen)
        
        pg.display.flip()
        clock.tick(60)

    pg.quit()
    sys.exit()

if __name__ == '__main__':
    main()