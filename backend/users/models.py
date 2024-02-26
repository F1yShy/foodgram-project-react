from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import F, Q

from core.constraints import (MAX_FIRST_NAME_LENGTH, MAX_LAST_NAME_LENGTH,
                              MAX_PASSWORD_LENGTH, MAX_USERNAME_LENGTH)


class CustomUser(AbstractUser):
    username = models.CharField(
        verbose_name="Логин",
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=[UnicodeUsernameValidator()],
    )
    password = models.CharField(
        verbose_name="Пароль",
        max_length=MAX_PASSWORD_LENGTH,
    )
    email = models.EmailField(
        verbose_name="Почта",
        unique=True,
    )
    first_name = models.CharField(
        verbose_name="Имя пользователя",
        max_length=MAX_FIRST_NAME_LENGTH,
    )
    last_name = models.CharField(
        verbose_name="Фамилия пользователя",
        max_length=MAX_LAST_NAME_LENGTH,
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "username"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self) -> str:
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="subcriptions",
        verbose_name="Пользователь",
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ("user",)

        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_subscriber"
            ),
            models.CheckConstraint(
                check=~Q(user=F("author")), name="deny_self_subscribing"
            ),
        ]

    def __str__(self):
        return f"{self.author} - {self.user}"
