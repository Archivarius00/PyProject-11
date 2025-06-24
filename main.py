import tkinter as tk
from backend import Game
from interface import FantasyInterface
from Daddy import *

if __name__ == "__main__":
    root = tk.Tk()
    game = Game()
    app = FantasyInterface(root, logic=game)
    app.logic.trader_menu()
    root.mainloop()
    game.interface = app