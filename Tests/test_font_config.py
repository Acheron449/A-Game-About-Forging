import os
import unittest

import pygame

from Engine.config.config import config, get_game_font


class FontConfigTests(unittest.TestCase):
    def test_default_font_path_exists(self):
        self.assertTrue(os.path.exists(config.DEFAULT_FONT_PATH), config.DEFAULT_FONT_PATH)

    def test_get_game_font_returns_a_renderable_font(self):
        font = get_game_font(18)
        self.assertTrue(hasattr(font, 'render'))
        self.assertTrue(isinstance(font, pygame.font.FontType))


if __name__ == '__main__':
    unittest.main()
