"""User Status HUD: live HP/MP/Stamina reads and bar fill rendering."""

from __future__ import annotations

from typing import Any, Callable, Optional, Tuple

import pygame

from ..configuration.constants import config


class StatusBarTracker:
    """Reads one player stat each frame and exposes a 0–1 fill ratio."""

    stat_name: str = 'stat'

    def __init__(
        self,
        player: Any,
        current_attr: str,
        max_attr: str,
    ):
        self.player = player
        self.current_attr = current_attr # set the current attribute to the current attribute from the player
        self.max_attr = max_attr # set the max attribute to the max attribute from the player
        self.current_value = 0.0 # set the current value to 0.0
        self.max_value = 1.0 # set the max value to 1.0
        self.fill_ratio = 0.0 # set the fill ratio to 0.0

    def refresh(self) -> float:
        current = float(getattr(self.player, self.current_attr, 0))
        maximum = float(getattr(self.player, self.max_attr, 1))
        self.current_value = max(0.0, current)
        self.max_value = max(1.0, maximum)
        self.fill_ratio = self.current_value / self.max_value
        return self.fill_ratio # return the fill ratio


class HPStatusBar(StatusBarTracker):
    stat_name = 'hp' # set the stat name to 'hp'

    def __init__(self, player: Any):
        super().__init__(player, 'health', 'max_health') # initialize the HP status bar with the player and the current and max health attributes


class MPStatusBar(StatusBarTracker):
    stat_name = 'mp' # set the stat name to 'mp'

    def __init__(self, player: Any):
        super().__init__(player, 'mana', 'max_mana') # initialize the MP status bar with the player and the current and max mana attributes


class StaminaStatusBar(StatusBarTracker):
    stat_name = 'stamina' # set the stat name to 'stamina'

    def __init__(self, player: Any):
        super().__init__(player, 'stamina', 'max_stamina') # initialize the stamina status bar with the player and the current and max stamina attributes


class StatusBarFillRenderer:
    """Draws a single coloured fill rectangle for one bar slot."""

    def __init__(
        self,
        tracker: StatusBarTracker,
        slot: Tuple[int, int, int, int],
        color: Tuple[int, int, int],
    ): # initialize the status bar fill renderer with the tracker, slot, and color
        self.tracker = tracker
        self.slot_x, self.slot_y, self.slot_height, self.max_fill_width = slot # set the slot x, y, height, and max fill width to the slot x, y, height, and max fill width from the slot
        self.color = color # set the color to the color from the color

    def refresh(self) -> float:
        return self.tracker.refresh() # return the fill ratio

    def draw(
        self,
        screen: pygame.Surface,
        origin: Tuple[int, int], # set the origin to the origin from the origin
        scale: float,
    ) -> None: # draw the status bar fill renderer with the screen, origin, and scale
        ratio = self.tracker.fill_ratio
        if ratio <= 0: # if the fill ratio is less than or equal to 0, return
            return
        fill_width = max(1, int(self.max_fill_width * scale * ratio))
        fill_height = max(1, int(self.slot_height * scale))
        x = origin[0] + int(self.slot_x * scale) # calculate the x position of the fill
        y = origin[1] + int(self.slot_y * scale) # calculate the y position of the fill
        pygame.draw.rect(screen, self.color, pygame.Rect(x, y, fill_width, fill_height))


class UserStatusUI:
    """
    Composite User Status frame with HP (top), MP (middle), and Stamina (bottom).
    Fills are drawn behind the frame sprite each frame.
    """

    def __init__(
        self,
        player: Any,
        sprite_path: str = config.USER_STATUS_SPRITE_PATH,
        position: Tuple[int, int] = config.USER_STATUS_POSITION,
        scale: float = config.USER_STATUS_SCALE,
        on_status_change: Optional[Callable[[str, float, float], None]] = None,
    ):
        self.player = player
        self.position = position
        self.scale = scale
        self._on_status_change = on_status_change
        self.frame_surface = self._load_frame(sprite_path)
        self.hp_bar = StatusBarFillRenderer(
            HPStatusBar(player), config.USER_STATUS_HP_SLOT, config.USER_STATUS_HP_COLOR,
        )
        self.mp_bar = StatusBarFillRenderer(
            MPStatusBar(player), config.USER_STATUS_MP_SLOT, config.USER_STATUS_MP_COLOR,
        )
        self.stamina_bar = StatusBarFillRenderer(
            StaminaStatusBar(player), config.USER_STATUS_STAMINA_SLOT, config.USER_STATUS_STAMINA_COLOR,
        )
        self._bars = (self.hp_bar, self.mp_bar, self.stamina_bar)

    @staticmethod
    def _load_frame(sprite_path: str) -> Optional[pygame.Surface]:
        try:
            image = pygame.image.load(sprite_path)
            if pygame.display.get_surface() is not None:
                image = image.convert_alpha()
            return image
        except (pygame.error, FileNotFoundError) as exc:
            print(f'Failed to load User Status sprite: {exc}')
            return None

    def refresh_status(self) -> None:
        for bar in self._bars:
            ratio = bar.refresh()
            if self._on_status_change:
                self._on_status_change(bar.tracker.stat_name, bar.tracker.current_value, ratio)

    def draw(self, screen: pygame.Surface) -> None:
        for bar in self._bars:
            bar.draw(screen, self.position, self.scale)
        if self.frame_surface is not None:
            if self.scale != 1.0:
                width = max(1, int(self.frame_surface.get_width() * self.scale))
                height = max(1, int(self.frame_surface.get_height() * self.scale))
                frame = pygame.transform.smoothscale(self.frame_surface, (width, height))
            else:
                frame = self.frame_surface
            screen.blit(frame, self.position)
