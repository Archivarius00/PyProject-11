from config import *
import time
import random
from interface import *
from Daddy import *

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

    def start(self): # надо активировать это где-то в начале
        self.interface.append_text("Вы просыпаетесь в каком-то лесу. Встав на ноги вы видите мужчину полностью завернутого в плащ с большим капюшоном, его лица не видно.", "system")
        self.interface.append_text("Он стоит возле стола на котором лежит довольно странный набор предметов. Вы решаете подойти", "system")
        self.interface.append_text("Мужчина: Хей, очередной путник пожаловал, говорю прямо: я торговец, могу продать разный полезный хлам, и, хех, я всегда рядом", "npc")
        self.interface.append_text("Вы с подозрением смотрите на торговца и отвечаете ему что-то невнятное", "system")
        self.interface.append_text("Вы уходите в чащу леса, ища выход. Видимо вы исекайнулись", "system")

    def walk(self):
        self.interface.append_text("\nВы решили побродить по округе...", "event")
        time.sleep(WALK_COOLDOWN)
        event = random.choices(["встреча", "камень", "ничего"], weights = [.50, .40, .10])[0]
        if event == "камень":
            self.player.inventory["камешки"] += 1
            self.interface.append_text("Вы нашли камешек", "item")
        elif event == "ничего":
            self.interface.append_text("Ничего интересного не произошло", "default")
        else:
            self.random_encounter()
        self.interface.update_status_display()

    def random_encounter(self):
        if self.current_location == "замок":
            if not self.player.has_shotgun and FLAG_HAROLD == 0 and 0.5 > ( random.random() ):
                self.meet_harold()
            elif FLAG_DRACULA == 0:
                self.meet_dracula()
            elif not self.player.has_shotgun and FLAG_HAROLD == 0:
                self.meet_harold()
            else:
                self.interface.append_text("Похоже замок пуст...", "location")

        elif self.current_location == "болото":
            if FLAG_FROG == 0:
                self.meet_frog()
            elif FLAG_FROG == 1:
                self.meet_frog_again()
            else:
                self.interface.append_text("Похоже все фроггиты разбежались, больше никого нет", "system")

        elif self.current_location == "лес":
            if FLAG_FORESTER == 0:
                self.meet_forester()
            elif FLAG_DEER == 0:
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
        self.interface.update_status_display()

    def meet_harold(self):
        global FLAG_HAROLD
        FLAG_HAROLD = 1
        self.interface.append_text("Гарольд: 'Хочешь дробовик? Вернёшь — живым будешь.'", "npc")
        choice = self.interface.show_choice_dialog("Взять дробовик?", ["1. Взять", "2. Отказаться"])
        if choice == "1. Взять":
            self.player.has_shotgun = True
            self.player.inventory["дробовик"] = 1
            self.player.inventory["патроны"] = 2
            self.player.debt_to_harold = True
            self.interface.append_text("Гарольд дал вам дробовик.", "item")
        else:
            self.interface.append_text("Гарольд: 'Тогда вали отсюда.'", "npc")
        self.interface.update_status_display()

    def meet_dracula(self):
        global FLAG_DRACULA
        FLAG_DRACULA = 1
        choice = self.interface.show_choice_dialog("Вы встретили Дракулу!", ["1. Отдать чеснок", "2. Стрелять"])
        if choice == "1. Отдать чеснок" and self.player.inventory["чеснок"] > 0:
            self.player.inventory["чеснок"] -= 1
            self.player.stones["синий камень"] = True
            self.player.defeated["dracula"] = True
            self.interface.append_text("Дракула исчезает от чеснока!", "event")
        elif choice == "2. Стрелять" and self.player.inventory["патроны"] > 0:
            self.player.inventory["патроны"] -= 1
            self.player.stones["синий камень"] = True
            self.player.defeated["dracula"] = True
            self.interface.append_text("Вы застрелили Дракулу!", "combat")
        else:
            self.interface.append_text("Дракула съел вас. Игра окончена.", "combat")
            self.interface.end_game("Дракула съел вас. Конец игры.", "combat")
        self.interface.update_status_display()

    def meet_frog(self):
        global FLAG_FROG
        FLAG_FROG = 1
        self.interface.start_ai_dialogue()

    def meet_frog_again(self):
        global FLAG_FROG
        global FLAG_TEMPLE
        choice = self.interface.show_choice_dialog("Фроггит снова перед вами", ["1. Стрелять", "2. Уйти"])
        if choice == "1. Стрелять" and self.player.inventory["дробовик"] and self.player.inventory["патроны"]:
            self.player.inventory["патроны"] -= 1
            self.temple_unlocked = True
            self.player.defeated["frog"] = True
            self.player.stones["камень - путеводитель"] = True
            self.interface.append_text("Вы убили Фроггита и нашли камень.", "system")
            self.interface.append_text("Кажется на камне проглядывается карта. Она показывает где можно пройти в... Храм?", "system")
            FLAG_TEMPLE = 1
            FLAG_FROG = 3
        else:
            self.interface.append_text("Вы ушли ни с чем.", "default")
        self.interface.update_status_display()

    def meet_deer(self):
        global FLAG_DEER
        self.interface.append_text("Путник! Заглядывают сюда иногда такие как ты... Думаю у меня для тебя кое что есть, но не просто так, конечно", "npc")
        choice = self.interface.show_choice_dialog("Вы встретили лань.", ["1. Дать яблоко", "2. Уйти"])
        if choice == "1. Дать яблоко" and self.player.inventory["яблоко"]:
            self.player.inventory["яблоко"] = 0
            self.player.stones["зеленый камень"] = True
            FLAG_DEER = 1
            self.interface.append_text("Лань аккуратно берет яблоко с вашей руки и в благодарность дастает из кармана зеленый светящийся камень", "system")
        else:
            self.interface.append_text("Лань: Думаю, что яблоко будет неплохим обменом", "npc")
        self.interface.update_status_display()

    def meet_forester(self):
        choice = self.interface.show_choice_dialog("Лесник: 'Убирайся!'", ["1. Грубо ответить", "2. Уйти", "3. Стрелять"])
        global FLAG_FORESTER
        if choice == "1. Грубо ответить" or (choice == "3. Стрелять" and self.player.inventory["патроны"] > 0):
            if choice == "3. Стрелять":
                self.player.inventory["патроны"] -= 1
                FLAG_FORESTER = 1
            self.player.stones["красный камень"] = True
            self.player.defeated["forester"] = True
            self.interface.append_text("Вы получили красный камень.", "item")
            FLAG_FORESTER = 1
        else:
            self.interface.append_text("Лесник уходит...", "npc")
        self.interface.update_status_display()

    def meet_harold_in_hut(self):
        choice = self.interface.show_choice_dialog("Гарольд: 'Что нужно?'", ["1. Вернуть дробовик", "2. Просто навестить"])
        if choice == "1. Вернуть дробовик" and self.player.inventory["дробовик"]:
            self.player.inventory["дробовик"] = 0
            self.player.has_shotgun = False
            self.player.debt_to_harold = False
            self.interface.append_text("Вы вернули дробовик Гарольду.", "event")
        else:
            self.interface.append_text("Гарольд: 'Ладно. Заходи ещё.'", "npc")
        self.interface.update_status_display()

    def trader_menu(self):
        self.interface.append_text("Вы оборачиваетесь и видите непонятно как появившуюся у вас за спиной лавку торговца", "event")
        self.interface.append_text("Торговец: Решил зайти в мою лавку?", "item")
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
        self.interface.update_status_display()

    def temple_ending(self):
        all_stones = self.player.has_all_stones()
        debt_paid = not self.player.debt_to_harold
        self.interface.append_text("Вы заходите в шаткий храм и видите некую арку с 4-мя отвертиями размером с небольшой камень", "event")

        if not debt_paid:
            self.interface.append_text("Гарольд с РПГ: Эй, куда собрался? Ты не вернул дробовик!", "combat")
            self.interface.append_text("В вас летит ракетный снаряд ПГ-7В с кумулятивной гранатой калибра 85 мм, вы умираете", "combat")
            self.interface.end_game("Вы не вернули Гарольду дробовик, он явно расстроился. Конец игры.", "combat")
        elif all_stones and debt_paid:
            self.interface.append_text("Воспользовавшись логикой вы вставляете все камни. Храм озарается светом, кажется вам удалось вернутся в ваш скучный и унылый мир!", "event")
            self.interface.end_game("Вы победили! Игра завершена.", "event")
        elif not all_stones and debt_paid:
            self.interface.append_text(f"Кажется тебе не хватает камней для активации портала, поищи еще", "warning")

