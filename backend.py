import time
import random
from config import *

class Player:
    """Класс игрока с инвентарем и прогрессом"""
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
    """Основной класс игры"""
    def __init__(self):
        self.player = Player()
        self.current_location = "замок"
        self.temple_unlocked = False
        self.frog_quiz_passed = False

    def change_location(self, new_location: str):
        """Смена локации с описанием"""
        self.current_location = new_location
        print(f"\n=== {LOCATIONS[new_location]} ===")
        time.sleep(1)

    def walk(self):
        """Механика прогулки с таймером"""
        print("\nВы начинаете бродить...")
        time.sleep(WALK_COOLDOWN)
        
        # Случайные события
        event = random.choice(["встреча", "камень", "ничего"])
        if event == "встреча":
            self.random_encounter()
        elif event == "камень" and random.random() <= STONE_DROP_CHANCE:
            self.player.add_item("камешки")
            print("Найден камешек!")
        else:
            print("Ничего интересного не произошло.")

    def random_encounter(self):
        """Обработка случайных встреч"""
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
        """Взаимодействие с Гарольдом"""
        print("\nГарольд: 'Эй, хочешь дробовик? Вернешь — живой будешь.'")
        choice = input("1. Взять дробовик\n2. Отказаться\n> ")
        if choice == "1":
            self.player.has_shotgun = True
            self.player.inventory["дробовик"] = 1
            self.player.inventory["патроны"] = 3
            self.player.debt_to_harold = True
            print("Гарольд: 'Ладно, но помни об обещании!'")
        else:
            print("Гарольд: 'Тогда проваливай!'")

    def meet_dracula(self):
        """Встреча с Дракулой"""
        if self.player.inventory.get("чеснок", 0) > 0:
            print("\nДракула: 'Аррргх! Чеснок!' Исчезает в дыму.")
            self.player.remove_item("чеснок")
        else:
            print("\nДракула съедает вас! Игра окончена.")
            exit()

    def meet_frog(self):
        """Квиз с лягушкой"""
        print("\nФроггит: 'Ты кто такой? Слабо ответить на вопросы?'")
        correct = 0
        for _ in range(3):
            q = random.choice(QUESTIONS_POOL)
            print(f"\n{q['вопрос']}")
            start = time.time()
            answer = input("Ответ: ").strip()
            if time.time() - start > QUESTION_TIMER:
                print("Время вышло! Фроггит сбежала.")
                return
            if answer.lower() == q['ответ'].lower():
                correct += 1
        if correct >= 2:
            print("Фроггит: 'Храм в локации храм. Катись отсюда!'")
            self.temple_unlocked = True
        else:
            print("Фроггит: 'Тупица! Проваливай!'")

    def trader_menu(self):
        """Торговец"""
        print("\nТорговец: 'Чем интересуешься?'")
        for item, data in TRADER_ITEMS.items():
            print(f"{item} - {data['цена']} камешков")
        item = input("Введите название предмета или 'выход': ").lower()
        if item == "выход":
            return
        if item in TRADER_ITEMS:
            if self.player.inventory["камешки"] >= TRADER_ITEMS[item]["цена"]:
                self.player.remove_item("камешки", TRADER_ITEMS[item]["цена"])
                self.player.add_item(item)
                print(f"Получено: {item}!")
            else:
                print("Не хватает камешков.")

    def meet_deer(self):
        """Взаимодействие с ланью"""
        if self.player.inventory.get("яблоко", 0) > 0:
            print("\nЛань съедает яблоко и оставляет зеленый камень.")
            self.player.stones["зеленый"] = True
            self.player.remove_item("яблоко")
        else:
            print("\nНужно яблоко, чтобы приманить лань!")

    def meet_forester(self):
        """Диалог с лесником"""
        print("\nЛесник: 'А ну пошёл вон отсюда!'")
        choice = input("1. Грубо ответить\n2. Уйти\n3. Выстрелить\n> ")
        if choice == "1":
            print("Лесник: 'Ах ты... Ладно, держи камень!'")
            self.player.stones["красный"] = True
        elif choice == "3" and self.player.inventory["патроны"] > 0:
            print("Вы стреляете в лесника и забираете камень.")
            self.player.inventory["патроны"] -= 1
            self.player.stones["красный"] = True
        else:
            print("Лесник прогоняет вас.")

    def temple_ending(self):
        """Финал в храме"""
        print("\n=== ХРАМ ===")
        if self.player.debt_to_harold:
            print("Гарольд с RPG: 'Ты не вернул дробовик!'")
            time.sleep(1)
            print("Вас взрывают. Конец игры.")
        else:
            print("Вы нашли все камни и победили!")
        exit()

    def main_loop(self):
        """Главный игровой цикл"""
        while True:
            print(f"\nЛокация: {self.current_location}")
            print("1. Побродить")
            print("2. Перейти в другую локацию")
            print("3. Вызвать торговца")
            print("4. Инвентарь")
            print("5. Выйти")
            
            choice = input("> ").strip()
            
            if choice == "1":
                self.walk()
            elif choice == "2":
                new_loc = input("Куда идем? (замок/болото/лес/хижина/храм): ").lower()
                if new_loc in LOCATIONS:
                    if new_loc == "храм" and not self.temple_unlocked:
                        print("Вы не знаете, где храм!")
                    else:
                        self.change_location(new_loc)
                        if new_loc == "храм":
                            self.temple_ending()
                else:
                    print("Недопустимая локация!")
            elif choice == "3":
                self.trader_menu()
            elif choice == "4":
                print("\nИнвентарь:")
                for item, count in self.player.inventory.items():
                    print(f"{item}: {count}")
                print("Камни:", [k for k, v in self.player.stones.items() if v])
            elif choice == "5":
                exit()
            else:
                print("Некорректный выбор")

if __name__ == "__main__":
    print("=== Гарольд с дробовиком аааа===")
    game = Game()
    game.main_loop()