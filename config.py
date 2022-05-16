import random

API_TOKEN = "5176288897:AAFWal8jXz6Z4SKPJYf4MNsxc5tRskDQRYY"
CHAT_ID = "478769369"

# Массив для выбора кодового имени юзера (для поиска его вопросов)
stuff = [
    "red", "blue", "green", "brown", "yellow", "white"
]

# Словарь категорий для обработки данных из таблицы активных пользователей
categories = {
    "Всем": ["<7", "8", "9", "10", "11", "12"],
    "Студентам": ["12"],
    "Школьникам": ["<7", "8", "9", "10", "11"]
}


# Класс для формирования кодовых имен
class Names:
    @classmethod
    def get_name(cls):
        return str("#" + random.choice(stuff)) + str(random.randint(1, 5000))


# Класс для формирования номеров вопросов
class Counter:
    TOKEN = 110

    @classmethod
    def get_count(cls):
        Counter.TOKEN = Counter.TOKEN + 1
        return "#q" + cls.TOKEN.__str__()
