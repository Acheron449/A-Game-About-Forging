import pygame as pg
import numpy as np
import random
import arcade
import os
import sys
import sysconfig
import time
import zipfile
import math
import json
import logging
import pytmx

# Default paths are defined in config.py, but we keep the path definition here if needed for initialization context
DEFAULT_FONT_PATH = os.path.join(
    os.path.dirname(__file__),
    '..',
    'Contents',
    'Resources',
    'Fonts',
    'Handjet',
    'Handjet-VariableFont_ELGR,ELSH,wght.ttf',
)

