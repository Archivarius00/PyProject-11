from interface import FantasyInterface

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import io




if __name__ == "__main__":
    root = tk.Tk()
    app = FantasyInterface(root)
    root.mainloop()
    logic = GameLogic() #или бекенд я хз

    # Реализуйте класс GameLogic, который управляет игровой логикой. Интерфейс FantasyInterface вызывает 
    # методы логики и отображает их результат. Вы не трогаете интерфейс, а только отдаёте данные — строки,
    #  списки, NPC и т.п. Весь "мозг" игры живёт в логике