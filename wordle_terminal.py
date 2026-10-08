"""
Play Wordle on the Terminal.
"""

from assets.wordle.load import FULL_DICTIONARY, TARGET_WORDS
from assets.wordle.logic import WordleGame, evaluate_guess, BOARD_WIDTH, MAX_ATTEMPTS
from assets.wordle.analytics import WordleAnalytics, TurnAnalysis

import os
from typing import Optional, Any

from tabulate import tabulate

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def main():
    game = WordleGame(TARGET_WORDS, FULL_DICTIONARY)
    # turn_analyses: list[list[Any]] = []
    all_guesses: list[str] = []
    try:
        while not game.is_game_over:
            clear_screen()
            print(f"Attempt {game.current_row + 1}/{MAX_ATTEMPTS}")
            print(tabulate(game.get_terminal_grid(), tablefmt="grid"))
            print(game.get_terminal_keyboard())
            
            guess = input("Input a 5-letter word: ").strip().upper()
            guess = game.validate_guess(guess)
            if guess is None:
                print("Invalid guess. Please try again.")
                continue
            all_guesses.append(guess)
            
            error_message = game.submit_guess()
            if error_message:
                print(error_message)
                continue
            
            # turn_analysis: TurnAnalysis = WordleAnalytics(TARGET_WORDS).analyze_turn(guess, game.target_word)
            # turn_analyses.append(turn_analysis.to_list())
            
            if game.is_won:
                clear_screen()
                # print(tabulate(game.grid_letters, tablefmt="grid"))
                print(tabulate(game.get_terminal_grid(), tablefmt="grid"))
                print(game.get_terminal_keyboard())
                print("Congratulations! You've guessed the word!")
                break
        else:
            clear_screen()
            print(tabulate(game.get_terminal_grid(), tablefmt="grid"))
            # print(tabulate(game.get_terminal_grid(), tablefmt="grid", stralign=))
            print(f"Game Over! The correct word was: {game.target_word}") 
        
    except KeyboardInterrupt:
        print("\nGame interrupted. The correct word was:", game.target_word)
        
    # print(tabulate(turn_analyses, headers=TurnAnalysis.get_headers(), tablefmt="grid"))
    
    all_analyses: list[list[str | int | float]] = [analysis.to_list() for analysis in WordleAnalytics(TARGET_WORDS).analyze(all_guesses, game.target_word)]
    print(tabulate(all_analyses, headers=TurnAnalysis.get_headers(), tablefmt="grid"))
        
        
if __name__ == "__main__":
    main()