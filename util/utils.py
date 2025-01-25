from itertools import product
from tkinter import PhotoImage
from tkinter.font import nametofont, BOLD
from typing import Callable

from settings import CLOSED_LIGHT_CELL_COLOR, CLOSED_DARK_CELL_COLOR, OPEN_LIGHT_CELL_COLOR, OPEN_DARK_CELL_COLOR, \
    GAME_HEIGHT_FIELD_SIZE, GAME_WIDTH_FIELD_SIZE


def get_cell_brightness(row: int, col: int) -> bool:
    """
    Получить яркость ячейки в зависимости от её расположения.
    Яркость определяется шахматным порядком, первая ячейка - светлая.
    :return: True, если ячейка светлая, иначе False
    """
    return (row + col) % 2 == 0


def get_unrevealed_cell_color(row: int, col: int) -> str:
    return CLOSED_LIGHT_CELL_COLOR if get_cell_brightness(row, col) else CLOSED_DARK_CELL_COLOR


def get_revealed_cell_color(row: int, col: int) -> str:
    return OPEN_LIGHT_CELL_COLOR if get_cell_brightness(row, col) else OPEN_DARK_CELL_COLOR


def traverse(width: int, height: int, call: Callable[[int, int], None]):
    for row in range(height):
        for col in range(width):
            call(row, col)


def get_neighbors(row: int, col: int):
    return (
        (r, c) for r, c in product(range(row - 1, row + 2), range(col - 1, col + 2))
        if is_in_game_area(r, c)
    )


def is_in_game_area(row: int, col: int) -> bool:
    return 0 <= row < GAME_HEIGHT_FIELD_SIZE and 0 <= col < GAME_WIDTH_FIELD_SIZE


def get_button_font():
    font = nametofont('TkDefaultFont')
    font.config(weight=BOLD)
    return font


def get_photo_image(image_path: str):
    return PhotoImage(file=image_path)
