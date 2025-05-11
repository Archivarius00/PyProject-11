import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import io



class FantasyInterface:
    def __init__(self, root, logic=None):
        self.root = root
        self.root.title("Фэнтези Квест")
        self.root.geometry("1200x900")
        self.root.configure(bg="black")

        self.logic = logic
        self.current_npc = None
        self.status_data = {}  # будет обновляться извне
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
        self.text_box.tag_config("item", foreground="gold")

        # === КНОПКИ ===
        self.button_frame = tk.Frame(root, bg="black")
        self.button_frame.pack(pady=10)

        self.buttons = {}
        self.button_labels = ["Побродить", "Поговорить", "Инвентарь", "Показать лог", "Торговец"]
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
        if self.logic:
            self.logic.on_action(action)
        else:
            self.append_text(f"Нет логики для действия: {action}", tag="warning")

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

    def show_dialogue(self, npc_name, messages):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Диалог с {npc_name}")
        dialog.geometry("600x500")
        dialog.configure(bg="black")

        chat_text = tk.Text(dialog, wrap=tk.WORD, bg="black", fg="white", font=("Arial", 12))
        chat_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=(10, 0))
        chat_text.tag_config("player", foreground="lightgreen")
        chat_text.tag_config("npc", foreground="lightblue")

        chat_text.config(state=tk.NORMAL)
        for speaker, msg in messages:
            tag = "player" if speaker == "player" else "npc"
            chat_text.insert(tk.END, f"{speaker.capitalize()}: {msg}\n", tag)
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
            response = self.logic.get_npc_response(npc_name, player_input) if self.logic else "..."
            chat_text.insert(tk.END, f"{npc_name}: {response}\n", "npc")
            chat_text.config(state=tk.DISABLED)
            entry.delete(0, tk.END)
            self.append_log(f"Вы -> {npc_name}: {player_input}")
            self.append_log(f"{npc_name}: {response}")

        send_button = tk.Button(entry_frame, text="Отправить", command=send_reply, bg="#333", fg="white")
        send_button.pack(side=tk.RIGHT)

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = FantasyInterface(root)
#     root.mainloop()


### ТАК КОРОЧЕ ЭТОТ ФАЙЛ УЖЕ ДЛЯ ИМПОРТА
# ЧТО БЫЛО СДЕЛАНО:
# Удалены/упрощены логические методы:
#   enter_location()
#   location_event()
#   dialogue_window() (оставлен шаблон с передачей текста)
#   show_inventory()
#   show_merchant_window() (упрощён, без логики покупок)
#   def send_reply():
#   def buy()
#   def sell()

# Через self.logic, который нужно передать при инициализации (можно задать объект логики).