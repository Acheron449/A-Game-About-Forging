"""Title screen and main menu flow (mainmenumanager.txt)."""

from __future__ import annotations

import pygame
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from Contents.Engine.configuration.constants import config, get_game_font
from ..game.save_manager import SaveManager
from ..game.ui_manager import UIManager


@dataclass
class MenuButton:
    """Represents a title menu button and its enabled state."""
    # Store the stable identifier used by input handling and rendering.
    id: str
    # Store the human-readable label shown to the player.
    label: str
    # Keep unavailable actions visible while preventing them from being selected.
    enabled: bool = True


class GameEngine:
    """Scene and save hooks referenced by the title menu pseudocode."""

    def __init__(
        self,
        on_load_scene: Optional[Callable[[str], None]] = None,
        on_apply_save_data: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_initialize_game_start: Optional[Callable[[], None]] = None,
    ):
        # Keep optional callbacks outside the menu logic so the scene can be hosted by different front ends.
        self._on_load_scene = on_load_scene
        self._on_apply_save_data = on_apply_save_data
        self._on_initialize_game_start = on_initialize_game_start

    def load_scene(self, scene_name: str) -> None:
        # Forward a requested scene transition only when the host supplied a transition handler.
        if self._on_load_scene:
            self._on_load_scene(scene_name)

    def apply_save_data(self, save_data: Dict[str, Any]) -> None:
        # Pass validated save data to the game session without assuming how it is stored.
        if self._on_apply_save_data:
            self._on_apply_save_data(save_data)

    def initialize_game_start(self) -> None:
        # Let the host create fresh runtime state before the new save is applied.
        if self._on_initialize_game_start:
            self._on_initialize_game_start()


class Application:
    """Application-level actions from the title menu pseudocode."""

    def __init__(self, on_quit: Optional[Callable[[], None]] = None):
        # Store quitting as a callback so this small application adapter remains testable.
        self._on_quit = on_quit

    def quit(self) -> None:
        # Leave process and window shutdown to the application that owns the menu.
        if self._on_quit:
            self._on_quit()


