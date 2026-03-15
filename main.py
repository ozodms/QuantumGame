# main.py - Quantum Cure: Main game loop

import pygame
import sys
import random
from constants import *
from grid import Grid
from quantum import assign_phase, check_interference, apply_interference_bonus, clear_phases
from ui import UI


def handle_treat(grid, ui, row, col, color):
    phase = assign_phase()
    interference = check_interference(grid, row, col, phase)

    if interference == "destructive" and random.random() < 0.5:
        grid.actions_left -= 1
        grid.cells[row][col].phase = phase
        return f"Destructive interference! Treatment failed (phase {phase})"

    result = grid.do_treat(row, col, color)
    grid.cells[row][col].phase = phase

    if result:
        msg = f"Cured with {color}! (phase {phase})"
        if interference == "constructive":
            bonus = apply_interference_bonus(grid, row, col)
            if bonus:
                msg += f" + Bonus heal at ({bonus[0]},{bonus[1]})!"
        return msg
    else:
        cell = grid.get_cell(row, col)
        if cell and cell.measured:
            return f"Wrong color! Strain is {cell.strain} (phase {phase})"
        return f"Miss! Wrong color (phase {phase})"


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Quantum Cure")
    clock = pygame.time.Clock()
    grid = Grid()
    ui = UI()
    selected_action = None
    selected_color = None

    running = True
    while running:
        screen.fill(LIGHT_GRAY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                if grid.game_over or grid.game_won:
                    if ui.restart_btn.is_clicked(mouse_pos):
                        grid = Grid()
                        selected_action = None
                        selected_color = None
                    continue

                for name, btn in ui.buttons.items():
                    if btn.is_clicked(mouse_pos):
                        if name == ACTION_AID:
                            if grid.do_aid():
                                ui.set_message("Aid sent! Panic -5")
                            else:
                                ui.set_message("No actions left!")
                            selected_action = None
                        else:
                            selected_action = name
                            selected_color = None
                        break

                if selected_action == ACTION_TREAT:
                    for color_name, btn in ui.color_buttons.items():
                        if btn.is_clicked(mouse_pos):
                            selected_color = color_name
                            break

                if ui.end_turn_btn.is_clicked(mouse_pos):
                    clear_phases(grid)
                    grid.end_turn()
                    selected_action = None
                    selected_color = None
                    ui.set_message(f"Turn {grid.turn} - Virus spreads!")
                    continue

                cell_pos = ui.get_cell_at_mouse(mouse_pos)
                if cell_pos and selected_action:
                    row, col = cell_pos

                    if selected_action == ACTION_TEST:
                        result = grid.do_test(row, col)
                        if result:
                            ui.set_message(f"Tested! Strain is {result}. Panic +10")
                        else:
                            ui.set_message("Can't test this cell")
                        selected_action = None
                    elif selected_action == ACTION_TREAT:
                        if selected_color:
                            msg = handle_treat(grid, ui, row, col, selected_color)
                            ui.set_message(msg)
                            selected_action = None
                            selected_color = None
                        else:
                            ui.set_message("Pick a color first (Red/Blue/Green)")
                    elif selected_action == ACTION_QUARANTINE:
                        if grid.do_quarantine(row, col):
                            ui.set_message(f"District quarantined for {QUARANTINE_DURATION} turns")
                        else:
                            ui.set_message("Can't quarantine this cell")
                        selected_action = None

        stats = grid.get_stats()
        ui.draw_info(screen, stats)
        ui.draw_panic_bar(screen, grid.panic)
        ui.draw_grid(screen, grid)
        ui.draw_buttons(screen, selected_action, selected_action == ACTION_TREAT)
        ui.draw_message(screen)

        if grid.game_over or grid.game_won:
            ui.draw_game_over(screen, grid.game_won)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
