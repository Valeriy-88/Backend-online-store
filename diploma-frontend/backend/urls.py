from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    TagsListView,
    ProductsListView,
    ReviewCreateView,
    RegisterView,
    LoginView,
    ProfileView,
    PasswordProfileView,
    AvatarProfileView,
)

app_name = "backend"

urlpatterns = [
    path('sign-in', LoginView.as_view(), name='sign-in'),
    path('sign-up', RegisterView.as_view(), name='sign-up'),
    path('sign-out', LogoutView.as_view(), name='sign-out'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('profile/password', PasswordProfileView.as_view(), name='profile_password'),
    path('profile/avatar', AvatarProfileView.as_view(), name='profile_avatar'),
    # path('categories', , name='categories'),
    # path('catalog', , name='catalog'),
    # path('products/popular', , name='products_popular'),
    # path('products/limited', , name='products_limited'),
    # path('sales', , name='sales'),
    # path('banners', , name='banners'),
    path('tags/', TagsListView.as_view(), name='tags'),
    path('product/<int:id>/', ProductsListView.as_view(), name='product_id'),
    path('product/<int:id>/review/', ReviewCreateView.as_view(), name='product_id_review'),
]
