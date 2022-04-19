import random

API_TOKEN = "5176288897:AAFWal8jXz6Z4SKPJYf4MNsxc5tRskDQRYY"
CHAT_ID = "-721759162"

# Массив для выбора кодового имени юзера (для поиска его вопросов)
stuff = [
    "red", "blue", "green", "brown", "yellow", "white"
]


# Класс для формирования кодовых имен
class NameCounter:
    TOKEN = 10

    @classmethod
    def get_count(cls):
        Counter.TOKEN = Counter.TOKEN + 1
        return str("#" + random.choice(stuff)) + cls.TOKEN.__str__()


# Класс для формирования номеров вопросов
class Counter:
    TOKEN = 110

    @classmethod
    def get_count(cls):
        Counter.TOKEN = Counter.TOKEN + 1
        return "#" + cls.TOKEN.__str__()
