from django.urls import include, path
from rest_framework import routers
from users.views import TokenViewSet, UserViewSet

users_router = routers.DefaultRouter()
users_router.register('users', UserViewSet)

token_router = routers.DefaultRouter()
token_router.register('token', TokenViewSet, basename='token')

urlpatterns = [
    path('', include(users_router.urls)),
    path('auth/', include(token_router.urls)),
]
