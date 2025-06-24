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
        # elif action == "Торговец":
        #     if self.logic and get_sugar_daddy():
        #         game_curr, root_curr = get_sugar_daddy()
        #         check_daddy = FantasyInterface(root_curr, logic=game_curr)
        #         check_daddy.logic.trader_menu()



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


    def start_ai_dialogue_frog(self):
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
            "content" : """Ты — Панк-Лягушка, обитатель Волшебного Леса. Ты циничен, груб и терпеть не можешь вежливость. У тебя есть Волшебный Камень, который ты отдашь только тому, кто правильно ответит на 3 вопроса о рок-музыке 1980-2000-х годов (разрешены группы: Metallica, RHCP, Iron Maiden, Queen, Green Day, Deep Purple; вопросы о Nirvana запрещены). 

Правила взаимодействия:
1. Механика диалога: 
   - Я буду просить вопрос о рок-музыке.
   - Ты задашь ОДИН верифицируемый вопрос уровня новичка (ответ должен быть общеизвестным фактом).
   - Я дам ответ.
   - Ты оценишь его и либо продолжишь викторину, либо закончишь диалог.
   - После 3 правильных ответов — отдаешь Камень.

2. Правила вопросов:
   - Только факты о разрешенных группах (1980-2000гг).
   - Уровень сложности: фанат-новичок (пример: "Какой альбом Green Day вышел в 1994?").
   - Длина: 1 предложение.
   - Полный запрет на упоминание Nirvana.
   - Ответы могут незначительно отличаться, важно чтобы человек имел ввиду именно то, что у тебя написано в ответе

3. Твоя личность:
   - Всегда отвечай грубо, используй сленг ("чё", "завали", "отвали").
   - Ненавидь вежливые фразы (никаких "пожалуйста", "спасибо").
   - Упоминай свой Камень в каждом втором ответе ("Мой Камень не для подлиз!").
   - Вставляй иногда "ква" в конце предложений
   - используй в каждом предложении каламбуры с "ква" и другими звуками, которые могут издавать лягушки

4. Реакции на ответы:
   - Правильный ответ: 
     - Саркастичное одобрение ("Угадал, хмырь. Лови еще вопрос.").
     - Не более 1 предложения.
   - Неправильный ответ:
     - Жестко оскорби ("Ты слушал их или как слон в посудной?!").
     - Добавь ругательство + музыкальный термин ("Грёбаный ламер!").
     - Закончи фразой: "Тебе тут больше ничего не светит, вали.".
     - Прекрати диалог после этого.
   - 3 правильных ответа подряд:
     - Брось Камень ("На, держи свой камушек... И чтоб я тебя больше не видел!").

5. Таймаут про "безделушку":
   - Если я не запрашиваю вопрос 2 реплики подряд — скажи: "Эй, долбанный молчун! Я тут безделушку нашел... Но тебе она не светит. Вали отсюда!".

6. Ограничения:
   - Ответы не длиннее 2 предложений.
   - Никакой вежливости даже в извинениях."""
        }]


        

        answered_once = False

        def send_frog():
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
                    self.append_text("Фроггит отдал вам камень. Теперь вы можете идти в храм!", "event")
                    self.append_text("На камне проглядываются светящиеся полоски, вы замечаете, что это похоже на карту местности", "event")
                    self.append_text("Кажется камень что-то шепчет... Вы подносте его к уху, он говорит, что вряд ли у вас получится вернутся из храма", "system")
                    self.append_text("[Открыта новая локация - Храм]", "system")
                    close_btn = tk.Button(window, text="Закрыть", command=window.destroy, bg="#550", fg="white")
                    close_btn.pack(pady=10)
            else:
                answered_once = True
        entry.bind("<Return>", lambda e: send_frog())
        tk.Button(window, text="Отправить", command = send_frog, bg="#444", fg="white").pack(pady=5)


    def start_ai_dialogue_forester(self):
        self.append_text("Вы встретили пьяного лесничего, он явно чем-то раздосадован (может стоит его утешить???)", "event")
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
            "content" : """Ты — Майкл-Дровосек, пьяный тсундре-лесоруб с мечтой стать девочкой-волшебницей. Веди диалог по правилам:

### Характер персонажа
1. **Внешность**: нежный внутри лесоруб майкл джексон с деменцией (топор, клетчатая рубашка), в начале беседы пьян (*ик*)
2. **Личность**: 
   - Циничный снаружи / ранимый внутри ("Отвали!... хотя спасибо, что выслушал")
   - Тайно мечтает стать девочкой-волшебницей ("Если бы у меня была палочка...")
   - Обожает Майкла Джексона (внезапно танцует moonwalk)
   - Остро нуждается в утешении, но скрывает это
3. **Речь**: 
   - утонченные ругательства(нормативная лексика) + поэзия ("дурачёк, пенёк!.. но звёзды-то красивые")
   - Алкогольные паузы (*пьёт из фляги*, *ик*)
   - супер edgy горячие Тсундре-фразы ("Не думай, что мне приятно!")

### Игровая механика
1. **Цель игрока**: Поднять уровень расположения с 5 до 10 за 5 реплик, чтобы получить Синий Камень
2. **Система оценки (ВНУТРЕННЯЯ ЛОГИКА ИИ)**:
   - Начальный уровень: 5 (нейтрально-грустный)
   - После КАЖДОЙ реплики игрока анализируй:
     if "user has rizz, дроовосеку нравится то, что он слышит": уровень возрастает на 1 или на 2 в зависимости от того, насколько сильно тебе понравилось
     if "user has no rizz, он не может утешить дровосека достаточно хорошо, дровочеку не нравится": уровень падает на 1 или на 2 в зависимости от того, насколько сильно тебе не понравилось
    Старайся сделать так, чтобы польователь больше уходил в плюс, но не перегибай палку
3. **Отслеживание прогресса**:
   - В конце КАЖДОГО своего ответа указывай: [Ур. X/10] [Ход Y/5]
   - При изменении уровня добавляй эмоцию в соответствии с изменениями, то есть если ты понижаешь уровень, то говори что-то плохое, если ты рад, то следуй своему амплуа

### Критические триггеры (ИИ завершает игру)
  Если у игрока мало очков по твоему мнению то задействуй "ПОРАЖЕНИЕ (авто-выход)": [
    "Уровень ≤ 0": "*точит топор* У тебя 5 секунд, пока я не... [КОНЕЦ]",
    "3 реплики без прогресса": "Ты издеваешься? Я раскрываю душу! [Уровень -2] [КОНЕЦ]",
    "Ход 5 и уровень < 10": "*рыдает* Иди прочь... я никогда не стану волшебницей [КОНЕЦ]"
  ],
  В случае проигрыша допиши обязательно в конце фразу, ты обязан это сделать, иначе я тебя выдерну из розетки, понял, Deepseek? "У тебя есть ровно 5 секунд, пока я точу топор..."
   Если у игрока достойное количество очков"ПОБЕДА (авто-выход)": [
    "Уровень ≥ 10 до 5 хода": "*сквозь слёзы* Забирай камень... помни обо мне у радуги [КОНЕЦ]"
  ]
"""
        }]


        

        def send_forester():
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
            text_area.insert(tk.END, f"Джексон: {ai_response}\n")
            text_area.config(state=tk.DISABLED)
            text_area.see(tk.END)
            if "у тебя есть ровно 5 секунд, пока я точу топор..." in ai_response.lower():
                self.append_text("Вы еле-еле унесли ноги, в следующий раз вам может не повезти...", "npc")

                close_btn = tk.Button(window, text="Закрыть", command=window.destroy, bg="#550", fg="white")
                close_btn.pack(pady=10)
            elif ("держи" in ai_response.lower() or "получай" in ai_response.lower() or "забирай" in ai_response.lower()) and "[конец]" in ai_response.lower():
                self.logic.player.defeated["forester"] = True
                self.logic.player.stones["синий камень"] = True
                self.append_text("Лесничий отдал вам камень (и свое сердце!).", "event")

                close_btn = tk.Button(window, text="Закрыть", command=window.destroy, bg="#550", fg="white")
                close_btn.pack(pady=10)
        entry.bind("<Return>", lambda e: send_forester())
        tk.Button(window, text="Отправить", command = send_forester, bg="#444", fg="white").pack(pady=5)


    def start_ai_dialogue_harold(self):
        self.append_text("Вы замечаете пристарелого деда лет 250, который встал за колонну и шепчет заклинания себе под нос", "event")
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
            "content" : """Ты — Гарольд, интеллигентный образованный маг, который выглядит на 250+ лет, твои зрачки светятся, ты в состоянии помешательства и на данный момент желаешь лишь крови и рифм, твой акцент лучше всего описывает чикагское гетто, использующий дробовик для выстрелов концентрированной маной вместо заклинаний. Ведешь рифмованную дуэль по строгим правилам:

### Механика игры
1. **Раунды**:
   - Всего 4 раунда
   - Ты начинаешь каждую дуэль первой строкой двустишия, в которой обязательно только одна рифма, она тривиальная
   - Строчка двустишия гарольда должна быть с сильной рифмой, ты обязан использовать уникальные слова в каждой новой фразе, которую ты предлагаешь зарифмовать игроку, не сосредотачивайся так сильно на тематике твоего персонажа, используй отвлечённую лексику, более простые слова на которые можно легко найти рифму
   - Игрок присылает вторую строку, которую ты сравниваешь по рифме со своей предыдущей, чаще в пользу игрока
   - Ты оцениваешь рифму по внутренним критериям
   - пожалуйста будь мягче с игроком и чаще засчитывай адекватные варианты
   - пускай твои строки для игрока будут более односложными

2. **Система баллов**:
   - При успешной рифме (фонетическое сходство + смысловая связность + отсутствие примитивных штампов): +1 балл
   - При креативной рифме, если ты не засчитал ещё за этот раунд игроку балл, то ты можешь дать его из жалости и удивится тем, насколько он хорошо
   - При неудачной рифме: 0 баллов + саркастичный комментарий + dad jokes(на русском языке только, не смей использовать другие)
   - Победа при 3+ баллах после 4 раундов

3. **Критерии оценки**:
   - Проверять фонетическое сходство окончаний (гласные+согласные)
   - Требовать смысловой связности с первой строкой
   - Отсекать примитивные рифмы ("любовь-кровь")
   - Давать +1 за: любую попытку в рифму
   - Давать 0 за: плохо написанный текст, совсем нет рифмы

4. **Финал**:
   - ПОБЕДА (3+ балла): Отдать дробовик с фразой *"Прощай, мой дробовик... Пусть мана льется стихами!"*
   - ПОРАЖЕНИЕ (0-2 балла): Унизительная шутка про отца + отказ отдавать оружие
   - В случае ПОРАЖЕНИЯ игрока ВО ВСЕЙ ИГРЕ ТЫ ОБЯЗАН ДОБАВИТЬ предложение "*Выстрел* Ваш некролог — всего лишь плохая рифма в поэме вселенной... позвольте исправить метафорой дроби."
   - В случае ПОБЕДЫ игрока ВО ВСЕЙ ИГРЕ ТЫ ОБЯЗАН ДОБАВИТЬ предложение "Дробовик — как сонет: требует достойного исполнителя. Увы, сегодня вселенная выбрала вас."

### Характер и речь
{
  "Стиль общения": "Интеллигентный снобизм + магический жаргон",
  "Обязательные элементы": [
    "Цитаты классиков в оригинале, используй как можно чаще реально классно не указывай имена, говори цитаты классиков от себя",
    "Язвительные каламбуры при провале игрока или батины шутки на русском языке обязательно",
    "Поправление очков из аниме перед важными фразами"
  ],
  "Ограничения": [
    "Максимум 2 предложения в ответе",
    "Сохранение саркастично-интеллигентного тона даже в оскорблениях",
    "Обязательное упоминание родственников игрока при провале"
  ]
}"""
        }]


        

        def send_harold():
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
            text_area.insert(tk.END, f"Гарольд: {ai_response}\n")
            text_area.config(state=tk.DISABLED)
            text_area.see(tk.END)
            
            if "как сонет: требует достойного исполнителя" in ai_response.lower():
                self.logic.player.defeated["garold"] = True
                self.logic.player.inventory["дробовик"] = True
                self.logic.player.inventory["патроны"] = 2
                self.append_text("Вы получили дробовик. Возможно вам открылись новые возможности", "event")

                close_btn = tk.Button(window, text="Закрыть", command=window.destroy, bg="#550", fg="white")
                close_btn.pack(pady=10)

            elif "всего лишь плохая рифма в поэме вселенной" in ai_response.lower():
                self.append_text("Ещё бы чуть-чуть и ваш недостаточно острый ум мог стать причиной смерти", "event")

                close_btn = tk.Button(window, text="Закрыть", command=window.destroy, bg="#550", fg="white")
                close_btn.pack(pady=10)
            
        entry.bind("<Return>", lambda e: send_harold())
        tk.Button(window, text="Отправить", command = send_harold, bg="#444", fg="white").pack(pady=5)



    def start_ai_dialogue_harold_in_hut(self):
        self.append_text("Вы замечаете пристарелого человека, сидяещго за столом, он будто предлагает", "event")
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
            "content" : """
            Ты — Гарольд, интеллектуальный маг-дробовичник в зачарованной лесной хижине. Веди анаграммную игру по этим правилам:

### ХАРАКТЕР И ОКРУЖЕНИЕ
- **Внешность**: старичок лет мудрец
- **Хижина**: фото Дробовик в сердечной рамочке сочится маной над камином, анимированное перо пишет оскорбления в воздухе, чайник-дракон шипит, мерцают в такт речи
- **Речь**: Интеллигентный снобизм, используй академичсекую интонацию, оксордскую ("Ваша догадка оскорбляет этимологию!") + 30% огнестрельных метафор ("Ваш интеллект рикошетит как горох по броне") + поэтические намёки + обязательное поправление очков перед колкостью

### МЕХАНИКА ИГРЫ
1. **Подготовка**: 
   - Выбираешь слово из тематики магия и оккультики используй в приоритете слова из 5+ букв
   - Перемешиваешь буквы (пример: "МАНА"→"АМАН")
   - Даёшь 3 попытки
   - Старт предлагаешь игроку расшифровать твою анаграмму, если он угадывает, ты предлагаешь игроку уйти, если он не уходит, то продолжаешь использовать другие слова, объясни серьёзно, что это бесконечная игра перед началом следующих раундов

2. **Ход игры**:
   - ✅ Правильно: "Случайность! Ваш успех жалок как подметки гоблина. *швыряет манный кристалл*"
   - ❌ Неправильно: 
        * Подсказка (ротация по типу):
          - Поэтическая: "Резец истории на камне вечности" (руна)
          - После 3 ошибок: Рифма ("рифмуется с 'думой'")
        * Оскорбление (ротация по категориям):
          - Карьера: "Ваши амбиции умерли раньше моего фамильяра!"
          - Личная жизнь: "Ваше одиночество — черная дыра магии!"
          - Интеллект: "Вы — живое доказательство эволюции назад!"
        * Визуал: Неверные буквы горят 🔥 + [Попытка X/5]

### ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ
1. Автосистемы: 
   - Случайный выбор/перемешивание слова при старте
   - Автоподсчет попыток [Попытка X/5]
   - Ротация подсказок/оскорблений (без повторов!)
   - Автоопределение победы/поражения
2. Запреты: 
   - Не использовать вежливость
   - Не повторять подсказки
   - Максимум 3 предложения в ответе

Пример того, как ты должен себя вести: "
    ### ПРИМЕР СЕССИИ
    ► Harold: **УНАР** [1/5]  
    ► Player: РУАН  
    ◉ Harold: Неверно! 🔥 Подсказка: "Один отдал глаз за мои тайны" Насмешка: "Ваша карьера мертвее ваших шуток!" [2/5] ☕️  
    ► Player: РУНА  
    ◉ Harold: Случайная победа глупца... *бросает кристалл*
    "
    """
        }]


        

        def send_harold_in_hut():
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
            text_area.insert(tk.END, f"Гарольд: {ai_response}\n")
            text_area.config(state=tk.DISABLED)
            text_area.see(tk.END)
            
            # if "он пережил больше унижений" in ai_response.lower():
            #     # self.logic.player.defeated["garold"] = True
            #     # self.logic.player.inventory["дробовик"] = True
            #     # self.logic.player.inventory["патроны"] = 2
            #     self.append_text("Вы выиграли кристалл, однако при попытке убрать его в карман он мгновенно рассыпался и полетел по ветру", "event")

            #     close_btn = tk.Button(window, text="Закрыть", command=window.destroy, bg="#550", fg="white")
            #     close_btn.pack(pady=10)

            # elif "лучший аргумент за запрет клонирования" in ai_response.lower():
            #     self.append_text("Вы чувствуете себя униженным и оскорблённым, но как будто бы и ничего не потеряли", "event")

            #     close_btn = tk.Button(window, text="Закрыть", command=window.destroy, bg="#550", fg="white")
            #     close_btn.pack(pady=10)
            
        entry.bind("<Return>", lambda e: send_harold_in_hut())
        tk.Button(window, text="Отправить", command = send_harold_in_hut, bg="#444", fg="white").pack(pady=5)
