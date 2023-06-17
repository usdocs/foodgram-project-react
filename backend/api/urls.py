from django.urls import include, path
from rest_framework import routers

from api.views import IngredientsViewSet, RecipeViewSet, TagsViewSet


v1_router = routers.DefaultRouter()
v1_router.register('tags', TagsViewSet, basename='tags')
v1_router.register('recipes', RecipeViewSet, basename='recipes')
v1_router.register('ingredients', IngredientsViewSet, basename='ingredients')


urlpatterns = [
    path('', include(v1_router.urls)),
]
