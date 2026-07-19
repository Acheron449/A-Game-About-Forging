import os 
import json
import pygame

from ..config.config import config
from ..config.imports import *
from .userStatusUi import UserStatusUI
from ..game import map_manager


class WorldRenderer: # Handles map rendering logic
    def __init__(self):
        # Initialize map-specific variables here
        pass

    def render_world(self, map_object, screen): # Render the world map, player, and entities to the screen.
        # --- 1. Render Map Background Layer (The fix for the grey screen) ---
        # The map object contains the layers, including the background imagelayer.
        background_layer = next((layer for layer in map_object.get('layers', []) if layer.get('type') == 'imagelayer'), None)

        if background_layer and background_layer.get('image'):
            image_path = background_layer['image'] # e.g., "../base/main.png"
            
            # DEBUGGING STEP: Print path and dimensions to confirm context
            print(f"--- Map Rendering Attempt ---")
            print(f"Map Image Path: {image_path}")
            print(f"Map Dimensions: {background_layer.get('imagewidth', '?')}x{background_layer.get('imageheight', '?')}")
            
            try:
                # Use os.path.join to construct the absolute path safely
                # This helps pygame resolve paths correctly based on the execution environment.
                # OLD CODE:
                # full_image_path = os.path.join(os.path.dirname(image_path), os.path.basename(image_path))
                # background_image = pygame.image.load(full_image_path).convert_alpha()

                # NEW TEST CODE (Use this ONLY for testing):
                background_image = pygame.image.load(image_path).convert_alpha()

                screen.blit(background_image, (0, 0))
            except pygame.error as e:
                print(f"CRITICAL ERROR: Failed to load background map image at {image_path}. Check path/file existence. Error: {e}")
                # If loading fails, the screen remains whatever it was before this frame.

        # --- 2. Render Dynamic Layers (Collisions, Object Groups, etc.) ---
        # Subsequent layers (like object groups) would be drawn on top of this background.
        pass

