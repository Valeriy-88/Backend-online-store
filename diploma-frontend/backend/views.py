from django.contrib.auth import authenticate, login
from django.db.models import Prefetch, Count
from django.http import JsonResponse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
import datetime

from .serializers import (
    ItemSerializer,
    ReviewSerializer,
    TagSerializer,
    UserSerializer,
    PasswordUserSerializer,
    CatalogSerializer,
    CatalogItemsSerializer,
    SalesSerializer,
    BasketItemSerializer,
    BannerSerializer,
)
from .models import (
    Item, Tag,
    Profile, Catalog,
    Category, Basket,
    BasketItem, UserAvatar,
)


class AvatarProfileView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        avatar = UserAvatar.objects.get(avatar_id=request.user.id)
        id = avatar.id
        avatar.delete()
        image = request.FILES['avatar']
        UserAvatar.objects.create(id=id, src=image, avatar_id=request.user.id)
        return Response(status=status.HTTP_205_RESET_CONTENT)


class PasswordProfileView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data_user = json.loads(request.body)
        data_user['password'] = data_user['currentPassword']
        instance = Profile.objects.get(id=request.user.id)
        serializer = PasswordUserSerializer(data=data_user, instance=instance, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"post": serializer.data}, status=status.HTTP_205_RESET_CONTENT)


