import random, copy
from typing import Literal

class SudokuGame:
    """Manages the Sudoku board."""
    
    def __init__(self, difficulty: Literal["EASY", "MEDIUM", "HARD"]):
        difficulty_str = difficulty.strip().upper()
        if difficulty_str not in ["EASY", "MEDIUM", "HARD"]:
            raise Exception(f"Invalid difficulty level: {difficulty_str}. Use one of ['EASY', 'MEDIUM', 'HARD']")
        holes_map = {"EASY": 32, "MEDIUM": 45, "HARD": 54}
        self.difficulty = difficulty_str
        self.holes = holes_map[self.difficulty]
        self.reset_board()
        
    def reset_board(self):
        self.board: list[list[int]] = [[0 for _ in range(9)] for _ in range(9)]
        
    def get_connected_cells(self, row: int, col: int) -> list[tuple[int, int]]:
        connected_cells: set[tuple[int, int]] = set()
        
        # Same row & column
        for i in range(9):
            if i != col:
                connected_cells.add((row, i))
            if i != row:
                connected_cells.add((i, col))
                
        # Same 3x3 box
        box_r, box_c = (row // 3) * 3, (col // 3) * 3
        for r in range(box_r, box_r + 3):
            for c in range(box_c, box_c + 3):
                if (r, c) != (row, col):
                    connected_cells.add((r, c))
                    
        return list(connected_cells)
    
    def get_value(self, row: int, col: int) -> int:
        return self.board[row][col]
    
    def set_value(self, row: int, col: int, value: int) -> None:
        if value not in list(range(10)):
            raise Exception(f"Attempting to set invalid number {value} at ({row}, {col})")
        self.board[row][col] = value
    
    def is_valid(self, row: int, col: int) -> bool:
        connected_cells: list[tuple[int, int]] = self.get_connected_cells(row, col)
        connected_cell_values: list[int] = [self.get_value(*coordinates) for coordinates in connected_cells]
        
        selected_cell_value: int = self.get_value(row, col)
        
        if selected_cell_value != 0 and selected_cell_value in connected_cell_values:
            return False
        
        return True
    
    def generate_solved_board(self) -> bool:
        # self.reset_board()
        for r in range(9):
            for c in range(9):
                if self.get_value(r, c) == 0:
                    digits = list(range(1, 10))
                    random.shuffle(digits)
                    
                    for num in digits:
                        self.set_value(r, c, num)
                        
                        if self.is_valid(r, c):
                            if self.generate_solved_board():
                                return True
                        
                        self.set_value(r, c, 0)
                    
                    return False
                
        return True
    
    def initialize_sudoku_board(self) -> list[list[int]]:
        self.generate_solved_board()
        
        new_board: list[list[int]] = copy.deepcopy(self.board)
        
        positions = [(r, c) for r in range(9) for c in range(9)]
        for r, c in random.sample(positions, self.holes):
            new_board[r][c] = 0
            
        return new_board