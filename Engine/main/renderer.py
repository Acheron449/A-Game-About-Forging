import os
import json
import pygame

from ..config.config import *
from ..config.imports import *

class WorldRenderer:
    def __init__(self):
        pass

    def render_world(self, world, screen):
        # Render map and entities
        # Placeholder for rendering logic
        pass

class UIRenderer:
    def __init__(self, player):
        self.player = player
        self.elements = {}  # Health bar, stats display, etc.
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.hp_bar_root = os.path.join(self.root_dir, "Contents", "Resources", "UI", "Bars", "HP")
        self.hp_frames = self._load_hp_frames()
        self.hp_frame_index = 0
        self.hp_bar_pos = (20, 20)

    def _load_hp_frames(self):
        frames = {}
        for folder_index in range(0, 12):
            folder_path = os.path.join(self.hp_bar_root, str(folder_index))
            if not os.path.isdir(folder_path):
                continue
            frame_images = []
            for image_name in ("0.png", "1.png"):
                image_path = os.path.join(folder_path, image_name)
                if os.path.isfile(image_path):
                    try:
                        frame_images.append(pygame.image.load(image_path).convert_alpha())
                    except Exception:
                        frame_images.append(None)
                else:
                    frame_images.append(None)
            frames[folder_index] = frame_images
        return frames

    def _hp_group_index(self):
        hp = max(0, min(self.player.health, self.player.max_health))
        if hp <= 0:
            return 0
        if hp >= self.player.max_health:
            return 11
        return min(10, ((hp - 1) // 10) + 1)

    def _select_hp_image(self):
        group = self._hp_group_index()
        frames = self.hp_frames.get(group, [None, None])

        if group == 0:
            # 0 HP uses the static zero-health image from folder 0
            return frames[0] or frames[1]

        if group == 1:
            # below 10 HP alternates between folder 1 images
            return frames[self.hp_frame_index % 2] or frames[0] or frames[1]

        if group == 11:
            # full HP alternates between folder 11 images
            return frames[self.hp_frame_index % 2] or frames[0] or frames[1]

        # For all other 10-HP intervals, use the image in the matching folder
        return frames[0] or frames[1]

    def _update_hp_frame(self):
        self.hp_frame_index = (self.hp_frame_index + 1) % 2

    def draw_ui(self, screen):
        hp_image = self._select_hp_image()
        if hp_image is not None:
            screen.blit(hp_image, self.hp_bar_pos)

    def update_ui(self):
        self._update_hp_frame()

    def configure_appearance(self, appearance):
        self.player.appearance = appearance
        config_dir = "Saves/player config"
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, "appearance.json")
        with open(config_path, 'w') as f:
            json.dump({"appearance": appearance}, f)
