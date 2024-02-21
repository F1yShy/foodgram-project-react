from collections import defaultdict

import django_filters
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (AbridgedRecipeSerializer, IngredientSerializer,
                             RecipeCreateAndUpdateSerializer,
                             RecipeReadSerializer, SubscribeSerializer,
                             TagSerializer)
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription


class CustomUserViewSet(UserViewSet):
    """
    Вьюсет для операций с пользователями.
    """

    pagination_class = LimitPageNumberPagination
    permission_classes = [AllowAny]

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, *args, **kwargs):
        author = self.get_object()
        if request.method == "POST":
            if author == request.user:
                return Response(
                    {"errors": "Вы не можете подписаться на себя"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Subscription.objects.filter(author=author).exists():
                return Response(
                    {"errors": "Вы уже подписаны на данного пользователя"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            subscribe = Subscription.objects.create(
                user=request.user, author=author
            )
            serializer = SubscribeSerializer(
                subscribe, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            if Subscription.objects.filter(
                user=request.user, author=author
            ).exists():
                subscription = Subscription.objects.get(
                    user=request.user, author=author
                )
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            return Response(
                {"errors": "Вы не подписаны на данного пользователя"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return None

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        queryset = Subscription.objects.filter(user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={"request": request},
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет с операцией GET, реализующий получение списка тегов и
    получением информации о теге по id.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет с операциями GET, POST, PATCH, DELETE,
    реализующий получение списка рецептов, созданием рецепта,
    получением, обновлением и удалением рецептов по id.
    """

    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = LimitPageNumberPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return RecipeReadSerializer
        return RecipeCreateAndUpdateSerializer

    def add_item(self, model, user, pk):
        if not Recipe.objects.filter(pk=pk).exists():
            return Response(
                {"errors": "Невозможно добавить несуществующий рецепт"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        recipe = get_object_or_404(Recipe, pk=pk)
        item = model.objects.filter(user=user, recipe=recipe)
        if item.exists():
            return Response(
                {"errors": "Невозможно повторно добавить"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        model.objects.create(user=user, recipe=recipe)
        serializer = AbridgedRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_item(self, model, user, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        item = model.objects.filter(user=user, recipe=recipe)
        if item.exists():
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "Ошибка! Рецепт не существует"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="favorite",
        url_name="favorite",
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        if request.method == "POST":
            return self.add_item(Favorite, request.user, pk)
        if request.method == "DELETE":
            return self.delete_item(Favorite, request.user, pk)
        return None

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="shopping_cart",
        url_name="shopping_cart",
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        if request.method == "POST":
            return self.add_item(ShoppingCart, request.user, pk)
        if request.method == "DELETE":
            return self.delete_item(ShoppingCart, request.user, pk)
        return None

    @action(
        detail=False,
        methods=["GET"],
        url_path="download_shopping_cart",
        url_name="download_shopping_cart",
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        shopping_list = []

        ingredients = defaultdict(int)
        items = ShoppingCart.objects.filter(user=request.user).select_related(
            "recipe"
        )
        for item in items:
            ingredient_recipes = IngredientRecipe.objects.filter(
                recipe=item.recipe
            )
            for ingredient_recipe in ingredient_recipes:
                ingredient_name = (
                    ingredient_recipe.ingredient.name.capitalize()
                )
                measurement_unit = (
                    ingredient_recipe.ingredient.measurement_unit
                )
                amount = ingredient_recipe.amount
                ingredients[(ingredient_name, measurement_unit)] += amount

        shopping_list.append("Список покупок\n")

        for i, (ingredient, amount) in enumerate(ingredients.items(), start=1):
            ingredient_name = ingredient[0]
            shopping_list.append(
                f"{i}. {ingredient_name} ({ingredient[1]}) - {amount}\n"
            )

        response = HttpResponse(shopping_list, content_type="text/plain")
        response["Content-Disposition"] = (
            'attachment; filename="shopping_list.txt"'
        )

        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет с операцией GET, реализующий получение списка ингредиентов и
    получением информации об ингредиенте по id.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = None
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = IngredientFilter
    search_fields = ("name",)
