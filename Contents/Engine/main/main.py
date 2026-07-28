import pygame
import sys
import os
from pathlib import Path
import pytmx # <-- Ensure this is present

# --- Path Setup ---
# This block MUST correctly point to the 'A-Game-About-Forging' root directory
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parents[3] 
# Add project root to path for sibling imports
sys.path.append(str(project_root)) 
# --- End Path Setup --- 

# Game Dependencies
from ..game.Settings.settings_ui_manager import SettingsScreen, SettingsUIManager
from .Title import Application, GameEngine, MainMenuManager, TitleScreen
from .renderer import PlayerRenderer, UIRenderer
from .worldRenderer import worldRenderer
from ..game.Map.map_loader import TiledMap


# --- Game Setup Function --- 

screen = pygame.display.set_mode((800, 600)) # Example screen size; adjust as needed

# --- Game Setup Function --- 
# (Removed the screen variable from out here)

def main(): # Main game loop
    # Initialize pygame FIRST
    pygame.init()
    pygame.font.init()
    
    # Create the screen AFTER initialization
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("A Game About Forging")

    # 1. --- Initialize Map Loading --- 
    try:
        base_dir = Path(__file__).parent.parent.parent 
        map_json_path = base_dir / 'Engine' / 'Resources' / 'World' /'maps'/ 'tmx' / 'cave.tmx'
        
        print(f"Attempting to load map from: {map_json_path}") 
        tmx_data = pytmx.load_pygame(str(map_json_path), pixelalpha=True) 
        game_map = TiledMap(tmx_data, map_json_path.parent)
    except FileNotFoundError: 
        print("CRITICAL ERROR: Map file not found at generated path.")
        return
    except Exception as e:
        print(f"CRITICAL ERROR DURING MAP INITIALIZATION: {e}")
        return 

    # --- THE GAME LOOP ---
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # 1. Process Events (Input)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        # 2. Update Game State (Player movement, physics, etc.)
        # (This is where your Application/GameEngine updates will go)
        
        # 3. Render Graphics
        screen.fill((0, 0, 0)) # Clear the screen with black each frame
        
        # Render our newly loaded map!
        game_map.render(screen)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate at 60 FPS
        clock.tick(60)

    # Clean exit when the loop breaks
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
