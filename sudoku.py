from __future__ import annotations

from assets.sudoku.logic import SudokuGame

import sys
from pathlib import Path
import copy
from typing import Literal

import pygame

# --- Configuration & Colors ---
SCREEN_WIDTH, SCREEN_HEIGHT = 500, 650
GRID_SIZE = 9
CELL_SIZE = 50
GRID_OFFSET_X = (SCREEN_WIDTH - (GRID_SIZE * CELL_SIZE)) // 2  # 25px margin
GRID_OFFSET_Y = 80

# Colors
COLOR_BG          = (255, 255, 255)
COLOR_GRID_THIN   = (200, 200, 200)
COLOR_GRID_THICK  = (30, 30, 30)
COLOR_TEXT_GIVEN  = (0, 0, 0)         # Fixed puzzle clues (Black)
COLOR_TEXT_USER   = (30, 100, 220)    # Player inputs (Blue)
COLOR_SELECTED    = (187, 222, 251)   # Active cell fill (Light Blue)
COLOR_HIGHLIGHT   = (232, 240, 254)   # Same row/col/box fill
COLOR_BTN_BG      = (238, 238, 238)
COLOR_BTN_HOVER   = (220, 220, 220)

pygame.init()
pygame.font.init()

def load_ui_font(size: int, bold: bool = False, role: str = "ui") -> pygame.font.Font:
    if sys.platform == "darwin":
        # Prefer native macOS UI fonts first.
        candidates = [
            "Avenir Next",
            "SF Pro Text",
            "Helvetica Neue",
            "Helvetica",
            "Arial",
        ]
    elif sys.platform.startswith("win"):
        candidates = [
            "Segoe UI Variable",
            "Segoe UI",
            "Calibri",
            "Arial",
        ]
    else:
        candidates = [
            "Noto Sans",
            "DejaVu Sans",
            "Liberation Sans",
            "Arial",
        ]

    if role == "title":
        candidates = ["Avenir Next", "Segoe UI", "Noto Sans"] + candidates

    for family in candidates:
        font_path = pygame.font.match_font(family, bold=bold)
        if font_path:
            return pygame.font.Font(font_path, size)

    return pygame.font.SysFont(None, size, bold=bold)

FONT_CELL: pygame.font.Font = load_ui_font(28, bold=True)
FONT_BTN: pygame.font.Font  = load_ui_font(13, bold=True)
FONT_STATUS: pygame.font.Font = load_ui_font(16, bold=True)

STATUS_INFO = (70, 74, 80)
STATUS_WARN = (180, 95, 20)
STATUS_GOOD = (40, 160, 80)
STATUS_Y = 66

def resolve_resource_path(relative_path: str) -> Path:
    source_root = Path(__file__).resolve().parent
    bundled_root = Path(getattr(sys, "_MEIPASS", source_root))

    normalized_parts = relative_path.replace("\\", "/").split("/")
    bundled_candidate = bundled_root.joinpath(*normalized_parts)
    if bundled_candidate.exists():
        return bundled_candidate

    return source_root.joinpath(*normalized_parts)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sudoku by Chinmay Mokashi")

icon_path = resolve_resource_path("assets/sudoku/logo.png")
if icon_path.exists():
    pygame.display.set_icon(pygame.image.load(str(icon_path)))

# --- UI Helper: Button Class ---
class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False

    def draw(self, surface: pygame.Surface):
        color = COLOR_BTN_HOVER if self.is_hovered else COLOR_BTN_BG
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GRID_THIN, self.rect, width=1, border_radius=6)

        text_surf = FONT_BTN.render(self.text, True, (30, 30, 30))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos: tuple[int, int]):
        self.is_hovered = self.rect.collidepoint(pos)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

Difficulty = Literal["EASY", "MEDIUM", "HARD"]


def create_game_state(difficulty: Difficulty) -> tuple[SudokuGame, list[list[int]], list[list[bool]]]:
    game = SudokuGame(difficulty)
    board = game.initialize_sudoku_board()
    given_mask = [[board[r][c] != 0 for c in range(9)] for r in range(9)]
    return game, board, given_mask

# Buttons Setup
btn_reset = Button(20, 20, 70, 36, "RESET")
btn_solve = Button(100, 20, 70, 36, "SOLVE")
btn_erase = Button(180, 20, 70, 36, "ERASE")
btn_difficulty = Button(260, 20, 220, 36, "MODE: MEDIUM")

DIFFICULTY_LEVELS: tuple[Difficulty, Difficulty, Difficulty] = ("EASY", "MEDIUM", "HARD")
difficulty_idx = DIFFICULTY_LEVELS.index("MEDIUM")
current_difficulty: Difficulty = DIFFICULTY_LEVELS[difficulty_idx]
btn_difficulty.text = f"MODE: {current_difficulty}"

# --- Board State Setup ---
game, board, given_mask = create_game_state(current_difficulty)
selected_cell: tuple[int, int] | None = None  # (row, col)
status_message = "Fill the board with numbers 1-9."
status_color = STATUS_INFO

