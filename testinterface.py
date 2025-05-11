# testinterface.py

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import io
import time
import config
import random


class FantasyInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Фэнтези Квест")
        self.root.geometry("1200x900")
        self.root.configure(bg="black")

        self.current_npc = None  # для обычного NPC
        self.status_data = config.STATUS_DATA.copy()
        self.log_content = ""

        # === ВЕРХ ===
        self.top_frame = tk.Frame(root, bg="black")
        self.top_frame.pack(fill=tk.BOTH, expand=True)

        self.image_panel = tk.Label(self.top_frame, bg="black", width=600, height=450)
        self.image_panel.pack(side=tk.LEFT, padx=10, pady=10)

        self.text_box = tk.Text(
            self.top_frame, wrap=tk.WORD, bg="black", fg="white",
            font=("Consolas", 14)
        )
        self.text_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.text_box.config(state=tk.DISABLED)
        self.text_box.tag_config("event", foreground="lightblue")
        self.text_box.tag_config("dialogue", foreground="lightgreen")
        self.text_box.tag_config("system", foreground="gray")
        self.text_box.tag_config("warning", foreground="orange")
        self.text_box.tag_config("error", foreground="red")

        # === КНОПКИ ===
        self.button_frame = tk.Frame(root, bg="black")
        self.button_frame.pack(pady=10)

        self.buttons = {}
        self.button_labels = ["Побродить", "Поговорить", "Осмотреть", "Инвентарь", "Показать лог", "Торговец"]
        for label in self.button_labels:
            btn = tk.Button(
                self.button_frame, text=label, width=15,
                command=lambda l=label: self.handle_action(l),
                bg="#333", fg="white", activebackground="#555", activeforeground="white"
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.buttons[label] = btn

        # === СТАТУС ===
        self.status_frame = tk.Frame(root, bd=2, relief=tk.RIDGE, bg="black")
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(
            self.status_frame, textvariable=self.status_var,
            font=("Arial", 11), fg="white", bg="black"
        )
        self.status_label.pack(anchor="w", padx=5, pady=2)
        self.update_status()

        self.log_window = None
        self.load_placeholder_image()

    def update_status(self):
        status_str = " • ".join(f"{key}: {value}" for key, value in self.status_data.items())
        self.status_var.set(status_str)

    def load_placeholder_image(self):
        img = Image.new("RGB", (600, 450), color=(50, 20, 80))
        output = io.BytesIO()
        img.save(output, format="PNG")
        image = Image.open(io.BytesIO(output.getvalue()))
        photo = ImageTk.PhotoImage(image)
        self.image_panel.configure(image=photo)
        self.image_panel.image = photo

    def handle_action(self, action):
        if action == "Побродить":
            self.enter_location()
        elif action == "Поговорить":
            if self.current_npc:
                self.dialogue_window(self.current_npc)
            else:
                self.append_text("В ответ лишь лёгкие дуновения ветра...", tag="warning")
        elif action == "Осмотреть":
            self.append_text("Вы осматриваете местность...", tag="event")
        elif action == "Инвентарь":
            self.show_inventory()
        elif action == "Показать лог":
            self.show_log_window()
        elif action == "Торговец":
            self.show_merchant_window()

    def append_text(self, text, tag=None):
        self.text_box.config(state=tk.NORMAL)
        self.text_box.insert(tk.END, f"\n{text}\n", tag)
        self.text_box.see(tk.END)
        self.text_box.config(state=tk.DISABLED)
        self.append_log(text)

    def append_log(self, log_text):
        self.log_content += f"{log_text}\n"
        if self.log_window and self.log_window.winfo_exists():
            self.update_log_window()

    def show_log_window(self):
        if self.log_window and self.log_window.winfo_exists():
            self.log_window.lift()
            return

        self.log_window = tk.Toplevel(self.root)
        self.log_window.title("Лог событий")
        self.log_window.geometry("700x400")
        self.log_window.configure(bg="black")

        main_frame = tk.Frame(self.log_window, bg="black")
        main_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(main_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_textbox_widget = tk.Text(
            main_frame, wrap=tk.WORD,
            bg="black", fg="white", font=("Consolas", 11),
            yscrollcommand=scrollbar.set
        )
        self.log_textbox_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_textbox_widget.yview)

        self.log_textbox_widget.insert(tk.END, self.log_content)
        self.log_textbox_widget.config(state=tk.DISABLED)

    def update_log_window(self):
        self.log_textbox_widget.config(state=tk.NORMAL)
        self.log_textbox_widget.delete("1.0", tk.END)
        self.log_textbox_widget.insert(tk.END, self.log_content)
        self.log_textbox_widget.config(state=tk.DISABLED)

    def enter_location(self):
        self.append_text("Вы входите в новую локацию...", tag="system")
        self.root.after(config.ENTER_DELAY_MS, self.location_event)

    def location_event(self):
        location = random.choice(config.LOCATIONS)
        self.status_data["Локация"] = location
        self.update_status()

        description = config.LOCATION_DESCRIPTIONS.get(location, "Здесь пусто и странно тихо.")
        self.append_text(description, tag="event")

        if random.random() < config.ENCOUNTER_CHANCE / 100:
            self.current_npc = random.choice([npc for npc in config.NPC_NAMES if npc != "Торговец"])
            self.append_text(f"Вы встречаете персонажа: {self.current_npc}", tag="dialogue")
        else:
            self.current_npc = None

    def dialogue_window(self, npc):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Диалог с {npc}")
        dialog.geometry("600x500")
        dialog.configure(bg="black")

        chat_text = tk.Text(dialog, wrap=tk.WORD, bg="black", fg="white", font=("Arial", 12))
        chat_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=(10, 0))
        chat_text.tag_config("player", foreground="lightgreen")
        chat_text.tag_config("npc", foreground="lightblue")

        chat_text.config(state=tk.NORMAL)
        chat_text.insert(tk.END, f"{npc}: Приветствую. Спрашивай что хочешь.\n", "npc")
        chat_text.config(state=tk.DISABLED)

        entry_frame = tk.Frame(dialog, bg="black")
        entry_frame.pack(fill=tk.X, padx=10, pady=10)

        entry = tk.Entry(entry_frame, font=("Arial", 12))
        entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        entry.focus()

        def send_reply():
            player_input = entry.get()
            if not player_input:
                return
            chat_text.config(state=tk.NORMAL)
            chat_text.insert(tk.END, f"Вы: {player_input}\n", "player")
            response = f"{npc}: Хм... интересная мысль."
            chat_text.insert(tk.END, response + "\n", "npc")
            chat_text.config(state=tk.DISABLED)
            entry.delete(0, tk.END)
            self.append_log(f"Вы -> {npc}: {player_input}")
            self.append_log(response)

        send_button = tk.Button(entry_frame, text="Отправить", command=send_reply, bg="#333", fg="white")
        send_button.pack(side=tk.RIGHT)

    def show_inventory(self):
        inv_text = "\n".join(config.INVENTORY)
        messagebox.showinfo("Инвентарь", f"У вас есть:\n{inv_text}")

    def show_merchant_window(self):
        win = tk.Toplevel(self.root)
        win.title("Торговец")
        win.geometry("400x400")
        win.configure(bg="black")

        label = tk.Label(win, text="Добро пожаловать к торговцу!", font=("Arial", 14), bg="black", fg="orange")
        label.pack(pady=10)

        item_list = tk.Listbox(win, font=("Arial", 12), bg="black", fg="white", selectbackground="gray")
        for item in ["Зелье здоровья", "Щит", "Амулет света"]:
            item_list.insert(tk.END, item)
        item_list.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        def buy():
            selection = item_list.curselection()
            if selection:
                item = item_list.get(selection)
                self.append_text(f"Вы купили: {item}", tag="item")
                self.append_log(f"Покупка у торговца: {item}")

        def sell():
            self.append_text("Вы ничего не продали. (ещё не реализовано)", tag="warning")

        buy_btn = tk.Button(win, text="Купить", command=buy, bg="#333", fg="white")
        sell_btn = tk.Button(win, text="Продать", command=sell, bg="#333", fg="white")
        close_btn = tk.Button(win, text="Закрыть", command=win.destroy, bg="#333", fg="white")

        buy_btn.pack(side=tk.LEFT, padx=10, pady=10, expand=True)
        sell_btn.pack(side=tk.LEFT, padx=10, pady=10, expand=True)
        close_btn.pack(side=tk.RIGHT, padx=10, pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = FantasyInterface(root)
    root.mainloop()
