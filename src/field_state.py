from enum import Flag, auto


class CellState(Flag):
    UNDEFIEND = 0
    UNREVEALED = auto()
    REVEALED = auto()
    FLAG = auto()
    MINE = auto()
