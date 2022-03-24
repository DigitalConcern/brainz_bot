from django.db import models


class User(models.Model):
    tg_id = models.CharField("Telegram User ID", default=0, max_length=255)
    username = models.CharField("Telegram Username", default=0, max_length=255)

    def __str__(self) -> str:
        return f"{self.username} - {self.tg_id}"

    class Meta:
        app_label = 'web'


class Comment(models.Model):
    text = models.CharField("Message text", max_length=1000)
