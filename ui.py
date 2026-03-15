# ui.py - Drawing and UI elements

import pygame
from constants import *


class Button:
    def __init__(self, x, y, width, height, text, action=None, color=COLOR_BUTTON):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color = color
        self.hover = False
        self.active = False

    def draw(self, surface, font):
        if self.active:
            color = COLOR_BUTTON_ACTIVE
        elif self.hover:
            color = COLOR_BUTTON_HOVER
        else:
            color = self.color

        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, DARK_GRAY, self.rect, 2, border_radius=6)

        text_surf = font.render(self.text, True, COLOR_BUTTON_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


class UI:
    def __init__(self):
        pygame.font.init()
        self.font_big = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 20)
        self.font_small = pygame.font.SysFont("Arial", 16)

        btn_y = 580
        btn_w = 120
        btn_h = 40
        btn_gap = 15
        btn_start_x = 50

        self.buttons = {
            ACTION_TEST: Button(btn_start_x, btn_y, btn_w, btn_h, "Test", ACTION_TEST),
            ACTION_TREAT: Button(btn_start_x + (btn_w + btn_gap), btn_y, btn_w, btn_h, "Treat", ACTION_TREAT),
            ACTION_QUARANTINE: Button(btn_start_x + 2 * (btn_w + btn_gap), btn_y, btn_w, btn_h, "Quarantine", ACTION_QUARANTINE),
            ACTION_AID: Button(btn_start_x + 3 * (btn_w + btn_gap), btn_y, btn_w, btn_h, "Aid", ACTION_AID),
        }

        color_btn_y = 635
        color_btn_w = 90
        self.color_buttons = {
            "Red": Button(btn_start_x, color_btn_y, color_btn_w, 35, "Red", "Red", COLOR_RED),
            "Blue": Button(btn_start_x + 100, color_btn_y, color_btn_w, 35, "Blue", "Blue", COLOR_BLUE),
            "Green": Button(btn_start_x + 200, color_btn_y, color_btn_w, 35, "Green", "Green", COLOR_GREEN),
        }

        self.end_turn_btn = Button(700, 580, 150, 40, "End Turn", "end_turn", DARK_GRAY)
        self.restart_btn = Button(350, 400, 200, 50, "Restart", "restart", COLOR_BUTTON)
        self.message = ""
        self.message_timer = 0

    def set_message(self, msg, duration=90):
        self.message = msg
        self.message_timer = duration

    def draw_grid(self, surface, grid):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                cell = grid.cells[r][c]
                x = GRID_OFFSET_X + c * CELL_SIZE
                y = GRID_OFFSET_Y + r * CELL_SIZE

                if cell.is_quarantined():
                    color = COLOR_QUARANTINE
                elif cell.state == STATE_CLEAN:
                    color = COLOR_CLEAN
                elif cell.state == STATE_CURED:
                    color = COLOR_CURED
                elif cell.state == STATE_INFECTED:
                    if cell.measured:
                        color = STRAIN_COLORS.get(cell.strain, COLOR_INFECTED)
                    else:
                        color = COLOR_INFECTED

                rect = pygame.Rect(x, y, CELL_SIZE - 2, CELL_SIZE - 2)
                pygame.draw.rect(surface, color, rect, border_radius=4)
                pygame.draw.rect(surface, DARK_GRAY, rect, 1, border_radius=4)

                if cell.state == STATE_INFECTED:
                    if cell.measured:
                        letter = cell.strain[0]  # R, B, or G
                        text = self.font_big.render(letter, True, WHITE)
                    else:
                        text = self.font_big.render("?", True, WHITE)
                    text_rect = text.get_rect(center=(x + CELL_SIZE // 2 - 1, y + CELL_SIZE // 2 - 1))
                    surface.blit(text, text_rect)

                elif cell.state == STATE_CURED:
                    text = self.font_med.render("\u2713", True, (0, 100, 0))
                    text_rect = text.get_rect(center=(x + CELL_SIZE // 2 - 1, y + CELL_SIZE // 2 - 1))
                    surface.blit(text, text_rect)

                if cell.is_quarantined():
                    q_text = self.font_small.render(f"Q:{cell.quarantine_turns}", True, DARK_GRAY)
                    surface.blit(q_text, (x + 5, y + 5))

    def draw_panic_bar(self, surface, panic):
        bar_x = 550
        bar_y = 20
        bar_w = 300
        bar_h = 30

        pygame.draw.rect(surface, COLOR_PANIC_BG, (bar_x, bar_y, bar_w, bar_h), border_radius=4)


        fill_w = int((panic / MAX_PANIC) * bar_w)
        if fill_w > 0:
            if panic < 50:
                bar_color = (220, 180, 50)
            else:
                bar_color = COLOR_PANIC_BAR
            pygame.draw.rect(surface, bar_color, (bar_x, bar_y, fill_w, bar_h), border_radius=4)

        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=4)

        label = self.font_med.render(f"Panic: {panic}/100", True, WHITE)
        label_rect = label.get_rect(midleft=(bar_x + 10, bar_y + bar_h // 2))
        surface.blit(label, label_rect)

    def draw_info(self, surface, stats):
        title = self.font_big.render("QUANTUM CURE", True, (30, 60, 120))
        surface.blit(title, (50, 15))


        turn_text = self.font_med.render(
            f"Turn: {stats['turn']}   Actions left: {stats['actions_left']}",
            True, BLACK
        )
        surface.blit(turn_text, (50, 55))

        stats_text = self.font_small.render(
            f"Clean: {stats['clean']}  Infected: {stats['infected']}  Cured: {stats['cured']}",
            True, DARK_GRAY
        )
        surface.blit(stats_text, (550, 58))

    def draw_buttons(self, surface, selected_action, show_colors):
        mouse_pos = pygame.mouse.get_pos()

        for name, btn in self.buttons.items():
            btn.check_hover(mouse_pos)
            btn.active = (selected_action == name)
            btn.draw(surface, self.font_med)

        self.end_turn_btn.check_hover(mouse_pos)
        self.end_turn_btn.draw(surface, self.font_med)

        if show_colors:
            color_label = self.font_small.render("Choose treatment color:", True, DARK_GRAY)
            surface.blit(color_label, (50, 618))
            for name, btn in self.color_buttons.items():
                btn.check_hover(mouse_pos)
                btn.draw(surface, self.font_small)

    def draw_message(self, surface):
        if self.message_timer > 0:
            self.message_timer -= 1
            msg_surf = self.font_med.render(self.message, True, (180, 50, 50))
            msg_rect = msg_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 25))
            surface.blit(msg_surf, msg_rect)

    def draw_game_over(self, surface, won):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        if won:
            text = self.font_big.render("CITY SAVED!", True, (100, 255, 100))
            sub = self.font_med.render("You stopped the epidemic!", True, WHITE)
        else:
            text = self.font_big.render("CITY LOST!", True, (255, 80, 80))
            sub = self.font_med.render("Panic overwhelmed the city...", True, WHITE)

        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 300))
        sub_rect = sub.get_rect(center=(WINDOW_WIDTH // 2, 350))
        surface.blit(text, text_rect)
        surface.blit(sub, sub_rect)

        self.restart_btn.check_hover(pygame.mouse.get_pos())
        self.restart_btn.draw(surface, self.font_med)

    def get_cell_at_mouse(self, mouse_pos):
        mx, my = mouse_pos
        col = (mx - GRID_OFFSET_X) // CELL_SIZE
        row = (my - GRID_OFFSET_Y) // CELL_SIZE
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            return (row, col)
        return None
