from rest_framework import serializers
from .models import Product, Author, Specification, Tag, ProductImage


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        exclude = ['id', 'product']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        exclude = ['id', 'product']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        exclude = ['id', 'product']


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        exclude = ['id', 'product']


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

