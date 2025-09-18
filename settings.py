"""Configuration constants and asset paths."""
import os
import json
import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 1200
MAP_WIDTH, MAP_HEIGHT = 3200, 1200

PLAYER_SIZE = 32
PLAYER_COLOR = (40, 40, 40)
PLAYER_HEAD_COLOR = (245, 219, 164)
PLAYER_SPEED = 5
SKATEBOARD_SPEED_MULT = 1.5

BG_COLOR = (180, 220, 190)
BUILDING_COLOR = (200, 170, 120)
HOME_COLOR = (128, 191, 255)
JOB_COLOR = (240, 221, 110)
SHOP_COLOR = (255, 115, 115)
PARK_COLOR = (100, 200, 140)
GYM_COLOR = (170, 120, 220)
LIBRARY_COLOR = (200, 160, 200)
CLINIC_COLOR = (180, 240, 230)
BAR_COLOR = (250, 190, 90)
BUS_STOP_COLOR = (255, 215, 0)
ROAD_COLOR = (90, 90, 90)
SIDEWALK_COLOR = (190, 190, 190)
CITY_WALL_COLOR = (120, 100, 70)
WINDOW_COLOR = (220, 240, 255)
DOOR_COLOR = (90, 70, 40)
SHADOW_COLOR = (40, 40, 40, 60)
TREE_COLOR = (80, 140, 60)
TRUNK_COLOR = (110, 80, 50)
FLOWER_COLORS = [(255, 100, 100), (255, 255, 120), (200, 100, 200)]


# Asset directories
ASSETS_DIR = "assets"
IMAGE_DIR = os.path.join(ASSETS_DIR, "images")
SOUND_DIR = os.path.join(ASSETS_DIR, "sounds")
BUILDING_IMAGE_DIR = os.path.join(IMAGE_DIR, "buildings")
BUILDING_WINDOW_LAYER = "window_layer.svg"

# Mapping of building types to sprite filenames
BUILDING_SPRITES = {
    "default": "default.svg",
    "home": "home.svg",
    "job": "job.svg",
    "shop": "shop.svg",
    "park": "park.svg",
    "dealer": "dealer.svg",
    "gym": "gym.svg",
    "library": "library.svg",
    "clinic": "clinic.svg",
    "bar": "bar.svg",
    "dungeon": "dungeon.svg",
    "petshop": "petshop.svg",
    "bank": "bank.svg",
    "townhall": "townhall.svg",
    "workshop": "workshop.svg",
    "farm": "farm.svg",
    "forest": "forest.svg",
    "mall": "mall.svg",
    "suburbs": "suburbs.svg",
    "beach": "beach.svg",
    "business": "business.svg",
    "boss": "boss.svg",
}

FONT_COLOR = (30, 30, 30)
UI_BG = (255, 255, 255, 230)
MINUTES_PER_FRAME = 0.1

# Simple audio settings and asset locations
MUSIC_FILE = os.path.join(SOUND_DIR, "music.wav")
STEP_SOUND_FILE = os.path.join(SOUND_DIR, "step.wav")
ENTER_SOUND_FILE = os.path.join(SOUND_DIR, "enter.wav")
QUEST_SOUND_FILE = os.path.join(SOUND_DIR, "quest.wav")
MUSIC_VOLUME = 0.3
SFX_VOLUME = 0.5


# Default control scheme. Values are pygame key constants; joystick buttons
# are stored as negative numbers (-(button+1)).
KEY_BINDINGS_FILE = os.path.join("data", "keybindings.json")
KEY_BINDINGS = {
    "move_up": [pygame.K_w, pygame.K_UP],
    "move_down": [pygame.K_s, pygame.K_DOWN],
    "move_left": [pygame.K_a, pygame.K_LEFT],
    "move_right": [pygame.K_d, pygame.K_RIGHT],
    "interact": [pygame.K_e],
    "run": [pygame.K_LSHIFT, pygame.K_RSHIFT],
}


if os.path.exists(KEY_BINDINGS_FILE):
    try:
        with open(KEY_BINDINGS_FILE) as f:
            loaded = json.load(f)
        KEY_BINDINGS.update({k: [int(vv) for vv in v] for k, v in loaded.items()})
    except Exception:
        pass
