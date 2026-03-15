# quantum.py - Quantum mechanics helpers

import random
from constants import *


def assign_phase():
    return random.choice(["+", "-"])


def check_interference(grid, row, col, phase):
    neighbors = grid._get_neighbors(row, col)

    for nr, nc in neighbors:
        neighbor = grid.get_cell(nr, nc)
        if neighbor and neighbor.phase is not None:
            if neighbor.phase == phase:
                return "constructive"
            else:
                return "destructive"
    return "none"


def apply_interference_bonus(grid, row, col):
    neighbors = grid._get_neighbors(row, col)
    random.shuffle(neighbors)

    for nr, nc in neighbors:
        neighbor = grid.get_cell(nr, nc)
        if neighbor and neighbor.state == STATE_INFECTED:
            if random.random() < 0.5:
                neighbor.state = STATE_CURED
                neighbor.strain = None
                neighbor.measured = False
                return (nr, nc)
    return None


def clear_phases(grid):
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            grid.cells[r][c].phase = None
