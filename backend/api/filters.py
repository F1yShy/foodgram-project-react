from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    """
    Фльтр для ингредиентов, позволяющий искать ингредиенты по имени.
    """

    name = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Ingredient
        fields = ["name"]


class RecipeFilter(FilterSet):
    """
    Фильтр для рецептов, позволяет фильтровать по полям:
    - тег
    - автор
    - в избранном
    - в корзине.
    """

    author = filters.NumberFilter(field_name="author__id")
    tags = filters.AllValuesMultipleFilter(field_name="tags__slug")
    is_favorited = filters.BooleanFilter(method="filter_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = ["author", "tags"]

    def filter_is_favorited(self, queryset, name, value):
        """Фильтр для рецептов по нахождению в избранном."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset.none()

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтр для рецептов по нахождению в корзине."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(shoppingcart__user=self.request.user)
        return queryset.none()
