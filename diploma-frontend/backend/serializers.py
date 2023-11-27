from rest_framework import serializers
from .models import (
    Item,
    Review,
    Specification,
    Tag,
    ItemImage,
    Profile,
    Catalog,
)


class AvatarUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['avatar']

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


class PasswordUserSerializer(serializers.ModelSerializer):
    newPassword = serializers.CharField(max_length=200)

    class Meta:
        model = Profile
        fields = ['newPassword', 'password']

    def update(self, instance, validated_data):
        for newPassword in PasswordUserSerializer.Meta.fields: setattr(instance, newPassword,
                                                                       validated_data[newPassword])
        instance.set_password(validated_data['newPassword'])
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['username', 'fullName', 'password', 'email', 'phone', 'avatar']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = Profile(
            username=validated_data['username'],
            fullName=validated_data['fullName']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.fullName = validated_data.get('fullName', instance.fullName)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.email = validated_data.get('email', instance.email)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        exclude = ['id', 'item']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        exclude = ['item']


class ItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemImage
        exclude = ['id', 'item']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        exclude = ['id']


class ItemSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%A %B %d %Y %H:%M:%S")
    reviews = ReviewSerializer(many=True)
    specifications = SpecificationSerializer(many=True)
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )
    images = ItemImageSerializer(many=True)
    catalog_id = serializers.IntegerField(default=1)

    class Meta:
        model = Item
        fields = ('id', 'category', 'price', 'count', 'date', 'title', 'description', 'fullDescription',
                  'freeDelivery', 'images', 'tags', 'reviews', 'specifications', 'rating', 'catalog_id')
        depth = 1


class SubcategorySerializer(serializers.ModelSerializer):
    images = ItemImageSerializer(many=True)

    class Meta:
        model = Item
        fields = ['id', 'title', 'images']


class CatalogMenuSerializer(serializers.ModelSerializer):
    images = ItemImageSerializer(many=True)
    subcategories = SubcategorySerializer(source="*")

    class Meta:
        model = Item
        fields = ['id', 'title', 'images', 'subcategories']
        depth = 1


class CatalogItemsSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%A %B %d %Y %H:%M:%S")
    reviews = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    images = ItemImageSerializer(many=True)

    class Meta:
        model = Item
        fields = ('id', 'category', 'price', 'count', 'date', 'title', 'description',
                  'freeDelivery', 'images', 'tags', 'reviews', 'rating')
        depth = 1

    def get_reviews(self, obj):
        return obj.reviews.count()


class CatalogSerializer(serializers.ModelSerializer):
    items = CatalogItemsSerializer(many=True)

    class Meta:
        model = Catalog
        fields = ['items', 'currentPage', 'lastPage']


class FilteredListSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        data = data.filter(freeDelivery=True)
        return super(FilteredListSerializer, self).to_representation(data)


class SalesItemsSerializer(serializers.ModelSerializer):
    dateFrom = serializers.DateField(format="%m-%d")
    dateTo = serializers.DateField(format="%m-%d")
    images = ItemImageSerializer(many=True)

    class Meta:
        list_serializer_class = FilteredListSerializer
        model = Item
        fields = ('id', 'price', 'silePrice', 'dateFrom', 'dateTo', 'title', 'images')
        depth = 1


class SalesSerializer(serializers.ModelSerializer):
    items = SalesItemsSerializer(many=True)

    class Meta:
        model = Catalog
        fields = ['items', 'currentPage', 'lastPage']

