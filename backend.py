from config import *
import time
import random

class Player:
    def __init__(self):
        self.inventory = {"камешки": 0, "дробовик": 0, "патроны": 0, "чеснок": 0, "яблоко": 0}
        self.stones = {"зеленый камень": False, "красный камень": False, "синий камень": False, "камень - путеводитель": False}
        self.has_shotgun = False
        self.debt_to_harold = False
        self.defeated = {"dracula": False, "deer": False, "forester": False, "frog": False}

    def has_all_stones(self):
        return all(self.stones.values())

class Game:
    def __init__(self):
        self.player = Player()
        self.interface = None
        self.current_location = "лес"
        self.temple_unlocked = False
        self.hut_visited = False
        self.frog_quiz_passed = False

    def walk(self):
        self.interface.append_text("\nВы начинаете бродить...", "event")
        time.sleep(WALK_COOLDOWN)
        event = random.choices(["встреча", "камень", "ничего"], weights=weights)[0]
        if event == "камень":
            self.player.inventory["камешки"] += 1
            self.interface.append_text("Найден камешек!", "item")
        elif event == "ничего":
            self.interface.append_text("Ничего интересного не произошло", "default")
        else:
            self.random_encounter()

    def random_encounter(self):
        if self.current_location == "замок":
            if not self.player.has_shotgun:
                self.meet_harold()
            elif not self.player.defeated["dracula"]:
                self.meet_dracula()
            else:
                self.interface.append_text("Замок пустой...", "location")

        elif self.current_location == "болото":
            if not self.player.defeated["frog"]:
                self.meet_frog()
            elif not self.frog_quiz_passed:
                self.meet_frog_again()
            else:
                self.interface.append_text("Фроггит: 'Я всё уже сказал, вали!'", "npc")

        elif self.current_location == "лес":
            if not self.player.defeated["forester"]:
                self.meet_forester()
            elif not self.player.defeated["deer"]:
                self.meet_deer()
            else:
                self.interface.append_text("Лес тих и пуст...", "location")

    def change_location(self, new_location):
        if new_location not in LOCATIONS:
            self.interface.append_text("Такой локации не существует!", "warning")
            return

        if new_location == "храм" and not self.temple_unlocked:
            self.interface.append_text("Вы не знаете, где храм!", "warning")
            return

        self.current_location = new_location
        self.interface.append_text(f"\n=== {LOCATIONS[new_location]} ===", "location")
        time.sleep(0.3)

        if new_location == "хижина":
            self.meet_harold_in_hut()
        elif new_location == "храм":
            self.temple_ending()

    def meet_harold(self):
        self.interface.append_text("Гарольд: 'Хочешь дробовик? Вернёшь — живым будешь.'", "npc")
        choice = self.interface.show_choice_dialog("Взять дробовик?", ["1. Взять", "2. Отказаться"])
        if choice == "1":
            self.player.has_shotgun = True
            self.player.inventory["дробовик"] = 1
            self.player.inventory["патроны"] = 2
            self.player.debt_to_harold = True
            self.interface.append_text("Гарольд дал вам дробовик.", "item")
        else:
            self.interface.append_text("Гарольд: 'Тогда вали отсюда.'", "npc")

    def meet_dracula(self):
        choice = self.interface.show_choice_dialog("Вы встретили Дракулу!", ["1. Отдать чеснок", "2. Стрелять"])
        if choice == "1" and self.player.inventory["чеснок"] > 0:
            self.player.inventory["чеснок"] -= 1
            self.player.stones["синий камень"] = True
            self.player.defeated["dracula"] = True
            self.interface.append_text("Дракула исчезает от чеснока!", "event")
        elif choice == "2" and self.player.inventory["патроны"] > 0:
            self.player.inventory["патроны"] -= 1
            self.player.stones["синий камень"] = True
            self.player.defeated["dracula"] = True
            self.interface.append_text("Вы застрелили Дракулу!", "combat")
        else:
            self.interface.append_text("Дракула съел вас. Игра окончена.", "combat")
            self.interface.end_game("Дракула съел вас. Конец игры.", "combat")

    def meet_frog(self):
        self.interface.enable_frog_dialogue()
        correct = 0
        # for _ in range(3):
        #     q = random.choice(QUESTIONS_POOL)
        #     answer = self.interface.show_text_input(f"{q['вопрос']} (время не ограничено)")
        #     if answer and answer.lower() == q['ответ'].lower():
        #         correct += 1
        if correct >= 2:
            self.temple_unlocked = True
            self.frog_quiz_passed = True
            self.player.defeated["frog"] = True
            self.player.stones["камень - путеводитель"] = True
            self.interface.append_text("Фроггит: 'Ладно, иди в храм.'", "npc")
        else:
            self.interface.append_text("Фроггит: 'Тупица! Вали отсюда!'", "npc")

    def meet_frog_again(self):
        choice = self.interface.show_choice_dialog("Фроггит снова перед вами", ["1. Стрелять", "2. Уйти"])
        if choice == "1" and self.player.inventory["дробовик"] and self.player.inventory["патроны"]:
            self.player.inventory["патроны"] -= 1
            self.temple_unlocked = True
            self.player.defeated["frog"] = True
            self.player.stones["камень - путеводитель"] = True
            self.interface.append_text("Вы убили Фроггита и нашли камень.", "combat")
        else:
            self.interface.append_text("Вы ушли ни с чем.", "default")

    def meet_deer(self):
        choice = self.interface.show_choice_dialog("Вы встретили лань.", ["1. Дать яблоко", "2. Уйти"])
        if choice == "1" and self.player.inventory["яблоко"]:
            self.player.inventory["яблоко"] -= 1
            self.player.stones["зеленый камень"] = True
            self.player.defeated["deer"] = True
            self.interface.append_text("Лань ест яблоко и оставляет камень.", "event")
        else:
            self.interface.append_text("Нужен яблоко!", "warning")

    def meet_forester(self):
        choice = self.interface.show_choice_dialog("Лесник: 'Убирайся!'", ["1. Грубо ответить", "2. Уйти", "3. Стрелять"])
        if choice == "1" or (choice == "3" and self.player.inventory["патроны"] > 0):
            if choice == "3":
                self.player.inventory["патроны"] -= 1
            self.player.stones["красный камень"] = True
            self.player.defeated["forester"] = True
            self.interface.append_text("Вы получили красный камень.", "item")
        else:
            self.interface.append_text("Лесник уходит...", "npc")

    def meet_harold_in_hut(self):
        choice = self.interface.show_choice_dialog("Гарольд: 'Что нужно?'", ["1. Вернуть дробовик", "2. Просто навестить"])
        if choice == "1" and self.player.inventory["дробовик"]:
            self.player.inventory["дробовик"] = 0
            self.player.has_shotgun = False
            self.player.debt_to_harold = False
            self.interface.append_text("Вы вернули дробовик Гарольду.", "event")
        else:
            self.interface.append_text("Гарольд: 'Ладно. Заходи ещё.'", "npc")

    def trader_menu(self):
        options = [f"{item} — {TRADER_ITEMS[item]['цена']} камешков" for item in TRADER_ITEMS]
        choice = self.interface.show_choice_dialog("Торговец: Что хочешь?", options + ["выход"])
        for item in TRADER_ITEMS:
            if choice and item in choice:
                cost = TRADER_ITEMS[item]["цена"]
                if self.player.inventory["камешки"] >= cost:
                    self.player.inventory["камешки"] -= cost
                    self.player.inventory[item] += 1
                    self.interface.append_text(f"Куплено: {item}", "item")
                else:
                    self.interface.append_text("Не хватает камешков!", "warning")

    def temple_ending(self):
        all_stones = self.player.has_all_stones()
        debt_paid = not self.player.debt_to_harold
        if all_stones and debt_paid:
            self.interface.append_text("Вы вставили все камни. Храм озарён светом. Вы победили!", "event")
            self.interface.end_game("Вы победили! Игра завершена.", "event")
        elif all_stones and not debt_paid:
            self.interface.append_text("Гарольд с РПГ: 'Ты не вернул дробовик!' БАБАХ.", "combat")
            self.interface.end_game("Гарольд убил вас. Конец игры.", "combat")
        elif not all_stones and debt_paid:
            missing = [k for k, v in self.player.stones.items() if not v]
            self.interface.append_text(f"Не хватает камней: {', '.join(missing)}", "warning")
        else:
            self.interface.append_text("Ты не вернул дробовик И не нашёл камни. Гарольд мстит. Конец.", "combat")
            self.interface.end_game("Вы проиграли. Всё пошло не так.", "combat")
