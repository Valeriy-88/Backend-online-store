from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    TagsListView,
    ItemDetailView,
    ReviewCreateView,
    RegisterView,
    LoginView,
    ProfileView,
    PasswordProfileView,
    AvatarProfileView,
    CatalogMenuView,
    CatalogItemsView,
    ItemPopularView,
    ItemLimitedView,
    SalesView,
    BannersView,
    BasketView,
    OrdersView, OrderDetailView,
)

app_name = "backend"

urlpatterns = [
    path('sign-in', LoginView.as_view(), name='sign-in'),
    path('sign-up', RegisterView.as_view(), name='sign-up'),
    path('sign-out', LogoutView.as_view(), name='sign-out'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('profile/password', PasswordProfileView.as_view(), name='profile_password'),
    path('profile/avatar', AvatarProfileView.as_view(), name='profile_avatar'),
    path('categories/', CatalogMenuView.as_view(), name='categories'),
    path('catalog/', CatalogItemsView.as_view({'get': 'list'}), name='catalog'),
    path('products/popular/', ItemPopularView.as_view(), name='products_popular'),
    path('products/limited/', ItemLimitedView.as_view(), name='products_limited'),
    path('sales/', SalesView.as_view(), name='sales'),
    path('banners/', BannersView.as_view(), name='banners'),
    path('tags/', TagsListView.as_view(), name='tags'),
    path('basket', BasketView.as_view(), name='basket'),
    path('orders', OrdersView.as_view(), name='orders'),
    path('order/<int:id>', OrderDetailView.as_view(), name='orders_id'),
    path('product/<int:id>/', ItemDetailView.as_view(), name='product'),
    path('product/<int:id>/reviews', ReviewCreateView.as_view(), name='product_id_reviews'),
]
