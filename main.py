from interface import FantasyInterface
from backend import Game
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    logic = Game()
    app = FantasyInterface(root, logic=logic)
    logic.interface = app  # обязательно!
    root.mainloop()