class MainMenuManager:
    """Title screen flow for Continue / New Game / Settings / Quit."""

    MENU_ORDER = ['continue', 'new_game', 'settings', 'quit']
    BUTTON_LABELS = {
        'continue': 'Continue',
        'new_game': 'New Game',
        'settings': 'Settings',
        'quit': 'Quit Game',
    }

    def __init__(
        self,
        save_manager: Optional[SaveManager] = None,
        ui_manager: Optional[UIManager] = None,
        game_engine: Optional[GameEngine] = None,
        application: Optional[Application] = None,
        on_render_title: Optional[Callable[[str], None]] = None,
        on_render_buttons: Optional[Callable[[List[MenuButton]], None]] = None,
        on_display_prompt: Optional[Callable[[str], None]] = None,
        on_open_settings: Optional[Callable[[], None]] = None,
        user_confirms: Optional[Callable[[], bool]] = None,
    ):
        # Read shared configuration once and establish the title-screen state before rendering.
        self.game_title = config.WINDOW_TITLE
        self.is_settings_menu_open = False
        self.save_manager = save_manager or SaveManager()
        self.ui_manager = ui_manager or UIManager()
        self.game_engine = game_engine or GameEngine()
        self.application = application or Application()
        self._on_render_title = on_render_title
        self._on_render_buttons = on_render_buttons
        self._on_display_prompt = on_display_prompt
        self._on_open_settings = on_open_settings
        self._user_confirms = user_confirms or (lambda: True)

        self.button_states: Dict[str, bool] = {
            # Start every action enabled; Continue is corrected from save data below.
            button_id: True for button_id in self.MENU_ORDER
        }
        self.prompt_message = ''
        self.initialize_menu()

    def initialize_menu(self) -> None:
        """Prepare the title menu and render the initial state."""
        # Clear stale prompts whenever the title screen is entered.
        self.prompt_message = ''
        # Render the title before controls so the host can establish the scene in order.
        self.render_title(self.game_title)
        # Continue is the only button whose availability depends on external state.
        self.update_continue_button_state()
        # Publish the final initial button model to the renderer.
        self.render_buttons()

    def handle_input(self, button_clicked: str) -> None:
        """Route title menu button presses to the matching handler."""
        # Map public button identifiers to their corresponding behavior.
        handlers = {
            'continue': self.on_continue_clicked,
            'new_game': self.on_new_game_clicked,
            'settings': self.on_settings_clicked,
            'quit': self.on_quit_clicked,
        }
        # Ignore unknown identifiers instead of allowing malformed input to crash the menu.
        handler = handlers.get(button_clicked)
        if handler:
            # Execute the action, then redraw so state changes become visible immediately.
            handler()
            self.render_buttons()

    def on_continue_clicked(self) -> None:
        """Continue from the latest save if it is valid."""
        # Ask the save manager for the most recent candidate before validating it.
        save_file = self.save_manager.retrieve_last_known_save()
        # A recognized save is applied before entering the main world.
        if self.save_manager.is_recognized(save_file):
            self.game_engine.apply_save_data(save_file)
            self.game_engine.load_scene(config.SCENE_MAIN_WORLD)
        else:
            # Keep the player on the title screen when no usable save exists.
            self.display_prompt('Save file corrupted or missing.')

    def on_new_game_clicked(self) -> None:
        """Start a new game after a confirmation prompt."""
        # Warn before creating a save because the operation may replace an automatic save.
        self.display_prompt('Are you sure? This may overwrite previous auto-saves.')
        if self.user_confirms():
            # Build clean data, initialize runtime state, and load the tutorial in that order.
            new_save = self.save_manager.create_new_save_file()
            self.game_engine.initialize_game_start()
            self.game_engine.apply_save_data(new_save)
            self.game_engine.load_scene(config.SCENE_TUTORIAL)

    def on_settings_clicked(self) -> None:
        """Open the settings screen from the title screen."""
        # Keep this handler small so all settings-opening behavior has one owner.
        self.open_settings_screen()

    def open_settings_screen(self) -> None:
        """Open the settings overlay and notify the host UI if requested."""
        # Record the overlay state locally and synchronize the shared UI manager.
        self.is_settings_menu_open = True
        self.ui_manager.toggle_settings_menu(True)
        if self._on_open_settings:
            # Notify an optional scene host after the UI manager has been updated.
            self._on_open_settings()
        self.display_prompt('Settings menu opened.')

    def on_quit_clicked(self) -> None:
        """Prompt before quitting the game."""
        # Require the same confirmation path used for other destructive navigation actions.
        self.display_prompt('Are you sure you want to quit?')
        if self.user_confirms():
            self.application.quit()

    def update_continue_button_state(self) -> None:
        """Enable or disable Continue automatically based on save presence."""
        # The save manager owns filesystem details; the menu only reflects its answer.
        if self.save_manager.check_for_existing_save():
            self.enable_button('continue')
        else:
            self.disable_button('continue')

    def get_button_data(self) -> List[MenuButton]:
        """Return the current title button states for rendering."""
        # Convert internal state into ordered view data without exposing the mutable dictionary.
        return [
            MenuButton(
                id=button_id,
                label=self.BUTTON_LABELS[button_id],
                enabled=self.button_states.get(button_id, True),
            )
            for button_id in self.MENU_ORDER
        ]

    def render_title(self, title: str) -> None:
        # Rendering is optional because headless tests can inspect state through callbacks.
        if self._on_render_title:
            self._on_render_title(title)

    def render_buttons(self) -> None:
        # Always derive a fresh button list so callbacks see current enabled values.
        if self._on_render_buttons:
            self._on_render_buttons(self.get_button_data())

    def enable_button(self, button_name: str) -> None:
        # Mark the action available, then publish the update to the renderer.
        self.button_states[button_name] = True
        if self._on_render_buttons:
            self._on_render_buttons(self.get_button_data())

    def disable_button(self, button_name: str) -> None:
        # Mark the action unavailable while retaining it in the menu layout.
        self.button_states[button_name] = False
        if self._on_render_buttons:
            self._on_render_buttons(self.get_button_data())

    def display_prompt(self, message: str) -> None:
        # Keep the latest prompt in state even when no visual callback is attached.
        self.prompt_message = message
        if self._on_display_prompt:
            self._on_display_prompt(message)

    def user_confirms(self) -> bool:
        # Delegate confirmation to the injected UI or the default affirmative test behavior.
        return self._user_confirms()


