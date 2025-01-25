import random

from field_state import CellState
from util.settings import GAME_WIDTH_FIELD_SIZE, GAME_HEIGHT_FIELD_SIZE, GAME_MINES_QUANTITY
from util.utils import get_neighbors, is_in_game_area


class Minefield:
    def __init__(self):
        self.__width = GAME_WIDTH_FIELD_SIZE
        self.__height = GAME_HEIGHT_FIELD_SIZE
        self.__mines = GAME_MINES_QUANTITY
        self.__cells = [[CellState.UNREVEALED for _ in range(self.__width)] for _ in range(self.__height)]

    def fill_field(self, row: int, col: int):
        safe_area = set(get_neighbors(row, col))
        all_positions = [(r, c) for r in range(self.__height) for c in range(self.__width)]
        mine_positions = random.sample([pos for pos in all_positions if pos not in safe_area], self.__mines)

        for r, c in mine_positions:
            self.__cells[r][c] |= CellState.MINE

        self.__reveal_empty_cells(row, col)

    def __reveal_empty_cells(self, row: int, col: int):
        stack = [(row, col)]
        visited = set()

        while stack:
            current_row, current_col = stack.pop()

            if (current_row, current_col) in visited:
                continue

            visited.add((current_row, current_col))
            self.reveal(current_row, current_col)

            if self.calculate_near_mines(current_row, current_col) == 0:
                stack.extend((r, c) for r, c in get_neighbors(current_row, current_col) if (r, c) not in visited)
    def reveal(self, row: int, col: int) -> CellState:
        cell_state = self.__cells[row][col]
        if cell_state == CellState.UNREVEALED:
            self.__cells[row][col] = CellState.REVEALED
            if self.calculate_near_mines(row, col) == 0:
                self.__reveal_empty_cells(row, col)

        return cell_state

    def calculate_near_mines(self, row, col) -> int:
        return sum(
            1 for r, c in get_neighbors(row, col)
            if self.get_cell(r, c) & CellState.MINE
        )

    def toggle_flag(self, row: int, col: int) -> bool | None:
        cell = self.__cells[row][col]

        if cell & CellState.REVEALED:
            return None

        if cell & CellState.FLAG:
            self.__cells[row][col] &= ~CellState.FLAG
            return False

        self.__cells[row][col] |= CellState.FLAG
        return True

    def get_cell(self, row: int, col: int):
        if not is_in_game_area(row, col):
            return CellState.UNDEFIEND

        return self.__cells[row][col]

    def get_width(self):
        return self.__width

    def get_height(self):
        return self.__height
