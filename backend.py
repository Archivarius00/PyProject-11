
import time
import random
from config import *
from ai_chat import chat_stream

class Player:
    def __init__(self):
        self.inventory = {"камешки": 0, "дробовик": 0, "патроны": 0, "чеснок": 0, "яблоко": 0, "еда": 1}
        self.stones = {"зеленый": False, "красный": False, "синий": False}
        self.has_shotgun = False
        self.debt_to_harold = False

    def add_item(self, item: str, quantity: int = 1):
        self.inventory[item] += quantity

    def remove_item(self, item: str, quantity: int = 1):
        if self.inventory.get(item, 0) >= quantity:
            self.inventory[item] -= quantity

class Game:
    def __init__(self, interface=None):
        self.interface = interface
        self.player = Player()
        self.current_location = "замок"
        self.temple_unlocked = False
        self.frog_quiz_passed = False
        self.current_npc = None  # ключ к кнопке "Поговорить"

    def print(self, text, tag="default"):
        if self.interface:
            self.interface.append_text(text, tag)
        else:
            print(text)

    def change_location(self, new_location: str):
        self.current_location = new_location
        self.print(f"=== {LOCATIONS[new_location]} ===", tag="location")
        time.sleep(1)

    def walk(self):
        self.print("Вы начинаете бродить...", tag="system")
        time.sleep(WALK_COOLDOWN)

        event = random.choice(["встреча", "камень", "ничего"])
        self.current_npc = None
        if event == "встреча":
            self.random_encounter()
        elif event == "камень" and random.random() <= STONE_DROP_CHANCE:
            self.player.add_item("камешки")
            self.print("Найден камешек!", tag="item")
        else:
            self.print("Ничего интересного не произошло.", tag="system")

    def random_encounter(self):
        if self.current_location == "замок":
            if random.random() <= SPAWN_CHANCE_HAROLD:
                self.meet_harold()
            else:
                self.meet_dracula()
        elif self.current_location == "болото":
            self.meet_frog()
        elif self.current_location == "лес":
            if random.random() <= DEER_SPAWN_CHANCE:
                self.meet_deer()
            else:
                self.meet_forester()

    def meet_harold(self):
        self.current_npc = "Гарольд"
        self.print("Гарольд: 'Эй, хочешь дробовик? Вернешь — живой будешь.'", tag="npc")

    def meet_dracula(self):
        self.current_npc = "Дракула"
        if self.player.inventory.get("чеснок", 0) > 0:
            self.print("Дракула: 'Аррргх! Чеснок!' Исчезает в дыму.", tag="npc")
            self.player.remove_item("чеснок")
        else:
            self.print("Дракула съедает вас! Игра окончена.", tag="combat")
            exit()

    def meet_frog(self):
        self.current_npc = "Фроггит"
        self.print("Фроггит: 'Ты кто такой? Проваливай отсюда!'", tag="npc")

    def trader_menu(self):
        self.print("Торговец: 'Чем интересуешься?'", tag="npc")
        for item, data in TRADER_ITEMS.items():
            self.print(f"{item} - {data['цена']} камешков", tag="item")

    def meet_deer(self):
        self.current_npc = "Лань"
        if self.player.inventory.get("яблоко", 0) > 0:
            self.print("Лань съедает яблоко и оставляет зеленый камень.", tag="event")
            self.player.stones["зеленый"] = True
            self.player.remove_item("яблоко")
        else:
            self.print("Нужно яблоко, чтобы приманить лань!", tag="warning")

    def meet_forester(self):
        self.current_npc = "Лесник"
        self.print("Лесник: 'А ну пошёл вон отсюда!'", tag="npc")

    def temple_ending(self):
        self.print("=== ХРАМ ===", tag="location")
        if self.player.debt_to_harold:
            self.print("Гарольд с RPG: 'Ты не вернул дробовик!'", tag="combat")
            time.sleep(1)
            self.print("Вас взрывают. Конец игры.", tag="combat")
        else:
            self.print("Вы нашли все камни и победили!", tag="event")
        exit()

    def get_npc_response(self, npc_name, player_input):
        messages = [
            {"role": "system", "content": f"Ты — {npc_name} в волшебном лесу. Говори в стиле злого колоритного персонажа."},
            {"role": "user", "content": player_input}
        ]
        try:
            return chat_stream(messages).strip()
        except Exception as e:
            return f"[Ошибка нейросети: {e}]"

    def on_action(self, action):
        if action == "Побродить":
            self.walk()
        elif action == "Инвентарь":
            items = "\n".join(f"{k}: {v}" for k, v in self.player.inventory.items())
            stones = ", ".join([k for k, v in self.player.stones.items() if v])
            self.print("Инвентарь:\n" + items + f"\nКамни: {stones}", tag="inventory")
        elif action == "Торговец":
            self.trader_menu()
        elif action == "Показать лог":
            if self.interface:
                self.interface.show_log_window()
        elif action == "Поговорить":
            if self.current_npc:
                self.interface.show_dialogue(self.current_npc, [(self.current_npc, "Чего тебе надо, путник?")])
            else:
                self.print("Некому ответить. Осмотрись вначале.", tag="warning")