class ProfileView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = Profile.objects.filter(fullName=request.user)
        serializer = UserSerializer(profile, many=True)
        return Response(*serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        avatar = UserAvatar.objects.get(avatar_id=request.user.id)
        data_user = json.loads(request.body)
        data_user['avatar']['src'] = avatar.src
        instance = Profile.objects.get(id=request.user.id)
        serializer = UserSerializer(data=data_user, instance=instance, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_205_RESET_CONTENT)


class RegisterView(APIView):
    def post(self, request):
        data_user = json.loads(request.body)
        data_user['fullName'] = data_user.pop('name')
        serializer = UserSerializer(data=data_user)
        if serializer.is_valid():
            serializer.save()
            user = authenticate(request, username=data_user['username'],
                                password=data_user['password'])
            login(request, user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        data_user = json.loads(request.body)
        username = data_user['username']
        password = data_user['password']
        user = None
        if not user:
            user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class CatalogMenuView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        categories_data = []
        for category in categories:
            subcategories = category.subcategory_set.all()
            subcategories_data = []
            for subcategory in subcategories:
                data_sub = {
                    'id': subcategory.pk,
                    'title': subcategory.title,
                    'image': subcategory.get_image(),
                }
                subcategories_data.append(data_sub)
            data_cat = {
                'id': category.pk,
                'title': category.title,
                'image': category.get_image(),
                'subcategories': subcategories_data,
            }
            categories_data.append(data_cat)

        return JsonResponse(categories_data, safe=False)


class CatalogItemsView(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    serializer_class = CatalogItemsSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = [
        'rating',
        'price',
        'reviews',
        'date',
    ]

    def get_queryset(self):
        sort = self.request.query_params.get('sort')
        if sort == '' or sort is None:
            sort = 'price'

        sortType = self.request.query_params.get('sortType')
        if sortType == '' or sortType is None:
            sortType = 'inc'

        if sortType == 'dec':
            sort = '-' + sort

        if sort == 'reviews':
            queryset = Item.objects.all().annotate(cnt=Count('reviews')).order_by('cnt')
        elif sort == '-reviews':
            queryset = Item.objects.all().annotate(cnt=Count('reviews')).order_by('-cnt')
        else:
            queryset = Item.objects.all().order_by(sort)

        title = self.request.query_params.get('filter[name]')
        title = None if title == '' else title

        price_min = self.request.query_params.get('filter[minPrice]')
        price_max = self.request.query_params.get('filter[maxPrice]')

        freeDelivery = self.request.query_params.get('filter[freeDelivery]')

        category = self.request.query_params.get('category')
        if category is not None:
            if category == '3':
                category = 2
            queryset = queryset.filter(category=category)

        if freeDelivery == '' or freeDelivery is None:
            freeDelivery = True
        else:
            freeDelivery = freeDelivery.title()

        available = self.request.query_params.get('filter[available]')
        if available == '' or available is None:
            available = True
        else:
            available = available.title()

        limit = int(self.request.query_params.get('limit')) \
            if self.request.query_params.get('limit') is not None else 20

        if title is not None:
            queryset = queryset.filter(title=title)

        if price_min != 0 or price_max != 50000:
            queryset = queryset.filter(price__range=[price_min, price_max])

        if freeDelivery:
            queryset = queryset.filter(freeDelivery=freeDelivery)

        else:
            queryset = queryset.filter(freeDelivery=freeDelivery)

        if available:
            queryset = queryset.filter(count__gt=0)
        else:
            queryset = queryset.filter(count=0)

        return queryset.filter(pk__lte=limit)

    def list(self, request, *args, **kwargs):
        a = dict(request.query_params.lists())
        if a != {}:
            catalog = (
                Catalog.objects.
                prefetch_related(Prefetch(
                    'items', queryset=self.get_queryset()))
            )
            serializer = CatalogSerializer(catalog, many=True)
            return Response(*serializer.data, status=status.HTTP_200_OK)

        catalog = Catalog.objects.all()
        serializer = CatalogSerializer(catalog, many=True)
        return Response(*serializer.data, status=status.HTTP_200_OK)


class ItemPopularView(APIView):
    def get(self, request):
        item = (
            Item.objects
            .prefetch_related("images", "reviews")
            .filter(count__gt=0).order_by('-rating')[:10]
        )
        serializer = BannerSerializer(item, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ItemLimitedView(APIView):
    def get(self, request):
        item = (
            Item.objects
            .prefetch_related("images", "reviews")
            .filter(count__gt=0).order_by('-rating')[:10]
        )
        serializer = BannerSerializer(item, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SalesView(APIView):
    pagination_class = PageNumberPagination

    def get(self, request):
        catalog = (
            Catalog.objects
            .prefetch_related(Prefetch(
                'items',
                queryset=Item.objects.filter(freeDelivery=True)))
        )
        serializer = SalesSerializer(catalog, many=True)
        return Response(*serializer.data, status=status.HTTP_200_OK)


class BannersView(APIView):
    def get(self, request):
        item = (
            Item.objects
            .prefetch_related("images", "reviews")
            .filter(rating__gt=0).order_by('-rating')[:3]
        )
        serializer = BannerSerializer(item, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BasketView(APIView):
    def get(self, request):
        if request.user.is_anonymous:
            anon_user = Profile.objects.get(username='anonymous')
            request.user = Profile.objects.get(id=anon_user.id)

        queryset = BasketItem.objects.filter(basket__profile=request.user)
        serializer = BasketItemSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        id = request.data['id']
        count = request.data['count']

        if request.user.is_anonymous:
            anon_user = Profile.objects.get(username='anonymous')
            basket, created = Basket.objects.update_or_create(profile=anon_user)
            basket = Basket.objects.get(profile=anon_user)
        else:
            try:
                basket = request.user.baskets
            except BaseException:
                basket = Basket.objects.create(profile=request.user)

        item = Item.objects.get(id=id)
        if item.count < count:
            return Response('Превышено количество имеющегося товара', status=status.HTTP_400_BAD_REQUEST)

        basket_item, created = BasketItem.objects.get_or_create(item=item, basket=basket)

        basket_item.quantity += count
        basket_item.save()

        basket_items = BasketItem.objects.filter(basket=basket)
        serializer = BasketItemSerializer(basket_items, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        id = request.data['id']
        count = request.data['count']

        try:
            if request.user.is_anonymous:
                anon_user = Profile.objects.get(username='anonymous')
                request.user = Profile.objects.get(id=anon_user.id)

            basket = request.user.baskets

            item = Item.objects.get(id=id)

            basket_item = BasketItem.objects.get(basket=basket, item=item)
            if basket_item.quantity > count:
                basket_item.quantity -= count
                basket_item.save()
            else:
                basket_item.delete()

            basket_items = BasketItem.objects.filter(basket=basket)
            serializer = BasketItemSerializer(basket_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Basket.DoesNotExist:
            return Response('Товары в корзине не найдены', status=status.HTTP_404_NOT_FOUND)


class TagsListView(APIView):
    def get(self, request):
        tag = Tag.objects.all()
        serializer = TagSerializer(tag, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ItemDetailView(APIView):
    def get(self, request, id):
        item = (
            Item.objects
            .prefetch_related("images", "reviews")
            .get(id=id)
        )
        serializer = ItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewCreateView(APIView):
    def post(self, request, id):
        current_date = datetime.datetime.now()
        current_date_string = current_date.strftime("%Y-%m-%d %H:%M")
        request.data['date'] = current_date_string
        request.data['item'] = id

        profile = Profile.objects.get(fullName=request.data['author'].title())
        request.data['author'] = profile.pk
        review = ReviewSerializer(data=request.data)
        if review.is_valid(raise_exception=True):
            review.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)
