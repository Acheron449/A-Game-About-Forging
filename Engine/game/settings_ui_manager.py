"""Settings menu layout and apply (uimanagersettings.txt)."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

import pygame

from ..config.config import SETTINGS_CATEGORIES
from .game_configuration import GameConfiguration
from .settings_modifier import SettingsModifier


class SettingsUIManager:
    def __init__(
        self,
        config: Optional[GameConfiguration] = None,
        on_draw_category: Optional[Callable[[str], None]] = None,
        on_draw_panel: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        on_apply_engine: Optional[Callable[[GameConfiguration], None]] = None,
    ):
        self.current_config = config or GameConfiguration.load_from_file()
        self.active_category = 'General'
        self.categories: List[str] = list(SETTINGS_CATEGORIES)
        self._on_draw_category = on_draw_category
        self._on_draw_panel = on_draw_panel
        self._on_apply_engine = on_apply_engine

    def render_menu(self) -> None:
        for category in self.categories:
            if self._on_draw_category:
                self._on_draw_category(category)
        self.draw_settings_panel(self.active_category, self.current_config.to_dict())

    def draw_settings_panel(self, category: str, config_data: Dict[str, Any]) -> None:
        if self._on_draw_panel:
            self._on_draw_panel(category, config_data)

    def on_category_button_clicked(self, clicked_category: str) -> None:
        self.active_category = clicked_category
        self.refresh_settings_panel()

    def refresh_settings_panel(self) -> None:
        self.draw_settings_panel(self.active_category, self.current_config.to_dict())

    def on_apply_changes(self) -> None:
        self.current_config.save_to_file()
        if self._on_apply_engine:
            self._on_apply_engine(self.current_config)

    def load_configuration_from_file(self) -> GameConfiguration:
        self.current_config = GameConfiguration.load_from_file()
        return self.current_config


class SettingsScreen:
    """Interactive Pygame settings panel for the project's configuration model."""

    OVERLAY = (8, 13, 14, 215)
    PANEL = (91, 108, 109)
    PANEL_DARK = (47, 61, 61)
    PANEL_LIGHT = (113, 132, 131)
    ACCENT = (246, 207, 54)
    TEXT = (250, 242, 209)
    MUTED = (210, 204, 174)
    DANGER = (164, 76, 62)

    DIFFICULTIES = ('Story', 'Normal', 'Hard')
    FPS_CHOICES = (30, 60, 120)
    RESOLUTION_CHOICES = ('1280 x 720', '1352 x 878', '1920 x 1080')

    def __init__(
        self,
        settings_ui: SettingsUIManager,
        modifier: SettingsModifier,
        on_close: Optional[Callable[[], None]] = None,
    ) -> None:
        self.settings_ui = settings_ui
        self.modifier = modifier
        self._on_close = on_close
        self.is_open = False
        self.status_message = ''
        self.category_rects: List[tuple[str, pygame.Rect]] = []
        self.control_rects: Dict[str, pygame.Rect] = {}
        self.title_font = pygame.font.SysFont('serif', 36, bold=True)
        self.heading_font = pygame.font.SysFont('serif', 25, bold=True)
        self.label_font = pygame.font.SysFont('serif', 18, bold=True)
        self.text_font = pygame.font.SysFont('serif', 17)
        self.small_font = pygame.font.SysFont('serif', 14)

    def open(self) -> None:
        self.is_open = True
        self.status_message = ''

    def close(self) -> None:
        self.is_open = False
        self.status_message = ''
        if self._on_close:
            self._on_close()

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.is_open:
            return False
        if self.modifier.is_listening_for_input:
            handled = self.modifier.poll_keybind_capture(event)
            if handled:
                self.status_message = ''
            return handled
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close()
            return True
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        for category, rect in self.category_rects:
            if rect.collidepoint(event.pos):
                self.settings_ui.on_category_button_clicked(category)
                return True
        for control, rect in self.control_rects.items():
            if rect.collidepoint(event.pos):
                self._activate_control(control, event.pos[0])
                return True
        return True

    def draw(self, screen: pygame.Surface) -> None:
        if not self.is_open:
            return
        width, height = screen.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill(self.OVERLAY)
        screen.blit(overlay, (0, 0))
        panel = pygame.Rect(0, 0, min(860, width - 40), min(610, height - 40))
        panel.center = (width // 2, height // 2)
        pygame.draw.rect(screen, self.PANEL, panel, border_radius=12)
        pygame.draw.rect(screen, self.ACCENT, panel, width=3, border_radius=12)
        self.category_rects.clear()
        self.control_rects.clear()

        title = self.title_font.render('SETTINGS', True, self.ACCENT)
        screen.blit(title, (panel.left + 26, panel.top + 22))
        subtitle = self.small_font.render('Changes are saved when you select Apply Changes.', True, self.MUTED)
        screen.blit(subtitle, (panel.left + 28, panel.top + 66))

        sidebar = pygame.Rect(panel.left + 22, panel.top + 104, 190, panel.height - 174)
        pygame.draw.rect(screen, self.PANEL_DARK, sidebar, border_radius=8)
        self._draw_categories(screen, sidebar)
        content = pygame.Rect(sidebar.right + 22, sidebar.top, panel.right - sidebar.right - 44, sidebar.height)
        self._draw_category_content(screen, content)
        self._draw_footer(screen, panel)
        if self.modifier.is_listening_for_input:
            self._draw_key_capture(screen, panel)

    def _draw_categories(self, screen: pygame.Surface, rect: pygame.Rect) -> None:
        y = rect.top + 16
        for category in self.settings_ui.categories:
            button = pygame.Rect(rect.left + 10, y, rect.width - 20, 45)
            active = category == self.settings_ui.active_category
            if active:
                pygame.draw.rect(screen, self.PANEL_LIGHT, button, border_radius=6)
            text = self.heading_font.render(category, True, self.ACCENT if active else self.TEXT)
            screen.blit(text, text.get_rect(midleft=(button.left + 12, button.centery)))
            self.category_rects.append((category, button))
            y += 54

    def _draw_category_content(self, screen: pygame.Surface, rect: pygame.Rect) -> None:
        category = self.settings_ui.active_category
        heading = self.heading_font.render(category, True, self.ACCENT)
        screen.blit(heading, (rect.left, rect.top + 5))
        config = self.settings_ui.current_config
        if category == 'General':
            self._draw_choice(screen, rect, 55, 'Difficulty', config.difficulty, 'difficulty')
            self._draw_slider(screen, rect, 120, 'Mouse Sensitivity', config.mouse_sensitivity, 'mouse_sensitivity')
        elif category == 'Video':
            self._draw_choice(screen, rect, 55, 'Frames per second', str(config.fps_limit), 'fps_limit')
            self._draw_choice(screen, rect, 120, 'Resolution', config.resolution, 'resolution')
        elif category == 'Audio':
            self._draw_slider(screen, rect, 55, 'Master Volume', config.master_volume, 'master_volume')
            self._draw_slider(screen, rect, 120, 'Music', config.music_volume, 'music_volume')
            self._draw_slider(screen, rect, 185, 'Sound Effects', config.sfx_volume, 'sfx_volume')
        elif category == 'Directories':
            self._draw_readonly(screen, rect, 58, 'Save File Location', config.save_file_location)
            self._draw_readonly(screen, rect, 124, 'Game Directory', config.game_directory)
        elif category == 'Keybinds':
            self._draw_choice(screen, rect, 55, 'Attack', config.bind_attack, 'Bind_Attack')
            self._draw_choice(screen, rect, 120, 'Block', config.bind_block, 'Bind_Block')
            self._draw_choice(screen, rect, 185, 'Interact', config.bind_interact, 'Bind_Interact')

    def _draw_choice(self, screen: pygame.Surface, rect: pygame.Rect, y: int, label: str, value: str, control: str) -> None:
        label_surface = self.label_font.render(label, True, self.TEXT)
        screen.blit(label_surface, (rect.left, rect.top + y))
        button = pygame.Rect(rect.left + 205, rect.top + y - 8, min(230, rect.width - 205), 38)
        pygame.draw.rect(screen, self.PANEL_DARK, button, border_radius=6)
        pygame.draw.rect(screen, self.ACCENT, button, width=1, border_radius=6)
        value_surface = self.text_font.render(value, True, self.ACCENT)
        screen.blit(value_surface, value_surface.get_rect(midleft=(button.left + 12, button.centery)))
        arrow = self.small_font.render('CHANGE  ›', True, self.MUTED)
        screen.blit(arrow, arrow.get_rect(midright=(button.right - 8, button.centery)))
        self.control_rects[control] = button

    def _draw_slider(self, screen: pygame.Surface, rect: pygame.Rect, y: int, label: str, value: float, control: str) -> None:
        label_surface = self.label_font.render(label, True, self.TEXT)
        screen.blit(label_surface, (rect.left, rect.top + y))
        bar = pygame.Rect(rect.left + 205, rect.top + y + 7, min(230, rect.width - 205), 12)
        pygame.draw.rect(screen, self.PANEL_DARK, bar, border_radius=6)
        pygame.draw.rect(screen, self.ACCENT, (bar.left, bar.top, int(bar.width * value), bar.height), border_radius=6)
        knob_x = bar.left + int(bar.width * value)
        pygame.draw.circle(screen, self.TEXT, (knob_x, bar.centery), 9)
        percentage = self.text_font.render(f'{round(value * 100)}%', True, self.ACCENT)
        screen.blit(percentage, (bar.right + 10, rect.top + y - 2))
        self.control_rects[control] = pygame.Rect(bar.left, bar.top - 12, bar.width, 36)

    def _draw_readonly(self, screen: pygame.Surface, rect: pygame.Rect, y: int, label: str, value: str) -> None:
        label_surface = self.label_font.render(label, True, self.TEXT)
        screen.blit(label_surface, (rect.left, rect.top + y))
        value_surface = self.small_font.render(value, True, self.MUTED)
        screen.blit(value_surface, (rect.left, rect.top + y + 26))

    def _draw_footer(self, screen: pygame.Surface, panel: pygame.Rect) -> None:
        apply = pygame.Rect(panel.right - 300, panel.bottom - 52, 168, 34)
        close = pygame.Rect(panel.right - 120, panel.bottom - 52, 94, 34)
        pygame.draw.rect(screen, self.ACCENT, apply, border_radius=6)
        pygame.draw.rect(screen, self.DANGER, close, border_radius=6)
        apply_text = self.label_font.render('Apply Changes', True, self.PANEL_DARK)
        close_text = self.label_font.render('Close', True, self.TEXT)
        screen.blit(apply_text, apply_text.get_rect(center=apply.center))
        screen.blit(close_text, close_text.get_rect(center=close.center))
        self.control_rects['apply'] = apply
        self.control_rects['close'] = close
        if self.status_message:
            status = self.small_font.render(self.status_message, True, self.ACCENT)
            screen.blit(status, (panel.left + 28, panel.bottom - 42))

    def _draw_key_capture(self, screen: pygame.Surface, panel: pygame.Rect) -> None:
        overlay = pygame.Surface(panel.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, panel.topleft)
        prompt = self.heading_font.render('Press a key or mouse button  •  ESC cancels', True, self.ACCENT)
        screen.blit(prompt, prompt.get_rect(center=panel.center))

    def _activate_control(self, control: str, mouse_x: int) -> None:
        config = self.settings_ui.current_config
        if control == 'apply':
            self.settings_ui.on_apply_changes()
            self.status_message = 'Settings saved and applied.'
        elif control == 'close':
            self.close()
        elif control.startswith('Bind_'):
            self.modifier.initiate_keybind_change(control.removeprefix('Bind_'))
        elif control in ('mouse_sensitivity', 'master_volume', 'music_volume', 'sfx_volume'):
            rect = self.control_rects[control]
            value = max(0.0, min(1.0, (mouse_x - rect.left) / rect.width))
            self.modifier.handle_setting_change(control, round(value, 2))
        elif control == 'difficulty':
            config.difficulty = self._next_value(self.DIFFICULTIES, config.difficulty)
        elif control == 'fps_limit':
            config.fps_limit = int(self._next_value(tuple(map(str, self.FPS_CHOICES)), str(config.fps_limit)))
        elif control == 'resolution':
            config.resolution = self._next_value(self.RESOLUTION_CHOICES, config.resolution)

    @staticmethod
    def _next_value(options: tuple[str, ...], current: str) -> str:
        try:
            return options[(options.index(current) + 1) % len(options)]
        except ValueError:
            return options[0]
