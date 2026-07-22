from config import *
from pygame import *
from numpy import *
import random as r
from arcade import *
import os as os
import sys as sys
import sysconfig as sysconfig
import time as t
import zipfile as zip
import math as m
import json as js
import logging as log
import pytmx as tmx
import pygame as pg

DEFAULT_FONT_PATH = os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    'Contents',
    'Resources',
    'Fonts',
    'Handjet',
    'Handjet-VariableFont_ELGR,ELSH,wght.ttf',
)
