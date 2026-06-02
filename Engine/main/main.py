import pygame
import sys

def main(): # Main game loop
    from .agaf import Player, Item, Inventory, World #, Ore, Enemy, UpgradeTree, UI
    from .renderer import PlayerRenderer, UIRenderer #, OreRenderer, EnemyRenderer
    from ..config.config import (
        KEYBINDS,
        QUIT_KEY,
        SCREEN_CLEAR_COLOR,
        SCREEN_HEIGHT,
        SCREEN_WIDTH,
        TARGET_FPS,
        WINDOW_TITLE,
    )

    # Initialize pygame
    pygame.init()
    
    # Create windowed mode
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    
    # Clock for FPS
    clock = pygame.time.Clock()
    
    # Initialize game entities
    player = Player(0, 0)
    world = World(player)
    
    # Initialize sprite renderer
    player_renderer = PlayerRenderer(player)
    
    # Initialize UI renderer
    ui_renderer = UIRenderer(player)

    # Per-axis scancode sets: classify movement on KEYDOWN (event.key), release on KEYUP
    # (event.scancode) so macOS/SDL mismatched KEYUP key codes don't stick or break input.
    # key_to_scancode() can disagree with event.scancode — do not use it for comparisons.
    axis_scancodes_held = {axis: set() for axis in KEYBINDS}
    
    # Game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == QUIT_KEY:
                    running = False
                else:
                    for axis, keys in KEYBINDS.items():
                        if event.key in keys:
                            axis_scancodes_held[axis].add(event.scancode)
            elif event.type == pygame.KEYUP:
                for axis in KEYBINDS:
                    axis_scancodes_held[axis].discard(event.scancode)
            elif event.type == pygame.WINDOWFOCUSLOST:
                for held in axis_scancodes_held.values():
                    held.clear()
        
        keys_pressed = pygame.key.get_pressed()
        # Update player sprite (shift/sprint uses keys_pressed; movement uses axis_scancodes_held)
        player_renderer.update(axis_scancodes_held, keys_pressed)
        
        # Update UI
        ui_renderer.update_ui()
        
        # Clear screen (dark background)
        screen.fill(SCREEN_CLEAR_COLOR)
        
        # Draw player in center of screen
        player_center_x = SCREEN_WIDTH // 2
        player_center_y = SCREEN_HEIGHT // 2
        player_renderer.draw_player(screen, (player_center_x, player_center_y))
        
        # Draw UI (User Status bars in top-left)
        ui_renderer.draw_ui(screen)
        
        # Update display
        pygame.display.flip()
        
        # Cap frame rate
        clock.tick(TARGET_FPS)
    
    # Cleanup
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main() 