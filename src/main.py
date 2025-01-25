import tkinter as tk

from game import Game


def start():
    root = tk.Tk()
    root.resizable(False, False)
    root.title("Сапер")

    Game(root)

    root.mainloop()


if __name__ == '__main__':
    start()
