import pygame
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Screen Settings ---
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 400
FPS = 60

# --- Font Settings ---
pygame.font.init()
FONT_SMALL = pygame.font.SysFont(None, 36)
FONT_MEDIUM = pygame.font.SysFont(None, 48)
FONT_LARGE = pygame.font.SysFont(None, 72)


# --- Assets ---
MUSIC_FILE = os.path.join(BASE_DIR, "assets/media/loon.mp3")
HIT_SOUND_FILE = os.path.join(BASE_DIR, "assets/media/hit.wav")
ZOMBIE_IMG = os.path.join(BASE_DIR, "assets/img/zombie_head.png")
ZOMBIE_HIT_IMG = os.path.join(BASE_DIR, "assets/img/zombie_hit.png")
HAMMER_IMG = os.path.join(BASE_DIR, "assets/img/hammer.png")


# --- Game Settings ---
ZOMBIE_SIZE = (80, 80)
HAMMER_SIZE = (100, 100)
OFFSET_X, OFFSET_Y = -40, -40

ZOMBIE_HIT_DURATION = 150   # ms
HAMMER_DURATION = 100       # ms
WAVE_INTERVAL = 1500        # ms
GAME_DURATION = 60000       # ms

# --- Zombie hole positions ---
HOLES = [
    (150, 150), (350, 150), (550, 150),
    (150, 300), (350, 300), (550, 300)
]
