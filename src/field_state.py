from enum import Flag, auto, IntFlag


class CellState(Flag):
    UNDEFIEND = 0
    UNREVEALED = auto()
    REVEALED = auto()
    FLAG = auto()
    MINE = auto()
