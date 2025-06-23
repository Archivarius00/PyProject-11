import time
import random
from config import *
roll = random.random() # это для проверки что выпадает ничего событие или камень. удаллить после уверенности что все хорошо

class Player:
    """Класс игрока с инвентарем и прогрессом"""
    def __init__(self):
        self.inventory = {"камешки": 0, "дробовик": 0, "патроны": 0, "чеснок": 1, "яблоко": 0}
        self.stones = {"зеленый камень": False, "красный камень": False, "синий камень": False, "камень - путеводитель": False}
        self.has_shotgun = False
        self.debt_to_harold = False
        self.defeated = {
            "dracula": False,
            "deer": False,
            "forester": False
        }
        
    def add_item(self, item: str, quantity: int = 1):
        self.inventory[item] += quantity

    def remove_item(self, item: str, quantity: int = 1):
        if self.inventory.get(item, 0) >= quantity:
            self.inventory[item] -= quantity
    
    def has_all_stones(self):
        """Проверяет, собраны ли все камни"""
        return all(self.stones.values())

class Game:
    """Основной класс игры"""
    def __init__(self):
        self.player = Player()
        self.current_location = "замок"
        self.temple_unlocked = False
        self.frog_quiz_passed = False
        self.hut_visited = False
        self.frog_defeated = False
        
    def change_location(self, new_location: str):
        """Смена локации с описанием"""
        self.current_location = new_location
        print(f"\n=== {LOCATIONS[new_location]} ===")
        time.sleep(1)
        if new_location == "хижина": # триггер встречи гарольда в хижине
            self.meet_harold_in_hut()
   
    def walk(self):
        """Механика прогулки с таймером"""
        print("\nВы начинаете бродить...")
        time.sleep(WALK_COOLDOWN)
        global roll
        # Случайные события
        event = random.choices(["встреча", "камень", "ничего"], weights=[.50, .40, .10])[0]
        print(*event)
        if event == "встреча":
            self.random_encounter()
        elif event == "камень":
             self.player.add_item("камешки")
             print("Найден камешек!")
        else:
            print("Ничего интересного не произошло")

    def random_encounter(self):
        """Объявляем"""
        global FLAG_DRACULA
        global FLAG_FROG
        global FLAG_HAROLD
        global FLAG_FORESTER
        global FLAG_DEER
        
        """Обработка случайных встреч с учетом побежденных персонажей"""
        if self.current_location == "замок":
            if FLAG_HAROLD == 0 and self.player.has_shotgun == False:
                self.meet_harold()
                if self.player.has_shotgun:
                   FLAG_HAROLD = 1
            elif FLAG_DRACULA == 0:
                FLAG_DRACULA = 1
                self.meet_dracula()
            elif FLAG_HAROLD == 1 and FLAG_DRACULA == 1:
                print("Вы прошли весь замок вдоль и поперек, похоже здесь никого не осталось")
            else:
                print("Ничего интересного не произошло")
            
        elif self.current_location == "болото":
            if FLAG_FROG == 0:
                FLAG_FROG = 1
                self.meet_frog()
            elif FLAG_FROG == 1:
                if not self.frog_quiz_passed:
                    self.meet_frog_again()
                else:
                    print("Фроггит: 'Я уже все тебе рассказал! Иди к храму!'")
            else:
                print("Вы обошли все болото вдоль и поперек, похоже здесь никого не осталось")
                return
        
        elif self.current_location == "лес":
            if  FLAG_DEER == 0 and FLAG_FORESTER:
                self.meet_deer()
            elif FLAG_FORESTER == 0:
                self.meet_forester()
            elif FLAG_DEER and FLAG_FORESTER:
                print("Вы прошли весь лес вдоль и поперек, похоже здесь никого не осталось")
            else:
                 print("Ничего интересного не произошло")
            
    
    def meet_harold(self):
        """Взаимодействие с Гарольдом"""
        print("\nГарольд: 'Эй, хочешь дробовик? Вернешь — живой будешь.'")
        choice = input("1. Взять дробовик\n2. Отказаться\n> ")
        if choice == "1":
            self.player.has_shotgun = True
            self.player.inventory["дробовик"] = 1
            self.player.inventory["патроны"] = 2
            self.player.debt_to_harold = True
            print("Гарольд: 'Ладно, но помни об обещании!'")
        else:
            self.has_shotgun = False
            print("Гарольд: 'Тогда проваливай!'")

    def meet_dracula(self):
        """Встреча с Дракулой"""
        print("\nВы встретили Дракулу'")
        choice = input("1. Отдать чеснок\n2. Выстрелить в Дракулу \n> ")
        if choice == "1" and self.player.inventory.get("чеснок", 0) > 0:
            print("\nДракула: 'Аррргх! Чеснок!' Исчезает в дыму.")
            self.player.stones["синий камень"] = True
            self.player.remove_item("чеснок")
        elif choice == "2" and self.player.inventory["патроны"] > 0:
            print("Вы стреляете в дракулу и забираете камень.")
            self.player.inventory["патроны"] -= 1
            self.player.stones["синий камень"] = True
        else:
            print("\n Похоже, что сегодня не ваш день. Дракула съедает вас! Игра окончена.")
            exit()

    def meet_frog(self):
        """Квиз с лягушкой"""
        global FLAG_FROG

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
            print("Фроггит: 'Храм в локации храм. Катись отсюда! и да чтобы ты не заблудился возьми камень - путеводитель.'")
            self.temple_unlocked = True
            self.frog_quiz_passed = True
            FLAG_FROG = 2
            self.player.stones["камень - путеводитель"] = True
        else:
            print("Фроггит: 'Тупица! Проваливай!'")
    
    def meet_frog_again(self):
        """Повторная встреча с лягушкой после провала квеста"""
        print("\nФроггит: 'Опять ты? Неудачник! Ну что, хочешь решить вопросы силой?'")
        choice = input("1. Выстрелить в лягушку\n2. Уйти\n> ")
        if self.player.inventory.get("дробовик", 0) > 0 and self.player.inventory.get("патроны", 0) > 0:
            if choice == "1":
                print("Вы стреляете в Фроггита. Он успевает крикнуть: 'Храм... в храме...'")
                self.temple_unlocked = True
                self.player.inventory["патроны"] -= 1
                self.frog_defeated = True
                self.player.stones["камень - путеводитель"] = True
                global FLAG_FROG
                FLAG_FROG = 2
            else:
                print("Вы уходите, слыша насмешки лягушки.")
        else:
            print("Фроггит: 'Ха-ха! У тебя даже нет дробовика или патронов! Проваливай!'")    
 
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
        print("Вы встретили лань")
        global FLAG_DEER
        choice = input("1. Покормить яблоком\n2. Выстрелить в Лань\n3. Уйти\n> ").strip()
        
        if choice == "1" and self.player.inventory.get("яблоко", 0) > 0:
            print("\nЛань съедает яблоко и оставляет зеленый камень.")
            self.player.stones["зеленый камень"] = True
            FLAG_DEER = 1
            self.player.remove_item("яблоко")
        elif choice == "2" and self.player.inventory["патроны"] > 0:
            print("Вы стреляете в Лань и забираете камень.")
            self.player.inventory["патроны"] -= 1
            self.player.stones["зеленый камень"] = True
            FLAG_DEER = 1
        elif choice == "2" and self.player.inventory["патроны"] == 0:
            print('Из-за отсутствия патронов, вы не смогли убить лань')
        elif choice == "3":
             print("Вы уходите, не тронув лань.")
        else:
            print("\nНужно яблоко, чтобы приманить лань!")

    def meet_forester(self):
        """Диалог с лесником"""
        global FLAG_FORESTER
        print("\nЛесник: 'А ну пошёл вон отсюда!'")
        choice = input("1. Грубо ответить\n2. Уйти\n3. Выстрелить\n> ")
        if choice == "1":
            print("Лесник: 'Ах ты... Ладно, держи камень!'")
            self.player.stones["красный камень"] = True
            FLAG_FORESTER = 1
        elif choice == "3" and self.player.inventory["патроны"] > 0:
            print("Вы стреляете в лесника и забираете камень.")
            self.player.inventory["патроны"] -= 1
            self.player.stones["красный камень"] = True
            FLAG_FORESTER = 1
        elif choice == "3" and self.player.inventory["патроны"] == 0:
             print("ахаха, дробовик взял а патронов то нет")
        else:
            print("Лесник прогоняет вас.")

    
    
    
    
    
    def meet_harold_in_hut(self):
        """Взаимодействие с Гарольдом в хижине"""
        if not self.hut_visited:
            print("\nГарольд: 'О, ты вернулся! Чего хочешь?'")
            self.hut_visited = True
        else:
            print("\nГарольд: 'Снова пришел? Чем могу помочь?'")
            
        print("1. Вернуть дробовик")
        print("2. Я пришел проведать тебя просто так")
        
        choice = input("> ").strip()
        
        if choice == "1":
            if self.player.inventory.get("дробовик", 0) > 0:
                self.player.remove_item("дробовик")
                self.player.has_shotgun = False
                self.player.debt_to_harold = False
                print("Гарольд: 'О, как я давно тебя не видел! Спасибо, что вернул оружие.'")
            else:
                print("У вас нет дробовика!")
        elif choice == "2":
            if self.player.debt_to_harold:
                print("Гарольд: 'Спасибо что навестил, надеюсь мое ружье скоро тоже меня навестит.'")
            else:
                print("Гарольд: 'Всегда рад гостям! Заходи еще.'")
        else:
            print("Гарольд не понял ваш выбор.")
    
    def temple_ending(self):
        """Финал в храме"""
        print("\n=== ХРАМ ===")
        all_stones = self.player.has_all_stones()
        debt_paid = not self.player.debt_to_harold
        if all_stones and debt_paid:
            # Идеальный финал: Собрал все камни и вернул дробовик
            print("Вы вставляете все 4 камня в алтарь.")
            print("Храм озаряется ярким светом!")
            print("Голос из ниоткуда: 'Ты доказал свою мудрость и честность!'")
            print("Поздравляем! Вы прошли игру!")
            exit()
        elif self.player.debt_to_harold and all_stones:
            # Собрал все камни, но не вернул дробовик
            print("Вы вставляете все 4 камня в алтарь.")
            print("Храм начинает дрожать, когда вдруг...")
            print("Гарольд с RPG: 'Ты не вернул дробовик!'")
            time.sleep(1)
            print("Ракета летит прямо в вас...")
            time.sleep(1)
            print("Вас взрывают. Конец игры.")
            exit()
        elif self.player.debt_to_harold and not all_stones:
            # Не собрал все камни и не вернул дробовик
            print("Вы пытаетесь активировать алтарь, но камней не хватает.")
            print("Внезапно появляется Гарольд с RPG: 'Ты не вернул дробовик!'")
            time.sleep(1)
            print("Ракета летит прямо в вас...")
            time.sleep(1)
            print("Вас взрывают. Конец игры.")
            exit()
        else:  # отдал дробовик, но не собрал все камни
            print("Вы осматриваете алтарь, но понимаете, что у вас не хватает камней.")
            missing_stones = [stone for stone, has in self.player.stones.items() if not has]
            print(f"Не хватает: {', '.join(missing_stones)} камней.")
            print("Вернитесь и найдите недостающие камни!")
            self.current_location = "замок"  # Возвращаем в замок
            print("Вы возвращаетесь в замок.")
            time.sleep(2)

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
    print("=== Гарольд с дробовиком ===")
    game = Game()
    game.main_loop()