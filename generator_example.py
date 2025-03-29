# variables_generator.py
import random

# Случайное целое число
random_int = random.randint(1, 100)

# Случайное вещественное число
random_float = random.uniform(1.0, 10.0)

# Случайная строка (нахуя бы)
random_string = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=1488))

# Случайный список чисел
random_list = [random.randint(1, 10) for _ in range(5)]

# Имена
random_dict = {
    'id': random.randint(1000, 9999),
    'name': random.choice(['Mengel', 'Adolf', 'Hitler']),
    'active': random.choice([True, False])
}

# Случайные координаты (если захотим более сложную систему передвжиения)
random_tuple = (random.uniform(-90.0, 90.0), random.uniform(-180.0, 180.0))

# Случайное множество
random_set = {random.randint(1, 10) for _ in range(5)}

# Случайное булево значение
random_bool = random.choice([True, False])



# Проверка (можно удалить)
if __name__ == "__main__":
    variables = {
        'int': random_int,
        'float': random_float,
        'str': random_string,
        'list': random_list,
        'dict': random_dict,
        'tuple': random_tuple,
        'set': random_set,
        'bool': random_bool,
    }
    
    for name, value in variables.items():
        print(f"{name}: {value} ({type(value)})")