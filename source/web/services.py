from typing import Tuple, Union
from . import models


def add_user(tg_id: int, name: str) -> Tuple[models.User, bool]:
    return models.User.objects.get_or_create(
        tg_id=tg_id, name=name
    )
