from tortoise import Tortoise, fields
from tortoise.models import Model

# Классы ORM


# Зарегситрировавшиеся пользователи добавляются в базу данных
class ActiveUsers(Model):
    user_id = fields.IntField(pk=True)
    code_name = fields.TextField()
    user_name = fields.TextField()
    grade = fields.TextField()
    questions: fields.ReverseRelation["Questions"]

    class Meta:
        table = "users"


# Таблица с администраторами
class Admins(Model):
    user_id = fields.IntField()

    class Meta:
        table = "admins"


# Таблица с вопросами
class Questions(Model):
    key = fields.TextField(pk=True)
    user_id: fields.ForeignKeyRelation[ActiveUsers] = fields.ForeignKeyField(
        "models.ActiveUsers", related_name='questions')
    question = fields.TextField()
    is_answered = fields.BooleanField()

    class Meta:
        table = "questions"


# Инициализация базы данных
async def run():
    await Tortoise.init(
        db_url="postgres://postgres:postgres@localhost:5432/postgres",
        modules={
            "models": ["DB"]
        })
    await Tortoise.generate_schemas()
