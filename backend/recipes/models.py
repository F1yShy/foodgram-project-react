from colorfield.fields import ColorField
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from core.constraints import MAX_COLOR_LENGTH, MAX_NAME_LENGTH
from core.models import BaseNameModel, BaseUserModel
from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Название", unique=True, max_length=MAX_NAME_LENGTH
    )
    color = ColorField(
        verbose_name="Цвет в HEX",
        max_length=MAX_COLOR_LENGTH,
        default="#FF0000",
        unique=True,
    )
    slug = models.CharField(
        verbose_name="Уникальный слаг",
        unique=True,
        validators=[RegexValidator(regex=r"^[-a-zA-Z0-9_]+$")],
        max_length=MAX_NAME_LENGTH,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)


class Ingredient(BaseNameModel):
    measurement_unit = models.CharField(
        verbose_name="Единицы измерения", max_length=MAX_NAME_LENGTH
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)


class Recipe(BaseNameModel):
    author = models.ForeignKey(
        CustomUser,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="recipes",
    )
    image = models.ImageField(
        verbose_name="Картинка",
        upload_to="recipes/images",
    )
    text = models.TextField(verbose_name="Описание")
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Список ингредиентов",
        through="IngredientRecipe",
        through_fields=("recipe", "ingredient"),
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
    )
    cooking_time = models.SmallIntegerField(
        verbose_name="Время приготовления (в минутах)",
        default=1,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("name",)


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Рецепт",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredientes",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveIntegerField(
        verbose_name="Количество", validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("recipe",)

    def __str__(self):
        return f"{self.ingredient} в {self.recipe} в кол-ве {self.amount}"


class BaseUserRecipeModel(BaseUserModel):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_recipes",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class Favorite(BaseUserRecipeModel):

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"


class ShoppingCart(BaseUserRecipeModel):

    class Meta:
        verbose_name = "Рецепт в корзине"
        verbose_name_plural = "Рецепты в корзине"
