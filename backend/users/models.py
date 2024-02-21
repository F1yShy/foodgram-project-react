from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import F, Q

from core.constraints import (MAX_EMAIL_LENGTH, MAX_FIRST_NAME_LENGTH,
                              MAX_LAST_NAME_LENGTH, MAX_PASSWORD_LENGTH,
                              MAX_USERNAME_LENGTH)


class CustomUser(AbstractUser):
    username = models.CharField(
        verbose_name="Логин",
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=[RegexValidator(regex=r"^[\w.@+-]+\Z")],
    )
    password = models.CharField(
        verbose_name="Пароль",
        max_length=MAX_PASSWORD_LENGTH,
    )
    email = models.EmailField(
        verbose_name="Почта",
        max_length=MAX_EMAIL_LENGTH,
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

    def __str__(self) -> str:
        return self.username

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)


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
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_subscriber"
            ),
            models.CheckConstraint(
                check=~Q(user=F("author")), name="deny_self_subscribing"
            ),
        ]

    def __str__(self):
        return f"{self.author.username} - {self.user.username}"
