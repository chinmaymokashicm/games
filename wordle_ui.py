from assets.wordle.load import FULL_DICTIONARY, TARGET_WORDS
from assets.wordle.logic import WordleGame, evaluate_guess
from assets.wordle.analytics import WordleAnalytics, TurnAnalysis

import pygame
from pathlib import Path
import sys

SCREEN_WIDTH, SCREEN_HEIGHT = 450, 620

# --- Color Scheme ---
BG_COLOR         = (255, 255, 255)  # Clean white background
TEXT_MAIN        = (18, 18, 19)     # Almost black for high readability
BORDER_EMPTY     = (211, 214, 218)  # Light gray for empty tile outlines
BORDER_FILLED    = (135, 138, 141)  # Darker gray when a tile has a letter

# Game Feedback Colors
COLOR_CORRECT    = (106, 170, 100)  # Green
COLOR_PRESENT    = (201, 180, 88)   # Yellow
COLOR_ABSENT     = (120, 124, 126)  # Dark Gray

# UI Element / Button Colors
BTN_BG           = (238, 238, 238)  # Light gray button fill
BTN_HOVER        = (220, 220, 220)  # Slightly darker on hover
BTN_TEXT         = (30, 30, 30)     # Dark button text

HEADER_HEIGHT = 75

# Grid Dimensions
ROWS, COLS = 6, 5
TILE_SIZE = 52
GAP = 6
START_X = (SCREEN_WIDTH - (COLS * TILE_SIZE + (COLS - 1) * GAP)) // 2
START_Y = HEADER_HEIGHT + 25

color_map = {
    "CORRECT": COLOR_CORRECT,
    "PRESENT": COLOR_PRESENT,
    "ABSENT": COLOR_ABSENT
}

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        # Change background color if mouse is hovering over the button
        color = BTN_HOVER if self.is_hovered else BTN_BG
        
        # Draw rounded button box and subtle border
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, BORDER_EMPTY, self.rect, width=1, border_radius=6)

        # Draw centered text
        text_surf: pygame.Surface = font.render(self.text, True, BTN_TEXT)
        text_rect: pygame.Rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos: tuple[int, int]):
        # collidepoint checks if the mouse cursor coordinates are inside the button
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        # Returns True if left mouse button was clicked over this button
        return (
            event.type == pygame.MOUSEBUTTONDOWN 
            and event.button == 1 
            and self.rect.collidepoint(event.pos)
        )

# 1. Initialize Pygame & Fonts
pygame.init()
pygame.font.init()

FONT_TITLE: pygame.font.Font = pygame.font.SysFont("Helvetica", 24, bold=True)
FONT_BTN: pygame.font.Font = pygame.font.SysFont("Helvetica", 14, bold=True)
FONT_TILE: pygame.font.Font = pygame.font.SysFont("Helvetica", 28, bold=True)
FONT_STATUS: pygame.font.Font = pygame.font.SysFont("Helvetica", 16, bold=True)


def resolve_resource_path(relative_path: str) -> Path:
    source_root = Path(__file__).resolve().parent
    bundled_root = Path(getattr(sys, "_MEIPASS", source_root))

    normalized_parts = relative_path.replace("\\", "/").split("/")
    bundled_candidate = bundled_root.joinpath(*normalized_parts)
    if bundled_candidate.exists():
        return bundled_candidate

    return source_root.joinpath(*normalized_parts)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Wordle by Chinmay Mokashi")

icon_path = resolve_resource_path("assets/wordle/logo.png")
if icon_path.exists():
    pygame.display.set_icon(pygame.image.load(str(icon_path)))

# 2. Instantiate Header Buttons
# Left button: Reset / Restart game
btn_reset = Button(x=15, y=20, width=80, height=36, text="RESET")

# Right button: View Stats (Placed on top right)
btn_stats = Button(x=SCREEN_WIDTH - 95, y=20, width=80, height=36, text="STATS")

def draw_header(surface: pygame.Surface):
    
    # Draw top header title
    title_surf = FONT_TITLE.render("WORDLE", True, TEXT_MAIN)
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 38))
    surface.blit(title_surf, title_rect)

    # Draw divider line underneath header
    pygame.draw.line(surface, BORDER_EMPTY, (0, HEADER_HEIGHT), (SCREEN_WIDTH, HEADER_HEIGHT), width=1)

    # Draw buttons
    btn_reset.draw(surface, FONT_BTN)
    btn_stats.draw(surface, FONT_BTN)
    