# --- Render Functions ---
def draw_grid(surface: pygame.Surface):
    # 1. Highlight selected cell and related row/col
    if selected_cell:
        sel_r, sel_c = selected_cell
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                # Highlight same row, column, or 3x3 block
                if r == sel_r or c == sel_c or (r // 3 == sel_r // 3 and c // 3 == sel_c // 3):
                    x = GRID_OFFSET_X + c * CELL_SIZE
                    y = GRID_OFFSET_Y + r * CELL_SIZE
                    pygame.draw.rect(surface, COLOR_HIGHLIGHT, (x, y, CELL_SIZE, CELL_SIZE))

        # Highlight exact active cell
        x = GRID_OFFSET_X + sel_c * CELL_SIZE
        y = GRID_OFFSET_Y + sel_r * CELL_SIZE
        pygame.draw.rect(surface, COLOR_SELECTED, (x, y, CELL_SIZE, CELL_SIZE))

    # 2. Draw cell numbers
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            val = board[r][c]
            if val != 0:
                x = GRID_OFFSET_X + c * CELL_SIZE + CELL_SIZE // 2
                y = GRID_OFFSET_Y + r * CELL_SIZE + CELL_SIZE // 2
                
                color = COLOR_TEXT_GIVEN if given_mask[r][c] else COLOR_TEXT_USER
                text_surf = FONT_CELL.render(str(val), True, color)
                text_rect = text_surf.get_rect(center=(x, y))
                surface.blit(text_surf, text_rect)

    # 3. Draw Grid Lines (Thin for 1x1, Thick for 3x3)
    for i in range(GRID_SIZE + 1):
        line_w = 3 if i % 3 == 0 else 1
        
        # Horizontal lines
        y = GRID_OFFSET_Y + i * CELL_SIZE
        pygame.draw.line(surface, COLOR_GRID_THICK if i % 3 == 0 else COLOR_GRID_THIN,
                         (GRID_OFFSET_X, y), (GRID_OFFSET_X + 9 * CELL_SIZE, y), line_w)
        
        # Vertical lines
        x = GRID_OFFSET_X + i * CELL_SIZE
        pygame.draw.line(surface, COLOR_GRID_THICK if i % 3 == 0 else COLOR_GRID_THIN,
                         (x, GRID_OFFSET_Y), (x, GRID_OFFSET_Y + 9 * CELL_SIZE), line_w)

def draw_status_message(
    surface: pygame.Surface,
    message: str,
    color: tuple[int, int, int]
):
    if not message:
        return

    message_surf = FONT_STATUS.render(message, True, color)
    message_rect = message_surf.get_rect(center=(SCREEN_WIDTH // 2, STATUS_Y))
    surface.blit(message_surf, message_rect)

def is_board_complete(candidate_board: list[list[int]]) -> bool:
    return all(value != 0 for row in candidate_board for value in row)

# --- Main Event Loop ---
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    btn_reset.check_hover(mouse_pos)
    btn_solve.check_hover(mouse_pos)
    btn_erase.check_hover(mouse_pos)
    btn_difficulty.check_hover(mouse_pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Button Clicks
        if btn_reset.is_clicked(event):
            # Clear all non-given entries
            for r in range(9):
                for c in range(9):
                    if not given_mask[r][c]:
                        board[r][c] = 0
            status_message = "Board reset to original clues."
            status_color = STATUS_INFO

        if btn_erase.is_clicked(event):
            if selected_cell and not given_mask[selected_cell[0]][selected_cell[1]]:
                board[selected_cell[0]][selected_cell[1]] = 0
                status_message = "Cell cleared."
                status_color = STATUS_INFO

        if btn_solve.is_clicked(event):
            board = copy.deepcopy(game.board)
            status_message = "Puzzle solved."
            status_color = STATUS_GOOD

        if btn_difficulty.is_clicked(event):
            difficulty_idx = (difficulty_idx + 1) % len(DIFFICULTY_LEVELS)
            current_difficulty = DIFFICULTY_LEVELS[difficulty_idx]
            btn_difficulty.text = f"MODE: {current_difficulty}"
            game, board, given_mask = create_game_state(current_difficulty)
            selected_cell = None
            status_message = f"New {current_difficulty.lower()} puzzle started."
            status_color = STATUS_INFO

        # Grid Selection via Mouse Click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if GRID_OFFSET_X <= mx < GRID_OFFSET_X + 9 * CELL_SIZE and \
               GRID_OFFSET_Y <= my < GRID_OFFSET_Y + 9 * CELL_SIZE:
                c = (mx - GRID_OFFSET_X) // CELL_SIZE
                r = (my - GRID_OFFSET_Y) // CELL_SIZE
                selected_cell = (r, c)

        # Keyboard Number Inputs (1-9 & Backspace)
        if event.type == pygame.KEYDOWN and selected_cell:
            r, c = selected_cell
            if not given_mask[r][c]:  # Only edit user cells
                if event.unicode.isdigit() and event.unicode != '0':
                    board[r][c] = int(event.unicode)
                    # Check if the board is complete
                    if is_board_complete(board):
                        if board == game.board:
                            status_message = "Congratulations! You completed the puzzle."
                            status_color = STATUS_GOOD
                        else:
                            status_message = "Board is full, but there are mistakes."
                            status_color = STATUS_WARN
                    else:
                        status_message = ""
                elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                    board[r][c] = 0
                    status_message = ""

    # Render
    screen.fill(COLOR_BG)
    
    # Draw Header Buttons
    btn_reset.draw(screen)
    btn_solve.draw(screen)
    btn_erase.draw(screen)
    btn_difficulty.draw(screen)
    draw_status_message(screen, status_message, status_color)

    draw_grid(screen)
    
    pygame.display.flip()

pygame.quit()