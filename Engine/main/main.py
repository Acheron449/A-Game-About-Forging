import pygame
import sys
from pathlib import Path

from ..config.config import config

from ..game.inventory import InventoryItem, InventoryManager, InventoryScreen
from ..game.inventory_hotbar import InventoryHotbar
from ..game.pause_menu_manager import PauseMenuManager, PauseScreen
from ..game.save_manager import SaveManager
from ..game.settings_modifier import SettingsModifier
from ..game.settings_ui_manager import SettingsScreen, SettingsUIManager
from .Title import Application, GameEngine, MainMenuManager, TitleScreen


def main(): # Main game loop
    from .agaf import Player, Item, Inventory, World #, Ore, Enemy, UpgradeTree, UI
    from .renderer import PlayerRenderer, UIRenderer #, OreRenderer, EnemyRenderer

    # Initialize pygame
    pygame.init()
    pygame.font.init()

    # Create windowed mode
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(config.WINDOW_TITLE)

    # Clock for FPS
    clock = pygame.time.Clock()

    # Initialize game entities
    player = Player(0, 0)
    world = World(player)

    # Initialize sprite renderer
    player_renderer = PlayerRenderer(player)

    # Initialize UI renderer
    ui_renderer = UIRenderer(player)

    # Title-screen state
    scene_state = {'name': config.SCENE_MAIN_MENU}
    running_state = {'running': True}
    title_prompt_text = {'message': ''}

    def on_load_scene(scene_name: str) -> None:
        scene_state['name'] = scene_name

    def on_apply_save_data(save_data: dict) -> None:
        player.health = save_data.get('health', getattr(player, 'health', 0))
        player.max_health = save_data.get('max_health', getattr(player, 'max_health', 0))
        player.mana = save_data.get('mana', getattr(player, 'mana', 0))
        player.max_mana = save_data.get('max_mana', getattr(player, 'max_mana', 0))
        player.level = save_data.get('level', getattr(player, 'level', 1))
        player.gold = save_data.get('gold', getattr(player, 'gold', 0))

    def on_initialize_game_start() -> None:
        on_load_scene('TutorialLevel')

    def on_display_prompt(message: str) -> None:
        title_prompt_text['message'] = message

    def on_quit() -> None:
        running_state['running'] = False

    def apply_runtime_settings(configuration) -> None:
        """Apply settings that Pygame can change immediately."""
        nonlocal screen
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(configuration.music_volume * configuration.master_volume)
        try:
            width, height = (int(value.strip()) for value in configuration.resolution.split('x', 1))
            screen = pygame.display.set_mode((width, height))
            title_screen.screen_size = (width, height)
            pause_screen.screen_size = (width, height)
        except (TypeError, ValueError):
            pass

    def capture_current_state() -> dict:
        return {
            'health': getattr(player, 'health', 0),
            'max_health': getattr(player, 'max_health', 0),
            'mana': getattr(player, 'mana', 0),
            'max_mana': getattr(player, 'max_mana', 0),
            'level': getattr(player, 'level', 1),
            'gold': getattr(player, 'gold', 0),
            'scene': 'MainWorld',
        }

    settings_ui = SettingsUIManager(on_apply_engine=apply_runtime_settings)
    settings_modifier = SettingsModifier(current_config=settings_ui.current_config)
    settings_screen = SettingsScreen(
        settings_ui,
        settings_modifier,
        on_close=lambda: setattr(title_menu, 'is_settings_menu_open', False),
    )

    def open_settings() -> None:
        settings_screen.open()

    save_manager = SaveManager()
    pause_menu = PauseMenuManager(
        save_manager=save_manager,
        on_capture_state=capture_current_state,
        on_notification=on_display_prompt,
        on_open_settings=open_settings,
        on_return_main_menu=lambda: on_load_scene(config.SCENE_MAIN_MENU),
        on_quit_game=on_quit,
    )

    title_menu = MainMenuManager(
        game_engine=GameEngine(
            on_load_scene=on_load_scene,
            on_apply_save_data=on_apply_save_data,
            on_initialize_game_start=on_initialize_game_start,
        ),
        application=Application(on_quit=on_quit),
        on_display_prompt=on_display_prompt,
        on_open_settings=open_settings,
        user_confirms=lambda: True,
    )
    settings_modifier._on_warning = lambda message: setattr(settings_screen, 'status_message', message)

    title_screen = TitleScreen(title_menu, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pause_screen = PauseScreen(pause_menu, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

    inventory_manager = InventoryManager()
    inventory_hotbar = InventoryHotbar()
    inventory_screen = InventoryScreen(inventory_manager, inventory_hotbar)
    weapon_icons = Path(config.RESOURCES_PATH) / 'UI' / 'Items' / 'Arms' / '32 Free Weapon Icons' / 'Icons'
    inventory_manager.bag_slots[0].set_item(InventoryItem('Forged Sword', 'weapon', weapon_icons / 'Iicon_32_01.png'))
    inventory_manager.bag_slots[3].set_item(InventoryItem('Iron Ingot', 'material', weapon_icons / 'Iicon_32_12.png', quantity=12))
    inventory_manager.bag_slots[12].set_item(InventoryItem('Runic Blade', 'weapon', weapon_icons / 'Iicon_32_06.png'))
    inventory_hotbar.hotbar_slots[0].set_item(InventoryItem('Health Tonic', 'consumable', weapon_icons / 'Iicon_32_13.png', quantity=3))

    # Per-axis scancode sets: classify movement on KEYDOWN (event.key), release on KEYUP
    # (event.scancode) so macOS/SDL mismatched KEYUP key codes don't stick or break input.
    # key_to_scancode() can disagree with event.scancode — do not use it for comparisons.
    axis_scancodes_held = {axis: set() for axis in config.KEYBINDS}

    # Game loop
    while running_state['running']:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_state['running'] = False
            elif event.type == pygame.KEYDOWN:
                if settings_screen.is_open:
                    settings_screen.handle_event(event)
                elif event.key == config.QUIT_KEY:
                    if scene_state['name'] == config.SCENE_MAIN_MENU:
                        running_state['running'] = False
                    elif inventory_screen.is_open:
                        inventory_screen.close()
                    else:
                        pause_menu.toggle_pause_menu()
                    for held in axis_scancodes_held.values():
                        held.clear()
                elif scene_state['name'] != config.SCENE_MAIN_MENU and event.key == pygame.K_i and not pause_menu.is_paused:
                    inventory_screen.toggle()
                    for held in axis_scancodes_held.values():
                        held.clear()
                else:
                    for axis, keys in config.KEYBINDS.items():
                        if event.key in keys:
                            axis_scancodes_held[axis].add(event.scancode)
            elif event.type == pygame.KEYUP:
                for axis in config.KEYBINDS:
                    axis_scancodes_held[axis].discard(event.scancode)
            elif event.type == pygame.WINDOWFOCUSLOST:
                for held in axis_scancodes_held.values():
                    held.clear()
            elif settings_screen.is_open:
                settings_screen.handle_event(event)
            elif inventory_screen.is_open:
                inventory_screen.handle_event(event)
            elif scene_state['name'] == config.SCENE_MAIN_MENU and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                title_screen.handle_event(event)
            elif pause_menu.is_paused and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pause_screen.handle_event(event)

            if scene_state['name'] == config.SCENE_MAIN_MENU:
                title_screen.render(screen)
            else:
                if not pause_menu.is_paused and not inventory_screen.is_open:
                    keys_pressed = pygame.key.get_pressed()
                    # Update player sprite (shift/sprint uses keys_pressed; movement uses axis_scancodes_held)
                    player_renderer.update(axis_scancodes_held, keys_pressed)

                    # Update UI
                    ui_renderer.update_ui()

                # Keep the latest gameplay frame visible underneath modal overlays.
                screen.fill(config.SCREEN_CLEAR_COLOR)

                # Draw player in center of screen
                player_center_x, player_center_y = (value // 2 for value in screen.get_size())
                player_renderer.draw_player(screen, (player_center_x, player_center_y))

                # Draw UI (User Status bars in top-left)
                ui_renderer.draw_ui(screen)
                inventory_screen.draw(screen, player_renderer.current_sprite)
                pause_screen.render(screen)

        settings_screen.draw(screen)

        # Update display
        pygame.display.flip()

        # Cap frame rate
        clock.tick(settings_ui.current_config.fps_limit or config.TARGET_FPS)

    # Cleanup
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main() 