def draw_board(
    screen: pygame.Surface, 
    grid_letters: list[list[str]], 
    grid_colors: list[list[tuple[int, int, int] | None]]
) -> None:
    
    for row in range(ROWS):
        for col in range(COLS):
            # Step A: Calculate top-left corner of the current tile
            x = START_X + col * (TILE_SIZE + GAP)
            y = START_Y + row * (TILE_SIZE + GAP)
            
            tile_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            
            # Step B: Determine tile background color
            bg_color = grid_colors[row][col]
            
            if bg_color is not None:
                # Tile has been evaluated (Green, Yellow, or Gray)
                pygame.draw.rect(screen, bg_color, tile_rect)
            else:
                # Empty/unevaluated tile background
                pygame.draw.rect(screen, (255, 255, 255), tile_rect)
                
                # Draw subtle outline around empty or actively typed slots
                letter = grid_letters[row][col]
                border_color = (135, 138, 141) if letter != "" else (211, 214, 218)
                pygame.draw.rect(screen, border_color, tile_rect, width=2)

            # Step C: Render Letter (if present in the grid array)
            letter = grid_letters[row][col]
            if letter != "":
                # Text color is white on colored tiles, or dark gray on empty tiles
                text_color = (255, 255, 255) if bg_color is not None else (18, 18, 19)
                
                text_surface = FONT_TILE.render(letter, True, text_color)
                
                # Center text perfectly inside the tile rectangle
                text_rect = text_surface.get_rect(center=tile_rect.center)
                screen.blit(text_surface, text_rect)
    
# Color Priority Hierarchy (Higher number = higher priority)
COLOR_PRIORITY = {
    None: 0,
    COLOR_ABSENT: 1,
    COLOR_PRESENT: 2,
    COLOR_CORRECT: 3
}

# Add key status tracking to game state
key_colors: dict[str, tuple[int, int, int] | None] = {
    chr(code): None for code in range(ord('A'), ord('Z') + 1)
}

def update_key_colors(guess: str, results: list[str]):
    for char, status in zip(guess, results):
        new_color = color_map[status]
        current_color = key_colors[char]
        
        # Only upgrade status color
        if COLOR_PRIORITY[new_color] > COLOR_PRIORITY[current_color]:
            key_colors[char] = new_color

def reset_key_colors():
    for char in key_colors:
        key_colors[char] = None
            
KEYBOARD_LAYOUT = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
    ["Z", "X", "C", "V", "B", "N", "M"]
]

KEY_WIDTH = 30
KEY_HEIGHT = 42
KEY_GAP = 4
FONT_KEY = pygame.font.SysFont("Helvetica", 14, bold=True)
KEYBOARD_START_Y = START_Y + (ROWS * (TILE_SIZE + GAP)) + 15

def draw_keyboard(surface: pygame.Surface, key_colors: dict[str, tuple[int, int, int] | None]) -> None:
    for row_idx, row in enumerate(KEYBOARD_LAYOUT):
        # Calculate row width to center it horizontally on screen
        row_width = len(row) * KEY_WIDTH + (len(row) - 1) * KEY_GAP
        start_x = (SCREEN_WIDTH - row_width) // 2
        y = KEYBOARD_START_Y + row_idx * (KEY_HEIGHT + KEY_GAP)

        for col_idx, key in enumerate(row):
            x = start_x + col_idx * (KEY_WIDTH + KEY_GAP)
            key_rect = pygame.Rect(x, y, KEY_WIDTH, KEY_HEIGHT)

            # Determine key background and text color
            bg_color = key_colors[key]
            if bg_color is not None:
                fill_color = bg_color
                text_color = (255, 255, 255)
            else:
                fill_color = (211, 214, 218)  # Light gray for unused keys
                text_color = (18, 18, 19)

            pygame.draw.rect(surface, fill_color, key_rect, border_radius=4)

            # Render key text
            text_surf = FONT_KEY.render(key, True, text_color)
            text_rect = text_surf.get_rect(center=key_rect.center)
            surface.blit(text_surf, text_rect)

