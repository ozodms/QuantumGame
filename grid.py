# grid.py - Cell and Grid logic

import random
from constants import *

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.state = STATE_CLEAN
        self.strain = None
        self.measured = False
        self.phase = None
        self.quarantine_turns = 0
        self.entangled_with = None

    def infect(self):
        if self.state in (STATE_CLEAN, STATE_CURED) and self.quarantine_turns == 0:
            self.state = STATE_INFECTED
            self.strain = random.choice(STRAINS)
            self.measured = False
            return True
        return False

    def test(self):
        if self.state == STATE_INFECTED and not self.measured:
            self.measured = True
            return self.strain
        return None

    def treat(self, chosen_color):
        if self.state != STATE_INFECTED:
            return False

        if self.measured:
            if chosen_color == self.strain:
                self.state = STATE_CURED
                self.strain = None
                self.measured = False
                return True
            else:
                return False
        else:
            if chosen_color == self.strain:
                self.state = STATE_CURED
                self.strain = None
                return True
            else:
                self.measured = True
                return False

    def set_quarantine(self):
        if self.quarantine_turns == 0:
            self.quarantine_turns = QUARANTINE_DURATION
            return True
        return False

    def tick_quarantine(self):
        if self.quarantine_turns > 0:
            self.quarantine_turns -= 1

    def is_quarantined(self):
        return self.quarantine_turns > 0


class Grid:
    def __init__(self):
        self.cells = [[Cell(r, c) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
        self.panic = 0
        self.turn = 1
        self.actions_left = ACTIONS_PER_TURN
        self.game_over = False
        self.game_won = False
        self.selected_action = None
        self.selected_color = None
        self._place_initial_infections()

    def _place_initial_infections(self):
        start_r = random.randint(1, GRID_SIZE - 2)
        start_c = random.randint(1, GRID_SIZE - 2)

        self.cells[start_r][start_c].infect()
        positions = [(start_r, start_c)]

        neighbors = self._get_neighbors(start_r, start_c)
        random.shuffle(neighbors)
        for nr, nc in neighbors:
            if len(positions) >= INITIAL_INFECTED:
                break
            self.cells[nr][nc].infect()
            positions.append((nr, nc))

    def get_cell(self, row, col):
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            return self.cells[row][col]
        return None

    def do_test(self, row, col):
        if self.actions_left <= 0:
            return None
        cell = self.get_cell(row, col)
        if cell and cell.state == STATE_INFECTED and not cell.measured:
            result = cell.test()
            if result:
                self.panic = min(MAX_PANIC, self.panic + PANIC_PER_TEST)
                self.actions_left -= 1
                self._check_game_over()
                return result
        return None

    def do_treat(self, row, col, color):
        if self.actions_left <= 0:
            return False
        cell = self.get_cell(row, col)
        if cell and cell.state == STATE_INFECTED:
            result = cell.treat(color)
            self.actions_left -= 1
            self._check_game_over()
            return result
        return False

    def do_quarantine(self, row, col):
        if self.actions_left <= 0:
            return False
        cell = self.get_cell(row, col)
        if cell and not cell.is_quarantined():
            if cell.set_quarantine():
                self.actions_left -= 1
                return True
        return False

    def do_aid(self):
        if self.actions_left <= 0:
            return False
        self.panic = max(0, self.panic + PANIC_PER_AID)
        self.actions_left -= 1
        return True

    def end_turn(self):
        if self.game_over or self.game_won:
            return

        self._spread_virus()

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.cells[r][c].tick_quarantine()

        self.turn += 1
        self.actions_left = ACTIONS_PER_TURN
        self._check_game_over()

    def _spread_virus(self):
        if self.panic <= 30:
            max_spread = SPREAD_LOW
            spread_chance = SPREAD_CHANCE_LOW
        elif self.panic <= 60:
            max_spread = SPREAD_MED
            spread_chance = SPREAD_CHANCE_MED
        else:
            max_spread = SPREAD_HIGH
            spread_chance = SPREAD_CHANCE_HIGH

        infected_positions = []
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.cells[r][c].state == STATE_INFECTED:
                    infected_positions.append((r, c))

        for r, c in infected_positions:
            if self.cells[r][c].is_quarantined():
                continue

            if random.random() > spread_chance:
                continue

            neighbors = self._get_open_neighbors(r, c)
            random.shuffle(neighbors)

            spread_count = 0
            for nr, nc in neighbors:
                if spread_count >= max_spread:
                    break
                neighbor = self.cells[nr][nc]

                if neighbor.state == STATE_CLEAN:
                    neighbor.infect()
                    spread_count += 1
                elif neighbor.state == STATE_CURED and self.panic > 60:
                    if random.random() < 0.2:
                        neighbor.infect()
                        spread_count += 1

        self._check_lone_cured()

    def _get_neighbors(self, row, col):
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                neighbors.append((nr, nc))
        return neighbors

    def _get_open_neighbors(self, row, col):
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                if not self.cells[nr][nc].is_quarantined():
                    neighbors.append((nr, nc))
        return neighbors

    def _check_lone_cured(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                cell = self.cells[r][c]
                if cell.state != STATE_CURED or cell.is_quarantined():
                    continue

                has_cured_neighbor = False
                has_infected_neighbor = False
                for nr, nc in self._get_neighbors(r, c):
                    neighbor = self.cells[nr][nc]
                    if neighbor.state == STATE_CURED:
                        has_cured_neighbor = True
                        break
                    if neighbor.state == STATE_INFECTED:
                        has_infected_neighbor = True

                if not has_cured_neighbor and has_infected_neighbor:
                    if random.random() < LONE_CURED_REINFECT_CHANCE:
                        cell.infect()

    def _check_game_over(self):
        if self.panic >= MAX_PANIC:
            self.game_over = True
            return

        total = GRID_SIZE * GRID_SIZE
        cured = 0
        infected = 0
        clean = 0

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                state = self.cells[r][c].state
                if state == STATE_CURED:
                    cured += 1
                elif state == STATE_INFECTED:
                    infected += 1
                elif state == STATE_CLEAN:
                    clean += 1

        healthy = cured + clean
        if infected == 0 or healthy / total >= WIN_PERCENT:
            if infected == 0:
                self.game_won = True

        if cured / total >= WIN_PERCENT:
            self.game_won = True

        if infected == total:
            self.game_over = True

    def get_stats(self):

        total = GRID_SIZE * GRID_SIZE
        cured = sum(1 for r in range(GRID_SIZE) for c in range(GRID_SIZE)
                     if self.cells[r][c].state == STATE_CURED)
        infected = sum(1 for r in range(GRID_SIZE) for c in range(GRID_SIZE)
                       if self.cells[r][c].state == STATE_INFECTED)
        clean = total - cured - infected
        return {
            "total": total,
            "cured": cured,
            "infected": infected,
            "clean": clean,
            "panic": self.panic,
            "turn": self.turn,
            "actions_left": self.actions_left,
        }
