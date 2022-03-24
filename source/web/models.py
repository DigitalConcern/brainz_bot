from tortoise import Tortoise, models, fields
from orm_converter.tortoise_to_django import ConvertedModel


class User(models.Model):
    name = fields.CharField(description="Telegram username", max_length=255)
    tg_id = fields.IntField(description="Telegram id", max_length=20)

    def __str__(self):
        return self.tg_id

    class Meta:
        table = "users"


def register_models() -> None:
    Tortoise.init_models(
        models_paths=["source.web.models"],
        app_label="web",
        _init_relations=False,
    )
