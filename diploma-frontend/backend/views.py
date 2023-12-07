import django_filters
from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from .serializers import (
    ItemSerializer,
    ReviewSerializer,
    TagSerializer,
    UserSerializer,
    PasswordUserSerializer,
    AvatarUserSerializer,
    CatalogMenuSerializer,
    CatalogSerializer,
    CatalogItemsSerializer,
    SalesSerializer,
)
from .models import Item, Tag, Profile, Catalog, Subcategory


class AvatarProfileView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        instance = Profile.objects.get(id=request.user.id)
        serializer = AvatarUserSerializer(data=request.data, instance=instance, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"post": serializer.data}, status=status.HTTP_205_RESET_CONTENT)


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
        profile = Profile.objects.filter(username=request.user)
        serializer = UserSerializer(profile, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data_user = json.loads(request.body)
        instance = Profile.objects.get(id=request.user.id)
        serializer = UserSerializer(data=data_user, instance=instance, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"post": serializer.data}, status=status.HTTP_205_RESET_CONTENT)


class RegisterView(APIView):
    def post(self, request):
        data_user = json.loads(request.body)
        data_user['fullName'] = data_user.pop('name')
        serializer = UserSerializer(data=data_user)
        if serializer.is_valid():
            serializer.save()
            user = authenticate(request, username=data_user['username'], password=data_user['password'])
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
        subcategory = Subcategory.objects.all()
        serializer = CatalogMenuSerializer(subcategory, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ItemFilter(filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='in')
    price = filters.RangeFilter(field_name='price', lookup_expr='in')
    freeDelivery = filters.BooleanFilter(field_name='freeDelivery', lookup_expr='in')
    available = filters.BooleanFilter(field_name='available')

    class Meta:
        model = Item
        fields = ['name', 'price', 'freeDelivery', ]


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
        queryset = Item.objects.all()

        title = self.request.query_params.get('filter[name]')
        title = None if title == '' else title

        price_min = self.request.query_params.get('filter[minPrice]')
        price_max = self.request.query_params.get('filter[maxPrice]')

        freeDelivery = self.request.query_params.get('filter[freeDelivery]')
        if freeDelivery == '' or freeDelivery is None:
            freeDelivery = True
        else:
            freeDelivery = freeDelivery.title()

        available = self.request.query_params.get('filter[available]')
        if available == '' or available is None:
            available = True
        else:
            available = available.title()

        sort = self.request.query_params.get('sort')
        if sort == '' or sort is None:
            sort = 'price'

        sortType = self.request.query_params.get('sortType')
        if sortType == '' or sortType is None:
            sortType = 'inc'

        limit = self.request.query_params.get('limit')

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
        if sortType == ['dec']:
            sort = '-' + sort

        return queryset.order_by(sort)[:20]

    def list(self, request, *args, **kwargs):
        x = {
            'filter[name]': [''],
            'filter[minPrice]': ['0'],
            'filter[maxPrice]': ['50000'],
            'filter[freeDelivery]': ['false'],
            'filter[available]': ['true'],
            'currentPage': ['1'],
            'sort': ['price'],
            'sortType': ['inc'],
            'limit': ['20']
        }
        a = dict(request.query_params.lists())

        ser = self.get_serializer(self.get_queryset(), many=True)
        catalog = Catalog.objects.all()
        serializer = CatalogSerializer(catalog, many=True)

        #print(ser.data)
        s1 = serializer.data[0]
        #s1['items'] = ser.data
        #print(s1)
        return Response(s1, status=status.HTTP_200_OK)


class ItemPopularView(APIView):
    def get(self, request):
        item = (
            Item.objects
            .prefetch_related("specifications", "images", "reviews")
            .all())
        serializer = CatalogItemsSerializer(item, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ItemLimitedView(APIView):
    def get(self, request):
        item = (
            Item.objects
            .prefetch_related("specifications", "images", "reviews")
            .all())
        serializer = CatalogItemsSerializer(item, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SalesView(APIView):
    pagination_class = PageNumberPagination

    def get(self, request):
        catalog = (
            Catalog.objects
            .prefetch_related('items')
            .all())
        serializer = SalesSerializer(catalog, many=True)
        return Response(*serializer.data, status=status.HTTP_200_OK)


class BannersView(APIView):
    def get(self, request):
        item = (
            Item.objects
            .prefetch_related("specifications", "images", "reviews")
            .all())
        serializer = CatalogItemsSerializer(item, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagsListView(APIView):
    def get(self, request):
        tag = Tag.objects.all()
        serializer = TagSerializer(tag, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ItemDetailView(APIView):
    def get(self, request, id):
        item = (
            Item.objects
            .prefetch_related("specifications", "images", "reviews")
            .filter(id=id))
        serializer = ItemSerializer(item, many=True)
        return Response(*serializer.data, status=status.HTTP_200_OK)


class ReviewCreateView(APIView):
    def post(self, request, id):
        request.data['item'] = id
        review = ReviewSerializer(data=request.data)
        if review.is_valid():
            review.save()
        return Response(status=status.HTTP_201_CREATED)
