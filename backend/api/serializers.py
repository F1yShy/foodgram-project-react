from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import CustomUser, Subscription


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра аккаунтов пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        """
        Возвращает True, если подписка существует,
        пользователь авторизован и существует реквест.
        В остальных случаях возвращает False.
        """
        request = self.context.get("request")

        return bool(
            request
            and request.user.is_authenticated
            and Subscription.objects.filter(
                user=request.user, author=obj
            ).exists()
        )


class SubscribeSerializer(CustomUserSerializer):
    """Сериализатор для подписки."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = CustomUserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        """Возвращает список рецептов."""
        request = self.context["request"]
        limit = request.GET.get("recipes_limit")
        queryset = Recipe.objects.filter(author=obj)
        if limit:
            try:
                limit = int(limit)
            except ValueError:
                pass
            queryset = queryset[:limit]
        return AbridgedRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        """Возвращает количество рецептов."""
        return Recipe.objects.filter(author=obj.id).count()


class SubscribeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки."""

    user = SlugRelatedField(
        read_only=True,
        slug_field="username",
        default=serializers.CurrentUserDefault(),
    )
    author = SlugRelatedField(
        slug_field="username", queryset=CustomUser.objects.all()
    )

    class Meta:
        fields = ("user", "author")
        model = Subscription
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=["user", "author"],
                message="Ошибка, вы уже подписаны на данного пользователя",
            ),
        ]

    def validate_author(self, value):
        """Проверка, что пользователь не может подписаться сам на себя."""

        if self.context["request"].user == value:
            raise serializers.ValidationError(
                "Вы не можете подписаться на себя"
            )
        return value

    def to_representation(self, instance):
        return SubscribeSerializer(
            instance=instance.author, context=self.context
        ).data


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(
        source="ingredient.id",
    )
    name = serializers.ReadOnlyField(
        source="ingredient.name",
    )
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit",
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тега."""

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиента."""

    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта."""

    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True, read_only=True, source="ingredientes"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        """
        Возвращает True, если рецепт находится в избранном,
        пользователь авторизован и существует реквест.
        В остальных случаях возвращает False.
        """
        request = self.context.get("request")

        return bool(
            request
            and request.user.is_authenticated
            and Recipe.objects.filter(
                favorite__user=request.user, id=obj.id
            ).exists(),
        )

    def get_is_in_shopping_cart(self, obj):
        """
        Возвращает True, если рецепт находится в корзине,
        пользователь авторизован и существует реквест.
        В остальных случаях возвращает False.
        """
        request = self.context.get("request")

        return bool(
            request
            and request.user.is_authenticated
            and Recipe.objects.filter(
                shoppingcart__user=request.user, id=obj.id
            ).exists(),
        )


class IngredientCreateInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания ингредиентов в рецепте."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = ("id", "amount")


class AbridgedRecipeSerializer(serializers.ModelSerializer):
    """Сокращенный сериализатор рецепта."""

    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )
        read_only_fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class RecipeCreateAndUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецепта."""

    image = Base64ImageField(represent_in_base64=True)
    ingredients = IngredientCreateInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def create_ingredients(self, recipe, ingredients_data):
        IngredientRecipe.objects.bulk_create(
            [
                IngredientRecipe(
                    recipe=recipe,
                    ingredient_id=ingredient_data.get("id"),
                    amount=ingredient_data["amount"],
                )
                for ingredient_data in ingredients_data
            ]
        )

    def validate(self, data):
        ingredients = self.initial_data.get("ingredients")
        cooking_time = data.get("cooking_time")
        tags = data.get("tags")
        image = data.get("image")

        if not ingredients:
            raise serializers.ValidationError("Поле ingredients обязательно")

        if not cooking_time:
            raise serializers.ValidationError("Поле cooking_time обязательно")

        if not tags:
            raise serializers.ValidationError("Поле tags обязательно")

        if not image:
            raise serializers.ValidationError("Поле image обязательно")

        ingredients_ids = {ingredient["id"] for ingredient in ingredients}

        if len(ingredients_ids) != len(ingredients):

            raise serializers.ValidationError(
                "Требуются неповторяющиеся ингредиенты"
            )

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError("Требуются неповторяющиеся теги")

        data["ingredients"] = ingredients
        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        author = self.context.get("request").user

        recipe = Recipe.objects.create(author=author, **validated_data)

        self.create_ingredients(recipe, ingredients_data)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")

        instance.ingredients.clear()

        self.create_ingredients(instance, ingredients_data)
        instance.tags.set(tags_data)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class BaseUserRecipeSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для избранного и корзины покупок."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        fields = ("user", "recipe")

    def to_representation(self, instance):
        return AbridgedRecipeSerializer(
            instance.recipe, context=self.context
        ).data


class ShoppingCartCreateSerializer(BaseUserRecipeSerializer):
    """Сериализатор для создания подписки."""

    class Meta:
        fields = BaseUserRecipeSerializer.Meta.fields
        model = ShoppingCart
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=["user", "recipe"],
                message="Ошибка, вы уже добавили рецепт в корзину",
            ),
        ]


class FavoriteCreateSerializer(BaseUserRecipeSerializer):
    """Сериализатор для создания подписки."""

    class Meta:
        fields = BaseUserRecipeSerializer.Meta.fields
        model = Favorite
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=["user", "recipe"],
                message="Ошибка, вы уже добавили рецепт в избранное",
            ),
        ]
