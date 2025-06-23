import tkinter as tk
from backend import Game
from interface import FantasyInterface

if __name__ == "__main__":
    root = tk.Tk()
    game = Game()
    app = FantasyInterface(root, logic=game)
    root.mainloop()
