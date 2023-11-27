from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from django.shortcuts import render
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

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
from .models import Item, Tag, Profile, Catalog


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
        item = (
                Item.objects
                .prefetch_related("images")
                .all())
        serializer = CatalogMenuSerializer(item, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CatalogItemsView(APIView):
    def get(self, request):
        catalog = Catalog.objects.all()
        serializer = CatalogSerializer(catalog, many=True)
        return Response(*serializer.data, status=status.HTTP_200_OK)


class ItemPopularView(APIView):
    def get(self, request):
        item = (
            Item.objects
            .prefetch_related("specifications", "tags", "images", "reviews")
            .all())
        serializer = CatalogItemsSerializer(item, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ItemLimitedView(APIView):
    def get(self, request):
        item = (
            Item.objects
            .prefetch_related("specifications", "tags", "images", "reviews")
            .all())
        serializer = CatalogItemsSerializer(item, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SalesView(APIView):
    def get(self, request):
        catalog = Catalog.objects.all()
        serializer = SalesSerializer(catalog, many=True)
        return Response(*serializer.data, status=status.HTTP_200_OK)


class BannersView(APIView):
    def get(self, request):
        item = (
            Item.objects
            .prefetch_related("specifications", "tags", "images", "reviews")
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
                .prefetch_related("specifications", "tags", "images", "reviews")
                .filter(id=id))
        serializer = ItemSerializer(item, many=True)
        # print("*" * 50)
        # print(*serializer.data)
        print("*" * 50)
        return Response(*serializer.data, status=status.HTTP_200_OK)

    def post(self, request, id):
        item = ItemSerializer(data=request.data)
        print(item)
        if item.is_valid():
            item.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response({"status": "error", "data": item.errors})


class ReviewCreateView(APIView):
    def post(self, request, id):
        request.data['item'] = id
        review = ReviewSerializer(data=request.data)
        if review.is_valid():
            review.save()
        return Response(status=status.HTTP_201_CREATED)
