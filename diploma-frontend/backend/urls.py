from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    TagsListView,
    ProductsListView,
    ReviewCreateView,
    RegisterView,
    LoginView,
)

app_name = "backend"

urlpatterns = [
    path('sign-in', LoginView.as_view(), name='sign-in'),
    path('sign-up', RegisterView.as_view(), name='sign-up'),
    path('sign-out', LogoutView.as_view(), name='sign-out'),
    # path('profile/', ProfileView.as_view(), name='profile'),
    # path('profile/password/', , name='profile_password'),
    # path('profile/avatar/', , name='profile_avatar'),
    path('tags/', TagsListView.as_view(), name='tags'),
    path('product/<int:id>/', ProductsListView.as_view(), name='product_id'),
    path('product/<int:id>/review/', ReviewCreateView.as_view(), name='product_id_review'),
]
