import random
from collections import Counter
from typing import Optional
import string

BOARD_WIDTH = 5
MAX_ATTEMPTS = 6

# Standard Status Indicators
STATUS_CORRECT = "CORRECT"
STATUS_PRESENT = "PRESENT"
STATUS_ABSENT  = "ABSENT"

# ANSI Color Constants
COLOR_GREEN  = "\033[30;42m"  # Black text on Green
COLOR_YELLOW = "\033[30;43m"  # Black text on Yellow
COLOR_GRAY   = "\033[97;100m" # White text on Dark Gray
COLOR_RESET  = "\033[0m"

def evaluate_guess(guess: str, target: str) -> list[str]:
    """Evaluates a guess against target using two-pass count tracking."""
    matches = [STATUS_ABSENT] * BOARD_WIDTH
    target_counts = Counter(target)
    
    # Pass 1: Greens
    for i in range(BOARD_WIDTH):
        if guess[i] == target[i]:
            matches[i] = STATUS_CORRECT
            target_counts[guess[i]] -= 1
            
    # Pass 2: Yellows
    for i in range(BOARD_WIDTH):
        if matches[i] == STATUS_CORRECT:
            continue
        char = guess[i]
        if target_counts[char] > 0:
            matches[i] = STATUS_PRESENT
            target_counts[char] -= 1
            
    return matches

class WordleGame:
    """Manages full game state cleanly across both Terminal and GUI apps."""
    
    def __init__(self, target_words: list[str], full_dictionary: set[str]):
        self.target_words = target_words
        self.full_dictionary = full_dictionary
        # self.possible_words = target_words
        self.reset()
    
    def validate_guess(self, guess: str) -> Optional[str]:

        if len(guess) != BOARD_WIDTH:
            print(f"The word should be exactly {BOARD_WIDTH} letters long.")
            return None

        if not guess.isalpha():
            print("Not all characters are letters.")
            return None

        if guess not in self.full_dictionary:
            print("Not in word list.")
            return None

        # Populate the current row so submit_guess() sees the letters!
        for char in guess:
            self.add_letter(char)

        return guess

    def reset(self):
        self.target_word = random.choice(self.target_words)
        self.grid_letters = [["" for _ in range(BOARD_WIDTH)] for _ in range(MAX_ATTEMPTS)]
        self.grid_statuses: list[list[Optional[str]]] = [
            [None for _ in range(BOARD_WIDTH)] for _ in range(MAX_ATTEMPTS)
        ]
        self.letter_statuses = {}  # Stores best status for A-Z
        self.current_row = 0
        self.current_col = 0
        self.is_won = False
        self.is_game_over = False

    def add_letter(self, char: str):
        if not self.is_game_over and self.current_col < BOARD_WIDTH:
            self.grid_letters[self.current_row][self.current_col] = char.upper()
            self.current_col += 1

    def remove_letter(self):
        if not self.is_game_over and self.current_col > 0:
            self.current_col -= 1
            self.grid_letters[self.current_row][self.current_col] = ""

    def submit_guess(self) -> Optional[str]:
        """Submits current row guess. Returns error message string if invalid."""
        if self.current_col < BOARD_WIDTH:
            return "Not enough letters"
            
        guess = "".join(self.grid_letters[self.current_row])
        if guess not in self.full_dictionary:
            return "Not in word list"

        # Evaluate matches
        statuses = evaluate_guess(guess, self.target_word)
        for i, status in enumerate(statuses):
            self.grid_statuses[self.current_row][i] = status

        # Update keyboard statuses
        for char, status in zip(guess, statuses):
            curr = self.letter_statuses.get(char)
            if status == STATUS_CORRECT:
                self.letter_statuses[char] = STATUS_CORRECT
            elif status == STATUS_PRESENT and curr != STATUS_CORRECT:
                self.letter_statuses[char] = STATUS_PRESENT
            elif status == STATUS_ABSENT and curr not in (STATUS_CORRECT, STATUS_PRESENT):
                self.letter_statuses[char] = STATUS_ABSENT

        # Check win/loss
        if guess == self.target_word:
            self.is_won = True
            self.is_game_over = True
        elif self.current_row + 1 >= MAX_ATTEMPTS:
            self.is_game_over = True
        else:
            self.current_row += 1
            self.current_col = 0
            
        return None  # Success
    
    def get_terminal_grid(self) -> list[list[str]]:
        """Returns a copy of grid_letters formatted with ANSI color codes for terminal display."""
        formatted_grid = [["" for _ in range(BOARD_WIDTH)] for _ in range(MAX_ATTEMPTS)]
        
        for row in range(MAX_ATTEMPTS):
            for col in range(BOARD_WIDTH):
                letter = self.grid_letters[row][col]
                status = self.grid_statuses[row][col]
                
                if not letter:
                    formatted_grid[row][col] = " "
                elif status == STATUS_CORRECT:
                    formatted_grid[row][col] = f"{COLOR_GREEN} {letter} {COLOR_RESET}"
                elif status == STATUS_PRESENT:
                    formatted_grid[row][col] = f"{COLOR_YELLOW} {letter} {COLOR_RESET}"
                elif status == STATUS_ABSENT:
                    formatted_grid[row][col] = f"{COLOR_GRAY} {letter} {COLOR_RESET}"
                else:
                    # Unsubmitted letter in current row
                    formatted_grid[row][col] = f" {letter} "
                    
        return formatted_grid

    def get_terminal_keyboard(self) -> str:
        """Renders the A-Z alphabet formatted with current letter statuses."""
        formatted_keys = []
        for char in string.ascii_uppercase:
            status = self.letter_statuses.get(char)
            if status == STATUS_CORRECT:
                formatted_keys.append(f"{COLOR_GREEN} {char} {COLOR_RESET}")
            elif status == STATUS_PRESENT:
                formatted_keys.append(f"{COLOR_YELLOW} {char} {COLOR_RESET}")
            elif status == STATUS_ABSENT:
                formatted_keys.append(f"{COLOR_GRAY} {char} {COLOR_RESET}")
            else:
                formatted_keys.append(f" {char} ")
        return " ".join(formatted_keys)