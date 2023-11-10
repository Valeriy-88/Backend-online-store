from rest_framework import serializers
from .models import Product, Author, Specification, Tag, ProductImage, Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['username', 'last_name', 'password', 'email', 'phone', 'avatar']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = Profile(
            username=validated_data['username'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        exclude = ['id', 'product']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        exclude = ['product']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        exclude = ['id', 'product']


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        exclude = ['id']


class ProductSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%A %B %d %Y %H:%M:%S")
    authors = AuthorSerializer(many=True)
    specifications = SpecificationSerializer(many=True)
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )
    images = ProductImageSerializer(many=True)

    class Meta:
        model = Product
        fields = ('id', 'category', 'price', 'count', 'date', 'title', 'description', 'fullDescription',
                 'freeDelivery', 'images', 'tags', 'authors', 'specifications', 'rating')
        depth = 1

