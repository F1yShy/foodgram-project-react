from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                       TagViewSet)

v1_router = DefaultRouter()
v1_router.register("tags", TagViewSet, basename="tag")
v1_router.register("ingredients", IngredientViewSet, basename="ingredient")
v1_router.register("recipes", RecipeViewSet, basename="recipe")
v1_router.register("users", CustomUserViewSet, basename="users")

urlpatterns = [
    path("", include(v1_router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
