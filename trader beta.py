import tkinter as tk
from tkinter import messagebox, ttk

def trader_shop(player_money):
    trader_window = tk.Toplevel()
    trader_window.title("Торговец")
    trader_window.geometry("500x600")
    trader_window.configure(bg="black")
    trader_window.resizable(False, False)

    # Список товаров
    items = {
        1: {"name": "хуй1", "price": 100, "description": "хуй1"},
        2: {"name": "хуй2", "price": 250, "description": "хуй2"},
        3: {"name": "хуй3", "price": 50, "description": "хуй3"},
        4: {"name": "хуй4", "price": 150, "description": "хуй4"},
        5: {"name": "хуй5", "price": 300, "description": "хуй5"}
    }


    separator_style = ttk.Style()
    separator_style.configure("White.TSeparator", background="white")

    # Фрейм для содержимого
    main_frame = tk.Frame(trader_window, bg="black")
    main_frame.pack(padx=10, pady=10, fill="both", expand=True)


    title_label = tk.Label(
        main_frame,
        text="Д О Б Р О   П О Ж А Л О В А Т Ь !",
        font=("Arial", 14, "bold"),
        fg="white",
        bg="black"
    )
    title_label.pack(pady=10)


    ttk.Separator(main_frame, orient="horizontal", style="White.TSeparator").pack(fill="x", pady=5)

    # Фразы
    trader_phrases = [
        "Чего желаете, странник?",
        "У меня есть вещи, которые вам пригодятся... за соответствующую цену.",
        "Выбирайте, но выбирайте с умом!",
        "Ха-ха! Отличный выбор!",
        "Это вам очень пригодится... или нет."
    ]

    trader_label = tk.Label(
        main_frame,
        text=trader_phrases[0],
        font=("Arial", 10, "italic"),
        fg="white",
        bg="black",
        wraplength=400
    )
    trader_label.pack(pady=10)


    ttk.Separator(main_frame, orient="horizontal", style="White.TSeparator").pack(fill="x", pady=5)

    # Список
    items_frame = tk.Frame(main_frame, bg="black")
    items_frame.pack(pady=10)

    for num, item in items.items():
        item_frame = tk.Frame(items_frame, bg="black")
        item_frame.pack(fill="x", pady=5)

        tk.Label(
            item_frame,
            text=f"{num}. {item['name']} - {item['price']} камней",
            font=("Arial", 10),
            fg="white",
            bg="black",
            anchor="w"
        ).pack(side="left")

        tk.Label(
            item_frame,
            text=f"{item['description']}",
            font=("Arial", 8),
            fg="gray",
            bg="black",
            anchor="w"
        ).pack(side="left", padx=10)


    ttk.Separator(main_frame, orient="horizontal", style="White.TSeparator").pack(fill="x", pady=5)

    # Баланс 
    money_label = tk.Label(
        main_frame,
        text=f"Ваши деньги: {player_money} монет",
        font=("Arial", 10, "bold"),
        fg="gold",
        bg="black"
    )
    money_label.pack(pady=10)

    # Поле для ввода
    choice_frame = tk.Frame(main_frame, bg="black")
    choice_frame.pack(pady=10)

    tk.Label(
        choice_frame,
        text="Выберите товар (1-5) или 0 для выхода:",
        font=("Arial", 10),
        fg="white",
        bg="black"
    ).pack(side="left")

    choice_entry = tk.Entry(choice_frame, width=5, font=("Arial", 10))
    choice_entry.pack(side="left", padx=10)



    def process_purchase():
        try:
            choice = int(choice_entry.get())
        except ValueError:
            trader_label.config(text="Эй, здесь нужны цифры, а не ваши каракули!")
            return

        if choice == 0:
            trader_window.destroy()
            return

        if choice not in items:
            trader_label.config(text="У меня нет такого товара, странник...")
            return

        selected_item = items[choice]

        if player_money < selected_item["price"]:
            trader_label.config(text="Ха! У тебя недостаточно монет, странник!")
            return


        confirm = messagebox.askyesno(
            "Подтверждение покупки",
            f"Купить {selected_item['name']} за {selected_item['price']} монет?"
        )

        if confirm:

            player_money -= selected_item["price"]
            money_label.config(text=f"Ваши деньги: {player_money} монет")
            trader_label.config(text=f"Отличная покупка! {selected_item['name']} теперь ваш! Ха-ха!")

            # здесь надо добавить логику добавления предмета в инвентарь

        else:
            trader_label.config(text="Передумали? Ну и ладно...")

    # Кнопка
    buy_button = tk.Button(
        main_frame,
        text="Купить",
        command=process_purchase,
        font=("Arial", 10, "bold"),
        bg="gray20",
        fg="white",
        activebackground="gray30",
        activeforeground="white",
        relief="flat"
    )
    buy_button.pack(pady=10)


    trader_window.grab_set()
    trader_window.wait_window()

    return player_money



#///////////////////////////////////////////////////////////



trader_shop(500)