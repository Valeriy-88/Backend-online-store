from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView

from .serializers import ProductSerializer, AuthorSerializer, TagSerializer, UserSerializer
from .models import Product, Tag


# class ProfileView(APIView):
#     def get(self, request):
#         profile = Profile.objects.all()
#         serializer = UserSerializer(profile, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         return Response(template_name="frontend/profile.html")


class RegisterView(APIView):
    def post(self, request):
        data_user = json.loads(request.body)
        data_user['last_name'] = data_user.pop('name')
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


class TagsListView(APIView):
    def get(self, request):
        tag = Tag.objects.all()
        serializer = TagSerializer(tag, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductsListView(APIView):
    def get(self, request, id):
        product = Product.objects.filter(id=id)
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewCreateView(APIView):
    def post(self, request, id):
        request.data['product'] = id
        review = AuthorSerializer(data=request.data)
        if review.is_valid():
            review.save()
        return Response(status=status.HTTP_201_CREATED)
