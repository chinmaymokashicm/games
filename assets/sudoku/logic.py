import random, copy
from typing import Literal, Optional

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
        
    def reset_board(self, board: Optional[list[list[int]]] = None) -> list[list[int]]:
        self.board: list[list[int]] = [[0 for _ in range(9)] for _ in range(9)]
        if board is not None:
            self.board = copy.deepcopy(board)
        return self.board
    
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
    
    def get_value(self, row: int, col: int, board: Optional[list[list[int]]] = None) -> int:
        if board is None:
            board = self.board
        return board[row][col]
    
    def set_value(self, row: int, col: int, value: int, board: Optional[list[list[int]]] = None) -> None:
        if value not in list(range(10)):
            raise Exception(f"Attempting to set invalid number {value} at ({row}, {col})")
        if board is None:
            board = self.board
        board[row][col] = value
    
    def is_cell_valid(self, row: int, col: int, board: Optional[list[list[int]]] = None) -> bool:
        connected_cells: list[tuple[int, int]] = self.get_connected_cells(row, col)
        connected_cell_values: list[int] = [self.get_value(*coordinates, board) for coordinates in connected_cells]
        
        selected_cell_value: int = self.get_value(row, col, board)
        
        if selected_cell_value != 0 and selected_cell_value in connected_cell_values:
            return False
        
        return True
    
    def is_board_valid(self, board: Optional[list[list[int]]] = None) -> bool:
        if board is None:
            board = self.board
        for r in range(9):
            for c in range(9):
                if not self.is_cell_valid(r, c, board):
                    return False
        return True
    
    def generate_solved_board(self, board: Optional[list[list[int]]] = None) -> bool:
        if board is None:
            self.reset_board()
            board = self.board

        for r in range(9):
            for c in range(9):
                if self.get_value(r, c, board) == 0:
                    digits = list(range(1, 10))
                    random.shuffle(digits)
                    
                    for num in digits:
                        self.set_value(r, c, num, board)
                        
                        if self.is_cell_valid(r, c, board):
                            if self.generate_solved_board(board):
                                return True
                        
                        self.set_value(r, c, 0, board)
                    
                    return False
                
        return True
    
    def initialize_sudoku_board(self) -> list[list[int]]:
        self.generate_solved_board()
        
        new_board: list[list[int]] = copy.deepcopy(self.board)
        
        positions = [(r, c) for r in range(9) for c in range(9)]
        for r, c in random.sample(positions, self.holes):
            new_board[r][c] = 0
            
        return new_board