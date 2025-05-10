import random
import threading
from tkinter import Tk, Button, Label, Frame, IntVar, Toplevel
from tkinter.constants import FLAT, DISABLED, LEFT
from typing import Callable

from const import *
from field_state import CellState
from minefield import Minefield
from settings import BOMB_NUMBER_DICT, MENU_BACKGROUND_COLOR, GAME_MINES_QUANTITY, UNREVEALED_HOVER_CELL_COLOR, REVEALED_HOVER_CELL_COLOR
from utils import get_unrevealed_cell_color, get_revealed_cell_color, traverse, get_button_font, get_photo_image


class Game:
    def __init__(self, root: Tk):
        self.__root = root
        self.__flag_quantity = IntVar(value=GAME_MINES_QUANTITY)
        self.__time = IntVar()
        self.__best_time = IntVar()

        self.__initialize_start_data()

        self.__create_menu()

    def __initialize_start_data(self):
        self.__minefield = Minefield()

        self.__flag_quantity.set(GAME_MINES_QUANTITY)
        self.__time.set(0)
        self.__threading_timer = threading.Timer(1, self.__on_timer_tick)

        self.__is_first_move = True
        self.__is_game_finished = False  # состояние игры
        self.__is_player_loss = False  # сотсояние игры, для отображения мин

        # todo: по-хорошему надо от этого избавляться, но как-нибудь потом... :)
        self.__buttons: list[list[Button | None]] = [[None for _ in range(self.__minefield.get_width())] for _ in
                                                     range(self.__minefield.get_height())]

        self.__traverse(self.__create_button)

    def __create_button(self, row, col):
        bg_color = get_unrevealed_cell_color(row, col)
        button = Button(
            self.__root,
            width=2,
            highlightthickness=0,
            bd=0,
            relief=FLAT,
            font=get_button_font(),
            bg=bg_color,
            activebackground=bg_color,
            command=lambda r=row, c=col: not self.__is_game_finished and self.__reveal(r, c)
        )
        button.grid(row=row, column=col, ipadx=IPADX_UNREVELAED_CELL, ipady=IPADY_UNREVEALED_CELL, padx=0, pady=0)

        button.bind(ENTER_EVENT_NAME, lambda e, r=row, c=col: self.__on_cell_enter(r, c))
        button.bind(LEAVE_EVENT_NAME, lambda e, r=row, c=col: self.__on_cell_leave(r, c))
        button.bind(RIGHT_MOUSE_BUTTON, lambda e, r=row, c=col: self.__toggle_flag(r, c))

        self.__buttons[row][col] = button

    def __create_menu(self):
        outter_frame = Frame(self.__root, width=CELL_SIDE_SIZE * self.__minefield.get_width(), height=CELL_SIDE_SIZE)
        outter_frame.grid(row=self.__minefield.get_height(), column=0, columnspan=self.__minefield.get_width())

        inner_left_frame = Frame(outter_frame)
        inner_left_frame.pack()

        inner_right_frame = Frame(outter_frame)
        inner_right_frame.pack()

        flag_image = get_photo_image(FLAG_IMAGE_PATH)
        flag_label = Label(master=inner_left_frame, image=flag_image, textvariable=self.__flag_quantity, compound=LEFT)
        flag_label.image = flag_image
        flag_label.pack(side=LEFT)

        timer_image = get_photo_image(TIMER_IMAGE_PATH)
        timer_label = Label(master=inner_left_frame, image=timer_image, textvariable=self.__time, compound=LEFT)
        timer_label.image = timer_image
        timer_label.pack(side=LEFT)

        cup_image = get_photo_image(CUP_IMAGE_PATH)
        cup_label = Label(master=inner_left_frame, image=cup_image, textvariable=self.__best_time, compound=LEFT)
        cup_label.image = cup_image
        cup_label.pack(side=LEFT)

        restart_button = Button(master=inner_right_frame, text='Начать заново', highlightthickness=0, bd=1, bg=MENU_BACKGROUND_COLOR,
                                command=self.__restart_game)
        restart_button.pack()

    def __reveal(self, row, col):
        if self.__is_first_move:
            self.__is_first_move = False
            self.__minefield.fill_field(row, col)
            self.__threading_timer.start()

        cell_state = self.__minefield.reveal(row, col)
        if cell_state & (CellState.MINE | CellState.FLAG) == CellState.MINE:
            # Если состояние клетки - мина, но без флага
            self.__on_player_loss()

        self.__update_field()

        self.__check_if_player_win()

    def __toggle_flag(self, row, col):
        if self.__is_first_move or self.__is_game_finished:
            return

        is_flag_up = self.__minefield.toggle_flag(row, col)
        if is_flag_up is not None:
            self.__flag_quantity.set(self.__flag_quantity.get() + (-1 if is_flag_up else 1))

        self.__update_cell(row, col)

    def __update_field(self):
        self.__traverse(self.__update_cell)

    def __update_cell(self, row, col):
        cell_state = self.__minefield.get_cell(row, col)

        if self.__is_player_loss and cell_state & CellState.MINE:
            self.__update_mine_cell(row, col)
            return

        if cell_state & CellState.FLAG:
            self.__update_flag_cell(row, col)
            return

        self.__restore_configure(row, col)

        if cell_state & CellState.UNREVEALED:
            self.__set_cell_color(row, col, get_unrevealed_cell_color(row, col))
            return

        if cell_state & CellState.REVEALED:
            self.__update_revealed_cell(row, col)
            return

        print('tried update cell with ' + cell_state.__str__() + ' state')

    def __update_flag_cell(self, row, col):
        self.__update_image_cell(row, col, FLAG_IMAGE_PATH)

    def __update_mine_cell(self, row, col):
        self.__update_image_cell(row, col, NAVAL_MINE_IMAGE_PATH)
        color = BOMB_NUMBER_DICT.get(random.randint(1, len(BOMB_NUMBER_DICT)))
        self.__get_button(row, col).configure(activebackground=color)
        self.__set_cell_color(row, col, color)

    def __update_image_cell(self, row: int, col: int, image_path: str):
        button = self.__get_button(row, col)
        photo_image = get_photo_image(image_path)
        button.configure(image=photo_image)
        button.grid(row=row, column=col, ipadx=IPADX_IMAGE_CELL, ipady=IPADY_IMAGE_CELL)
        button.image = photo_image

    def __update_revealed_cell(self, row, col):
        near_mines = self.__minefield.calculate_near_mines(row, col)
        mines_str = '' if near_mines == 0 else near_mines
        fg_color = BOMB_NUMBER_DICT.get(near_mines, 'black')
        self.__get_button(row, col).config(text=mines_str, disabledforeground=fg_color, state=DISABLED)
        self.__set_cell_color(row, col, get_revealed_cell_color(row, col))

    def __restore_configure(self, row: int, col: int):
        button = self.__get_button(row, col)
        button.config(image='')
        button.image = None
        button.grid(row=row, column=col, ipadx=IPADX_UNREVELAED_CELL, ipady=IPADY_UNREVEALED_CELL)

    def __traverse(self, call: Callable[[int, int], None]):
        traverse(self.__minefield.get_width(), self.__minefield.get_height(), call)

    def __check_if_player_win(self):
        # Если количество UNREVEALED клеток = количеству мин, то игра выиграна
        all_positions = [(r, c) for r in range(self.__minefield.get_height()) for c in range(self.__minefield.get_width())]
        unrevealed_cells = sum(1 for r, c in all_positions if self.__minefield.get_cell(r, c) & CellState.UNREVEALED)
        if unrevealed_cells == GAME_MINES_QUANTITY:
            self.__on_player_won()

    def __on_player_won(self):
        self.__is_game_finished = True

        cur_time = self.__time.get()
        best_time = self.__best_time.get()
        if best_time == 0 or cur_time < best_time:
            self.__best_time.set(cur_time)

        self.__create_game_result_menu("Победа", "Поздравляем с прохождением сапёра.")

    def __on_player_loss(self):
        self.__is_player_loss = True
        self.__is_game_finished = True

        self.__create_game_result_menu("Поражение", "К сожалению, вы проиграли.")

    def __on_cell_leave(self, row: int, col: int):
        if self.__is_game_finished:
            return

        color = get_revealed_cell_color(row, col) if self.__is_cell_revealed(row, col) else get_unrevealed_cell_color(row, col)
        self.__set_cell_color(row, col, color)

    def __on_cell_enter(self, row: int, col: int):
        if self.__is_game_finished:
            return

        color = REVEALED_HOVER_CELL_COLOR if self.__is_cell_revealed(row, col) else UNREVEALED_HOVER_CELL_COLOR
        self.__set_cell_color(row, col, color)

    def __is_cell_revealed(self, row: int, col: int):
        return self.__minefield.get_cell(row, col) & CellState.REVEALED

    def __set_cell_color(self, row, col, color: str):
        self.__get_button(row, col).config(bg=color)

    def __get_button(self, row: int, col: int):
        return self.__buttons[row][col]

    def __on_timer_tick(self):
        if self.__is_game_finished:
            return

        self.__time.set(self.__time.get() + 1)
        self.__threading_timer = threading.Timer(1, self.__on_timer_tick)
        self.__threading_timer.start()

    def __restart_game(self):
        if self.__threading_timer.is_alive():
            self.__threading_timer.cancel()

        self.__initialize_start_data()

    def __create_game_result_menu(self, title: str, message: str):
        new_window = Toplevel(self.__root)
        new_window.geometry('256x48')
        new_window.resizable(False, False)
        new_window.title(title)

        label = Label(new_window, text=message)
        label.pack()

        button = Button(new_window, text="ОК", command=new_window.destroy)
        button.pack()

        new_window.grab_set()
