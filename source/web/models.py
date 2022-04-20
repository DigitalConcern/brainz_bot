from django.db import models


# Зарегситрировавшиеся пользователи добавляются в базу данных
class ActiveUsers(models.Model):
    user_id = models.IntegerField(primary_key=True)
    is_admin = models.BooleanField()
    code_name = models.TextField()
    user_name = models.TextField()
    grade = models.TextField()

    class Meta:
        db_table = "users"


class Programs(models.Model):
    id = models.IntegerField(primary_key=True)
    key = models.IntegerField()
    description = models.TextField()
    info = models.TextField()
    category = models.TextField()
    is_active = models.BooleanField()

    class Meta:
        db_table = "programs"