class TitleScreen:
    """Render the title-screen panel, menu buttons, and prompt text."""

    BACKGROUND_COLOR = (24, 24, 28)
    PANEL_COLOR = (34, 34, 44)
    PANEL_BORDER_COLOR = (180, 130, 80)
    BUTTON_COLOR = (80, 68, 52)
    BUTTON_DISABLED_COLOR = (64, 64, 64)
    BUTTON_BORDER_COLOR = (220, 200, 160)
    TEXT_COLOR = (236, 216, 180)
    SUBTEXT_COLOR = (220, 220, 220)
    PROMPT_COLOR = (210, 210, 210)

    def __init__(self, title_menu: MainMenuManager, screen_size: tuple[int, int]):
        self.title_menu = title_menu
        self.screen_size = screen_size
        self.title_font = get_game_font(88)
        self.button_font = get_game_font(30)
        self.prompt_font = get_game_font(24)
        self.button_rects: list[tuple[MenuButton, pygame.Rect]] = []

    def render(self, screen: pygame.Surface) -> None:
        screen.fill(self.BACKGROUND_COLOR)
        width, height = self.screen_size

        panel_width = 800
        panel_height = 700
        panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
        panel_rect.center = (width // 2, height // 2)
        pygame.draw.rect(screen, self.PANEL_COLOR, panel_rect, border_radius=28)
        pygame.draw.rect(screen, self.PANEL_BORDER_COLOR, panel_rect, width=3, border_radius=28)

        title_surface = self.title_font.render(self.title_menu.game_title, True, self.TEXT_COLOR)
        title_rect = title_surface.get_rect(midtop=(width // 2, panel_rect.top + 52))
        screen.blit(title_surface, title_rect)

        subtitle_text = 'Continue your journey through the forge'
        subtitle_surface = self.button_font.render(subtitle_text, True, self.SUBTEXT_COLOR)
        subtitle_rect = subtitle_surface.get_rect(midtop=(width // 2, title_rect.bottom + 16))
        screen.blit(subtitle_surface, subtitle_rect)

        self.button_rects = self.layout_buttons(panel_rect)
        for button, rect in self.button_rects:
            button_color = self.BUTTON_COLOR if button.enabled else self.BUTTON_DISABLED_COLOR
            pygame.draw.rect(screen, button_color, rect, border_radius=18)
            pygame.draw.rect(screen, self.BUTTON_BORDER_COLOR, rect, width=3, border_radius=18)
            label_surface = self.button_font.render(button.label, True, self.TEXT_COLOR if button.enabled else (180, 180, 180))
            label_rect = label_surface.get_rect(center=rect.center)
            screen.blit(label_surface, label_rect)

        prompt_text = self.title_menu.prompt_message
        if prompt_text:
            prompt_surface = self.prompt_font.render(prompt_text, True, self.PROMPT_COLOR)
            prompt_rect = prompt_surface.get_rect(midtop=(width // 2, panel_rect.bottom - 48))
            screen.blit(prompt_surface, prompt_rect)

    def layout_buttons(self, panel_rect: pygame.Rect) -> list[tuple[MenuButton, pygame.Rect]]:
        buttons = self.title_menu.get_button_data()
        button_width = 360
        button_height = 64
        spacing = 16
        total_height = len(buttons) * button_height + (len(buttons) - 1) * spacing
        top = panel_rect.centery - total_height // 2 + 34

        rects: list[tuple[MenuButton, pygame.Rect]] = []
        for index, button in enumerate(buttons):
            rect = pygame.Rect(0, 0, button_width, button_height)
            rect.centerx = panel_rect.centerx
            rect.top = top + index * (button_height + spacing)
            rects.append((button, rect))
        return rects

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        for button, rect in self.button_rects:
            if rect.collidepoint(event.pos) and button.enabled:
                self.title_menu.handle_input(button.id)
                break
