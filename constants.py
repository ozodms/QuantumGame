# constants.py - Game settings and configuration

import pygame

# Window
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
FPS = 30

# Grid
GRID_SIZE = 6
CELL_SIZE = 80
GRID_OFFSET_X = 50
GRID_OFFSET_Y = 80

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
LIGHT_GRAY = (230, 230, 230)

# Cell state colors
COLOR_CLEAN = (180, 220, 180)
COLOR_INFECTED = (180, 180, 180)
COLOR_CURED = (140, 200, 255)
COLOR_QUARANTINE = (255, 255, 150)

# Virus strain colors
COLOR_RED = (220, 60, 60)
COLOR_BLUE = (60, 60, 220)
COLOR_GREEN = (60, 180, 60)

# UI colors
COLOR_PANIC_BAR = (220, 50, 50)
COLOR_PANIC_BG = (60, 60, 60)
COLOR_BUTTON = (70, 130, 180)
COLOR_BUTTON_HOVER = (100, 160, 210)
COLOR_BUTTON_ACTIVE = (50, 100, 150)
COLOR_BUTTON_TEXT = (255, 255, 255)

# Virus strains
STRAINS = ["Red", "Blue", "Green"]
STRAIN_COLORS = {
    "Red": COLOR_RED,
    "Blue": COLOR_BLUE,
    "Green": COLOR_GREEN,
}

# Cell states
STATE_CLEAN = "clean"
STATE_INFECTED = "infected"
STATE_CURED = "cured"

# Actions
ACTION_TEST = "test"
ACTION_TREAT = "treat"
ACTION_QUARANTINE = "quarantine"
ACTION_AID = "aid"

# Game balance
ACTIONS_PER_TURN = 2
PANIC_PER_TEST = 10
PANIC_PER_AID = -5
MAX_PANIC = 100
WIN_PERCENT = 0.80
QUARANTINE_DURATION = 2
INITIAL_INFECTED = 3

# Spread chance per infected cell (not every cell spreads every turn)
SPREAD_CHANCE_LOW = 0.4     # panic 0-30: 40% chance each infected cell spreads
SPREAD_CHANCE_MED = 0.6     # panic 31-60: 60%
SPREAD_CHANCE_HIGH = 0.8    # panic 61-99: 80%

# Lone cured cell re-infection chance
LONE_CURED_REINFECT_CHANCE = 0.25

# Max neighbors to spread to per infected cell
SPREAD_LOW = 1       # panic 0-30
SPREAD_MED = 1       # panic 31-60
SPREAD_HIGH = 2      # panic 61-99 (+ can re-infect cured)
