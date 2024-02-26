from django.db import models

from core.constraints import MAX_NAME_LENGTH
from users.models import CustomUser


class BaseNameModel(models.Model):
    """Базовая модель, содержащая общее поле - имя."""

    name = models.CharField(
        verbose_name="Название",
        max_length=MAX_NAME_LENGTH,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class BaseUserModel(models.Model):
    """Базовая модель, содержащая общее поле - пользователь."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )

    class Meta:
        abstract = True
