# fantasy_interface.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import io
import random
import config

class FantasyInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Фэнтези Квест")
        self.root.geometry("1200x900")
        self.root.configure(bg="black")

        # Инициализация игрового состояния
        self.current_npc = None
        self.status_data = config.STATUS_DATA.copy()
        self.inventory = config.INVENTORY.copy()
        self.log_content = ""
        self.player_location = "Зачарованный лес"
        self.knows_temple = False
        self.promised_return = False
        self.timer_active = False
        self.shotgun_ammo = 0
        self.has_shotgun = False
        self.deer_encountered = False
        self.trader_visible = False

        # Инициализация интерфейса
        self.setup_ui()
        self.append_text(f"Вы начинаете в {self.player_location}!", tag="system")

    def setup_ui(self):
        """Создание графического интерфейса"""
        # Верхняя панель
        self.top_frame = tk.Frame(self.root, bg="black")
        self.top_frame.pack(fill=tk.BOTH, expand=True)

        # Панель изображения локации
        self.image_panel = tk.Label(self.top_frame, bg="black", width=600, height=450)
        self.image_panel.pack(side=tk.LEFT, padx=10, pady=10)
        self.load_placeholder_image()

        # Прогресс-бар для перемещения
        self.progress_frame = tk.Frame(self.top_frame, bg="black")
        self.progress_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate', length=580)
        self.progress_bar.pack(pady=5)
        self.progress_label = tk.Label(self.progress_frame, text="", fg="white", bg="black")
        self.progress_label.pack()

        # Текстовое поле для лога событий
        self.text_box = tk.Text(
            self.top_frame,
            wrap=tk.WORD,
            bg="black",
            fg="white",
            font=("Consolas", 14)
        )
        self.text_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.text_box.config(state=tk.DISABLED)
        self.setup_text_tags() 

        # Панель кнопок действий
        self.button_frame = tk.Frame(self.root, bg="black")
        self.button_frame.pack(pady=10)
        self.setup_buttons()

        # Панель статуса игрока
        self.status_frame = tk.Frame(self.root, bg="black")
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)
        self.setup_status()

    def setup_text_tags(self):
        """Настройка цветовых тегов для текста"""
        color_scheme = {
            "event": "lightblue",    # События
            "dialogue": "lightgreen", # Диалоги NPC
            "system": "gray",       # Системные сообщения
            "warning": "orange",    # Предупреждения
            "error": "red",         # Критические ошибки
            "success": "green",     # Успешные действия
            "item": "yellow"        # Предметы
        }
        for tag, color in color_scheme.items():
            self.text_box.tag_config(tag, foreground=color)

    def setup_buttons(self):
        """Инициализация кнопок управления"""
        buttons = [
            ("Переместиться", self.start_movement),
            ("Поговорить", self.handle_dialogue),
            ("Инвентарь", self.show_inventory),
            ("Торговец", self.show_merchant),
            ("Лог", self.show_log)
        ]
        for text, command in buttons:
            btn = tk.Button(
                self.button_frame,
                text=text,
                width=15,
                command=command,
                bg="#333",
                fg="white")
            btn.pack(side=tk.LEFT, padx=5)

    def setup_status(self):
        """Инициализация панели статуса"""
        self.status_var = tk.StringVar()
        self.status_label = tk.Label(
            self.status_frame,
            textvariable=self.status_var,
            font=("Arial", 11),
            fg="white",
            bg="black")
        self.status_label.pack(anchor="w", padx=5, pady=2)
        self.update_status()

    def load_placeholder_image(self):
        """Загрузка фонового изображения"""
        img = Image.new("RGB", (600, 450), color=(50, 20, 80))  # Фиолетовый фон
        output = io.BytesIO()
        img.save(output, format="PNG")
        image = Image.open(io.BytesIO(output.getvalue()))
        photo = ImageTk.PhotoImage(image)
        self.image_panel.configure(image=photo)
        self.image_panel.image = photo

    def start_movement(self):
        """Начало процесса перемещения"""
        if self.timer_active:
            return

        if action == "Побродить":
            self.start_timer("Побродить")
        elif action == "Поговорить":
            if self.current_npc:
                if "Гарольд" in self.current_npc:
                    self.dialogue_harold()
                elif "Фроггит" in self.current_npc:
                    self.dialogue_froggit()
                elif "Дракула" in self.current_npc:
                    self.encounter_dracula()
                elif "Лань" in self.current_npc:
                    self.dialogue_deer()
                elif "Лесник" in self.current_npc:
                    self.dialogue_forester()
                else:
                    self.dialogue_window(self.current_npc)
            else:
                self.append_text("Здесь нет никого, с кем можно поговорить.", tag="warning")
        elif action == "Осмотреть":
            self.append_text(config.LOCATION_DESCRIPTIONS.get(self.player_location, "Ничего интересного."), tag="event")
        elif action == "Инвентарь":
            self.show_inventory()
        elif action == "Торговец":
            self.show_merchant_window()
        elif action == "Показать лог":
            self.show_log_window()

    def start_timer(self, action):
        self.timer_active = True
        self.progress_bar["value"] = 0
        self.progress_label.config(text="Перемещение...")
        self.update_progress(0)

    def update_progress(self, value):
        """Обновление прогресс-бара"""
        if value < 100:
            self.progress_bar["value"] = value
            self.root.after(50, lambda: self.update_progress(value + 4))
        else:
            self.timer_active = False
            self.progress_label.config(text="")
            self.move_to_new_location()

    def move_to_new_location(self):
        """Обработка перемещения между локациями"""
        available = self.get_available_locations()
        choice = self.show_location_dialog(available)
        
        if choice:
            self.player_location = choice
            self.append_text(f"Вы прибыли в {self.player_location}", tag="system")
            self.update_status()
            self.check_npc_spawn()

    def get_available_locations(self):
        """Получение доступных локаций для перемещения"""
        connections = {
            "Зачарованный лес": ["Замок", "Болото"],
            "Замок": ["Зачарованный лес", "Хижина Гарольда"],
            "Болото": ["Зачарованный лес", "Храм"],
            "Хижина Гарольда": ["Замок"],
            "Храм": ["Болото"]
        }
        return connections.get(self.player_location, [])

    def show_location_dialog(self, locations):
        """Диалоговое окно выбора локации"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Выбор пути")
        dialog.geometry("300x200")
        dialog.configure(bg="black")
        
        tk.Label(dialog, text="Куда отправимся?", bg="black", fg="white").pack(pady=10)
        selected = tk.StringVar()
        
        for loc in locations:
            tk.Radiobutton(
                dialog,
                text=loc,
                variable=selected,
                value=loc,
                bg="black",
                fg="white",
                selectcolor="black"
            ).pack(anchor="w")
        
        def confirm():
            dialog.destroy()
            
        tk.Button(dialog, text="Подтвердить", command=confirm).pack(pady=10)
        self.root.wait_window(dialog)
        return selected.get()

    def check_npc_spawn(self):
        """Проверка появления NPC с шансом 80%"""
        if random.randint(1, 100) <= config.ENCOUNTER_CHANCE:
            npc_map = {
                "Замок": ["Гарольд с дробовиком", "Дракула"],
                "Болото": ["Лягушка Фроггит"],
                "Зачарованный лес": ["Лань", "Лесник"],
                "Хижина Гарольда": ["Гарольд с дробовиком"]
            }
            npc_list = npc_map.get(self.player_location, [])
            if npc_list:
                self.current_npc = random.choice(npc_list)
                self.append_text(f"Появился: {self.current_npc}", tag="event")

    def handle_dialogue(self):
        """Обработка диалогов с NPC"""
        if not self.current_npc:
            self.append_text("Здесь никого нет", tag="warning")
            return

        # РЕПЛИКА ПЕРСОНАЖА: Гарольд с дробовиком
        if "Гарольд" in self.current_npc:
            if self.has_shotgun:
                self.append_text("Гарольд: Верни мой дробовик!", tag="dialogue")
                return
                
            answer = messagebox.askyesno("Гарольд", "Одолжить дробовик? (3 патрона)")
            if answer:
                self.append_text("Гарольд: Держи, но верни вовремя!", tag="dialogue")
                self.inventory.append("дробовик")
                self.has_shotgun = True
                self.shotgun_ammo = 3
                self.promised_return = True

        # РЕПЛИКА ПЕРСОНАЖА: Лягушка Фроггит
        elif "Фроггит" in self.current_npc:
            correct = 0
            for question, answer in random.sample(config.QUESTIONS, 3):
                user_answer = simpledialog.askstring("Вопрос", f"{question}")
                if user_answer and user_answer.lower() == answer.lower():
                    correct += 1
            if correct == 3:
                self.append_text("Фроггит: Храм за болотом!", tag="dialogue")
                self.knows_temple = True
                self.status_data["Камни"] += 1
                self.append_text("Получен камень!", tag="item")
            else:
                self.append_text("Фроггит: Ты не достоин!", tag="warning")

        # РЕПЛИКА ПЕРСОНАЖА: Лань
        elif "Лань" in self.current_npc:
            if "Яблоко" in self.inventory:
                answer = messagebox.askyesno("Лань", "Накормить лань яблоком?")
                if answer:
                    self.inventory.remove("Яблоко")
                    self.status_data["Камни"] += 1
                    self.append_text("Лань дала вам камень!", tag="success")
            else:
                self.append_text("Лань хочет яблоко...", tag="dialogue")

        self.update_status()

    def show_inventory(self):
        """Отображение инвентаря"""
        items = "\n".join(self.inventory)
        if self.has_shotgun:
            items += f"\nДробовик (патроны: {self.shotgun_ammo})"
        messagebox.showinfo("Инвентарь", f"Содержимое:\n{items}")

    def show_merchant(self):
        """Окно торговца"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Торговец")
        dialog.geometry("300x400")
        dialog.configure(bg="black")
        
        tk.Label(dialog, text="Что желаете купить?", bg="black", fg="white").pack(pady=10)
        for item, price in config.TRADER_ITEMS.items():
            frame = tk.Frame(dialog, bg="black")
            frame.pack(fill=tk.X, padx=10, pady=2)
            tk.Label(frame, text=f"{item} - {price} камней", bg="black", fg="white").pack(side=tk.LEFT)
            btn = tk.Button(
                frame,
                text="Купить",
                command=lambda i=item, p=price: self.buy_item(i, p),
                bg="#333",
                fg="white"
            )
            btn.pack(side=tk.RIGHT)
        
    def buy_item(self, item, price):
        """Покупка предмета у торговца"""
        if self.status_data["Камни"] >= price:
            self.status_data["Камни"] -= price
            self.inventory.append(item)
            self.append_text(f"Куплено: {item}", tag="item")
            self.update_status()
        else:
            messagebox.showerror("Ошибка", "Недостаточно камней!")

    def update_status(self):
        """Обновление панели статуса"""
        status = f"Локация: {self.player_location} | " + " • ".join(
            f"{k}: {v}" for k, v in self.status_data.items()
        )
        self.status_var.set(status)

    def append_text(self, text, tag=None):
        """Добавление текста в лог"""
        self.text_box.config(state=tk.NORMAL)
        self.text_box.insert(tk.END, f"\n{text}\n", tag)
        self.text_box.see(tk.END)
        self.text_box.config(state=tk.DISABLED)
        self.log_content += f"{text}\n"

    def show_log(self):
        """Отображение окна лога"""
        log_win = tk.Toplevel(self.root)
        log_win.title("Лог событий")
        log_win.geometry("700x400")
        log_win.configure(bg="black")
        
        text = tk.Text(log_win, wrap=tk.WORD, bg="black", fg="white", font=("Consolas", 11))
        scroll = tk.Scrollbar(log_win, command=text.yview)
        text.config(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, self.log_content)
        text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = FantasyInterface(root)
    root.mainloop()