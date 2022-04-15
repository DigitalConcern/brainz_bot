import asyncio
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


class Programs(Model):
    key = fields.IntField(pk=True)
    text = fields.TextField()
    is_student = fields.TextField()

    # is_active = fields.BooleanField()

    class Meta:
        table = "programs_student"


# Инициализация базы данных
async def run():
    await Tortoise.init(
        config={
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "database": "postgres",
                        "host": "172.18.0.2",
                        "password": "postgres",
                        "port": 5432,
                        "user": "postgres"
                    }
                }
            },
            "apps": {
                "models": {
                    "models": ["database"],
                    "default_connection": "default",
                }
            },
        }
    )
    await Tortoise.generate_schemas()


async def loop_db():
    loop = asyncio.get_event_loop()
    loop.create_task(run())
