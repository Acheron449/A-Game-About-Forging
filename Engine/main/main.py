import pygame
import sys

def main():
    from .agaf import Player, Item, Inventory, World
    from .renderer import PlayerRenderer, UIRenderer

    # Initialize pygame
    pygame.init()
    
    # Set window resolution
    screen_width = 1352
    screen_height = 878
    
    # Create windowed mode
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("A Game About Forging")
    
    # Clock for FPS
    clock = pygame.time.Clock()
    fps = 60
    
    # Initialize game entities
    player = Player(0, 0)
    world = World(player)
    
    # Initialize sprite renderer
    player_renderer = PlayerRenderer(player)
    
    # Initialize UI renderer
    ui_renderer = UIRenderer(player)
    
    # Game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Get pressed keys
        keys_pressed = pygame.key.get_pressed()
        
        # Update player sprite
        player_renderer.update(keys_pressed)
        
        # Update UI
        ui_renderer.update_ui()
        
        # Clear screen (dark background)
        screen.fill((20, 20, 20))
        
        # Draw player in center of screen
        player_center_x = screen_width // 2
        player_center_y = screen_height // 2
        player_renderer.draw_player(screen, (player_center_x, player_center_y))
        
        # Draw UI (HP and Mana bars in top-left)
        ui_renderer.draw_ui(screen)
        
        # Update display
        pygame.display.flip()
        
        # Cap frame rate
        clock.tick(fps)
    
    # Cleanup
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main() 