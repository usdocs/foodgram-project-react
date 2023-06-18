from django.shortcuts import get_object_or_404
from rest_framework import mixins, status
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.include.pagination import PageNumberLimitPagination
from api.serializers import UserSubscribeSerializer
from users.models import Follow, User
from users.serializers import (TokenSerializer, UserCreateSerializer,
                               UserSerializer)


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberLimitPagination

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        user = get_object_or_404(User, username=self.request.user.username)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request):
        user = get_object_or_404(User, username=self.request.user.username)
        if not check_password(request.data['current_password'], user.password):
            return Response(
                {'Введен неверный пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(request.data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
        serializer_class=UserSubscribeSerializer,
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(
            following__user=self.request.user
        )
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        serializer_class=UserSubscribeSerializer
    )
    def subscribe(self, request, pk):
        following_user = get_object_or_404(User, id=pk)
        user = get_object_or_404(User, username=self.request.user.username)
        if request.method == 'DELETE':
            if not user.follower.filter(following=following_user).exists():
                return Response(
                    {'Вы не подписаны на данного пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                user.follower.filter(following=following_user).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        subscribe, created = Follow.objects.get_or_create(
            user=user,
            following=following_user
        )
        if not created:
            return Response(
                {'Вы уже подписаны на данного пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(following_user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TokenViewSet(GenericViewSet):
    serializer_class = TokenSerializer

    @action(
        detail=False,
        methods=['post'],
    )
    def login(self, request):
        """Выдает токен авторизации по емейлу и паролю"""
        if not User.objects.filter(email=request.data['email']).exists():
            return Response(
                {'Пользователя с таким email не существует'},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            user = User.objects.get(email=request.data['email'])
        if not check_password(request.data['password'], user.password):
            return Response(
                {'Введен неверный пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )
        token, created = Token.objects.get_or_create(user=user)
        if created:
            stat = status.HTTP_201_CREATED
        else:
            stat = status.HTTP_200_OK
        response = {'auth_token': str(token)}
        return Response(response, status=stat)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=(IsAuthenticated,),
    )
    def logout(self, request):
        """Удаляет токен авторизации"""
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
