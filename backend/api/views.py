from api.include.filters import IngredientFilter, RecipeFilter
from api.include.pagination import PageNumberLimitPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CreateRecipeSerializer, IngredientSerializer,
                             RecipeSerializer, TagSerializer,
                             ViewRecipeSerializer)
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from users.models import User


class TagsViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = PageNumberLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CreateRecipeSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        print(RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=self.request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ))
        recipe_ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=self.request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        shopping_list = ''
        for ingredient in recipe_ingredients:
            shopping_list += (
                f"{ingredient['ingredient__name']} - "
                f"{ingredient['amount']} "
                f"{ingredient['ingredient__measurement_unit']}\n"
            )
        return HttpResponse(shopping_list, content_type='text/plain')

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        shopping_cart_recipe = get_object_or_404(Recipe, id=pk)
        user = get_object_or_404(User, username=self.request.user.username)
        if request.method == 'DELETE':
            shopping_cart = (
                user.shopping_cart.filter(recipe=shopping_cart_recipe).first()
            )
            if shopping_cart:
                shopping_cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'Рецепт отсутствует в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_cart, created = ShoppingCart.objects.get_or_create(
            user=user,
            recipe=shopping_cart_recipe
        )
        if not created:
            return Response(
                {'Рецепт уже добавлен в список покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ViewRecipeSerializer(
            shopping_cart_recipe
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        favorite_recipe = get_object_or_404(Recipe, id=pk)
        user = get_object_or_404(User, username=self.request.user.username)
        if request.method == 'DELETE':
            favorite = user.favorite.filter(recipe=favorite_recipe).first()
            if favorite:
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'Рецепт отсутствует в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite, created = Favorite.objects.get_or_create(
            user=user,
            recipe=favorite_recipe
        )
        if not created:
            return Response(
                {'Рецепт уже добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ViewRecipeSerializer(favorite_recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class IngredientsViewSet(mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
