import base64

from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from core.constraints import MAX_USERNAME_LENGTH
from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag
from users.models import CustomUser, Subscription


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""

    username = serializers.CharField(
        max_length=MAX_USERNAME_LENGTH,
        validators=[
            UniqueValidator(
                queryset=CustomUser.objects.all(),
            ),
            RegexValidator(regex=r"^[\w.@+-]+\Z"),
        ],
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
        )


class CustomUserSerializer(UserSerializer):
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
        """Возвращает подписан ли пользователь на автора"""
        user = self.context.get("request").user
        if user.is_authenticated:
            return Subscription.objects.filter(user=user, author=obj).exists()
        return False


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки."""

    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    email = serializers.ReadOnlyField(source="author.email")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        """Возввращает подписан ли пользователь на автора."""
        return Subscription.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        """Возвращает список рецептов."""
        request = self.context["request"]
        limit = request.GET.get("recipes_limit")
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[: int(limit)]
        return AbridgedRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        """Возвращает количество рецептов."""
        return Recipe.objects.filter(author=obj.id).count()


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


class BaseConvert64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


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
    image = BaseConvert64ImageField()

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
        """Возвращает, находится ли рецепт в избранном."""
        user = self.context["request"].user
        if user.is_authenticated:
            return Recipe.objects.filter(
                favorite__user=user, id=obj.id
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Возвращает, находится ли рецепт в корзине."""
        user = self.context["request"].user
        if user.is_authenticated:
            return Recipe.objects.filter(
                shoppingcart__user=user, id=obj.id
            ).exists()
        return False


class IngredientCreateInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания ингредиентов в рецепте."""

    id = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ("id", "amount")

    def validate(self, data):
        if not Ingredient.objects.filter(pk=data.get("id")).exists():
            raise serializers.ValidationError(
                f'Отсутствует ингредиент с id={data.get("id")}'
            )
        return data


class AbridgedRecipeSerializer(serializers.ModelSerializer):
    """Сокращенный сериализатор рецепта."""

    image = BaseConvert64ImageField(read_only=True)

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

    image = BaseConvert64ImageField()
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

    def validate(self, data):
        ingredients = data.get("ingredients")
        cooking_time = data.get("cooking_time")
        tags = data.get("tags")

        if not ingredients:
            raise serializers.ValidationError("Поле ingredients обязательно")

        if not cooking_time:
            raise serializers.ValidationError("Поле cooking_time обязательно")

        if not tags:
            raise serializers.ValidationError("Поле tags обязательно")

        ingredients_ids = {ingredient["id"] for ingredient in ingredients}
        if len(ingredients_ids) != len(ingredients):
            raise serializers.ValidationError(
                "Требуются неповторяющиеся ингредиенты"
            )

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError("Требуются неповторяющиеся теги")

        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        author = self.context.get("request").user

        recipe = Recipe.objects.create(author=author, **validated_data)

        ingredient_objects = [
            IngredientRecipe(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient_data["id"]),
                amount=ingredient_data["amount"],
            )
            for ingredient_data in ingredients_data
        ]

        IngredientRecipe.objects.bulk_create(ingredient_objects)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        instance.name = validated_data.get("name", instance.name)
        instance.image = validated_data.get("image", instance.image)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )

        instance.save()
        instance.ingredients.clear()
        for ingredient_data in ingredients_data:
            IngredientRecipe.objects.create(
                recipe=instance,
                ingredient=Ingredient.objects.get(pk=ingredient_data["id"]),
                amount=ingredient_data["amount"],
            )

        instance.tags.set(tags_data)

        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data
