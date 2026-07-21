"""Handles rendering of the player and UI elements."""
import os 
import json
import pygame

from ..config.config import config
from ..config.imports import *
from .userStatusUi import *
from ...Contents.Resources.World.maps.worldRenderer import WorldRenderer # <-- This is the dedicated map renderer
from .playerRenderer import *# Engine/main/renderer.py
from playerRenderer import PlayerRenderer
from ..game.ui_manager import UIManager