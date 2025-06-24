import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import io
from config import *
from ai_chat import chat_stream
import time
from backend import *
from Daddy import *

class FantasyInterface:
    def __init__(self, root, logic=None):
        self.root = root
        self.root.title("Фэнтези Квест")
        self.root.geometry("1200x900")
        self.root.configure(bg="black")

        self.logic = logic
        self.log_content = ""
        self.log_window = None
        self.dialogue_window = None
        self.frog_ai_enabled = False

        self.create_widgets()
        self.load_placeholder_image()

        if self.logic:
            self.logic.interface = self
            self.update_status_display()
            self.append_text("Добро пожаловать в игру!")

    def create_widgets(self):
        self.top_frame = tk.Frame(self.root, bg="black")
        self.top_frame.pack(fill=tk.BOTH, expand=True)

        self.image_panel = tk.Label(self.top_frame, bg="black", width=600, height=450)
        self.image_panel.pack(side=tk.LEFT, padx=10, pady=10)

        self.text_box = tk.Text(self.top_frame, wrap=tk.WORD, bg="black", fg="white", font=("Consolas", 14), state=tk.DISABLED)
        self.text_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        for tag, color in TEXT_COLORS.items():
            self.text_box.tag_config(tag, foreground=color)

        self.input_frame = tk.Frame(self.root, bg="black")
        self.input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.command_entry = tk.Entry(self.input_frame, bg="#222", fg="white", font=("Consolas", 12), insertbackground="white")
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind("<Return>", self.process_command)

        self.send_button = tk.Button(self.input_frame, text="Отправить", command=self.process_command, bg="#333", fg="white", activebackground="#555")
        self.send_button.pack(side=tk.RIGHT)

        self.button_frame = tk.Frame(self.root, bg="black")
        self.button_frame.pack(fill=tk.X, pady=5)

        self.buttons = {
            "Побродить": tk.Button(self.button_frame, text="Побродить", command=lambda: self.handle_action("Побродить"), bg="#333", fg="white", width=15),
            "Торговец": tk.Button(self.button_frame, text="Торговец", command=lambda: self.handle_action("Торговец"), bg="#333", fg="white", width=15),
            "Инвентарь": tk.Button(self.button_frame, text="Инвентарь", command=lambda: self.handle_action("Инвентарь"), bg="#333", fg="white", width=15),
            "Локации": tk.Button(self.button_frame, text="Локации", command=lambda: self.handle_action("Локации"), bg="#333", fg="white", width=15)
        }

        for btn in self.buttons.values():
            btn.pack(side=tk.LEFT, padx=5)

        self.status_frame = tk.Frame(self.root, bg="black")
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(self.status_frame, textvariable=self.status_var, font=("Arial", 11), fg="white", bg="black")
        self.status_label.pack(anchor="w")

    def enable_frog_dialogue(self):
        self.frog_ai_enabled = True
        self.buttons["Поговорить"].config(state="normal")

    def append_text(self, text, tag=None):
        self.text_box.config(state=tk.NORMAL)
        self.text_box.insert(tk.END, "\n", tag)
        for char in text:
            self.text_box.insert(tk.END, char, tag)
            self.text_box.see(tk.END)
            self.text_box.update()
            time.sleep(0.01)
        self.text_box.insert(tk.END, "\n")
        self.text_box.config(state=tk.DISABLED)

    def handle_action(self, action):
        global _daddy_is_aroused
        global get_sugar_daddy

        if action == "Побродить":
            if self.logic:
                self.logic.walk()
        elif action == "Инвентарь":
            self.show_inventory()
        elif action == "Локации":
            self.show_location_selector()
        elif action == "Торговец":
            if self.logic and get_sugar_daddy():
                game_curr, root_curr = get_sugar_daddy()
                check_daddy = FantasyInterface(root_curr, logic=game_curr)
                check_daddy.logic.trader_menu()



    def process_command(self, event=None):
        command = self.command_entry.get().strip()
        self.command_entry.delete(0, tk.END)

        if not command:
            return

        self.append_text(f"> {command}", "player")

        if self.logic:
            if command.lower().startswith("идти "):
                location = command[5:].strip()
                self.logic.change_location(location)
            elif command.lower() == "инвентарь":
                self.show_inventory()
            else:
                self.append_text("Неизвестная команда", "warning")

    def show_inventory(self):
        if not self.logic:
            return
        inv = self.logic.player.inventory
        stones = [k for k, v in self.logic.player.stones.items() if v]
        messagebox.showinfo("Инвентарь", "\n".join([f"{k}: {v}" for k, v in inv.items()]) + "\n\nКамни: " + ", ".join(stones))

    def show_location_selector(self):
        window = tk.Toplevel(self.root)
        window.title("Выбор локации")
        tk.Label(window, text="Куда пойдём?").pack(pady=5)

        if FLAG_TEMPLE == 0:
            for loc in ["замок", "болото", "лес", "хижина"]:
                tk.Button(window, text=loc, command=lambda l=loc: self.select_location(l, window)).pack(padx=10, pady=2)
        else:
            for loc in ["замок", "болото", "лес", "хижина", "храм"]:
                tk.Button(window, text=loc, command=lambda l=loc: self.select_location(l, window)).pack(padx=10, pady=2)

    def select_location(self, location, window):
        if self.logic:
            self.logic.change_location(location)
            if location == "храм":
                self.logic.temple_ending()
        window.destroy()

    def update_status_display(self):
        if not self.logic:
            return
        p = self.logic.player
        status = [
            f"Камешки: {p.inventory['камешки']}",
            f"Патроны: {p.inventory['патроны']}",
            f"Дробовик: {'Да' if p.has_shotgun else 'Нет'}",
            f"Камни: {', '.join(k for k, v in p.stones.items() if v)}"
        ]
        self.status_var.set(" | ".join(status))

    def load_placeholder_image(self):
        img = Image.new("RGB", (600, 450), color=(50, 20, 80))
        output = io.BytesIO()
        img.save(output, format="PNG")
        image = Image.open(io.BytesIO(output.getvalue()))
        photo = ImageTk.PhotoImage(image)
        self.image_panel.configure(image=photo)
        self.image_panel.image = photo

    def show_choice_dialog(self, prompt, options):
        self.choice_result = None
        dialog = tk.Toplevel(self.root)
        dialog.title("Выбор")
        dialog.configure(bg="black")
        dialog.grab_set()
        tk.Label(dialog, text=prompt, bg="black", fg="white", font=("Arial", 14), wraplength=400).pack(padx=20, pady=20)
        for option in options:
            tk.Button(dialog, text=option, width=30, font=("Arial", 12), command=lambda opt=option: self._choose_option(dialog, opt)).pack(pady=5)
        self.root.wait_window(dialog)
        return self.choice_result

    def _choose_option(self, dialog, option):
        self.choice_result = option
        dialog.destroy()

    def show_text_input(self, prompt):
        return simpledialog.askstring("Ввод", prompt, parent=self.root)

    def end_game(self, message, tag="info"):
        if tag == "win":
            messagebox.showinfo("Победа", message)
        elif tag == "fail":
            messagebox.showwarning("Конец игры", message)
        else:
            messagebox.showinfo("Конец", message)
        self.root.destroy()

    def start_ai_dialogue(self):
        self.append_text("Вы встретили лягушку, которая выглядит как самый отвязный панк", "event")
        self.frog_ai_enabled = True

        window = tk.Toplevel(self.root)
        window.title("диалог")
        window.geometry("600x800")
        window.configure(bg="black")

        text_area = tk.Text(window, bg="black", fg="white", font=("Consolas", 12), wrap=tk.WORD, state=tk.DISABLED)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        entry = tk.Entry(window, bg="#222", fg="white", font=("Consolas", 12))
        entry.pack(fill=tk.X, padx=10, pady=5)

        messages = [{
            "role": "system",
            "content": "ты - лягушка панк в волшебном лесу, ты очень сильно ненавидишь вежливых людей и общаешься очень грубо, у тебя есть волшебный камень и ты отдашь его только если человек ответит на 3 вопроса про популярную рок музыку 1980-2000-х (можно спрашивать про металику, RHCP, Iron maiden, Queen, Green Day, Deep Purple, вопросы про нирвану запрещены). если человек не ответит хотя бы на один вопрос, ты должен написать: тебе тут больше ничего не светит, вали. также скажи что нашел какую-то безделушку, если человек долго не будет спрашивать о ней"
        }]

        answered_once = False

        def send():
            nonlocal answered_once
            user_msg = entry.get().strip()
            if not user_msg:
                return
            entry.delete(0, tk.END)
            text_area.config(state=tk.NORMAL)
            text_area.insert(tk.END, f"Вы: {user_msg}\n")
            text_area.config(state=tk.DISABLED)
            messages.append({"role": "user", "content": user_msg})
            window.update()
            ai_response = chat_stream(messages)
            messages.append({"role": "assistant", "content": ai_response})
            text_area.config(state=tk.NORMAL)
            text_area.insert(tk.END, f"Фроггит: {ai_response}\n")
            text_area.config(state=tk.DISABLED)
            text_area.see(tk.END)
            if answered_once:
                if "тебе тут больше ничего не светит" in ai_response.lower():
                    self.append_text("Фроггит прогнал вас. Попробуй в другой раз...", "npc")

                    close_btn = tk.Button(window, text="Закрыть", command=window.destroy, bg="#550", fg="white")
                    close_btn.pack(pady=10)
                elif ("держи" in ai_response.lower() or "получай" in ai_response.lower()) and "камень" in ai_response.lower():
                    self.logic.temple_unlocked = True
                    self.logic.frog_quiz_passed = True
                    self.logic.player.defeated["frog"] = True
                    self.logic.player.stones["камень - путеводитель"] = True
                    self.logic.temple_unlocked = True
                    self.logic.frog_quiz_passed = True
                    self.logic.player.defeated["frog"] = True
                    self.logic.player.stones["камень - путеводитель"] = True
                    self.append_text("Фроггит отдал вам камень. Теперь вы можете идти в храм!", "event")

                    close_btn = tk.Button(window, text="Закрыть", command=window.destroy, bg="#550", fg="white")
                    close_btn.pack(pady=10)
            else:
                answered_once = True
        entry.bind("<Return>", lambda e: send())
        tk.Button(window, text="Отправить", command=send, bg="#444", fg="white").pack(pady=5)