# --- Additional Fonts for Analytics Modal ---
FONT_ANALYTICS_HEADER = pygame.font.SysFont("Helvetica", 18, bold=True)
FONT_ANALYTICS_CELL   = pygame.font.SysFont("Helvetica", 13)
FONT_MODAL_TITLE      = pygame.font.SysFont("Helvetica", 20, bold=True)

# Extended Colors
MODAL_BG     = (255, 255, 255)
MODAL_BORDER = (200, 202, 205)
HEADER_BG    = (240, 242, 245)
STATUS_INFO  = (70, 74, 80)
STATUS_WARN  = (180, 95, 20)
STATUS_GOOD  = (40, 160, 80)

def draw_status_message(
    surface: pygame.Surface,
    message: str,
    color: tuple[int, int, int]
) -> None:
    if not message:
        return

    message_surf = FONT_STATUS.render(message, True, color)
    message_rect = message_surf.get_rect(center=(SCREEN_WIDTH // 2, HEADER_HEIGHT + 14))
    surface.blit(message_surf, message_rect)

def draw_analytics_modal(
    surface: pygame.Surface, 
    history: list[TurnAnalysis], 
    close_btn: Button
) -> None:
    # 1. Dark overlay
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    # 2. Main Modal Card
    modal_width, modal_height = 420, 440
    modal_x = (SCREEN_WIDTH - modal_width) // 2
    modal_y = (SCREEN_HEIGHT - modal_height) // 2
    modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)

    pygame.draw.rect(surface, (255, 255, 255), modal_rect, border_radius=10)
    pygame.draw.rect(surface, (200, 202, 205), modal_rect, width=2, border_radius=10)

    # 3. Modal Title
    title_surf = FONT_MODAL_TITLE.render("GAME ANALYTICS", True, (18, 18, 19))
    surface.blit(title_surf, (modal_x + 20, modal_y + 18))

    # 4. Draw Close Button
    close_btn.rect.topright = (modal_x + modal_width - 15, modal_y + 12)
    close_btn.draw(surface, FONT_BTN)

    # 5. Table Geometry
    headers = ["Guess", "Before", "After", "Elim %", "Rating"]
    col_widths = [65, 55, 55, 65, 110]
    table_x = modal_x + 20
    table_y = modal_y + 60
    row_height = 30

    # 6. Header Row
    header_rect = pygame.Rect(table_x, table_y, sum(col_widths), row_height)
    pygame.draw.rect(surface, (240, 242, 245), header_rect, border_radius=4)

    curr_x = table_x
    for i, h in enumerate(headers):
        text_surf = FONT_ANALYTICS_HEADER.render(h, True, (18, 18, 19))
        surface.blit(text_surf, (curr_x + 5, table_y + 6))
        curr_x += col_widths[i]

    # Debug Check: If history is empty, show a fallback message
    if not history:
        empty_surf = FONT_ANALYTICS_CELL.render("No turns played yet!", True, (120, 120, 120))
        surface.blit(empty_surf, (table_x + 10, table_y + 40))
        return

    # 7. Turn Rows Data Loop
    for row_idx, turn in enumerate(history):
        y_pos = table_y + (row_idx + 1) * row_height
        
        # Row Background
        if row_idx % 2 == 1:
            bg_rect = pygame.Rect(table_x, y_pos, sum(col_widths), row_height)
            pygame.draw.rect(surface, (248, 249, 250), bg_rect)

        # Convert data to strings
        row_data = [
            str(turn.guess),
            str(turn.possibilities_before),
            str(turn.possibilities_after),
            f"{turn.elimination_pct:.1f}%",
            str(turn.skill_rating)
        ]

        curr_x = table_x
        for i, val in enumerate(row_data):
            # Highlight rating column with color
            if i == 4 and turn.skill_rating in ("Solution!", "Pinpointed!"):
                color = (40, 160, 80)  # Green accent
            else:
                color = (18, 18, 19)   # Dark Gray / Black

            cell_surf = FONT_ANALYTICS_CELL.render(val, True, color)
            surface.blit(cell_surf, (curr_x + 5, y_pos + 6))
            curr_x += col_widths[i]

        # Row Separator Line
        pygame.draw.line(
            surface, 
            (220, 222, 225), 
            (table_x, y_pos + row_height), 
            (table_x + sum(col_widths), y_pos + row_height), 
            width=1
        )


running = True
game_over = False  # Track game status

# Game State
grid_letters = [["" for _ in range(5)] for _ in range(6)]
grid_colors: list[list[tuple[int, int, int] | None]]  = [[None for _ in range(5)] for _ in range(6)]
current_row = 0
current_col = 0

game: WordleGame = WordleGame(TARGET_WORDS, FULL_DICTIONARY)
analytics = WordleAnalytics(TARGET_WORDS)
show_analytics = False
btn_close_analytics = Button(x=0, y=0, width=30, height=30, text="X")
status_message = "Type a 5-letter word"
status_color = STATUS_INFO
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    # Update hover states
    btn_reset.check_hover(mouse_pos)
    btn_stats.check_hover(mouse_pos)
    if show_analytics:
        btn_close_analytics.check_hover(mouse_pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Toggle Analytics Modal open
        if btn_stats.is_clicked(event):
            show_analytics = True
            
        # Close Analytics Modal
        if show_analytics and btn_close_analytics.is_clicked(event):
            show_analytics = False

        # Button Click Checks
        if btn_reset.is_clicked(event):
            # TODO: Add reset logic here (clear board, select new word)
            game = WordleGame(TARGET_WORDS, FULL_DICTIONARY)
            analytics = WordleAnalytics(TARGET_WORDS)
            grid_letters = [["" for _ in range(5)] for _ in range(6)]
            grid_colors = [[None for _ in range(5)] for _ in range(6)]
            current_row = 0
            current_col = 0
            reset_key_colors()
            status_message = "Game reset. Type a new guess."
            status_color = STATUS_INFO
        
        if not show_analytics and event.type == pygame.KEYDOWN and not game.is_game_over:
            # 1. Handle Letter Input (A-Z)
            if event.unicode.isalpha() and len(event.unicode) == 1:
                if current_col < 5 and current_row < 6:
                    grid_letters[current_row][current_col] = event.unicode.upper()
                    current_col += 1
                    status_message = ""

            # 2. Handle Backspace
            elif event.key == pygame.K_BACKSPACE:
                if current_col > 0:
                    current_col -= 1
                    grid_letters[current_row][current_col] = ""
                    
            # 3. Handle Enter (Evaluate guess)
            elif event.key == pygame.K_RETURN and current_col == COLS:
                guess = "".join(grid_letters[current_row])
                validated_guess = game.validate_guess(guess)
                
                if validated_guess is not None:
                    # Capture analytics for this submitted guess (appends to analytics.history).
                    analytics.analyze_turn(validated_guess, game.target_word)

                    # Evaluate guess and update grid_colors
                    results = evaluate_guess(validated_guess, game.target_word)
                    for col_idx, status in enumerate(results):
                        grid_colors[current_row][col_idx] = color_map[status]
                    
                    update_key_colors(validated_guess, results)
                    
                    error_message = game.submit_guess()
                    if error_message:
                        status_message = error_message
                        status_color = STATUS_WARN
                    elif game.is_game_over:
                        if game.is_won:
                            status_message = "Congratulations! You guessed the word!"
                            status_color = STATUS_GOOD
                        else:
                            status_message = f"Game Over! The word was {game.target_word}."
                            status_color = STATUS_WARN
                    else:
                        current_row += 1
                        current_col = 0
                        status_message = "Guess submitted"
                        status_color = STATUS_INFO
                else:
                    status_message = "Invalid guess. Not in word list."
                    status_color = STATUS_WARN
            elif event.key == pygame.K_RETURN:
                status_message = "Not enough letters"
                status_color = STATUS_WARN

    # --- Rendering ---
    screen.fill(BG_COLOR)
    
    draw_header(screen)
    draw_status_message(screen, status_message, status_color)
    draw_board(screen, grid_letters, grid_colors)
    draw_keyboard(screen, key_colors)
    
    if show_analytics:
        draw_analytics_modal(screen, analytics.history, btn_close_analytics)

    pygame.display.flip()

pygame.quit()