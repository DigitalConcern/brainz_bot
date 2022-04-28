from django.db import models


# Зарегситрировавшиеся пользователи добавляются в базу данных
class ActiveUsers(models.Model):
    user_id = models.IntegerField(primary_key=True)
    is_admin = models.BooleanField()
    code_name = models.TextField()
    user_name = models.TextField()
    grade = models.TextField()
    def get_absolute_url(self):
        return '/users'

    class Meta:
        db_table = "users"


class Programs(models.Model):
    id = models.BigAutoField(primary_key=True)
    key = models.IntegerField()
    name = models.TextField()
    description = models.TextField()
    info = models.TextField()
    category = models.TextField()
    is_active = models.BooleanField()
    link = models.TextField()

    def get_absolute_url(self):
        return '/programs'

    class Meta:
        db_table = "programs"

class Links(models.Model):
    link = models.TextField()

    class Meta:
        db_table = "links"