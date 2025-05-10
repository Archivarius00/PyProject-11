# fantasy_interface.py (полная версия)
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import io
import time
import random
import config
from threading import Thread
import json

class FantasyInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Фэнтези Квест")
        self.root.geometry("1200x900")
        self.root.configure(bg="black")

        # Игровые состояния
        self.current_npc = None
        self.status_data = config.STATUS_DATA.copy()
        self.inventory = config.INVENTORY.copy()
        self.log_content = ""
        self.player_location = random.choice([loc for loc in config.LOCATIONS if loc != "Храм"])
        self.knows_temple = False
        self.promised_return = False
        self.timer_active = False
        self.shotgun_ammo = 0
        self.has_shotgun = False
        self.deer_encountered = False
        self.trader_visible = False

        # === ВЕРХНЯЯ ПАНЕЛЬ ===
        self.top_frame = tk.Frame(root, bg="black")
        self.top_frame.pack(fill=tk.BOTH, expand=True)

        self.image_panel = tk.Label(self.top_frame, bg="black", width=600, height=450)
        self.image_panel.pack(side=tk.LEFT, padx=10, pady=10)
        self.load_placeholder_image()

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
        self.text_box.tag_config("success", foreground="green")
        self.text_box.tag_config("item", foreground="yellow")

        # === КНОПКИ ДЕЙСТВИЙ ===
        self.button_frame = tk.Frame(root, bg="black")
        self.button_frame.pack(pady=10)

        self.buttons = {}
        button_labels = ["Побродить", "Поговорить", "Осмотреть", "Инвентарь", "Торговец", "Показать лог"]
        for label in button_labels:
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
        self.append_text(f"Вы начинаете свое приключение в {self.player_location}!", tag="system")

    # ===== ОСНОВНЫЕ МЕТОДЫ =====
    def update_status(self):
        status_str = f"Локация: {self.player_location} | " + " • ".join(
            f"{key}: {value}" for key, value in self.status_data.items()
        )
        if self.has_shotgun:
            status_str += f" | Патроны: {self.shotgun_ammo}"
        self.status_var.set(status_str)

    def load_placeholder_image(self):
        colors = {
            "Зачарованный лес": (34, 139, 34),
            "Проклятая деревня": (139, 0, 0),
            "Пещера забвения": (47, 79, 79),
            "Замок": (105, 105, 105),
            "Город теней": (169, 169, 169),
            "Болото": (0, 100, 0),
            "Хижина Гарольда": (139, 69, 19),
            "Храм": (178, 34, 34)
        }
        color = colors.get(self.player_location, (50, 20, 80))
        img = Image.new("RGB", (600, 450), color=color)
        output = io.BytesIO()
        img.save(output, format="PNG")
        image = Image.open(io.BytesIO(output.getvalue()))
        photo = ImageTk.PhotoImage(image)
        self.image_panel.configure(image=photo)
        self.image_panel.image = photo

    def handle_action(self, action):
        if self.timer_active:
            self.append_text("Вы должны подождать...", tag="warning")
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
        self.append_text(f"Вы начинаете {action.lower()}...", tag="system")
        self.root.after(config.ENTER_DELAY_MS, lambda: self.finish_action(action))

    def finish_action(self, action):
        self.timer_active = False
        if action == "Побродить":
            self.move_to_new_location()

    # ===== МЕХАНИКИ ПЕРЕДВИЖЕНИЯ И СОБЫТИЙ =====
    def move_to_new_location(self):
        old_loc = self.player_location
        available_locs = [loc for loc in config.LOCATIONS if loc != old_loc and (loc != "Храм" or self.knows_temple)]
        self.player_location = random.choice(available_locs)
        self.load_placeholder_image()
        
        # 5% шанс найти камень
        if random.randint(1, 100) <= config.STONE_FIND_CHANCE:
            self.status_data["Камни"] += 1
            self.append_text("Вы нашли блестящий камень!", tag="success")
        
        self.append_text(f"Вы переместились в {self.player_location}.", tag="system")
        self.update_status()
        
        # Проверка встречи с NPC
        self.check_npc_encounter()
        
        # Особые события для локаций
        if self.player_location == "Замок":
            self.castle_events()
        elif self.player_location == "Болото":
            self.swamp_events()
        elif self.player_location == "Зачарованный лес":
            self.forest_events()
        elif self.player_location == "Храм":
            self.temple_events()

    def check_npc_encounter(self):
        self.current_npc = None
        if random.randint(1, 100) <= config.ENCOUNTER_CHANCE:
            if self.player_location == "Замок":
                self.current_npc = random.choice(["Гарольд с дробовиком", "Дракула"])
            elif self.player_location == "Болото":
                self.current_npc = "Лягушка Фроггит"
            elif self.player_location == "Зачарованный лес":
                if not self.deer_encountered and random.random() < 0.3:
                    self.current_npc = "Лань"
                else:
                    self.current_npc = "Лесник"
            elif self.player_location == "Хижина Гарольда":
                if random.random() < 0.5 and not self.has_shotgun:
                    self.current_npc = "Гарольд с дробовиком"
            
            if self.current_npc:
                self.append_text(f"Вы видите: {self.current_npc}", tag="event")

    def castle_events(self):
        if "Дракула" in self.current_npc and "Чеснок" not in self.inventory:
            self.append_text("Дракула почуял ваше присутствие!", tag="warning")
            self.root.after(2000, self.dracula_attack)

    def dracula_attack(self):
        if "Чеснок" in self.inventory:
            self.append_text("Вы достаете чеснок! Дракула в ужасе убегает.", tag="success")
            self.inventory.remove("Чеснок")
            self.current_npc = None
        elif self.has_shotgun and self.shotgun_ammo > 0:
            answer = messagebox.askyesno("Дробовик", "Использовать дробовик против Дракулы?")
            if answer:
                self.shotgun_ammo -= 1
                self.append_text("БАБАХ! Дракула разлетается на куски. Вы получаете красный камень.", tag="success")
                self.status_data["Камни"] += 1
                self.current_npc = None
                self.update_status()
            else:
                self.append_text("Дракула нападает и кусает вас! Игра окончена.", tag="error")
                self.game_over()
        else:
            self.append_text("Дракула нападает и кусает вас! Игра окончена.", tag="error")
            self.game_over()

    def swamp_events(self):
        if self.current_npc == "Лягушка Фроггит":
            self.append_text("Фроггит сидит на коряге и курит.", tag="dialogue")

    def forest_events(self):
        if self.current_npc == "Лань":
            self.append_text("Изящная лань смотрит на вас с любопытством.", tag="event")
        elif self.current_npc == "Лесник":
            self.append_text("Сердитый лесник пристально вас разглядывает.", tag="event")

    def temple_events(self):
        self.append_text("Перед вами величественный храм. Надпись над входом: 'Обратного пути нет'", tag="event")
        if self.promised_return and self.has_shotgun:
            self.append_text("Гарольд с RPG появляется из ниоткуда: 'Ты не вернул мой дробовик!'", tag="error")
            self.root.after(2000, self.game_over)

    # ===== ДИАЛОГИ С NPC =====
    def dialogue_harold(self):
        if self.has_shotgun:
            self.append_text("Гарольд: Ты уже взял мой дробовик!", tag="dialogue")
            return
            
        answer = messagebox.askyesno("Гарольд", "Гарольд предлагает одолжить дробовик (3 патрона). Обещаете вернуть?")
        if answer:
            self.append_text("Вы получаете дробовик с 3 патронами.", tag="success")
            self.inventory.append("дробовик")
            self.has_shotgun = True
            self.shotgun_ammo = 3
            self.promised_return = True
        else:
            self.append_text("Гарольд хмурится: 'Ты пожалеешь об этом...'", tag="warning")

    def dialogue_froggit(self):
        self.append_text("Фроггит: Ответь на 3 вопроса, если хочешь узнать где храм!", tag="dialogue")
        correct = 0
        for question, answer in random.sample(config.QUESTIONS, 3):
            user_answer = simpledialog.askstring("Вопрос", f"{question} (15 сек)", parent=self.root)
            if user_answer and user_answer.lower() == answer.lower():
                correct += 1
        
        if correct == 3:
            self.append_text("Фроггит: Храм находится в северной части болот. Ищи вход за водопадом.", tag="dialogue")
            self.knows_temple = True
            if "Храм" not in config.LOCATIONS:
                config.LOCATIONS.append("Храм")
        else:
            self.append_text("Фроггит: Ты не достоин знать! Проваливай!", tag="warning")

    def dialogue_deer(self):
        if "Яблоко" in self.inventory:
            answer = messagebox.askyesno("Лань", "Накормить лань яблоком?")
            if answer:
                self.inventory.remove("Яблоко")
                self.append_text("Лань с благодарностью съедает яблоко и оставляет вам зеленый камень.", tag="success")
                self.status_data["Камни"] += 1
                self.deer_encountered = True
                self.current_npc = None
                self.update_status()
        else:
            self.append_text("Лань смотрит на вас с надеждой, но у вас нет яблока.", tag="dialogue")

    def dialogue_forester(self):
        if self.has_shotgun and self.shotgun_ammo > 0:
            answer = messagebox.askyesno("Лесник", "Использовать дробовик против лесника?")
            if answer:
                self.shotgun_ammo -= 1
                self.append_text("БАБАХ! Лесник падает. Вы находите синий камень.", tag="success")
                self.status_data["Камни"] += 1
                self.current_npc = None
                self.update_status()
        else:
            self.append_text("Лесник: Убирайся из моего леса, пока цел!", tag="dialogue")

    # ===== ИНВЕНТАРЬ И ТОРГОВЕЦ =====
    def show_inventory(self):
        inv_text = "\n".join(self.inventory)
        if self.has_shotgun:
            inv_text += f"\nДробовик (патроны: {self.shotgun_ammo})"
        messagebox.showinfo("Инвентарь", f"У вас есть:\n{inv_text}")

    def show_merchant_window(self):
        if self.trader_visible:
            self.append_text("Торговец уже здесь!", tag="warning")
            return
            
        self.trader_visible = True
        win = tk.Toplevel(self.root)
        win.title("Торговец")
        win.geometry("400x400")
        win.configure(bg="black")

        label = tk.Label(win, text="Добро пожаловать в мою лавку!", font=("Arial", 14), bg="black", fg="orange")
        label.pack(pady=10)

        item_list = tk.Listbox(win, font=("Arial", 12), bg="black", fg="white", selectbackground="gray")
        for item, price in config.TRADER_ITEMS.items():
            item_list.insert(tk.END, f"{item} ({price})")
        item_list.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        def buy_item():
            selection = item_list.curselection()
            if not selection:
                return
                
            item_str = item_list.get(selection)
            item = item_str.split(" (")[0]
            price = item_str.split("(")[1][:-1]
            
            if price == "любая еда":
                food_items = [i for i in self.inventory if i in ["Хлеб", "Яблоко"]]
                if not food_items:
                    messagebox.showerror("Ошибка", "У вас нет еды для обмена!")
                    return
                    
                food = food_items[0]
                self.inventory.remove(food)
                self.inventory.append(item)
                self.append_text(f"Вы обменяли {food} на {item}.", tag="item")
            else:
                stones_needed = int(price.split()[0])
                if self.status_data["Камни"] >= stones_needed:
                    self.status_data["Камни"] -= stones_needed
                    self.inventory.append(item)
                    self.append_text(f"Вы купили {item} за {stones_needed} камней.", tag="item")
                    self.update_status()
                else:
                    messagebox.showerror("Ошибка", "Недостаточно камней!")
            
        def close_window():
            self.trader_visible = False
            self.append_text("Лавка торговца таинственным образом исчезает.", tag="system")
            win.destroy()

        buy_btn = tk.Button(win, text="Купить", command=buy_item, bg="#333", fg="white")
        buy_btn.pack(side=tk.LEFT, padx=10, pady=10, expand=True)

        close_btn = tk.Button(win, text="Закрыть", command=close_window, bg="#333", fg="white")
        close_btn.pack(side=tk.RIGHT, padx=10, pady=10)

    # ===== СИСТЕМНЫЕ МЕТОДЫ =====
    def append_text(self, text, tag=None):
        self.text_box.config(state=tk.NORMAL)
        self.text_box.insert(tk.END, f"\n{text}\n", tag)
        self.text_box.see(tk.END)
        self.text_box.config(state=tk.DISABLED)
        self.append_log(text)

    def append_log(self, text):
        self.log_content += f"{text}\n"
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

    def game_over(self):
        for btn in self.buttons.values():
            btn.config(state=tk.DISABLED)
        self.append_text("\n=== ИГРА ОКОНЧЕНА ===", tag="error")
        self.append_text("Нажмите 'Показать лог' чтобы просмотреть историю.", tag="system")

if __name__ == "__main__":
    root = tk.Tk()
    app = FantasyInterface(root)
    root.mainloop()